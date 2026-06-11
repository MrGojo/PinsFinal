import io
from pathlib import Path

import pandas as pd
import pytest

from server import infer_pin_name_from_row, parse_file


def _build_multi_title_xlsx(path: Path, data_row_count: int) -> bytes:
  rows = [
    ["", "TOP", "CENTER", "BOTTOM"],
    ["PIC NO.", "PIN TITLE- TOP", "PIN TITLE- CENTER", "PIN TITLE- BOTTOM", "END LINE", "PIN NAME"],
  ]
  for index in range(1, data_row_count + 1):
    rows.append(
      [
        str(index),
        f"Top title {index}",
        f"Center title {index}",
        f"Bottom title {index}",
        "Tap to learn more",
        f"pin-name-{index}",
      ]
    )
  rows.append(["", "", "PIN SIZE : 1 - 1000 x 2100 pixels (1:2.1 Ratio)", "", "", ""])
  frame = pd.DataFrame(rows)
  frame.to_excel(path, index=False, header=False)
  return path.read_bytes()


def test_parse_multi_title_many_rows(tmp_path):
  xlsx_path = tmp_path / "many-rows.xlsx"
  file_bytes = _build_multi_title_xlsx(xlsx_path, 30)
  parsed = parse_file(xlsx_path.name, file_bytes)
  assert len(parsed) == 30
  assert parsed.iloc[0]["PIN TITLE - CENTER"] == "Center title 1"
  assert parsed.iloc[29]["PIN NAME"] == "pin-name-30"


def test_infer_pin_name_when_name_column_blank():
  row = {
    "PIN NAME": "",
    "PIC NO.": "7",
    "PIN TITLE - TOP": "",
    "PIN TITLE - CENTER": "Center only",
    "PIN TITLE - BOTTOM": "",
    "PIN TITLE 2ND LINE": "",
  }
  assert infer_pin_name_from_row(row, 1) == "pin-7"


def test_parse_multi_title_rows_without_pin_name_column(tmp_path):
  rows = [
    ["", "TOP", "CENTER", "BOTTOM"],
    ["PIC NO.", "PIN TITLE- TOP", "PIN TITLE- CENTER", "PIN TITLE- BOTTOM", "END LINE", "PIN NAME"],
  ]
  for index in range(1, 16):
    rows.append([str(index), f"T{index}", f"C{index}", f"B{index}", "Learn more", ""])
  frame = pd.DataFrame(rows)
  xlsx_path = tmp_path / "no-pin-name.xlsx"
  frame.to_excel(xlsx_path, index=False, header=False)
  parsed = parse_file(xlsx_path.name, xlsx_path.read_bytes())
  assert len(parsed) == 15
  assert parsed.iloc[14]["PIN NAME"] == "pin-15"
