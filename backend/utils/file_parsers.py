import base64
import io
import sys
from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageOps

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Settings

# Prevent decompression bomb attacks
Image.MAX_IMAGE_PIXELS = 100_000_000


class FileParsingError(Exception):
    """Base exception for file parsing failures."""
    pass


class UnsupportedFileTypeError(FileParsingError):
    """Raised when file magic bytes do not match permitted types."""
    pass


class FileTooLargeError(FileParsingError):
    """Raised when file exceeds MAX_UPLOAD_MB."""
    pass


class EmptyFileError(FileParsingError):
    """Raised when file payload is 0 bytes."""
    pass


class CorruptFileError(FileParsingError):
    """Raised when PDF or image decoding fails."""
    pass


@dataclass
class PreparedDocument:
    mime: str
    pages_b64: list[str]
    page_count: int
    truncated: bool


def detect_mime(file_bytes: bytes) -> str:
    """Inspect magic bytes to detect file MIME type strictly."""
    if not file_bytes:
        raise EmptyFileError("File payload is empty (0 bytes).")

    if file_bytes.startswith(b"%PDF-"):
        return "application/pdf"
    if file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if file_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if len(file_bytes) >= 12 and file_bytes[:4] == b"RIFF" and file_bytes[8:12] == b"WEBP":
        return "image/webp"

    raise UnsupportedFileTypeError(
        "Unsupported file type. Only PDF, PNG, JPG, and WEBP formats are accepted."
    )


def validate_size(file_bytes: bytes, max_mb: int) -> None:
    """Validate file payload size boundaries."""
    if len(file_bytes) == 0:
        raise EmptyFileError("Uploaded file is empty (0 bytes).")
    max_bytes = max_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise FileTooLargeError(
            f"File size ({len(file_bytes)} bytes) exceeds the allowed limit of {max_mb} MB."
        )


def pdf_to_images(
    file_bytes: bytes, dpi: int, max_pages: int
) -> tuple[list[Image.Image], bool]:
    """Convert PDF bytes into a list of PIL Images, handling pagination and truncation."""
    try:
        import pdf2image
        from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError
    except ImportError as e:
        raise CorruptFileError("pdf2image library is required for PDF parsing.") from e

    try:
        images = pdf2image.convert_from_bytes(
            file_bytes,
            dpi=dpi,
            first_page=1,
            last_page=max_pages + 1,
            fmt="jpeg",
        )
    except PDFInfoNotInstalledError as exc:
        raise CorruptFileError(
            "Poppler is not installed or not in system PATH. "
            "Please install poppler-utils (apt/brew) or download poppler binary on Windows."
        ) from exc
    except (PDFPageCountError, PDFSyntaxError) as exc:
        raise CorruptFileError(f"Corrupt or encrypted PDF file: {str(exc)}") from exc
    except Exception as exc:
        raise CorruptFileError(f"Failed to decode PDF: {str(exc)}") from exc

    if not images:
        raise CorruptFileError("PDF contains no readable pages.")

    truncated = len(images) > max_pages
    final_images = images[:max_pages]
    return final_images, truncated


def image_bytes_to_image(file_bytes: bytes) -> Image.Image:
    """Verify and safely load an image from bytes as an RGB PIL Image with bomb protection."""
    try:
        verify_stream = io.BytesIO(file_bytes)
        with Image.open(verify_stream) as img:
            img.verify()

        load_stream = io.BytesIO(file_bytes)
        image = Image.open(load_stream)
        image = ImageOps.exif_transpose(image)
        return image.convert("RGB")
    except Image.DecompressionBombError as dbe:
        raise CorruptFileError(f"Image exceeds safe decompression limits: {str(dbe)}") from dbe
    except Exception as exc:
        raise CorruptFileError(f"Corrupt or unreadable image: {str(exc)}") from exc


def downscale_if_needed(img: Image.Image, max_side: int = 2400) -> Image.Image:
    """Downscale image if longest side exceeds max_side while maintaining aspect ratio."""
    width, height = img.size
    max_dim = max(width, height)
    if max_dim <= max_side:
        return img

    scale = max_side / float(max_dim)
    new_width = int(round(width * scale))
    new_height = int(round(height * scale))
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)


def image_to_base64_jpeg(img: Image.Image, quality: int = 90) -> str:
    """Convert PIL image to raw base64 JPEG string (without data URI prefix)."""
    buffer = io.BytesIO()
    rgb_img = img if img.mode == "RGB" else img.convert("RGB")
    rgb_img.save(buffer, format="JPEG", quality=quality, optimize=True)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def prepare_document(file_bytes: bytes, settings: Settings) -> PreparedDocument:
    """End-to-end ingestion pipeline returning base64 JPEG strings for each document page."""
    validate_size(file_bytes, settings.MAX_UPLOAD_MB)
    mime = detect_mime(file_bytes)

    if mime == "application/pdf":
        pil_images, truncated = pdf_to_images(
            file_bytes,
            dpi=settings.PDF_RENDER_DPI,
            max_pages=settings.MAX_PDF_PAGES,
        )
    else:
        pil_img = image_bytes_to_image(file_bytes)
        pil_images = [pil_img]
        truncated = False

    pages_b64: list[str] = []
    for raw_img in pil_images:
        scaled = downscale_if_needed(raw_img, max_side=2400)
        b64 = image_to_base64_jpeg(scaled, quality=90)
        pages_b64.append(b64)

    return PreparedDocument(
        mime=mime,
        pages_b64=pages_b64,
        page_count=len(pages_b64),
        truncated=truncated,
    )
