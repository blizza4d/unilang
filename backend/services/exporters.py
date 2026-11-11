import codecs
import csv
from datetime import datetime, timezone
import io
import json
import zipfile
from typing import Any
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from db.models import DocumentRecord


def _sanitize_csv_cell(val: object) -> str:
    s = str(val if val is not None else "")
    if s.startswith(("=", "+", "-", "@")):
        return f"'{s}"
    return s


def export_json(doc: DocumentRecord, include_grounding: bool = True) -> bytes:
    data = json.loads(doc.result_json)
    created_at_iso = (
        doc.created_at.isoformat()
        if getattr(doc, "created_at", None)
        else datetime.now(timezone.utc).isoformat()
    )
    payload = {
        "document_id": doc.id,
        "filename": doc.filename,
        "sha256": doc.sha256,
        "created_at": created_at_iso,
        "status": doc.status,
        "extracted_data": data.get("extracted_data"),
        "validation_metrics": data.get("validation_metrics"),
        "processing_ms": getattr(doc, "processing_ms", 0),
        "source": data.get("source"),
        "is_demo": bool(data.get("is_demo") or getattr(doc, "is_demo", False)),
    }
    if include_grounding and doc.grounding_json:
        payload["grounding"] = json.loads(doc.grounding_json)
    return json.dumps(payload, indent=2).encode("utf-8")


def export_csv_zip(doc: DocumentRecord) -> bytes:
    data = json.loads(doc.result_json)
    invoice = data.get("extracted_data", {})
    items = invoice.get("line_items", [])
    is_demo = bool(
        data.get("source") == "demo_fixture"
        or data.get("is_demo")
        or getattr(doc, "is_demo", False)
    )

    # Header CSV
    header_io = io.StringIO()
    header_writer = csv.writer(header_io)
    header_writer.writerow(
        [
            "Invoice Number",
            "Vendor Name",
            "Date",
            "Currency",
            "Tax Amount",
            "Total Amount",
            "Status",
            "SHA256",
            "Provenance",
        ]
    )
    header_writer.writerow(
        [
            _sanitize_csv_cell(invoice.get("invoice_number", "")),
            _sanitize_csv_cell(invoice.get("vendor_name", "")),
            _sanitize_csv_cell(invoice.get("date", "")),
            _sanitize_csv_cell(invoice.get("currency", "")),
            _sanitize_csv_cell(invoice.get("tax_amount", 0.0)),
            _sanitize_csv_cell(invoice.get("total_amount", 0.0)),
            _sanitize_csv_cell(doc.status),
            _sanitize_csv_cell(doc.sha256),
            _sanitize_csv_cell("DEMO_FIXTURE" if is_demo else "LIVE_PIPELINE"),
        ]
    )

    # Line Items CSV
    items_io = io.StringIO()
    items_writer = csv.writer(items_io)
    items_writer.writerow(
        ["Invoice Number", "Item Index", "Description", "Quantity", "Unit Price", "Total Price"]
    )
    inv_num = invoice.get("invoice_number", "")
    for idx, item in enumerate(items):
        items_writer.writerow(
            [
                _sanitize_csv_cell(inv_num),
                idx + 1,
                _sanitize_csv_cell(item.get("description", "")),
                _sanitize_csv_cell(item.get("quantity", 0.0)),
                _sanitize_csv_cell(item.get("unit_price", 0.0)),
                _sanitize_csv_cell(item.get("total_price", 0.0)),
            ]
        )

    # Assemble into ZIP with UTF-8 BOM
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "header.csv",
            codecs.BOM_UTF8 + header_io.getvalue().encode("utf-8"),
        )
        zf.writestr(
            "line_items.csv",
            codecs.BOM_UTF8 + items_io.getvalue().encode("utf-8"),
        )

    return zip_buffer.getvalue()


