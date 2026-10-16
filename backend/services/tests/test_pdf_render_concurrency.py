"""Page thumbnails and OCR must safely share the PDFium runtime."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import pymupdf
from PIL import Image

from backend.services.ocr import TyphoonOCRService
from backend.services.pdf_render import render_pdf_page


def test_parallel_citation_and_ocr_renders(tmp_path):
    path = tmp_path / "concurrent.pdf"
    with pymupdf.open() as pdf:
        pdf.new_page(width=200, height=300).insert_text((20, 40), "Shared PDF evidence")
        pdf.save(path)
    # Exercise only local rendering; do not initialize an OCR client or model.
    ocr = TyphoonOCRService.__new__(TyphoonOCRService)
    ocr.render_dpi = 72

    def render(index):
        if index % 2:
            return ocr._render_pdf_page_to_png(str(path), 1, 72)
        return render_pdf_page(str(path), 1, 72)

    with ThreadPoolExecutor(max_workers=6) as workers:
        images = list(workers.map(render, range(18)))
    for png in images:
        with Image.open(BytesIO(png)) as image:
            assert image.format == "PNG"
            assert image.size == (200, 300)
