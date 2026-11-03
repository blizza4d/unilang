import pytest
from agents.grounding_agent import sanitize_box_coords
from utils.grounding_verify import calculate_iou, verify_box_dimensions


def test_sanitize_box_coords_clamping():
    # Coords outside [0, 1000] should be clamped
    raw_box = [-50, -10, 1050, 1200]
    sanitized = sanitize_box_coords(raw_box)
    assert sanitized == [0, 0, 1000, 1000]


def test_sanitize_box_coords_inversion_fix():
    # If ymin > ymax or xmin > xmax, they should be swapped
    raw_box = [600, 700, 200, 100]
    sanitized = sanitize_box_coords(raw_box)
    assert sanitized[0] <= sanitized[2]
    assert sanitized[1] <= sanitized[3]
    assert sanitized == [200, 100, 600, 700]


def test_calculate_iou_exact_match():
    box1 = [100, 100, 200, 200]
    box2 = [100, 100, 200, 200]
    iou = calculate_iou(box1, box2)
    assert pytest.approx(iou, 0.001) == 1.0


def test_calculate_iou_disjoint():
    box1 = [0, 0, 50, 50]
    box2 = [100, 100, 150, 150]
    iou = calculate_iou(box1, box2)
    assert iou == 0.0


def test_calculate_iou_partial_overlap():
    box1 = [0, 0, 100, 100]
    box2 = [50, 50, 150, 150]
    # Inter: 50x50 = 2500
    # Union: 10000 + 10000 - 2500 = 17500
    # IoU: 2500 / 17500 = 1/7 ~= 0.1428
    iou = calculate_iou(box1, box2)
    assert pytest.approx(iou, 0.01) == 0.143


def test_verify_box_dimensions_valid():
    valid_box = [100, 100, 300, 400]
    assert verify_box_dimensions(valid_box) is True


def test_verify_box_dimensions_degenerate():
    # Zero width
    zero_w = [100, 100, 200, 100]
    assert verify_box_dimensions(zero_w) is False

    # Zero height
    zero_h = [100, 100, 100, 200]
    assert verify_box_dimensions(zero_h) is False
