from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from PIL import Image, ImageChops, ImageDraw, ImageFont

try:
    RESAMPLE_LANCZOS = Image.Resampling.LANCZOS
except AttributeError:  # pragma: no cover - Pillow < 9 compatibility
    RESAMPLE_LANCZOS = Image.LANCZOS


RGB = tuple[int, int, int]


@dataclass(frozen=True)
class PanelSpec:
    """One bitmap panel in a generated montage."""

    path: str | Path
    label: str | None = None
    scale: float = 1.0
    fit_width: int | None = None
    fit_height: int | None = None
    align_x: str = "center"
    align_y: str = "center"
    trim_border: int | None = None
    trim_tolerance: int = 8


def compose_subfigures(
    panels: Sequence[PanelSpec],
    output_path: str | Path,
    *,
    layout: str = "horizontal",
    rows: int | None = None,
    cols: int | None = None,
    padding: int | Sequence[int] = 72,
    gutter: int | tuple[int, int] = 72,
    cell_widths: Sequence[int] | None = None,
    cell_heights: Sequence[int] | None = None,
    background: RGB = (255, 255, 255),
    label_font_size: int = 54,
    label_position: str = "top-left",
    label_inset: int = 20,
    label_box: bool = True,
    label_box_padding: int = 10,
    font_path: str | Path | None = None,
    dpi: tuple[int, int] = (300, 300),
) -> dict[str, Any]:
    """Compose bitmap panels and draw journal-style subfigure labels.

    The helper intentionally works on finished bitmaps.  It supports left-right,
    top-bottom, and arbitrary matrix layouts while leaving the source plotting
    code untouched.
    """

    if not panels:
        raise ValueError("compose_subfigures requires at least one panel")
    row_count, col_count = _resolve_grid(len(panels), layout, rows, cols)
    if len(panels) > row_count * col_count:
        raise ValueError("panel count exceeds the requested grid")

    pad_left, pad_top, pad_right, pad_bottom = _normalize_padding(padding)
    gutter_x, gutter_y = _normalize_gutter(gutter)

    loaded = [_load_panel_image(panel) for panel in panels]
    panel_meta: list[dict[str, Any]] = []
    rendered: list[Image.Image] = []
    for panel, image in zip(panels, loaded):
        resized = _resize_panel(image, panel)
        rendered.append(resized)
        panel_meta.append(
            {
                "source": _path_text(panel.path),
                "label": panel.label,
                "original_size": list(image.size),
                "rendered_size": list(resized.size),
                "scale": panel.scale,
                "fit_width": panel.fit_width,
                "fit_height": panel.fit_height,
                "align_x": panel.align_x,
                "align_y": panel.align_y,
                "trim_border": panel.trim_border,
                "trim_tolerance": panel.trim_tolerance,
            }
        )

    widths = [0] * col_count
    heights = [0] * row_count
    for idx, image in enumerate(rendered):
        row = idx // col_count
        col = idx % col_count
        widths[col] = max(widths[col], image.width)
        heights[row] = max(heights[row], image.height)

    if cell_widths is not None:
        if len(cell_widths) != col_count:
            raise ValueError("cell_widths length must match the column count")
        widths = [max(auto, int(user)) for auto, user in zip(widths, cell_widths)]
    if cell_heights is not None:
        if len(cell_heights) != row_count:
            raise ValueError("cell_heights length must match the row count")
        heights = [max(auto, int(user)) for auto, user in zip(heights, cell_heights)]

    canvas_width = pad_left + pad_right + sum(widths) + gutter_x * (col_count - 1)
    canvas_height = pad_top + pad_bottom + sum(heights) + gutter_y * (row_count - 1)
    canvas = Image.new("RGB", (canvas_width, canvas_height), background)
    draw = ImageDraw.Draw(canvas)
    font = _load_font(label_font_size, font_path)

    for idx, (panel, image) in enumerate(zip(panels, rendered)):
        row = idx // col_count
        col = idx % col_count
        cell_x = pad_left + sum(widths[:col]) + gutter_x * col
        cell_y = pad_top + sum(heights[:row]) + gutter_y * row
        paste_x = cell_x + _alignment_offset(widths[col], image.width, panel.align_x, axis="x")
        paste_y = cell_y + _alignment_offset(heights[row], image.height, panel.align_y, axis="y")
        canvas.paste(image, (paste_x, paste_y))

        panel_meta[idx]["cell"] = {
            "row": row,
            "col": col,
            "x": cell_x,
            "y": cell_y,
            "width": widths[col],
            "height": heights[row],
        }
        panel_meta[idx]["paste_box"] = [paste_x, paste_y, paste_x + image.width, paste_y + image.height]

        if panel.label:
            _draw_label(
                draw,
                panel.label,
                paste_box=(paste_x, paste_y, paste_x + image.width, paste_y + image.height),
                position=label_position,
                inset=label_inset,
                font=font,
                box=label_box,
                box_padding=label_box_padding,
            )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, dpi=dpi)
    return {
        "output": _path_text(output),
        "size": list(canvas.size),
        "layout": layout,
        "rows": row_count,
        "cols": col_count,
        "padding": [pad_left, pad_top, pad_right, pad_bottom],
        "gutter": [gutter_x, gutter_y],
        "panels": panel_meta,
    }


