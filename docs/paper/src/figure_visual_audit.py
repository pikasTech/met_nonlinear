from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import median
from typing import Any, Iterable

import numpy as np
from PIL import Image

VISUAL_AUDIT_KEY = "visual_quality_audit"
SCHEMATIC_GEOMETRY_AUDIT_KEY = "schematic_geometry_audit"
AUDIT_VERSION = 1

DEFAULT_THRESHOLDS = {
    "text_clip_margin_px": 1.0,
    "text_text_overlap_min_area_px": 25.0,
    "text_text_overlap_min_fraction": 0.08,
    "text_data_overlap_min_area_px": 45.0,
    "text_data_overlap_min_fraction": 0.12,
    "axis_label_tick_font_ratio_max": 1.85,
    "axis_label_font_min_pt": 14.0,
    "edge_guard_px": 4,
    "edge_dark_luminance_max": 245,
    "edge_nonwhite_delta_min": 14,
    "edge_dark_pixel_min_count": 28,
    "edge_dark_pixel_min_ratio": 0.0015,
    "schematic_endpoint_tolerance": 0.018,
    "schematic_box_margin": 0.006,
    "schematic_axis_alignment_tolerance": 0.006,
    "schematic_arrow_overlap_min_length": 0.030,
    "schematic_arrow_length_fraction_max": 0.700,
    "schematic_arrow_length_fraction_tolerance": 0.006,
    "schematic_endpoint_intrusion_tolerance": 0.003,
    "schematic_endpoint_clearance_min": 0.010,
    "schematic_endpoint_clearance_max": 0.060,
}


