# Expenses Quick Guide

## Run the dashboard

In PowerShell:

```powershell
cd D:\rdev\personal\fin\expenses
python .\build_expenses_report.py
```

This reads `expenses.csv` and regenerates `expenses_dashboard.html`.

## Update expenses

Keep the CSV columns in this order:

```text
type,category,date,month,amount,notes,status
```

Add one expense per row. Enter amounts as plain numbers, without a currency symbol or thousands separators.

- `type`: Expense name or description.
- `category`: Your category label. If blank, the script assigns one based on keywords in `type`.
- `date`: Optional full date in `YYYY-MM-DD` format. Use the payment date for Paid expenses and the due date for Pending expenses. When entered, this date determines the month and year used in the dashboard.
- `month`: Month such as `Oct` or `Nov`; used when `date` is blank. Leave blank with `date` also blank for an undated recurring expense.
- `amount`: Numeric amount in rupees.
- `notes`: Optional details. Quote the field in CSV if it contains a comma.
- `status`: Use `Paid` or `Pending`. Capitalization does not matter.

Example:

```csv
School fee,Education,2026-10-07,Oct,20000,Term payment,Pending
```

Do not guess unknown dates; leave `date` blank and use `month` until the exact date is known. Month-only entries are assigned to the current year in the budget table, so use full dates for accurate year-end tracking.

## Budget and totals

The monthly budget is set near the top of `build_expenses_report.py`:

```python
MONTHLY_BUDGET = 120_000
```

Change `120_000` to adjust the monthly budget, then rerun the script.

The Monthly Budget vs Actual table shows:

- `Actual (Paid)`: Expenses marked Paid.
- `Pending`: Expenses not marked Paid.
- `Remaining After Paid`: Budget minus paid expenses.
- `Projected Remaining`: Budget minus paid and pending expenses.

Remaining values are green when zero or positive, and orange when negative. Investment entries are included in the totals. The current-month category breakdown includes Paid expenses only.
