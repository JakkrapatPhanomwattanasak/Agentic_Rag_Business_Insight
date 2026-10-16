"""Preview the real frontend with synthetic, read-only fixtures (no cloud calls).

Run from the repository root: python scripts/preview_ui.py
Requires the project's duckdb, Pillow and PyMuPDF dependencies.
This is a local UI preview, not a RAG evaluation or production server.
"""
from __future__ import annotations

import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit

import duckdb
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
NOTICE = "UI PREVIEW / SYNTHETIC DATA / NO MODEL CALLS"
LABELS = ["สินทรัพย์รวม", "กำไรสุทธิ (ส่วนที่เป็นของธนาคาร)",
          "รายได้ดอกเบี้ยสุทธิ", "เงินรับฝาก", "หนี้สินรวม"]
VALUES = [[125000, 138000, 149000], [3200, 3650, 4100],
          [6800, 7200, 7900], [98000, 105000, 113000], [108000, 119000, 128000]]
DOC = dict(id=1, filename="SYNTHETIC_BANK_REPORT.pdf", doc_type="pdf",
           status="completed", page_count=3, indexed_pages=3, chunk_count=3,
           table_row_count=5, created_at="2026-10-16T00:00:00Z")
CHUNKS = [dict(id=i, chunk_index=i, page_number=i + 1, token_count=60,
               chunk_text="ข้อมูลตัวอย่างสำหรับทดสอบหน้าจอเท่านั้น ธนาคารตัวอย่างมีเป้าหมาย Net Zero ภายในปี 2050 " * 2,
               similarity_to_next=0.8 if i == 0 else 0.3 if i == 1 else None)
          for i in range(3)]


def warehouse():
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE fact_financial_metrics (document_id INTEGER, table_name VARCHAR, "
                 "row_label VARCHAR, metric_year VARCHAR, raw_value VARCHAR, numeric_value DOUBLE, "
                 "unit VARCHAR, quality_status VARCHAR)")
    for index, (label, values) in enumerate(zip(LABELS, VALUES)):
        for year, value in zip(("2565", "2566", "2567"), values):
            conn.execute("INSERT INTO fact_financial_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                         [1, f"[p{index % 3 + 1}] Synthetic statement", label, year,
                          f"{value:,}", value, "ล้านบาท", "unverified"])
    return conn


class Preview(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "frontend"), **kwargs)

    def send_bytes(self, data, mime, status=200):
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, value, status=200):
        self.send_bytes(json.dumps(value, ensure_ascii=False).encode(), "application/json; charset=utf-8", status)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ("/", "/index.html"):
            html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
            banner = f'<div role="note" style="text-align:center;padding:8px;background:#f2b544;color:#16171b;font:600 12px sans-serif">{NOTICE}</div>'
            self.send_bytes(html.replace("<body>", "<body>" + banner).encode(), "text/html; charset=utf-8")
        elif path == "/api/health":
            self.send_json({"status": "ok", "preview": True})
        elif path == "/api/documents":
            self.send_json({"documents": [DOC]})
        elif path == "/api/warehouse/status":
            self.send_json(dict(status="ok", total_fact_records=15, total_lookup_records=0,
                                total_documents=1, available_years=["2565", "2566", "2567"], tables=[]))
        elif path == "/api/chunks/1":
            self.send_json(dict(filename=DOC["filename"], total_chunks=3, chunks=CHUNKS))
        elif path.startswith("/api/documents/1/pages/") and path.endswith("/image"):
            pdf = pymupdf.open()
            page = pdf.new_page(width=595, height=842)
            page.insert_text((45, 55), "SYNTHETIC BANK / UI PREVIEW", fontsize=22)
            page.insert_text((45, 88), "Illustrative figures only. Not an actual financial report.", fontsize=12)
            for i, (label, values) in enumerate(zip(
                ["Total assets", "Net profit", "Net interest income", "Deposits", "Liabilities"], VALUES)):
                page.insert_text((45, 160 + i * 60), f"{label}     2565: {values[0]:,}     2566: {values[1]:,}     2567: {values[2]:,}", fontsize=11)
            image = page.get_pixmap().tobytes("png")
            pdf.close()
            self.send_bytes(image, "image/png")
        elif path.startswith("/api/"):
            self.send_json({"error": "Unavailable in the read-only synthetic UI preview"}, 404)
        else:
            super().do_GET()

    def do_POST(self):
        if urlsplit(self.path).path != "/api/warehouse/query":
            self.send_json({"error": "Uploads, scraping and model calls are disabled in this preview"}, 405)
            return
        try:
            body = json.loads(self.rfile.read(min(int(self.headers.get("Content-Length", 0)), 16384)))
            sql = body.get("sql", "")
            # Only the frontend's SELECT statements against the synthetic table.
            import re
            scrubbed = re.sub(r"'(?:''|[^'])*'", "''", sql)
            if (not re.match(r"^\s*SELECT\b", sql, re.I)
                    or re.search(r";|--|/\*|\b(read_|sqlite|http|attach|copy|pragma|install|load)", scrubbed, re.I)):
                raise ValueError("Only preview SELECT queries are supported")
            with warehouse() as conn:
                conn.execute("SET enable_external_access=false")
                result = conn.execute(sql)
                columns = [col[0] for col in result.description]
                rows = [dict(zip(columns, row)) for row in result.fetchmany(100)]
            self.send_json(dict(columns=columns, rows=rows))
        except Exception:
            self.send_json({"error": "Unsupported preview query"}, 400)


if __name__ == "__main__":
    print(f"{NOTICE}\nhttp://127.0.0.1:5081", flush=True)
    HTTPServer(("127.0.0.1", 5081), Preview).serve_forever()