def audit_schematic_geometry(
    boxes: list[dict[str, Any]],
    arrows: list[dict[str, Any]],
    *,
    context: str | None = None,
) -> dict[str, Any]:
    """Audit normalized schematic boxes and connector arrows before rasterization.

    Coordinates are in the same normalized 0..1 axes space used by the schematic
    drawing code. The check intentionally focuses on geometry that image-space
    audits miss: connector endpoints that land away from box boundaries, arrows
    crossing unrelated boxes, and unintended arrow-arrow intersections.
    """

    box_map = {str(item.get("id")): _normalize_box(item) for item in boxes if item.get("id") is not None}
    violations: list[dict[str, Any]] = []
    normalized_arrows: list[dict[str, Any]] = []
    arrow_length_fractions: list[dict[str, Any]] = []

    for arrow_index, arrow in enumerate(arrows):
        points = _normalize_points(arrow.get("points") or [arrow.get("start"), arrow.get("end")])
        if len(points) < 2:
            violations.append(
                _violation(
                    "schematic_arrow_invalid",
                    "A schematic arrow must contain at least two points.",
                    details={"arrow_index": arrow_index, "arrow": arrow},
                )
            )
            continue
        normalized = dict(arrow)
        normalized["points"] = points
        normalized["id"] = str(arrow.get("id", f"arrow_{arrow_index}"))
        normalized_arrows.append(normalized)
        endpoint_policy = str(arrow.get("endpoint_policy", "boundary"))
        endpoint_box_ids: list[str] = []

        full_points = _normalize_points(arrow.get("full_points"))
        max_length_fraction = arrow.get("max_length_fraction")
        if len(full_points) >= 2 and max_length_fraction is not None:
            actual_length = _polyline_length(points)
            full_length = _polyline_length(full_points)
            limit = full_length * float(max_length_fraction) + DEFAULT_THRESHOLDS["schematic_arrow_length_fraction_tolerance"]
            fraction = actual_length / full_length if full_length > 0 else 0.0
            arrow_length_fractions.append(
                {
                    "arrow": normalized["id"],
                    "actual_length": round(actual_length, 6),
                    "full_length": round(full_length, 6),
                    "fraction": round(fraction, 6),
                    "max_length_fraction": float(max_length_fraction),
                }
            )
            if full_length > 0 and actual_length > limit:
                violations.append(
                    _violation(
                        "schematic_arrow_too_long",
                        "A schematic arrow exceeds the reserved short-connector length fraction.",
                        details={
                            "arrow": normalized["id"],
                            "actual_length": round(actual_length, 6),
                            "full_length": round(full_length, 6),
                            "max_length_fraction": float(max_length_fraction),
                            "allowed_length": round(limit, 6),
                        },
                    )
                )

        for endpoint_name, point, box_id in [
            ("source", points[0], arrow.get("source")),
            ("target", points[-1], arrow.get("target")),
        ]:
            if not box_id:
                continue
            box = box_map.get(str(box_id))
            if box is None:
                violations.append(
                    _violation(
                        "schematic_arrow_unknown_box",
                        "A schematic arrow references a box id that is not registered.",
                        details={"arrow": normalized["id"], "endpoint": endpoint_name, "box_id": box_id},
                    )
                )
                continue
            endpoint_box_ids.append(str(box_id))
            if endpoint_policy == "boundary_no_intrusion":
                boundary = _point_on_box_boundary_without_intrusion(
                    point,
                    box,
                    tol=DEFAULT_THRESHOLDS["schematic_endpoint_tolerance"],
                    intrusion_tol=DEFAULT_THRESHOLDS["schematic_endpoint_intrusion_tolerance"],
                )
                if boundary is None:
                    violations.append(
                        _violation(
                            "schematic_arrow_endpoint_box_intrusion",
                            "A schematic arrow endpoint must land on the declared box boundary without entering the box interior.",
                            details={
                                "arrow": normalized["id"],
                                "endpoint": endpoint_name,
                                "point": point,
                                "box_id": box_id,
                                "box": box,
                                "endpoint_policy": endpoint_policy,
                            },
                        )
                    )
            elif endpoint_policy == "outside_clearance":
                clearance = _point_outside_box_clearance(
                    point,
                    box,
                    tol=DEFAULT_THRESHOLDS["schematic_endpoint_tolerance"],
                    min_clearance=float(arrow.get("endpoint_clearance_min", DEFAULT_THRESHOLDS["schematic_endpoint_clearance_min"])),
                    max_clearance=float(arrow.get("endpoint_clearance_max", DEFAULT_THRESHOLDS["schematic_endpoint_clearance_max"])),
                )
                if clearance is None:
                    violations.append(
                        _violation(
                            "schematic_arrow_endpoint_box_intrusion",
                            "A schematic arrow endpoint touches or intrudes into the declared box instead of leaving a visible gap.",
                            details={
                                "arrow": normalized["id"],
                                "endpoint": endpoint_name,
                                "point": point,
                                "box_id": box_id,
                                "box": box,
                                "endpoint_policy": endpoint_policy,
                            },
                        )
                    )
            elif not _point_on_box_boundary(point, box, DEFAULT_THRESHOLDS["schematic_endpoint_tolerance"]):
                violations.append(
                    _violation(
                        "schematic_arrow_endpoint_misaligned",
                        "A schematic arrow endpoint is not aligned with the declared box boundary.",
                        details={
                            "arrow": normalized["id"],
                            "endpoint": endpoint_name,
                            "point": point,
                            "box_id": box_id,
                            "box": box,
                        },
                    )
                )

        if endpoint_policy in {"boundary_no_intrusion", "outside_clearance"}:
            for segment_index, segment in enumerate(_segments(points)):
                for box_id in endpoint_box_ids:
                    box = box_map.get(box_id)
                    if box is None:
                        continue
                    hit = _segment_intersects_box_interior(segment, box, DEFAULT_THRESHOLDS["schematic_box_margin"])
                    if hit:
                        violations.append(
                            _violation(
                                "schematic_arrow_declared_box_intrusion",
                                "A schematic arrow crosses into a declared endpoint box despite requiring outside clearance.",
                                details={
                                    "arrow": normalized["id"],
                                    "segment_index": segment_index,
                                    "segment": segment,
                                    "box_id": box_id,
                                    "box": box,
                                    "intersection": hit,
                                },
                            )
                        )

        if arrow.get("require_axis_aligned", False):
            for segment_index, segment in enumerate(_segments(points)):
                if not _segment_axis_aligned(segment, DEFAULT_THRESHOLDS["schematic_axis_alignment_tolerance"]):
                    violations.append(
                        _violation(
                            "schematic_arrow_not_axis_aligned",
                            "A schematic arrow marked as axis-aligned contains a diagonal segment.",
                            details={"arrow": normalized["id"], "segment_index": segment_index, "segment": segment},
                        )
                    )

        allowed = {str(item) for item in arrow.get("allowed_boxes", [])}
        if arrow.get("source"):
            allowed.add(str(arrow["source"]))
        if arrow.get("target"):
            allowed.add(str(arrow["target"]))
        for segment_index, segment in enumerate(_segments(points)):
            for box_id, box in box_map.items():
                if box_id in allowed:
                    continue
                hit = _segment_intersects_box_interior(segment, box, DEFAULT_THRESHOLDS["schematic_box_margin"])
                if hit:
                    violations.append(
                        _violation(
                            "schematic_arrow_box_overlap",
                            "A schematic arrow crosses an unrelated flow box.",
                            details={
                                "arrow": normalized["id"],
                                "segment_index": segment_index,
                                "segment": segment,
                                "box_id": box_id,
                                "box": box,
                                "intersection": hit,
                            },
                        )
                    )

    for first_index, first in enumerate(normalized_arrows):
        for second in normalized_arrows[first_index + 1:]:
            if _arrow_pair_allowed(first, second):
                continue
            for first_seg_index, first_segment in enumerate(_segments(first["points"])):
                for second_seg_index, second_segment in enumerate(_segments(second["points"])):
                    relation = _segment_relation(first_segment, second_segment)
                    if not relation:
                        continue
                    if relation["kind"] == "endpoint_touch":
                        continue
                    if relation["kind"] == "collinear_overlap" and relation.get("length", 0.0) < DEFAULT_THRESHOLDS["schematic_arrow_overlap_min_length"]:
                        continue
                    violations.append(
                        _violation(
                            "schematic_arrow_arrow_overlap",
                            "Two schematic arrows overlap or cross away from intentional endpoints.",
                            details={
                                "first_arrow": first["id"],
                                "second_arrow": second["id"],
                                "first_segment_index": first_seg_index,
                                "second_segment_index": second_seg_index,
                                "first_segment": first_segment,
                                "second_segment": second_segment,
                                "relation": relation,
                            },
                        )
                    )

    audit = _base_audit(
        context=context,
        checks={
            "schematic_box_count": len(box_map),
            "schematic_arrow_count": len(normalized_arrows),
            "schematic_arrow_length_fractions": arrow_length_fractions,
        },
        violations=violations,
    )
    audit["kind"] = SCHEMATIC_GEOMETRY_AUDIT_KEY
    return audit


