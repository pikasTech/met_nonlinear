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
    fit_mode: str = "both"  # "width" | "height" | "both"
    align_x: str = "center"
    align_y: str = "center"
    offset_x: int = 0
    offset_y: int = 0
    row_span: int = 1
    col_span: int = 1
    trim_border: int | None = None
    trim_border_left: int | None = None
    trim_border_right: int | None = None
    trim_border_top: int | None = None
    trim_border_bottom: int | None = None
    trim_tolerance: int = 8
    margin_left: int = 0
    margin_right: int = 0
    margin_top: int = 0
    margin_bottom: int = 0


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
    label_font_size_pt: float | None = None,
    label_reference_width_pt: float = 372.0,
    latex_width_fraction: float = 1.0,
    label_position: str = "top-left",
    label_inset: int = 20,
    label_gap: int = 18,
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
    placements = _assign_grid_positions(panels, row_count, col_count)

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
                "offset_x": panel.offset_x,
                "offset_y": panel.offset_y,
                "row_span": panel.row_span,
                "col_span": panel.col_span,
                "trim_border": panel.trim_border,
                "trim_border_left": panel.trim_border_left,
                "trim_border_right": panel.trim_border_right,
                "trim_border_top": panel.trim_border_top,
                "trim_border_bottom": panel.trim_border_bottom,
                "trim_tolerance": panel.trim_tolerance,
            }
        )

    widths = [0] * col_count
    heights = [0] * row_count
    for (row, col, row_span, col_span), image in zip(placements, rendered):
        if col_span == 1:
            widths[col] = max(widths[col], image.width)
        if row_span == 1:
            heights[row] = max(heights[row], image.height)

    if cell_widths is not None:
        if len(cell_widths) != col_count:
            raise ValueError("cell_widths length must match the column count")
        widths = [max(auto, int(user)) for auto, user in zip(widths, cell_widths)]
    if cell_heights is not None:
        if len(cell_heights) != row_count:
            raise ValueError("cell_heights length must match the row count")
        heights = [max(auto, int(user)) for auto, user in zip(heights, cell_heights)]
    _ensure_span_capacity(widths, heights, placements, rendered, gutter_x, gutter_y)

    canvas_width = pad_left + pad_right + sum(widths) + gutter_x * (col_count - 1)
    resolved_label_font_size = _resolve_label_font_size(
        label_font_size,
        canvas_width,
        label_font_size_pt,
        label_reference_width_pt,
        latex_width_fraction,
    )
    font = _load_font(resolved_label_font_size, font_path)
    label_outside_top = label_position.lower().strip() in {"outside-top-left", "outside-top-right", "outside-top-center"}
    row_label_heights = [0] * row_count
    if label_outside_top:
        measuring_draw = ImageDraw.Draw(Image.new("RGB", (1, 1), background))
        for idx, panel in enumerate(panels):
            if not panel.label:
                continue
            row = placements[idx][0]
            bbox = measuring_draw.textbbox((0, 0), panel.label, font=font, anchor="lt")
            row_label_heights[row] = max(row_label_heights[row], bbox[3] - bbox[1] + max(0, label_gap))

    canvas_height = pad_top + pad_bottom + sum(heights) + sum(row_label_heights) + gutter_y * (row_count - 1)
    canvas = Image.new("RGB", (canvas_width, canvas_height), background)
    draw = ImageDraw.Draw(canvas)

    for idx, (panel, image) in enumerate(zip(panels, rendered)):
        row, col, row_span, col_span = placements[idx]
        cell_x = pad_left + sum(widths[:col]) + gutter_x * col
        cell_y = pad_top + sum(heights[:row]) + sum(row_label_heights[:row]) + gutter_y * row
        cell_width = sum(widths[col:col + col_span]) + gutter_x * (col_span - 1)
        extra_row_label_height = sum(row_label_heights[row + 1:row + row_span])
        content_height = sum(heights[row:row + row_span]) + extra_row_label_height + gutter_y * (row_span - 1)
        content_y = cell_y + row_label_heights[row]
        paste_x = cell_x + _alignment_offset(cell_width, image.width, panel.align_x, axis="x") + int(panel.offset_x)
        paste_y = content_y + _alignment_offset(content_height, image.height, panel.align_y, axis="y") + int(panel.offset_y)
        canvas.paste(image, (paste_x, paste_y))

        panel_meta[idx]["cell"] = {
            "row": row,
            "col": col,
            "row_span": row_span,
            "col_span": col_span,
            "x": cell_x,
            "y": cell_y,
            "width": cell_width,
            "height": row_label_heights[row] + content_height,
            "content_y": content_y,
            "content_height": content_height,
            "label_band_height": row_label_heights[row],
        }
        panel_meta[idx]["paste_box"] = [paste_x, paste_y, paste_x + image.width, paste_y + image.height]

        if panel.label:
            _draw_label(
                draw,
                panel.label,
                paste_box=(paste_x, paste_y, paste_x + image.width, paste_y + image.height),
                cell_box=(cell_x, cell_y, cell_x + cell_width, cell_y + row_label_heights[row]),
                position=label_position,
                inset=label_inset,
                gap=label_gap,
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
        "label_font_size_px": resolved_label_font_size,
        "label_font_size_pt": label_font_size_pt,
        "label_reference_width_pt": label_reference_width_pt,
        "latex_width_fraction": latex_width_fraction,
        "label_font_family": "Times New Roman",
        "label_font_path": _path_text(getattr(font, "path", "")) if getattr(font, "path", None) else None,
        "label_position": label_position,
        "label_gap": label_gap,
        "label_outside_top": label_outside_top,
        "row_label_heights": row_label_heights,
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


def _assign_grid_positions(
    panels: Sequence[PanelSpec],
    row_count: int,
    col_count: int,
) -> list[tuple[int, int, int, int]]:
    occupancy = [[False] * col_count for _ in range(row_count)]
    placements: list[tuple[int, int, int, int]] = []
    for panel in panels:
        row_span = max(1, int(panel.row_span))
        col_span = max(1, int(panel.col_span))
        if row_span > row_count:
            raise ValueError("panel row_span exceeds the requested grid height")
        if col_span > col_count:
            raise ValueError("panel col_span exceeds the requested grid width")
        placed = False
        for row in range(row_count - row_span + 1):
            for col in range(col_count - col_span + 1):
                blocked = False
                for row_offset in range(row_span):
                    if any(occupancy[row + row_offset][col + col_offset] for col_offset in range(col_span)):
                        blocked = True
                        break
                if blocked:
                    continue
                for row_offset in range(row_span):
                    for col_offset in range(col_span):
                        occupancy[row + row_offset][col + col_offset] = True
                placements.append((row, col, row_span, col_span))
                placed = True
                break
            if placed:
                break
        if not placed:
            raise ValueError("panel spans exceed the requested grid capacity")
    return placements


def _ensure_span_capacity(
    widths: list[int],
    heights: list[int],
    placements: Sequence[tuple[int, int, int, int]],
    rendered: Sequence[Image.Image],
    gutter_x: int,
    gutter_y: int,
) -> None:
    for (row, col, row_span, col_span), image in zip(placements, rendered):
        if col_span <= 1:
            available_width = widths[col]
        else:
            available_width = sum(widths[col:col + col_span]) + gutter_x * (col_span - 1)
        if available_width < image.width:
            deficit = image.width - available_width
            grow_each, remainder = divmod(deficit, col_span)
            for offset in range(col_span):
                widths[col + offset] += grow_each + (1 if offset < remainder else 0)

        if row_span <= 1:
            available_height = heights[row]
        else:
            available_height = sum(heights[row:row + row_span]) + gutter_y * (row_span - 1)
        if available_height < image.height:
            deficit = image.height - available_height
            grow_each, remainder = divmod(deficit, row_span)
            for offset in range(row_span):
                heights[row + offset] += grow_each + (1 if offset < remainder else 0)


def _resolve_label_font_size(
    fallback_size: int,
    canvas_width_px: int,
    label_font_size_pt: float | None,
    reference_width_pt: float,
    latex_width_fraction: float,
) -> int:
    if label_font_size_pt is None:
        return int(fallback_size)
    if reference_width_pt <= 0:
        raise ValueError("label_reference_width_pt must be positive")
    if latex_width_fraction <= 0:
        raise ValueError("latex_width_fraction must be positive")
    font_size = float(label_font_size_pt) * float(canvas_width_px) / (reference_width_pt * latex_width_fraction)
    return max(1, int(round(font_size)))


def _load_panel_image(panel: PanelSpec) -> Image.Image:
    source = Path(panel.path)
    with Image.open(source) as image:
        image = image.convert("RGBA")
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        background.alpha_composite(image)
        rgb_image = background.convert("RGB")
        if panel.trim_border is not None:
            rgb_image = _trim_uniform_background(rgb_image, panel.trim_border, panel.trim_tolerance)
        elif (panel.trim_border_left is not None or panel.trim_border_right is not None
              or panel.trim_border_top is not None or panel.trim_border_bottom is not None):
            rgb_image = _trim_directional_background(
                rgb_image,
                panel.trim_border_left,
                panel.trim_border_right,
                panel.trim_border_top,
                panel.trim_border_bottom,
                panel.trim_tolerance,
            )
        rgb_image = _apply_margin(
            rgb_image,
            panel.margin_left,
            panel.margin_right,
            panel.margin_top,
            panel.margin_bottom,
        )
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


def _trim_directional_background(
    image: Image.Image,
    left: int | None,
    right: int | None,
    top: int | None,
    bottom: int | None,
    tolerance: int,
) -> Image.Image:
    if left is not None and left < 0:
        raise ValueError("trim_border_left must be non-negative")
    if right is not None and right < 0:
        raise ValueError("trim_border_right must be non-negative")
    if top is not None and top < 0:
        raise ValueError("trim_border_top must be non-negative")
    if bottom is not None and bottom < 0:
        raise ValueError("trim_border_bottom must be non-negative")
    background = Image.new("RGB", image.size, (255, 255, 255))
    diff = ImageChops.difference(image, background).convert("L")
    mask = diff.point(lambda value: 255 if value > tolerance else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return image.copy()
    cropped = image.crop(bbox)
    L = left if left is not None else 0
    R = right if right is not None else 0
    T = top if top is not None else 0
    B = bottom if bottom is not None else 0
    framed = Image.new("RGB", (cropped.width + L + R, cropped.height + T + B), (255, 255, 255))
    framed.paste(cropped, (L, T))
    return framed


def _apply_margin(
    image: Image.Image,
    margin_left: int,
    margin_right: int,
    margin_top: int,
    margin_bottom: int,
) -> Image.Image:
    if margin_left == 0 and margin_right == 0 and margin_top == 0 and margin_bottom == 0:
        return image
    new_width = image.width + margin_left + margin_right
    new_height = image.height + margin_top + margin_bottom
    result = Image.new("RGB", (new_width, new_height), (255, 255, 255))
    result.paste(image, (margin_left, margin_top))
    return result


def _resize_panel(image: Image.Image, panel: PanelSpec) -> Image.Image:
    if panel.scale <= 0:
        raise ValueError("panel scale must be positive")
    mode = panel.fit_mode.lower().strip() if panel.fit_mode else "both"
    fit_ratios: list[float] = []
    if panel.fit_width is not None:
        fit_ratios.append(float(panel.fit_width) / float(image.width))
    if panel.fit_height is not None:
        fit_ratios.append(float(panel.fit_height) / float(image.height))
    if not fit_ratios:
        ratio = panel.scale
    elif mode == "width":
        ratio = float(panel.fit_width) / float(image.width) if panel.fit_width else panel.scale
    elif mode == "height":
        ratio = float(panel.fit_height) / float(image.height) if panel.fit_height else panel.scale
    else:
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
        try:
            from src.visualization.paper_plot_style import paper_font_candidates

            candidates = list(paper_font_candidates(bold=True)) + [
                Path("C:/Windows/Fonts/arialbd.ttf"),
                Path("C:/Windows/Fonts/arial.ttf"),
            ]
        except Exception:  # pragma: no cover - standalone helper fallback
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
    cell_box: tuple[int, int, int, int],
    position: str,
    inset: int,
    gap: int,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    box: bool,
    box_padding: int,
) -> None:
    left, top, right, bottom = paste_box
    cell_left, cell_top, cell_right, cell_label_bottom = cell_box
    normalized = position.lower().strip()
    anchor_map = {
        "top-left": ("la", left + inset, top + inset),
        "top-right": ("ra", right - inset, top + inset),
        "top-center": ("ma", (left + right) // 2, top + inset),
        "bottom-left": ("ld", left + inset, bottom - inset),
        "bottom-right": ("rd", right - inset, bottom - inset),
        "bottom-center": ("md", (left + right) // 2, bottom - inset),
    }
    outside_anchor_map = {
        "outside-top-left": ("lt", left + inset, cell_top),
        "outside-top-right": ("rt", right - inset, cell_top),
        "outside-top-center": ("mt", (left + right) // 2, cell_top),
    }
    if normalized in outside_anchor_map:
        anchor, x, y = outside_anchor_map[normalized]
        max_y = max(cell_top, cell_label_bottom - gap)
        bbox = draw.textbbox((x, y), label, font=font, anchor=anchor)
        if bbox[3] > max_y:
            y -= bbox[3] - max_y
        bbox = draw.textbbox((x, y), label, font=font, anchor=anchor)
    elif normalized in anchor_map:
        anchor, x, y = anchor_map[normalized]
        bbox = draw.textbbox((x, y), label, font=font, anchor=anchor)
    else:
        raise ValueError(f"Unsupported label position: {position}")
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
