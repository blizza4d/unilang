import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://uni-lang.vercel.app"),
  title: "DataNova Extract | Multilingual Document Understanding",
  description:
    "Intelligent multilingual invoice understanding powered by LangGraph multi-agent architecture, deterministic math verification, and human-in-the-loop review.",
  keywords: [
    "invoice extraction",
    "document AI",
    "multilingual OCR",
    "LangGraph",
    "FastAPI",
    "Next.js",
    "math verification",
    "human in the loop",
  ],
  authors: [{ name: "DataNova Extract Team" }],
  openGraph: {
    title: "DataNova Extract | Multilingual Document Understanding",
    description:
      "Intelligent multilingual invoice understanding with deterministic arithmetic verification and interactive human review.",
    url: "https://uni-lang.vercel.app",
    siteName: "DataNova Extract",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "DataNova Extract v1.0.0-rc.1 Interface Preview",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "DataNova Extract | Multilingual Document Understanding",
    description:
      "Intelligent multilingual invoice understanding with deterministic arithmetic verification.",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  themeColor: "#0A0A0A",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`dark ${inter.variable} ${jetbrainsMono.variable} h-full antialiased`}
    >
      <body className="h-full bg-app text-bright font-sans overflow-hidden">
        {children}
      </body>
    </html>
  );
}