def audit_matplotlib_figure(fig: Any, *, context: str | None = None) -> dict[str, Any]:
    """Collect publication layout checks from a Matplotlib figure."""

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    canvas_bbox = _bbox_to_list(fig.bbox)
    texts = _collect_text_artists(fig, renderer)
    patches = _collect_patch_artists(fig, renderer)
    three_d_axes = {
        axis_index
        for axis_index, ax in enumerate(getattr(fig, "axes", []))
        if getattr(ax, "name", "") == "3d" or hasattr(ax, "get_zlim")
    }
    bbox_reliable_texts = [text for text in texts if text.get("axis_index") not in three_d_axes]
    bbox_reliable_patches = [patch for patch in patches if patch.get("axis_index") not in three_d_axes]
    axes_font_balance = _audit_axis_font_balance(fig)
    violations: list[dict[str, Any]] = []
    canvas_overflows: list[dict[str, Any]] = []

    for text in bbox_reliable_texts:
        clip = _bbox_clip_violation(text["bbox"], canvas_bbox, DEFAULT_THRESHOLDS["text_clip_margin_px"])
        if clip:
            canvas_overflows.append({"text": _compact_text(text), "details": clip})

    for first, second, overlap in _iter_text_overlaps(bbox_reliable_texts):
        violations.append(
            _violation(
                "text_text_overlap",
                "Two text elements overlap in the rendered figure.",
                text=first,
                other_text=second,
                details=overlap,
            )
        )

    for text, patch, overlap in _iter_text_data_overlaps(bbox_reliable_texts, bbox_reliable_patches):
        violations.append(
            _violation(
                "text_data_overlap",
                "Annotation text overlaps a plotted data object.",
                text=text,
                data_object=patch,
                details=overlap,
            )
        )

    for item in axes_font_balance:
        if item["violation"]:
            violations.append(
                _violation(
                    "font_size_imbalance",
                    "Axis-label font size is disproportionate to tick-label font size.",
                    details={key: value for key, value in item.items() if key != "violation"},
                )
            )

    return _base_audit(
        context=context,
        checks={
            "matplotlib_text_count": len(texts),
            "matplotlib_patch_count": len(patches),
            "matplotlib_canvas_bbox": canvas_bbox,
            "bbox_reliable_text_count": len(bbox_reliable_texts),
            "three_d_axes_bbox_checks_skipped": sorted(three_d_axes),
            "matplotlib_canvas_overflows": canvas_overflows[:40],
            "matplotlib_canvas_overflow_count": len(canvas_overflows),
            "axes_font_balance": axes_font_balance,
        },
        violations=violations,
    )


def audit_image_file(image_path: str | Path, *, context: str | None = None) -> dict[str, Any]:
    """Run image-space checks that catch clipping after savefig/montage steps."""

    path = Path(image_path)
    violations: list[dict[str, Any]] = []
    edge_summary: dict[str, Any] | None = None
    if path.exists():
        with Image.open(path) as image:
            rgb = image.convert("RGB")
            array = np.asarray(rgb, dtype=np.int16)
        edge_summary = _audit_edge_content(array)
        if edge_summary["violation"]:
            violations.append(
                _violation(
                    "edge_content_clipping",
                    "Dark non-background pixels touch the saved bitmap edge.",
                    details=edge_summary,
                    image=str(path).replace("\\", "/"),
                )
            )
    else:
        violations.append(
            _violation(
                "image_missing",
                "Figure bitmap referenced by raw metadata does not exist.",
                image=str(path).replace("\\", "/"),
            )
        )

    return _base_audit(
        context=context or str(path).replace("\\", "/"),
        checks={"image_edge_content": edge_summary},
        violations=violations,
    )


