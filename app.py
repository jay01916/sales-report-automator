"""Streamlit front-end for the sales report automator."""
import streamlit as st

from report import ReportError, build_report, to_excel_bytes

st.set_page_config(page_title="Sales Report Automator", page_icon="📊", layout="wide")
st.title("📊 Sales Report Automator")
st.caption("Upload a messy sales CSV or Excel file and get a clean, summarised report in seconds.")

with st.expander("Expected columns"):
    st.write("`date`, `product`, `region`, `quantity`, `unit_price` (extra columns are ignored).")

uploaded = st.file_uploader("Upload sales file", type=["csv", "xlsx", "xls"])

if uploaded is None:
    st.info("Upload a file to begin. No file handy? Run `python generate_sample_data.py` to make one.")
    st.stop()

try:
    report = build_report(uploaded, uploaded.name)
except ReportError as e:
    st.error(str(e))
    st.stop()
except Exception as e:  # unexpected parse problems
    st.error(f"Could not read the file: {e}")
    st.stop()

if report.rows_dropped:
    st.warning(f"{report.rows_dropped} row(s) were removed (blank, invalid or duplicate).")

k = report.kpis
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total revenue", f"{k['Total revenue']:,.2f}")
c2.metric("Units sold", f"{k['Total units sold']:,}")
c3.metric("Orders", f"{k['Number of orders']:,}")
c4.metric("Avg order value", f"{k['Average order value']:,.2f}")
st.caption(f"Period: {k['Date range']}")

left, right = st.columns(2)
with left:
    st.subheader("Revenue by product")
    st.bar_chart(report.by_product.set_index("product")["revenue"])
with right:
    st.subheader("Revenue by region")
    st.bar_chart(report.by_region.set_index("region")["revenue"])

st.subheader("Revenue by month")
st.line_chart(report.by_month.set_index("month")["revenue"])

with st.expander("Tables"):
    st.dataframe(report.by_product, width="stretch")
    st.dataframe(report.by_region, width="stretch")
    st.dataframe(report.by_month, width="stretch")

st.download_button(
    "⬇️ Download Excel report",
    data=to_excel_bytes(report),
    file_name="sales_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