def export_xlsx(doc: DocumentRecord) -> bytes:
    data = json.loads(doc.result_json)
    invoice = data.get("extracted_data", {})
    metrics = data.get("validation_metrics", [])
    items = invoice.get("line_items", [])
    is_demo = bool(
        data.get("source") == "demo_fixture"
        or data.get("is_demo")
        or getattr(doc, "is_demo", False)
    )

    wb = Workbook()

    # Styles
    header_fill = PatternFill(start_color="141414", end_color="141414", fill_type="solid")
    header_font = Font(name="Arial", size=10, bold=True, color="FDFBF7")
    data_font = Font(name="Arial", size=10)
    amber_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    sage_fill = PatternFill(start_color="E6EFE6", end_color="E6EFE6", fill_type="solid")

    # Sheet 1: Invoice Header
    ws_invoice = wb.active
    ws_invoice.title = "Invoice"
    ws_invoice.freeze_panes = "A2"
    headers_s1 = ["Field", "Extracted Value", "Data Type"]
    ws_invoice.append(headers_s1)
    for col in range(1, 4):
        ws_invoice.cell(row=1, column=col).fill = header_fill
        ws_invoice.cell(row=1, column=col).font = header_font

    ws_invoice.append(["Vendor Name", invoice.get("vendor_name", ""), "String"])
    ws_invoice.append(["Invoice Number", invoice.get("invoice_number", ""), "String"])
    ws_invoice.append(["Invoice Date", invoice.get("date", ""), "Date"])
    ws_invoice.append(["Currency", invoice.get("currency", ""), "ISO 4217"])
    ws_invoice.append(["Tax Amount", float(invoice.get("tax_amount", 0.0) or 0.0), "Currency"])
    ws_invoice.append(["Total Amount", float(invoice.get("total_amount", 0.0) or 0.0), "Currency"])
    ws_invoice.append(["Verification Status", doc.status, "Status"])
    ws_invoice.append(
        ["Provenance", "DEMO MODE (SAMPLE FIXTURE)" if is_demo else "LIVE INFERENCE PIPELINE", "Provenance"]
    )

    # Sheet 2: Line Items
    ws_items = wb.create_sheet(title="Line Items")
    ws_items.freeze_panes = "A2"
    headers_s2 = ["#", "Description", "Quantity", "Unit Price", "Total Price", "Formula Check"]
    ws_items.append(headers_s2)
    for col in range(1, 7):
        ws_items.cell(row=1, column=col).fill = header_fill
        ws_items.cell(row=1, column=col).font = header_font

    for idx, item in enumerate(items):
        row_num = idx + 2
        q = float(item.get("quantity", 0.0) or 0.0)
        u = float(item.get("unit_price", 0.0) or 0.0)
        t = float(item.get("total_price", 0.0) or 0.0)
        calc_formula = f"=C{row_num}*D{row_num}"
        ws_items.append([idx + 1, item.get("description", ""), q, u, t, calc_formula])

    # Sheet 3: Validation Metrics
    ws_val = wb.create_sheet(title="Validation Metrics")
    ws_val.freeze_panes = "A2"
    headers_s3 = ["Field Name", "Confidence Score", "Needs Review", "Reasoning"]
    ws_val.append(headers_s3)
    for col in range(1, 5):
        ws_val.cell(row=1, column=col).fill = header_fill
        ws_val.cell(row=1, column=col).font = header_font

    for idx, m in enumerate(metrics):
        row_num = idx + 2
        conf = float(m.get("confidence_score", 0.0) or 0.0)
        needs_rev = "YES" if m.get("needs_review") else "NO"
        ws_val.append([m.get("field_name", ""), conf, needs_rev, m.get("reasoning", "")])

        # Cell conditional fills
        cell_rev = ws_val.cell(row=row_num, column=3)
        cell_conf = ws_val.cell(row=row_num, column=2)
        cell_conf.number_format = "0.0%"

        if m.get("needs_review"):
            cell_rev.fill = amber_fill
        else:
            cell_rev.fill = sage_fill

    # Sheet 4: Audit Trail
    ws_audit = wb.create_sheet(title="Audit Trail")
    ws_audit.freeze_panes = "A2"
    headers_s4 = ["Timestamp", "Field Path", "Old Value", "New Value", "Editor"]
    ws_audit.append(headers_s4)
    for col in range(1, 6):
        ws_audit.cell(row=1, column=col).fill = header_fill
        ws_audit.cell(row=1, column=col).font = header_font

    for e in getattr(doc, "edits", []):
        ws_audit.append([e.created_at.isoformat(), e.field_path, e.old_value, e.new_value, e.editor])

    # Column Widths
    for ws in [ws_invoice, ws_items, ws_val, ws_audit]:
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = col[0].column_letter
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def export_pdf(doc: DocumentRecord) -> bytes:
    data = json.loads(doc.result_json)
    invoice = data.get("extracted_data", {})
    metrics = data.get("validation_metrics", [])
    is_demo = bool(
        data.get("source") == "demo_fixture"
        or data.get("is_demo")
        or getattr(doc, "is_demo", False)
    )

    buf = io.BytesIO()
    doc_template = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0A0A0A"),
    )
    meta_style = ParagraphStyle(
        "MetaStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#555555"),
    )

    created_at_dt = getattr(doc, "created_at", None) or datetime.now(timezone.utc)
    gen_str = created_at_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    sha_str = (doc.sha256[:16] + "...") if doc.sha256 else "unhashed"

    elements = [
        Paragraph("<b>DataNova Extract — Verified Invoice Audit Summary</b>", title_style),
        Spacer(1, 8),
        Paragraph(
            f"<b>Document ID:</b> {doc.id} | <b>File:</b> {doc.filename} | <b>Status:</b> {doc.status}",
            meta_style,
        ),
        Paragraph(
            f"<b>Generated:</b> {gen_str} | <b>SHA-256:</b> {sha_str}",
            meta_style,
        ),
        Spacer(1, 14),
    ]

    if is_demo:
        demo_style = ParagraphStyle(
            "DemoWatermark",
            parent=styles["Normal"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#B45309"),
            alignment=1,
        )
        elements.insert(
            0,
            Paragraph(
                "<b>DEMO MODE DATA — SAMPLE FIXTURE (NOT FROM LIVE INFERENCE)</b>",
                demo_style,
            ),
        )
        elements.insert(1, Spacer(1, 8))

    # Invoice Entity Summary Table
    entity_data = [
        ["Vendor Name", invoice.get("vendor_name", "—")],
        ["Invoice Number", invoice.get("invoice_number", "—")],
        ["Date", invoice.get("date", "—")],
        ["Currency", invoice.get("currency", "—")],
        ["Tax Amount", f"{float(invoice.get('tax_amount', 0.0) or 0.0):.2f}"],
        ["Grand Total", f"{float(invoice.get('total_amount', 0.0) or 0.0):.2f}"],
    ]
    t_entities = Table(entity_data, colWidths=[150, 390])
    t_entities.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9F9F9")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#333333")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E5E5")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CCCCCC")),
            ]
        )
    )
    elements.append(t_entities)
    elements.append(Spacer(1, 14))

    # Validation Table
    elements.append(Paragraph("<b>Agent Verification & Math Validation Metrics</b>", styles["Heading3"]))
    val_rows = [["Field", "Score", "Needs Review", "Reasoning"]]
    for m in metrics:
        val_rows.append(
            [
                m.get("field_name", ""),
                f"{float(m.get('confidence_score', 0.0) or 0.0)*100:.0f}%",
                "YES" if m.get("needs_review") else "NO",
                str(m.get("reasoning", ""))[:60],
            ]
        )

    t_val = Table(val_rows, colWidths=[90, 50, 80, 320])
    t_val.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#141414")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#BBBBBB")),
            ]
        )
    )
    elements.append(t_val)
    elements.append(Spacer(1, 14))

    # Approvals Line
    elements.append(
        Paragraph(
            "<b>Compliance Sign-off:</b> ___________________________   <b>Date:</b> ______________",
            meta_style,
        )
    )

    doc_template.build(elements)
    return buf.getvalue()