def audit_montage_layout(metadata: dict[str, Any], *, context: str | None = None) -> dict[str, Any]:
    """Check montage metadata for panel overlap and off-canvas placement."""

    size = metadata.get("size") or [0, 0]
    canvas = [0.0, 0.0, float(size[0]), float(size[1])] if len(size) == 2 else [0.0, 0.0, 0.0, 0.0]
    panels = list(metadata.get("panels") or [])
    violations: list[dict[str, Any]] = []
    paste_boxes: list[dict[str, Any]] = []
    label_boxes: list[dict[str, Any]] = []
    for idx, panel in enumerate(panels):
        paste_box = [float(v) for v in panel.get("paste_box", [])[:4]]
        if len(paste_box) == 4:
            paste_boxes.append({"index": idx, "label": panel.get("label"), "bbox": paste_box})
            clip = _bbox_clip_violation(paste_box, canvas, DEFAULT_THRESHOLDS["text_clip_margin_px"])
            if clip:
                violations.append(
                    _violation(
                        "montage_panel_clipped",
                        "A pasted panel extends outside the montage canvas.",
                        details={"panel_index": idx, "label": panel.get("label"), **clip},
                    )
                )
        cell = panel.get("cell") or {}
        if panel.get("label") and cell.get("label_band_height", 0):
            label_box = [
                float(cell.get("x", 0)),
                float(cell.get("y", 0)),
                float(cell.get("x", 0)) + float(cell.get("width", 0)),
                float(cell.get("content_y", 0)),
            ]
            label_boxes.append({"index": idx, "label": panel.get("label"), "bbox": label_box})

    for i, first in enumerate(paste_boxes):
        for second in paste_boxes[i + 1:]:
            overlap = _bbox_overlap_details(first["bbox"], second["bbox"])
            if overlap and overlap["area_px"] > 0:
                violations.append(
                    _violation(
                        "montage_panel_overlap",
                        "Two pasted montage panels overlap.",
                        details={"first": first, "second": second, "overlap": overlap},
                    )
                )

    for label in label_boxes:
        for panel in paste_boxes:
            if label["index"] == panel["index"]:
                continue
            overlap = _bbox_overlap_details(label["bbox"], panel["bbox"])
            if overlap and overlap["area_px"] > 0:
                violations.append(
                    _violation(
                        "montage_label_panel_overlap",
                        "A subfigure label band overlaps another panel.",
                        details={"label": label, "panel": panel, "overlap": overlap},
                    )
                )

    return _base_audit(
        context=context,
        checks={"montage_panel_count": len(panels), "montage_size": size},
        violations=violations,
    )


def combine_audits(*audits: dict[str, Any], context: str | None = None) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    violations: list[dict[str, Any]] = []
    children: list[dict[str, Any]] = []
    for audit in audits:
        if not audit:
            continue
        children.append(audit)
        prefix = str(audit.get("context") or audit.get("kind") or len(children))
        checks[prefix] = audit.get("checks", {})
        for violation in audit.get("violations", []):
            merged = dict(violation)
            merged.setdefault("context", audit.get("context"))
            violations.append(merged)
    return _base_audit(context=context, checks=checks, violations=violations, children=children)


def validate_raw_visual_quality(raw_paths: Iterable[Path], *, root: Path | None = None) -> None:
    violations: list[str] = []
    for raw_path in raw_paths:
        raw_path = Path(raw_path)
        try:
            payload = json.loads(raw_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid figure raw JSON: {raw_path}") from exc

        rel_raw = _rel_text(raw_path, root)
        audit = payload.get(VISUAL_AUDIT_KEY)
        if audit:
            for item in audit.get("violations", []):
                violations.append(f"{rel_raw}:{item.get('kind', 'unknown')} -> {item.get('message', '')}")

    if violations:
        preview = "\n".join(f" - {item}" for item in violations[:80])
        if len(violations) > 80:
            preview += f"\n - ... {len(violations) - 80} more"
        raise ValueError(
            "Paper figure raw visual-quality audit failed. Fix clipping, overlap, "
            f"font-size imbalance, or schematic connector geometry before publication.\n{preview}"
        )


def _base_audit(
    *,
    context: str | None,
    checks: dict[str, Any] | None = None,
    violations: list[dict[str, Any]] | None = None,
    children: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "version": AUDIT_VERSION,
        "context": context,
        "thresholds": DEFAULT_THRESHOLDS,
        "checks": checks or {},
        "violations": violations or [],
    }
    if children is not None:
        result["children"] = children
    result["status"] = "pass" if not result["violations"] else "fail"
    return result


def _violation(kind: str, message: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"kind": kind, "message": message}
    payload.update(kwargs)
    return payload


def _normalize_box(item: dict[str, Any]) -> list[float]:
    bbox = item.get("bbox")
    if bbox is None:
        bbox = [item.get("x0"), item.get("y0"), item.get("x1"), item.get("y1")]
    if bbox is None or len(bbox) != 4:
        return [0.0, 0.0, 0.0, 0.0]
    x0, y0, x1, y1 = [float(value) for value in bbox]
    return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]


def _normalize_points(points: Any) -> list[list[float]]:
    normalized: list[list[float]] = []
    if not isinstance(points, list):
        return normalized
    for point in points:
        if point is None or len(point) != 2:
            continue
        normalized.append([float(point[0]), float(point[1])])
    return normalized