def _resolve_grid(panel_count: int, layout: str, rows: int | None, cols: int | None) -> tuple[int, int]:
    normalized = layout.lower().strip()
    if normalized in {"horizontal", "h", "row"}:
        return 1, panel_count if cols is None else cols
    if normalized in {"vertical", "v", "column"}:
        return panel_count if rows is None else rows, 1
    if normalized not in {"matrix", "grid"}:
        raise ValueError(f"Unsupported layout: {layout}")
    if rows is None and cols is None:
        cols = max(1, int(round(panel_count**0.5)))
        rows = (panel_count + cols - 1) // cols
    elif rows is None:
        rows = (panel_count + int(cols) - 1) // int(cols)
    elif cols is None:
        cols = (panel_count + int(rows) - 1) // int(rows)
    return int(rows), int(cols)


def _normalize_padding(padding: int | Sequence[int]) -> tuple[int, int, int, int]:
    if isinstance(padding, int):
        return padding, padding, padding, padding
    values = [int(value) for value in padding]
    if len(values) == 2:
        horizontal, vertical = values
        return horizontal, vertical, horizontal, vertical
    if len(values) == 4:
        return values[0], values[1], values[2], values[3]
    raise ValueError("padding must be an int, two values, or four values")


def _normalize_gutter(gutter: int | tuple[int, int]) -> tuple[int, int]:
    if isinstance(gutter, int):
        return gutter, gutter
    return int(gutter[0]), int(gutter[1])


def _load_panel_image(panel: PanelSpec) -> Image.Image:
    source = Path(panel.path)
    with Image.open(source) as image:
        image = image.convert("RGBA")
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        background.alpha_composite(image)
        rgb_image = background.convert("RGB")
        if panel.trim_border is not None:
            return _trim_uniform_background(rgb_image, panel.trim_border, panel.trim_tolerance)
        return rgb_image


def _trim_uniform_background(image: Image.Image, border: int, tolerance: int) -> Image.Image:
    if border < 0:
        raise ValueError("trim_border must be non-negative")
    background = Image.new("RGB", image.size, (255, 255, 255))
    diff = ImageChops.difference(image, background).convert("L")
    mask = diff.point(lambda value: 255 if value > tolerance else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return image.copy()
    cropped = image.crop(bbox)
    if border == 0:
        return cropped
    framed = Image.new("RGB", (cropped.width + border * 2, cropped.height + border * 2), (255, 255, 255))
    framed.paste(cropped, (border, border))
    return framed


def _resize_panel(image: Image.Image, panel: PanelSpec) -> Image.Image:
    if panel.scale <= 0:
        raise ValueError("panel scale must be positive")
    fit_ratios: list[float] = []
    if panel.fit_width is not None:
        fit_ratios.append(float(panel.fit_width) / float(image.width))
    if panel.fit_height is not None:
        fit_ratios.append(float(panel.fit_height) / float(image.height))
    ratio = min(fit_ratios) if fit_ratios else 1.0
    ratio *= panel.scale
    width = max(1, int(round(image.width * ratio)))
    height = max(1, int(round(image.height * ratio)))
    if (width, height) == image.size:
        return image.copy()
    return image.resize((width, height), RESAMPLE_LANCZOS)


def _alignment_offset(cell_size: int, image_size: int, align: str, *, axis: str) -> int:
    normalized = align.lower().strip()
    if normalized in {"center", "middle"}:
        return max(0, (cell_size - image_size) // 2)
    if normalized in {"left", "top"}:
        return 0
    if normalized in {"right", "bottom"}:
        return max(0, cell_size - image_size)
    raise ValueError(f"Unsupported {axis}-axis alignment: {align}")


def _load_font(size: int, font_path: str | Path | None) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates: Iterable[Path]
    if font_path is not None:
        candidates = [Path(font_path)]
    else:
        candidates = [
            Path("C:/Windows/Fonts/timesbd.ttf"),
            Path("C:/Windows/Fonts/times.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf"),
            Path("C:/Windows/Fonts/arial.ttf"),
        ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _draw_label(
    draw: ImageDraw.ImageDraw,
    label: str,
    *,
    paste_box: tuple[int, int, int, int],
    position: str,
    inset: int,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    box: bool,
    box_padding: int,
) -> None:
    left, top, right, bottom = paste_box
    normalized = position.lower().strip()
    anchor_map = {
        "top-left": ("la", left + inset, top + inset),
        "top-right": ("ra", right - inset, top + inset),
        "top-center": ("ma", (left + right) // 2, top + inset),
        "bottom-left": ("ld", left + inset, bottom - inset),
        "bottom-right": ("rd", right - inset, bottom - inset),
        "bottom-center": ("md", (left + right) // 2, bottom - inset),
    }
    if normalized not in anchor_map:
        raise ValueError(f"Unsupported label position: {position}")
    anchor, x, y = anchor_map[normalized]

    bbox = draw.textbbox((x, y), label, font=font, anchor=anchor)
    if box:
        padded = (
            bbox[0] - box_padding,
            bbox[1] - box_padding,
            bbox[2] + box_padding,
            bbox[3] + box_padding,
        )
        draw.rounded_rectangle(padded, radius=max(4, box_padding), fill=(255, 255, 255), outline=(40, 40, 40), width=1)
    draw.text((x, y), label, font=font, fill=(0, 0, 0), anchor=anchor)


def _path_text(path: str | Path) -> str:
    return str(Path(path)).replace("\\", "/")
