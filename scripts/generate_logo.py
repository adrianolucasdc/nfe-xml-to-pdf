#!/usr/bin/env python
"""Generate default logo for nfe2pdf package."""
from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow não instalado. Instale com: pip install pillow")
    raise


def generate_logo(output_path: Path, size: int = 120) -> None:
    """Gera logo padrão: folha XML -> seta -> PDF."""
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Cores
    BLUE = (30, 136, 229)       # Material Blue 500
    DARK_BLUE = (21, 101, 192)  # Material Blue 700
    WHITE = (255, 255, 255)
    GREEN = (46, 204, 113)      # Verde para PDF
    GRAY = (189, 189, 189)

    padding = size // 8
    sheet_w = size // 2 - padding
    sheet_h = int(sheet_w * 1.4)
    sheet_x = padding
    sheet_y = (size - sheet_h) // 2

    # Desenhar folha XML (azul)
    draw.rounded_rectangle(
        [sheet_x, sheet_y, sheet_x + sheet_w, sheet_y + sheet_h],
        radius=4,
        fill=BLUE,
        outline=DARK_BLUE,
        width=2,
    )

    # Texto "XML" na folha
    try:
        font = ImageFont.truetype("arial.ttf", size // 6)
    except OSError:
        font = ImageFont.load_default()

    text_x = sheet_x + sheet_w // 2
    text_y = sheet_y + sheet_h // 2
    draw.text((text_x, text_y), "XML", fill=WHITE, font=font, anchor="mm")

    # Seta no meio
    arrow_x = sheet_x + sheet_w + padding // 2
    arrow_y = size // 2
    arrow_len = padding
    draw.polygon(
        [
            (arrow_x, arrow_y - arrow_len // 2),
            (arrow_x + arrow_len, arrow_y),
            (arrow_x, arrow_y + arrow_len // 2),
        ],
        fill=GRAY,
    )

    # Desenhar folha PDF (verde)
    pdf_x = arrow_x + arrow_len + padding // 2
    pdf_y = sheet_y
    draw.rounded_rectangle(
        [pdf_x, pdf_y, pdf_x + sheet_w, pdf_y + sheet_h],
        radius=4,
        fill=GREEN,
        outline=(30, 160, 80),
        width=2,
    )

    # Texto "PDF" na folha
    text_x2 = pdf_x + sheet_w // 2
    text_y2 = pdf_y + sheet_h // 2
    draw.text((text_x2, text_y2), "PDF", fill=WHITE, font=font, anchor="mm")

    # Salvar
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Logo gerada: {output_path}")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    logo_path = project_root / "assets" / "logo.png"
    generate_logo(logo_path)