def _segments(points: list[list[float]]) -> list[list[list[float]]]:
    return [[points[index], points[index + 1]] for index in range(len(points) - 1)]


def _polyline_length(points: list[list[float]]) -> float:
    total = 0.0
    for start, end in _segments(points):
        total += math.hypot(end[0] - start[0], end[1] - start[1])
    return total


def _point_on_box_boundary(point: list[float], box: list[float], tol: float) -> bool:
    x, y = point
    x0, y0, x1, y1 = box
    within_x = x0 - tol <= x <= x1 + tol
    within_y = y0 - tol <= y <= y1 + tol
    on_vertical = (abs(x - x0) <= tol or abs(x - x1) <= tol) and within_y
    on_horizontal = (abs(y - y0) <= tol or abs(y - y1) <= tol) and within_x
    return bool(on_vertical or on_horizontal)


def _point_on_box_boundary_without_intrusion(
    point: list[float],
    box: list[float],
    *,
    tol: float,
    intrusion_tol: float,
) -> dict[str, Any] | None:
    if not _point_on_box_boundary(point, box, tol):
        return None
    x, y = point
    x0, y0, x1, y1 = box
    if x0 + intrusion_tol < x < x1 - intrusion_tol and y0 + intrusion_tol < y < y1 - intrusion_tol:
        return None
    if abs(x - x0) <= tol and y0 - tol <= y <= y1 + tol:
        return {"side": "left", "intrusion": round(max(0.0, x - x0), 6)}
    if abs(x - x1) <= tol and y0 - tol <= y <= y1 + tol:
        return {"side": "right", "intrusion": round(max(0.0, x1 - x), 6)}
    if abs(y - y0) <= tol and x0 - tol <= x <= x1 + tol:
        return {"side": "bottom", "intrusion": round(max(0.0, y - y0), 6)}
    if abs(y - y1) <= tol and x0 - tol <= x <= x1 + tol:
        return {"side": "top", "intrusion": round(max(0.0, y1 - y), 6)}
    return None


def _point_outside_box_clearance(
    point: list[float],
    box: list[float],
    *,
    tol: float,
    min_clearance: float,
    max_clearance: float,
) -> dict[str, Any] | None:
    x, y = point
    x0, y0, x1, y1 = box
    candidates: list[tuple[str, float]] = []
    if y0 - tol <= y <= y1 + tol:
        if x <= x0 + tol:
            candidates.append(("left", x0 - x))
        if x >= x1 - tol:
            candidates.append(("right", x - x1))
    if x0 - tol <= x <= x1 + tol:
        if y <= y0 + tol:
            candidates.append(("bottom", y0 - y))
        if y >= y1 - tol:
            candidates.append(("top", y - y1))
    for side, gap in candidates:
        if min_clearance <= gap <= max_clearance:
            return {"side": side, "gap": round(gap, 6)}
    return None


def _segment_axis_aligned(segment: list[list[float]], tol: float) -> bool:
    (x0, y0), (x1, y1) = segment
    return abs(x0 - x1) <= tol or abs(y0 - y1) <= tol


def _segment_intersects_box_interior(segment: list[list[float]], box: list[float], margin: float) -> dict[str, Any] | None:
    x0, y0, x1, y1 = box
    inner = [x0 + margin, y0 + margin, x1 - margin, y1 - margin]
    if inner[0] >= inner[2] or inner[1] >= inner[3]:
        inner = box
    p0, p1 = segment
    if _point_inside_box(p0, inner) or _point_inside_box(p1, inner):
        return {"kind": "endpoint_inside"}
    edges = [
        [[inner[0], inner[1]], [inner[2], inner[1]]],
        [[inner[2], inner[1]], [inner[2], inner[3]]],
        [[inner[2], inner[3]], [inner[0], inner[3]]],
        [[inner[0], inner[3]], [inner[0], inner[1]]],
    ]
    for edge_index, edge in enumerate(edges):
        relation = _segment_relation(segment, edge)
        if relation and relation["kind"] != "endpoint_touch":
            return {"kind": "edge_intersection", "edge_index": edge_index, "relation": relation}
    return None


def _point_inside_box(point: list[float], box: list[float]) -> bool:
    x, y = point
    return bool(box[0] < x < box[2] and box[1] < y < box[3])


def _arrow_pair_allowed(first: dict[str, Any], second: dict[str, Any]) -> bool:
    first_allowed = {str(item) for item in first.get("allowed_arrow_intersections", [])}
    second_allowed = {str(item) for item in second.get("allowed_arrow_intersections", [])}
    return str(second.get("id")) in first_allowed or str(first.get("id")) in second_allowed


