"""Core logic: load, clean and summarise a sales file, then export an Excel report."""
from __future__ import annotations

import io
from dataclasses import dataclass

import pandas as pd
from openpyxl.styles import Font

REQUIRED_COLUMNS = ["date", "product", "region", "quantity", "unit_price"]


class ReportError(ValueError):
    """Raised when the input file cannot be turned into a report."""


@dataclass
class Report:
    clean: pd.DataFrame
    kpis: dict
    by_product: pd.DataFrame
    by_region: pd.DataFrame
    by_month: pd.DataFrame
    rows_dropped: int


def load_file(file, filename: str) -> pd.DataFrame:
    """Read a CSV or Excel file-like object into a DataFrame."""
    name = filename.lower()
    if name.endswith(".csv"):
        return pd.read_csv(file)
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(file)
    raise ReportError("Unsupported file type. Please upload a .csv or .xlsx file.")


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Normalise column names, fix types, drop unusable rows."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ReportError(
            f"Missing required column(s): {', '.join(missing)}. "
            f"Expected: {', '.join(REQUIRED_COLUMNS)}."
        )

    before = len(df)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    for col in ("product", "region"):
        df[col] = df[col].astype("string").str.strip().str.title()

    df = df.dropna(subset=REQUIRED_COLUMNS)
    df = df[(df["quantity"] > 0) & (df["unit_price"] >= 0)]
    df = df.drop_duplicates()
    df["revenue"] = df["quantity"] * df["unit_price"]
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df.reset_index(drop=True), before - len(df)


def summarise(df: pd.DataFrame, rows_dropped: int = 0) -> Report:
    if df.empty:
        raise ReportError("No valid rows left after cleaning.")

    kpis = {
        "Total revenue": float(df["revenue"].sum()),
        "Total units sold": int(df["quantity"].sum()),
        "Number of orders": int(len(df)),
        "Average order value": float(df["revenue"].mean()),
        "Date range": f"{df['date'].min():%Y-%m-%d} to {df['date'].max():%Y-%m-%d}",
    }

    def group(col: str) -> pd.DataFrame:
        out = (
            df.groupby(col, as_index=False)
            .agg(revenue=("revenue", "sum"), units=("quantity", "sum"), orders=("revenue", "size"))
            .sort_values("revenue", ascending=False)
            .reset_index(drop=True)
        )
        out["share_%"] = (out["revenue"] / out["revenue"].sum() * 100).round(1)
        return out

    by_month = group("month").sort_values("month").reset_index(drop=True)
    return Report(df, kpis, group("product"), group("region"), by_month, rows_dropped)


def build_report(file, filename: str) -> Report:
    raw = load_file(file, filename)
    cleaned, dropped = clean(raw)
    return summarise(cleaned, dropped)


def to_excel_bytes(report: Report) -> bytes:
    """Export the report as a formatted multi-sheet Excel workbook."""
    buf = io.BytesIO()
    kpi_df = pd.DataFrame({"Metric": list(report.kpis), "Value": list(report.kpis.values())})
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        kpi_df.to_excel(xw, "Summary", index=False)
        report.by_product.to_excel(xw, "By Product", index=False)
        report.by_region.to_excel(xw, "By Region", index=False)
        report.by_month.to_excel(xw, "By Month", index=False)
        out = report.clean.copy()
        out["date"] = out["date"].dt.date
        out.to_excel(xw, "Clean Data", index=False)

        for ws in xw.book.worksheets:
            ws.freeze_panes = "A2"
            for cell in ws[1]:
                cell.font = Font(bold=True)
            for col in ws.columns:
                width = max(len(str(c.value)) if c.value is not None else 0 for c in col)
                ws.column_dimensions[col[0].column_letter].width = min(width + 3, 40)
    return buf.getvalue()
