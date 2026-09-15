"""One-off helper to build a tiny text-based sample PDF for local testing."""

from pathlib import Path


def build_text_pdf(lines: list[str]) -> bytes:
    def esc(text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    content_parts = ["BT", "/F1 11 Tf", "50 750 Td", "14 TL"]
    for index, line in enumerate(lines):
        if index == 0:
            content_parts.append(f"({esc(line)}) Tj")
        else:
            content_parts.append("T*")
            content_parts.append(f"({esc(line)}) Tj")
    content_parts.append("ET")
    stream = "\n".join(content_parts)

    objects = [
        "1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        "2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n",
        (
            "3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            "/Contents 4 0 R /Resources<< /Font<< /F1 5 0 R >> >> >>endobj\n"
        ),
        f"4 0 obj<< /Length {len(stream.encode('latin-1'))} >>stream\n{stream}\nendstream\nendobj\n",
        "5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n",
    ]

    pdf = "%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf.encode("latin-1")))
        pdf += obj

    xref_pos = len(pdf.encode("latin-1"))
    pdf += f"xref\n0 {len(offsets)}\n"
    pdf += "0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n"
    pdf += f"trailer<< /Size {len(offsets)} /Root 1 0 R >>\n"
    pdf += f"startxref\n{xref_pos}\n%%EOF\n"
    return pdf.encode("latin-1")


if __name__ == "__main__":
    sample_lines = [
        "Customer Complaint Form",
        "Customer: Apollo Pharma Distributors",
        "Complaint Source: Email",
        "Product: Metformin Hydrochloride API",
        "Strength/Grade: IP/BP",
        "Batch/Lot: MFH260712A",
        "Affected Quantity: 20 kg",
        "Manufacturing Date: 2026-01-10",
        "Expiry Date: 2028-01-10",
        "Complaint Type: Product Quality",
        "Complaint Date: 2026-09-15",
        "Description: Discoloration observed in received API drums.",
    ]
    out = Path(__file__).resolve().parent / "_tmp_sample_complaint.pdf"
    out.write_bytes(build_text_pdf(sample_lines))
    print(out)