def _segment_relation(first: list[list[float]], second: list[list[float]]) -> dict[str, Any] | None:
    p = first[0]
    p2 = first[1]
    q = second[0]
    q2 = second[1]
    r = [p2[0] - p[0], p2[1] - p[1]]
    s = [q2[0] - q[0], q2[1] - q[1]]
    rxs = _cross(r, s)
    q_minus_p = [q[0] - p[0], q[1] - p[1]]
    qmpxr = _cross(q_minus_p, r)
    eps = 1e-9

    if abs(rxs) <= eps and abs(qmpxr) <= eps:
        r_len_sq = _dot(r, r)
        s_len_sq = _dot(s, s)
        if r_len_sq <= eps or s_len_sq <= eps:
            return None
        t0 = _dot(q_minus_p, r) / r_len_sq
        t1 = t0 + _dot(s, r) / r_len_sq
        lo = max(0.0, min(t0, t1))
        hi = min(1.0, max(t0, t1))
        if hi < lo:
            return None
        overlap_length = max(0.0, hi - lo) * math.sqrt(r_len_sq)
        if overlap_length <= eps:
            return {"kind": "endpoint_touch", "point": _point_on_segment_projection(p, r, lo)}
        return {"kind": "collinear_overlap", "length": round(overlap_length, 6), "t_range": [round(lo, 6), round(hi, 6)]}

    if abs(rxs) <= eps:
        return None

    t = _cross(q_minus_p, s) / rxs
    u = _cross(q_minus_p, r) / rxs
    if -eps <= t <= 1.0 + eps and -eps <= u <= 1.0 + eps:
        point = [p[0] + t * r[0], p[1] + t * r[1]]
        if t <= eps or t >= 1.0 - eps or u <= eps or u >= 1.0 - eps:
            return {"kind": "endpoint_touch", "point": [round(point[0], 6), round(point[1], 6)]}
        return {
            "kind": "crossing",
            "point": [round(point[0], 6), round(point[1], 6)],
            "t": round(t, 6),
            "u": round(u, 6),
        }
    return None


def _point_on_segment_projection(start: list[float], direction: list[float], t: float) -> list[float]:
    return [round(start[0] + direction[0] * t, 6), round(start[1] + direction[1] * t, 6)]


def _cross(first: list[float], second: list[float]) -> float:
    return first[0] * second[1] - first[1] * second[0]


def _dot(first: list[float], second: list[float]) -> float:
    return first[0] * second[0] + first[1] * second[1]


def _collect_text_artists(fig: Any, renderer: Any) -> list[dict[str, Any]]:
    texts: list[dict[str, Any]] = []

    def add_text(artist: Any, *, role: str, axis_index: int | None = None, group: str | None = None) -> None:
        if artist is None or not getattr(artist, "get_visible", lambda: True)():
            return
        text = str(getattr(artist, "get_text", lambda: "")() or "")
        if not text.strip():
            return
        try:
            bbox = artist.get_window_extent(renderer)
        except Exception:
            return
        bbox_list = _bbox_to_list(bbox)
        if _bbox_area(bbox_list) <= 0:
            return
        texts.append(
            {
                "text": text,
                "role": role,
                "axis_index": axis_index,
                "group": group,
                "font_size_pt": float(getattr(artist, "get_fontsize", lambda: 0.0)()),
                "bbox": bbox_list,
            }
        )

    suptitle = getattr(fig, "_suptitle", None)
    add_text(suptitle, role="figure_suptitle", group="figure")
    for idx, artist in enumerate(getattr(fig, "texts", [])):
        add_text(artist, role="figure_text", group=f"figure_text_{idx}")

    for axis_index, ax in enumerate(getattr(fig, "axes", [])):
        add_text(getattr(ax, "xaxis", None).label if hasattr(ax, "xaxis") else None, role="axis_label_x", axis_index=axis_index, group=f"axis_{axis_index}")
        add_text(getattr(ax, "yaxis", None).label if hasattr(ax, "yaxis") else None, role="axis_label_y", axis_index=axis_index, group=f"axis_{axis_index}")
        zaxis = getattr(ax, "zaxis", None)
        add_text(getattr(zaxis, "label", None), role="axis_label_z", axis_index=axis_index, group=f"axis_{axis_index}")
        for tick_index, artist in enumerate(ax.get_xticklabels(minor=False) if hasattr(ax, "get_xticklabels") else []):
            add_text(artist, role="tick_label_x", axis_index=axis_index, group=f"axis_{axis_index}_xtick_{tick_index}")
        for tick_index, artist in enumerate(ax.get_yticklabels(minor=False) if hasattr(ax, "get_yticklabels") else []):
            add_text(artist, role="tick_label_y", axis_index=axis_index, group=f"axis_{axis_index}_ytick_{tick_index}")
        if zaxis is not None and hasattr(ax, "get_zticklabels"):
            for tick_index, artist in enumerate(ax.get_zticklabels(minor=False)):
                add_text(artist, role="tick_label_z", axis_index=axis_index, group=f"axis_{axis_index}_ztick_{tick_index}")
        for text_index, artist in enumerate(getattr(ax, "texts", [])):
            add_text(artist, role="annotation", axis_index=axis_index, group=f"axis_{axis_index}_annotation_{text_index}")
        legend = ax.get_legend() if hasattr(ax, "get_legend") else None
        if legend is not None:
            add_text(legend.get_title(), role="legend_title", axis_index=axis_index, group=f"axis_{axis_index}_legend")
            for text_index, artist in enumerate(legend.get_texts()):
                add_text(artist, role="legend_text", axis_index=axis_index, group=f"axis_{axis_index}_legend_{text_index}")

    for legend_index, legend in enumerate(getattr(fig, "legends", [])):
        add_text(legend.get_title(), role="figure_legend_title", group=f"figure_legend_{legend_index}")
        for text_index, artist in enumerate(legend.get_texts()):
            add_text(artist, role="figure_legend_text", group=f"figure_legend_{legend_index}_{text_index}")
    return texts


