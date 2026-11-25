# 📊 Sales Report Automator

Upload a messy sales CSV/Excel file and get a clean, summarised report: KPIs, charts by product, region and month, plus a formatted multi-sheet Excel download.

**Problem it solves:** many small businesses still build weekly sales reports by hand in Excel. This tool does the cleaning and summarising in seconds.

## Features
- Accepts `.csv`, `.xlsx`, `.xls`
- Normalises column names, trims and title-cases text, parses dates and numbers
- Removes blank, invalid (e.g. negative quantity) and duplicate rows, and tells you how many
- KPIs: total revenue, units, orders, average order value, date range
- Breakdowns by product, region and month, with revenue share
- Downloads a formatted Excel report (Summary, By Product, By Region, By Month, Clean Data)
- Clear error messages for missing columns or unsupported files

## Expected columns
`date`, `product`, `region`, `quantity`, `unit_price` (case and spaces don't matter; extra columns are ignored)

## Run it
```bash
pip install -r requirements.txt
python generate_sample_data.py   # creates a messy sample_sales.csv
streamlit run app.py
```

## Test it
```bash
pytest
```

## Project layout
- `report.py` – cleaning, summarising, Excel export (no UI code, easy to test)
- `app.py` – Streamlit interface
- `generate_sample_data.py` – fake messy data for demos
- `test_report.py` – unit tests

## Screenshot
![alt text](<Screenshot from 2026-11-25 12-41-16.png>)![alt text](<Screenshot from 2026-11-25 12-41-27.png>) ![alt text](<Screenshot from 2026-11-25 12-41-41.png>) ![alt text](<Screenshot from 2026-11-25 12-42-05.png>) 
## Possible next steps
Column-mapping screen for files with different headers, currency selection, PDF export, scheduled email delivery.
