import io

import pandas as pd
import pytest

from report import ReportError, build_report, to_excel_bytes


def csv(text: str) -> io.StringIO:
    return io.StringIO(text)


GOOD = """Date,Product,Region,Quantity,Unit Price
2025-01-05, laptop ,north,2,100
2025-01-06,Laptop,North,1,100
2025-02-01,phone,south,3,50
"""


def test_cleaning_and_kpis():
    r = build_report(csv(GOOD), "x.csv")
    assert r.kpis["Total revenue"] == 450.0
    assert r.kpis["Total units sold"] == 6
    assert set(r.by_product["product"]) == {"Laptop", "Phone"}
    assert list(r.by_month["month"]) == ["2025-01", "2025-02"]


def test_bad_rows_dropped():
    bad = GOOD + "not a date,Phone,south,1,10\n2025-03-01,Phone,south,-1,10\n2025-03-02,Phone,south,abc,10\n"
    r = build_report(csv(bad), "x.csv")
    assert r.rows_dropped == 3
    assert r.kpis["Number of orders"] == 3


def test_duplicates_removed():
    r = build_report(csv(GOOD + "2025-02-01,phone,south,3,50\n"), "x.csv")
    assert r.kpis["Number of orders"] == 3


def test_missing_column_message():
    with pytest.raises(ReportError, match="unit_price"):
        build_report(csv("date,product,region,quantity\n2025-01-01,a,b,1\n"), "x.csv")


def test_unsupported_type():
    with pytest.raises(ReportError):
        build_report(csv(""), "x.txt")


def test_excel_export_has_sheets():
    data = to_excel_bytes(build_report(csv(GOOD), "x.csv"))
    sheets = pd.ExcelFile(io.BytesIO(data)).sheet_names
    assert sheets == ["Summary", "By Product", "By Region", "By Month", "Clean Data"]