def _collect_patch_artists(fig: Any, renderer: Any) -> list[dict[str, Any]]:
    patches: list[dict[str, Any]] = []
    fig_area = max(_bbox_area(_bbox_to_list(fig.bbox)), 1.0)
    for axis_index, ax in enumerate(getattr(fig, "axes", [])):
        if not getattr(ax, "axison", True):
            continue
        for patch_index, patch in enumerate(getattr(ax, "patches", [])):
            if not getattr(patch, "get_visible", lambda: True)():
                continue
            try:
                if not patch.get_transform().contains_branch(ax.transData):
                    continue
            except Exception:
                continue
            try:
                alpha = patch.get_alpha()
                face_alpha = patch.get_facecolor()[-1]
            except Exception:
                alpha = None
                face_alpha = 1.0
            if alpha == 0 or face_alpha <= 0.05:
                continue
            try:
                bbox = _bbox_to_list(patch.get_window_extent(renderer))
            except Exception:
                continue
            area = _bbox_area(bbox)
            if area <= 1.0 or area > fig_area * 0.75:
                continue
            patches.append({"role": type(patch).__name__, "axis_index": axis_index, "patch_index": patch_index, "bbox": bbox})
    return patches


def _audit_axis_font_balance(fig: Any) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for axis_index, ax in enumerate(getattr(fig, "axes", [])):
        label_sizes: list[float] = []
        tick_sizes: list[float] = []
        for axis in [getattr(ax, "xaxis", None), getattr(ax, "yaxis", None), getattr(ax, "zaxis", None)]:
            label = getattr(axis, "label", None)
            if label is not None and str(label.get_text() or "").strip():
                label_sizes.append(float(label.get_fontsize()))
        for getter in ("get_xticklabels", "get_yticklabels", "get_zticklabels"):
            if not hasattr(ax, getter):
                continue
            for tick in getattr(ax, getter)(minor=False):
                if tick.get_visible() and str(tick.get_text() or "").strip():
                    tick_sizes.append(float(tick.get_fontsize()))
        if not label_sizes or not tick_sizes:
            continue
        max_label = max(label_sizes)
        tick_median = float(median(tick_sizes))
        ratio = max_label / tick_median if tick_median > 0 else math.inf
        results.append(
            {
                "axis_index": axis_index,
                "max_axis_label_font_pt": round(max_label, 3),
                "median_tick_label_font_pt": round(tick_median, 3),
                "ratio": round(ratio, 3),
                "violation": bool(
                    ratio > DEFAULT_THRESHOLDS["axis_label_tick_font_ratio_max"]
                    and max_label >= DEFAULT_THRESHOLDS["axis_label_font_min_pt"]
                ),
            }
        )
    return results


def _iter_text_overlaps(texts: list[dict[str, Any]]):
    for i, first in enumerate(texts):
        for second in texts[i + 1:]:
            if _ignore_text_pair(first, second):
                continue
            overlap = _bbox_overlap_details(first["bbox"], second["bbox"])
            if not overlap:
                continue
            if (
                overlap["area_px"] >= DEFAULT_THRESHOLDS["text_text_overlap_min_area_px"]
                and overlap["min_fraction"] >= DEFAULT_THRESHOLDS["text_text_overlap_min_fraction"]
            ):
                yield _compact_text(first), _compact_text(second), overlap


def _iter_text_data_overlaps(texts: list[dict[str, Any]], patches: list[dict[str, Any]]):
    for text in texts:
        if text.get("role") != "annotation":
            continue
        for patch in patches:
            if patch.get("axis_index") != text.get("axis_index"):
                continue
            overlap = _bbox_overlap_details(text["bbox"], patch["bbox"])
            if not overlap:
                continue
            if (
                overlap["area_px"] >= DEFAULT_THRESHOLDS["text_data_overlap_min_area_px"]
                and overlap["min_fraction"] >= DEFAULT_THRESHOLDS["text_data_overlap_min_fraction"]
            ):
                yield _compact_text(text), patch, overlap


