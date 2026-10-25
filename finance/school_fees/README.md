# 🎓 School Expense Manager

A beautiful, responsive dashboard to track and visualize your children's school expenses.

## 📁 Files Created

```
school_fees/
├── school_expenses.csv       ← Your expense data (edit this)
├── build_report.py           ← Run this to generate the report
├── template.html             ← HTML template (Jinja2)
├── school_report.html        ← Generated dashboard (open in browser)
├── requirements.txt          ← Python dependencies
└── README.md                 ← This file
```

## 🚀 Quick Start

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install pandas jinja2
```

### 2️⃣ Generate the Report

```bash
python build_report.py
```

### 3️⃣ View the Dashboard

Open `school_report.html` in your web browser!

## 📊 Features

### Dashboard Includes:
- ✅ **Total Expenditure Summary** - See all spending at a glance
- ✅ **Category Breakdown** - Fees, Books, Transport, Activities, etc.
- ✅ **Interactive Charts** - Pie charts, bar graphs, and trend lines
- ✅ **Detailed Expense Table** - Sortable and filterable
- ✅ **Per-Child Summary** - Individual spending breakdown
- ✅ **Search & Filter** - Find specific expenses quickly
- ✅ **Mobile Responsive** - Works perfectly on phones
- ✅ **Print-Friendly** - Generate clean printouts

### Color Coding:
- 🔵 **Fees** - Blue
- 🟢 **Books** - Green  
- 🟣 **Uniform** - Purple
- 🟠 **Transport** - Orange
- 🔴 **Activities** - Pink
- ⚫ **Other** - Grey

## 📝 CSV Format

Your `school_expenses.csv` should have these columns:

| Column        | Type   | Example                    |
|---------------|--------|----------------------------|
| child_name    | string | "Sanvi", "Dhruvin"         |
| class_grade   | string | "Class 2", "Pre-KG"        |
| expense_type  | string | Fees / Books / Transport / Activities / Exam Fee / Uniform / Other |
| description   | string | "Term 1 Tuition Fee"       |
| amount        | float  | 4500.00                    |
| paid_date     | date   | 31-03-2026 (DD-MM-YYYY)    |
| payment_mode  | string | Cash / UPI / Bank Transfer / Cheque |
| paid_by       | string | "Father", "Mother"         |
| academic_year | string | "2025-26"                  |
| receipt_number| string | "RCP-2001" (optional)      |
| notes         | string | Optional notes             |

## 🔄 Updating Expenses

1. Edit `school_expenses.csv` - Add new rows for new expenses
2. Run `python build_report.py` again
3. Refresh `school_report.html` in your browser

## 💡 Tips

- **Keep your data organized** - Use consistent naming for children and expense types
- **Regular updates** - Run the script monthly to track trends
- **Backup your CSV** - Keep a copy of your expense data
- **Print reports** - Use browser print for clean PDF exports
- **Share with family** - The HTML file is self-contained and easy to share

## 📊 Current Summary (Generated: 03-Aug-2026)

**Total Expenditure:** ₹2,57,050.00

**Per-Child Breakdown:**
- Dhruvin: ₹88,650.00
- Sanvi: ₹1,68,400.00

**Records Tracked:** 20 expenses

## 🎨 Customization

### Change Colors
Edit the CSS in `template.html` under the `<style>` section.

### Add New Expense Types
Just add them to your CSV - the system will automatically pick them up!

### Modify Charts
Charts use Chart.js - customize them in the `<script>` section of `template.html`.

## 🐛 Troubleshooting

**"school_expenses.csv not found"**
- Ensure you're running the script from the school_fees directory
- Check the file name is spelled correctly

**"ModuleNotFoundError: No module named 'pandas'"**
- Run: `pip install pandas jinja2`

**Charts not displaying**
- Ensure you have internet connection (Chart.js loads from CDN)
- Check browser console for errors

**Date parsing errors**
- Ensure dates are in DD-MM-YYYY format (e.g., 31-03-2026)

## 📱 Mobile Support

The dashboard is fully responsive and works great on:
- 📱 Phones
- 📱 Tablets  
- 💻 Desktops
- 🖨️ Print

## 🔐 Privacy

- **No internet required** (except for Chart.js CDN)
- **No login needed**
- **Data stays local** - your CSV never leaves your computer
- **No tracking** - pure HTML/CSS/JS

## 🎯 Use Cases

- Track school expenses throughout the year
- Plan for upcoming fees
- Compare spending between children
- Generate reports for tax purposes
- Share with your spouse
- Monitor budget vs actual
- Identify spending patterns

## 📅 Academic Year Planning

Use this tool to:
1. Budget for the entire academic year
2. Track payment due dates
3. Identify peak expense months
4. Plan for major expenses (books, uniforms, etc.)

## 🤝 Contributing

Feel free to customize the template and scripts for your needs!

## 📄 License

Free to use and modify for personal use.

---

**Happy Expense Tracking! 🎉**

*Built with ❤️ using Python, Pandas, Jinja2, and Chart.js*
