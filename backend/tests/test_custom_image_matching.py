import io

from PIL import Image

from server import (
    build_custom_row_backgrounds,
    extract_pic_no_from_filename,
    normalize_pic_no,
)


def _tiny_image() -> Image.Image:
    return Image.new("RGB", (10, 10), color=(120, 80, 200))


def _asset(filename: str) -> dict:
    return {
        "filename": filename,
        "slug": filename.rsplit(".", 1)[0].lower(),
        "pic_no": extract_pic_no_from_filename(filename),
        "image": _tiny_image(),
    }


def test_normalize_pic_no_variants():
    assert normalize_pic_no("01") == "1"
    assert normalize_pic_no("10.0") == "10"
    assert normalize_pic_no("Pic 5") == "5"
    assert normalize_pic_no("PIC-12") == "12"


def test_extract_pic_no_from_filename():
    assert extract_pic_no_from_filename(r"folder\10.jpg") == "10"
    assert extract_pic_no_from_filename("pic_5.png") == "5"
    assert extract_pic_no_from_filename("IMG-23.webp") == "23"
    assert extract_pic_no_from_filename("seo-title-only.png") == ""


def test_sequential_fallback_when_filenames_do_not_match_pic_no():
    records = [{"PIC NO.": str(i), "PIN NAME": f"pin-{i}"} for i in range(1, 26)]
    assets = [_asset(f"random-name-{i}.jpg") for i in range(1, 26)]

    result = build_custom_row_backgrounds(records, assets, "pin_name_match_then_sequential")

    assert len(result["records"]) == 25
    assert len(result["backgrounds"]) == 25
    assert result["missing_count"] == 0


def test_pic_no_match_preferred_over_sequential():
    records = [
        {"PIC NO.": "1", "PIN NAME": "first"},
        {"PIC NO.": "2", "PIN NAME": "second"},
    ]
    assets = [
        _asset("2.jpg"),
        _asset("1.jpg"),
    ]

    result = build_custom_row_backgrounds(records, assets, "pin_name_match_then_sequential")

    assert len(result["records"]) == 2
    assert result["missing_count"] == 0