def _ignore_text_pair(first: dict[str, Any], second: dict[str, Any]) -> bool:
    if first.get("group") == second.get("group"):
        return True
    if str(first.get("role", "")).startswith("tick_label") and str(second.get("role", "")).startswith("tick_label"):
        return True
    if str(first.get("role", "")).startswith("legend") and str(second.get("role", "")).startswith("legend"):
        return True
    if str(first.get("role", "")).startswith("figure_legend") and str(second.get("role", "")).startswith("figure_legend"):
        return True
    return False


def _compact_text(text: dict[str, Any]) -> dict[str, Any]:
    return {
        "text": text.get("text"),
        "role": text.get("role"),
        "axis_index": text.get("axis_index"),
        "font_size_pt": text.get("font_size_pt"),
        "bbox": text.get("bbox"),
    }


def _bbox_to_list(bbox: Any) -> list[float]:
    return [round(float(bbox.x0), 3), round(float(bbox.y0), 3), round(float(bbox.x1), 3), round(float(bbox.y1), 3)]


def _bbox_area(bbox: list[float]) -> float:
    return max(0.0, float(bbox[2]) - float(bbox[0])) * max(0.0, float(bbox[3]) - float(bbox[1]))


def _bbox_overlap_details(first: list[float], second: list[float]) -> dict[str, Any] | None:
    x0 = max(float(first[0]), float(second[0]))
    y0 = max(float(first[1]), float(second[1]))
    x1 = min(float(first[2]), float(second[2]))
    y1 = min(float(first[3]), float(second[3]))
    if x1 <= x0 or y1 <= y0:
        return None
    area = (x1 - x0) * (y1 - y0)
    first_area = max(_bbox_area(first), 1e-9)
    second_area = max(_bbox_area(second), 1e-9)
    return {
        "area_px": round(area, 3),
        "fraction_first": round(area / first_area, 4),
        "fraction_second": round(area / second_area, 4),
        "min_fraction": round(area / min(first_area, second_area), 4),
        "bbox": [round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3)],
    }


def _bbox_clip_violation(bbox: list[float], canvas: list[float], margin: float) -> dict[str, Any] | None:
    overflow = {
        "left_px": round(max(0.0, float(canvas[0]) - float(bbox[0]) - margin), 3),
        "bottom_px": round(max(0.0, float(canvas[1]) - float(bbox[1]) - margin), 3),
        "right_px": round(max(0.0, float(bbox[2]) - float(canvas[2]) - margin), 3),
        "top_px": round(max(0.0, float(bbox[3]) - float(canvas[3]) - margin), 3),
    }
    if any(value > 0 for value in overflow.values()):
        return {"bbox": bbox, "canvas_bbox": canvas, "overflow": overflow}
    return None


def _audit_edge_content(array: np.ndarray) -> dict[str, Any]:
    height, width = array.shape[:2]
    edge = int(DEFAULT_THRESHOLDS["edge_guard_px"])
    if height == 0 or width == 0:
        return {"size": [width, height], "violation": False, "edge_dark_pixels": 0, "edge_ratio": 0.0}
    edge = max(1, min(edge, height // 2 if height > 1 else 1, width // 2 if width > 1 else 1))
    mask = np.zeros((height, width), dtype=bool)
    mask[:edge, :] = True
    mask[-edge:, :] = True
    mask[:, :edge] = True
    mask[:, -edge:] = True
    edge_pixels = array[mask]
    luminance = 0.2126 * edge_pixels[:, 0] + 0.7152 * edge_pixels[:, 1] + 0.0722 * edge_pixels[:, 2]
    nonwhite_delta = np.max(np.abs(edge_pixels - 255), axis=1)
    dark = (luminance < DEFAULT_THRESHOLDS["edge_dark_luminance_max"]) & (
        nonwhite_delta >= DEFAULT_THRESHOLDS["edge_nonwhite_delta_min"]
    )
    dark_count = int(np.count_nonzero(dark))
    edge_count = int(edge_pixels.shape[0])
    ratio = float(dark_count) / float(max(edge_count, 1))
    violation = bool(
        dark_count >= DEFAULT_THRESHOLDS["edge_dark_pixel_min_count"]
        and ratio >= DEFAULT_THRESHOLDS["edge_dark_pixel_min_ratio"]
    )
    return {
        "size": [int(width), int(height)],
        "edge_guard_px": edge,
        "edge_pixel_count": edge_count,
        "edge_dark_pixels": dark_count,
        "edge_ratio": round(ratio, 6),
        "violation": violation,
    }


def _resolve_image_for_raw(raw_path: Path, payload: dict[str, Any]) -> Path | None:
    figure = payload.get("figure")
    candidates: list[Path] = []
    if isinstance(figure, str) and figure.strip():
        figure_path = Path(figure)
        candidates.append(figure_path if figure_path.is_absolute() else raw_path.parent / figure_path)
    candidates.append(raw_path.with_suffix(".png"))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0] if candidates else None


def _rel_text(path: Path, root: Path | None) -> str:
    path = path.resolve()
    if root is not None:
        try:
            return str(path.relative_to(root.resolve())).replace("\\", "/")
        except ValueError:
            pass
    return str(path).replace("\\", "/")