def _to_record(data: DocumentRecord | dict[str, Any]) -> DocumentRecord:
    if isinstance(data, DocumentRecord):
        return data
    extracted = data.get("extracted_data") or data.get("data") or data
    metrics = data.get("validation_metrics", [])
    source = data.get("source") or ("demo_fixture" if data.get("is_demo") else None)
    is_demo = bool(data.get("is_demo") or source == "demo_fixture")
    result_dict = {
        "extracted_data": extracted,
        "validation_metrics": metrics,
        "overall_status": data.get("overall_status", "APPROVED"),
        "source": source,
        "is_demo": is_demo,
    }

    created_at = data.get("created_at")
    if isinstance(created_at, str):
        try:
            created_at_dt = datetime.fromisoformat(created_at)
        except Exception:
            created_at_dt = datetime.now(timezone.utc)
    elif isinstance(created_at, datetime):
        created_at_dt = created_at
    else:
        created_at_dt = datetime.now(timezone.utc)

    rec = DocumentRecord(
        id=data.get("document_id") or "direct",
        filename=data.get("filename") or "export",
        mime="application/pdf",
        size_bytes=1024,
        sha256=data.get("sha256") or "",
        page_count=1,
        status=data.get("overall_status", "APPROVED"),
        vendor_name=extracted.get("vendor_name", "") if isinstance(extracted, dict) else "",
        invoice_number=extracted.get("invoice_number", "") if isinstance(extracted, dict) else "",
        total_amount=float((extracted.get("total_amount") if isinstance(extracted, dict) else 0.0) or 0.0),
        currency=extracted.get("currency", "USD") if isinstance(extracted, dict) else "USD",
        result_json=json.dumps(result_dict),
        original_result_json=json.dumps(result_dict),
        created_at=created_at_dt,
    )
    rec.edits = []
    rec.approvals = []
    rec.is_demo = is_demo
    return rec


def export_json_bytes(data: DocumentRecord | dict[str, Any]) -> bytes:
    if isinstance(data, dict):
        return json.dumps(data, indent=2).encode("utf-8")
    return export_json(data)


def export_csv_bytes(data: DocumentRecord | dict[str, Any]) -> bytes:
    rec = _to_record(data)
    return export_csv_zip(rec)


def export_xlsx_bytes(data: DocumentRecord | dict[str, Any]) -> bytes:
    rec = _to_record(data)
    return export_xlsx(rec)


def export_pdf_bytes(data: DocumentRecord | dict[str, Any], filename: str = "") -> bytes:
    rec = _to_record(data)
    if filename:
        rec.filename = filename
    return export_pdf(rec)
