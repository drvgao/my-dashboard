import csv
import json
from datetime import datetime

MONTHLY_BUDGET = 140_000

CURRENT_MONTH_SORT_SCRIPT = r"""<script>
const expensesTable = document.querySelector('.current-month-table');
if (expensesTable) {
    const tableBody = expensesTable.tBodies[0];
    const sortButtons = expensesTable.querySelectorAll('.sort-button');

    function getSortValue(row, columnIndex, sortType) {
        const text = row.cells[columnIndex].textContent.trim();
        if (sortType === 'amount') {
            return Number(text.replace(/[^0-9.-]/g, '')) || 0;
        }
        if (sortType === 'date') {
            const dateMatch = text.match(/^\d{4}-\d{2}-(\d{2})$/);
            return dateMatch ? Number(dateMatch[1]) : Number.MAX_SAFE_INTEGER;
        }
        return text.toLocaleLowerCase();
    }

    sortButtons.forEach(button => {
        button.addEventListener('click', () => {
            const header = button.closest('th');
            const ascending = header.getAttribute('aria-sort') !== 'ascending';
            const columnIndex = Number(button.dataset.columnIndex);
            const sortType = button.dataset.sortType;

            expensesTable.querySelectorAll('thead th').forEach(cell => {
                cell.setAttribute('aria-sort', 'none');
            });
            header.setAttribute('aria-sort', ascending ? 'ascending' : 'descending');
            sortButtons.forEach(sortButton => {
                sortButton.querySelector('.sort-indicator').textContent = String.fromCharCode(8597);
            });
            button.querySelector('.sort-indicator').textContent = String.fromCharCode(ascending ? 8593 : 8595);

            const expenseRows = Array.from(tableBody.querySelectorAll('tr[data-expense-row="true"]'));
            expenseRows.sort((left, right) => {
                const leftValue = getSortValue(left, columnIndex, sortType);
                const rightValue = getSortValue(right, columnIndex, sortType);
                if (leftValue === rightValue) return 0;
                const order = leftValue < rightValue ? -1 : 1;
                return ascending ? order : -order;
            });

            const summaryRows = Array.from(tableBody.querySelectorAll('tr:not([data-expense-row="true"])'));
            tableBody.replaceChildren(...expenseRows, ...summaryRows);
        });
    });
}
</script>"""

def categorize_expense(expense_type):
    """Categorize expense based on type keywords"""
    expense_type_lower = expense_type.lower()
    
    if any(keyword in expense_type_lower for keyword in ['school', 'term', 'education', 'fee']):
        return 'Education'
    elif any(keyword in expense_type_lower for keyword in ['mutual fund', 'investment', 'sip']):
        return 'Investment'
    elif any(keyword in expense_type_lower for keyword in ['food', 'protein', 'health', 'medical']):
        return 'Health & Wellness'
    elif any(keyword in expense_type_lower for keyword in ['transport', 'travel', 'fuel']):
        return 'Transportation'
    elif any(keyword in expense_type_lower for keyword in ['rent', 'utility', 'electricity', 'water']):
        return 'Household'
    else:
        return 'Other'

def read_expenses(csv_file):
    """Read expenses from CSV file"""
    expenses = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = row.get('category', '').strip() or categorize_expense(row['type'])
            date_text = (row.get('date') or '').strip()
            try:
                date_value = datetime.strptime(date_text, '%Y-%m-%d') if date_text else None
            except ValueError as error:
                raise ValueError(
                    f"Invalid date for {row['type']}: {date_text}. Use YYYY-MM-DD."
                ) from error
            expenses.append({
                'type': row['type'],
                'category': category,
                'date': date_text,
                'date_value': date_value,
                'month': date_value.strftime('%b') if date_value else row['month'] if row['month'] else 'Recurring',
                'amount': float(row['amount']) if row['amount'] else 0,
                'status': row.get('status', 'Pending').strip() or 'Pending',
                'notes': row['notes']
            })
    return expenses

def calculate_summary(expenses):
    """Calculate summary statistics"""
    total = sum(exp['amount'] for exp in expenses)
    category_totals = {}
    for exp in expenses:
        cat = exp['category']
        category_totals[cat] = category_totals.get(cat, 0) + exp['amount']
    return total, category_totals

def calculate_monthly_budget_totals(expenses, today):
    """Group paid and pending amounts by month and year."""
    monthly_totals = {}
    for exp in expenses:
        if exp['date_value']:
            period = (exp['date_value'].year, exp['date_value'].month)
        elif exp['month'].strip().casefold() == 'recurring':
            period = (today.year, today.month)
        else:
            try:
                month_number = datetime.strptime(exp['month'][:3].title(), '%b').month
            except ValueError:
                continue
            period = (today.year, month_number)

        month_totals = monthly_totals.setdefault(period, {'paid': 0, 'pending': 0})
        status_key = 'paid' if exp['status'].strip().casefold() == 'paid' else 'pending'
        month_totals[status_key] += exp['amount']
    return monthly_totals

def generate_html(expenses, output_file):
    """Generate HTML report"""
    today = datetime.now()
    monthly_budget_totals = calculate_monthly_budget_totals(expenses, today)
    current_month = today.strftime('%B')
    current_month_number = today.month
    current_month_names = {current_month.casefold(), today.strftime('%b').casefold()}
    current_month_expenses = [
        exp for exp in expenses
        if (
            exp['date_value'].year == today.year and exp['date_value'].month == today.month
            if exp['date_value'] else exp['month'].strip().casefold() in current_month_names | {'recurring'}
        )
    ]
    paid_expenses = [
        exp for exp in current_month_expenses
        if exp['status'].strip().casefold() == 'paid'
    ]
    pending_expenses = [
        exp for exp in current_month_expenses
        if exp['status'].strip().casefold() != 'paid'
    ]
    upcoming_expenses = []
    for exp in expenses:
        if exp['date_value']:
            if (exp['date_value'].year, exp['date_value'].month) > (today.year, today.month):
                upcoming_expenses.append(exp)
            continue
        if exp['month'].strip().casefold() == 'recurring':
            continue
        try:
            expense_month_number = datetime.strptime(exp['month'][:3].title(), '%b').month
        except ValueError:
            continue
        if expense_month_number > current_month_number:
            upcoming_expenses.append(exp)
    upcoming_expenses.sort(
        key=lambda exp: exp['date_value'] or datetime(
            today.year, datetime.strptime(exp['month'][:3].title(), '%b').month, 1
        )
    )
    _, category_totals = calculate_summary(current_month_expenses)
    category_chart_items = sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
    category_chart_labels = json.dumps([category for category, _ in category_chart_items])
    category_chart_values = json.dumps([amount for _, amount in category_chart_items])
    category_chart_height = max(360, len(category_chart_items) * 44 + 50)
    paid_total = sum(exp['amount'] for exp in paid_expenses)
    pending_total = sum(exp['amount'] for exp in pending_expenses)
    current_month_total = paid_total + pending_total
    upcoming_total = sum(exp['amount'] for exp in upcoming_expenses)

    current_month_table = f"""        <h2 style="margin: 0 0 4px; color: #c9d1d9; font-size: 18px; line-height: 1.3;">{current_month} Expenses</h2>
        <div class="table-container">
            <table class="current-month-table">
                <thead>
                    <tr>
                        <th>Expense Type</th>
                        <th aria-sort="none"><button type="button" class="sort-button" data-column-index="1" data-sort-type="text">Category <span class="sort-indicator">&#8597;</span></button></th>
                        <th aria-sort="none"><button type="button" class="sort-button" data-column-index="2" data-sort-type="date">Date / Month <span class="sort-indicator">&#8597;</span></button></th>
                        <th aria-sort="none"><button type="button" class="sort-button" data-column-index="3" data-sort-type="amount">Amount <span class="sort-indicator">&#8597;</span></button></th>
                        <th aria-sort="none"><button type="button" class="sort-button" data-column-index="4" data-sort-type="text">Status <span class="sort-indicator">&#8597;</span></button></th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
"""

    for exp in current_month_expenses:
        category_class = exp['category'].lower().replace(' & ', '-').replace(' ', '-')
        row_class = 'paid-row' if exp['status'].strip().casefold() == 'paid' else ''
        current_month_table += f"""                    <tr class="{row_class}" data-expense-row="true">
                        <td>{exp['type']}</td>
                        <td><span class="category-badge badge-{category_class}">{exp['category']}</span></td>
                        <td>{exp['date'] or exp['month']}</td>
                        <td class="amount">₹{exp['amount']:,.0f}</td>
                        <td>{exp['status']}</td>
                        <td class="notes">{exp['notes']}</td>
                    </tr>
"""

    if not current_month_expenses:
        current_month_table += """                    <tr><td colspan="6">No expenses recorded for this month.</td></tr>
"""

    current_month_table += f"""                    <tr>
                        <td colspan="3"><strong>Paid Total</strong></td>
                        <td class="amount"><strong>₹{paid_total:,.0f}</strong></td>
                        <td></td>
                        <td></td>
                    </tr>
                    <tr>
                        <td colspan="3"><strong>Pending Total</strong></td>
                        <td class="amount"><strong>₹{pending_total:,.0f}</strong></td>
                        <td></td>
                        <td></td>
                    </tr>
                    <tr>
                        <td colspan="3"><strong>Current Month Total</strong></td>
                        <td class="amount"><strong>₹{current_month_total:,.0f}</strong></td>
                        <td></td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        </div>
"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Expense Management Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px 0;
            border-bottom: 1px solid #30363d;
        }}

        h1 {{
            font-size: 32px;
            font-weight: 600;
            color: #58a6ff;
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #8b949e;
            font-size: 14px;
        }}

        .category-badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 500;
            margin: 2px 2px 2px 0;
        }}

        .badge-education {{
            background: rgba(31, 111, 235, 0.2);
            border: 1px solid rgba(31, 111, 235, 0.4);
            color: #58a6ff;
        }}

        .badge-investment {{
            background: rgba(35, 134, 54, 0.2);
            border: 1px solid rgba(35, 134, 54, 0.4);
            color: #3fb950;
        }}

        .badge-health {{
            background: rgba(163, 113, 247, 0.2);
            border: 1px solid rgba(163, 113, 247, 0.4);
            color: #bc8cff;
        }}

        .badge-transportation {{
            background: rgba(210, 153, 34, 0.2);
            border: 1px solid rgba(210, 153, 34, 0.4);
            color: #e3b341;
        }}

        .badge-household {{
            background: rgba(248, 81, 73, 0.2);
            border: 1px solid rgba(248, 81, 73, 0.4);
            color: #ff7b72;
        }}

        .badge-other {{
            background: rgba(139, 148, 158, 0.2);
            border: 1px solid rgba(139, 148, 158, 0.4);
            color: #8b949e;
        }}

        .table-container {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 40px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        thead {{
            background: #21262d;
        }}

        th {{
            padding: 6px 8px;
            text-align: left;
            font-weight: 600;
            font-size: 11px;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid #30363d;
            border-right: 1px solid #30363d;
        }}

        td {{
            padding: 5px 8px;
            border-bottom: 1px solid #30363d;
            border-right: 1px solid #30363d;
            font-size: 12px;
        }}

        th:last-child, td:last-child {{
            border-right: none;
        }}

        tbody tr:hover {{
            background: #1c2128;
        }}

        .current-month-table tbody tr.paid-row td,
        .current-month-table tbody tr.paid-row td * {{
            color: #3fb950;
        }}

        tbody tr:last-child td {{
            border-bottom: none;
        }}

        .amount {{
            font-weight: 600;
            color: #58a6ff;
            font-variant-numeric: tabular-nums;
        }}

        .remaining-ok {{
            color: #3fb950;
        }}

        .remaining-over {{
            color: #e3b341;
        }}

        .notes {{
            color: #8b949e;
            font-size: 12px;
        }}

        .category-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 40px;
        }}

        .category-item {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .category-chart-container {{
            position: relative;
            height: {category_chart_height}px;
            padding: 16px;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            margin-bottom: 40px;
        }}

        .category-pie-container {{
            position: relative;
            height: 620px;
            padding: 12px;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            margin-bottom: 40px;
        }}

        .category-name {{
            font-size: 14px;
            color: #c9d1d9;
        }}

        .category-amount {{
            display: inline-flex;
            align-items: baseline;
            gap: 5px;
            white-space: nowrap;
            font-weight: 600;
            color: #58a6ff;
            font-size: 14px;
        }}

        .category-percent {{
            color: #8b949e;
            font-size: 11px;
            font-weight: 500;
        }}

        @media (max-width: 768px) {{
            table {{
                font-size: 11px;
            }}

            th, td {{
                padding: 6px 8px;
            }}

        }}

        @media print {{
            body {{
                background: white;
                color: black;
            }}

            .table-container {{
                border: 1px solid #ddd;
                background: white;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>💰 Expense Management Dashboard</h1>
            <p class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </header>

        {current_month_table}

        <h2 style="margin-bottom: 20px; color: #c9d1d9; font-size: 20px;">{current_month} Expenses by Category</h2>
        <div class="category-summary">
"""
    
    # Add category breakdown
    for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        category_class = category.lower().replace(' & ', '-').replace(' ', '-')
        category_percent = amount / current_month_total * 100 if current_month_total else 0
        html += f"""            <div class="category-item">
                <span class="category-name">
                    <span class="category-badge badge-{category_class}">{category}</span>
                </span>
                <span class="category-amount">₹{amount:,.0f}<span class="category-percent">{category_percent:.1f}%</span></span>
            </div>
"""
    
    html += """        </div>

        <h2 style="margin-bottom: 20px; color: #c9d1d9; font-size: 20px;">Monthly Budget vs Actual</h2>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Month</th>
                        <th>Budget</th>
                        <th>Actual (Paid)</th>
                        <th>Pending</th>
                        <th>Remaining After Paid</th>
                        <th>Projected Remaining</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for (year, month), totals in sorted(monthly_budget_totals.items()):
        remaining = MONTHLY_BUDGET - totals['paid']
        projected_remaining = remaining - totals['pending']
        remaining_class = 'remaining-ok' if remaining >= 0 else 'remaining-over'
        projected_class = 'remaining-ok' if projected_remaining >= 0 else 'remaining-over'
        html += f"""                    <tr>
                        <td>{datetime(year, month, 1).strftime('%b %Y')}</td>
                        <td class="amount">₹{MONTHLY_BUDGET:,.0f}</td>
                        <td class="amount">₹{totals['paid']:,.0f}</td>
                        <td class="amount">₹{totals['pending']:,.0f}</td>
                        <td class="amount {remaining_class}">₹{remaining:,.0f}</td>
                        <td class="amount {projected_class}">₹{projected_remaining:,.0f}</td>
                    </tr>
"""

    if not monthly_budget_totals:
        html += """                    <tr><td colspan="6">No monthly expenses recorded.</td></tr>
"""

    html += """                </tbody>
            </table>
        </div>
"""

    html += f"""        <h2 style="margin-bottom: 12px; margin-top: 40px; color: #c9d1d9; font-size: 20px;">Upcoming Expenses</h2>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Expense Type</th>
                        <th>Category</th>
                        <th>Date / Month</th>
                        <th>Amount</th>
                        <th>Status</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
"""

    for exp in upcoming_expenses:
        category_class = exp['category'].lower().replace(' & ', '-').replace(' ', '-')
        html += f"""                    <tr>
                        <td>{exp['type']}</td>
                        <td><span class="category-badge badge-{category_class}">{exp['category']}</span></td>
                        <td>{exp['date'] or exp['month']}</td>
                        <td class="amount">₹{exp['amount']:,.0f}</td>
                        <td>{exp['status']}</td>
                        <td class="notes">{exp['notes']}</td>
                    </tr>
"""

    if not upcoming_expenses:
        html += """                    <tr><td colspan="6">No upcoming expenses recorded.</td></tr>
"""

    html += f"""                    <tr>
                        <td colspan="3"><strong>Upcoming Total</strong></td>
                        <td class="amount"><strong>₹{upcoming_total:,.0f}</strong></td>
                        <td></td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <h2 style="margin-bottom: 12px; margin-top: 40px; color: #c9d1d9; font-size: 20px;">{current_month} Category Totals (Chart)</h2>
        <div class="category-chart-container">
            <canvas id="category-expenses-chart" role="img" aria-label="{current_month} expenses by category"></canvas>
        </div>

        <h2 style="margin-bottom: 12px; margin-top: 40px; color: #c9d1d9; font-size: 20px;">{current_month} Expense Summary (Pie Chart)</h2>
        <div class="category-pie-container">
            <canvas id="category-expenses-pie" role="img" aria-label="{current_month} expense category percentages and amounts"></canvas>
        </div>

        <div style="text-align: center; color: #6e7681; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #30363d;">
            <p>Expense Management Dashboard • Built with Python</p>
        </div>
    </div>
    {CURRENT_MONTH_SORT_SCRIPT}
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
    <script>
        const categoryLabels = {category_chart_labels};
        const categoryValues = {category_chart_values};
        const categoryColors = ['#58a6ff', '#3fb950', '#e3b341', '#ff7b72', '#bc8cff', '#79c0ff', '#ffa657', '#f778ba'];
        const currencyFormat = new Intl.NumberFormat('en-IN');
        const categoryCanvas = document.getElementById('category-expenses-chart');
        if (categoryLabels.length && window.Chart) {{
            new Chart(categoryCanvas, {{
                type: 'bar',
                data: {{
                    labels: categoryLabels,
                    datasets: [{{
                        data: categoryValues,
                        backgroundColor: categoryLabels.map((label, index) => categoryColors[index % categoryColors.length]),
                        borderRadius: 4,
                        barThickness: 24
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {{ padding: {{ right: 92 }} }},
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{
                            beginAtZero: true,
                            suggestedMax: Math.max(1, ...categoryValues) * 1.2,
                            grid: {{ color: 'rgba(139, 148, 158, 0.16)' }},
                            ticks: {{
                                color: '#8b949e',
                                callback: function(value) {{ return '₹' + currencyFormat.format(value); }}
                            }}
                        }},
                        y: {{
                            grid: {{ display: false }},
                            ticks: {{ color: '#c9d1d9' }}
                        }}
                    }}
                }},
                plugins: [{{
                    id: 'categoryValueLabels',
                    afterDatasetsDraw: function(chart) {{
                        const context = chart.ctx;
                        context.save();
                        context.fillStyle = '#c9d1d9';
                        context.font = '12px sans-serif';
                        chart.getDatasetMeta(0).data.forEach(function(bar, index) {{
                            context.fillText('₹' + currencyFormat.format(categoryValues[index]), bar.x + 8, bar.y + 4);
                        }});
                        context.restore();
                    }}
                }}]
            }});
        }}

        const categoryPieCanvas = document.getElementById('category-expenses-pie');
        if (categoryLabels.length && window.Chart) {{
            const categoryTotal = categoryValues.reduce((sum, value) => sum + value, 0);
            new Chart(categoryPieCanvas, {{
                type: 'pie',
                data: {{
                    labels: categoryLabels,
                    datasets: [{{
                        data: categoryValues,
                        backgroundColor: categoryLabels.map((label, index) => categoryColors[index % categoryColors.length]),
                        borderColor: '#0d1117',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {{ padding: 12 }},
                    plugins: {{
                        legend: {{
                            position: 'top',
                            align: 'start',
                            labels: {{
                                color: '#c9d1d9',
                                usePointStyle: true,
                                pointStyle: 'circle',
                                padding: 14,
                                generateLabels: function(chart) {{
                                    return chart.data.labels.map(function(label, index) {{
                                        const percent = categoryTotal ? categoryValues[index] / categoryTotal * 100 : 0;
                                        return {{
                                            text: label + ' : ' + percent.toFixed(1) + '%',
                                            fillStyle: categoryColors[index % categoryColors.length],
                                            fontColor: '#c9d1d9',
                                            strokeStyle: '#0d1117',
                                            lineWidth: 1,
                                            hidden: !chart.getDataVisibility(index),
                                            index: index
                                        }};
                                    }});
                                }}
                            }}
                        }}
                    }}
                }},
                plugins: [{{
                    id: 'pieValueLabels',
                    afterDatasetsDraw: function(chart) {{
                        const context = chart.ctx;
                        const arcs = chart.getDatasetMeta(0).data;
                        context.save();
                        context.fillStyle = '#0d1117';
                        context.textAlign = 'center';
                        context.textBaseline = 'middle';
                        context.font = 'bold 12px sans-serif';
                        arcs.forEach(function(arc, index) {{
                            const percent = categoryTotal ? categoryValues[index] / categoryTotal * 100 : 0;
                            if (percent < 6.5) return;
                            const angle = (arc.startAngle + arc.endAngle) / 2;
                            const radius = arc.outerRadius * 0.58;
                            const x = arc.x + Math.cos(angle) * radius;
                            const y = arc.y + Math.sin(angle) * radius;
                            const maxTextWidth = Math.max(40, 2 * radius * Math.sin((arc.endAngle - arc.startAngle) / 2) * 0.82);
                            const words = categoryLabels[index].split(' ').filter(Boolean);
                            let fontSize = 10;
                            context.font = 'bold ' + fontSize + 'px sans-serif';
                            while (fontSize > 8 && words.some(word => context.measureText(word).width > maxTextWidth)) {{
                                fontSize -= 1;
                                context.font = 'bold ' + fontSize + 'px sans-serif';
                            }}
                            const labelLines = [];
                            let line = '';
                            words.forEach(function(word) {{
                                const candidate = line ? line + ' ' + word : word;
                                if (line && context.measureText(candidate).width > maxTextWidth) {{
                                    labelLines.push(line);
                                    line = word;
                                }} else {{
                                    line = candidate;
                                }}
                            }});
                            if (line) labelLines.push(line);
                            const valueLines = labelLines.concat([
                                '₹' + currencyFormat.format(categoryValues[index]),
                                percent.toFixed(1) + '%'
                            ]);
                            const lineHeight = fontSize + 3;
                            const firstLineY = y - ((valueLines.length - 1) * lineHeight) / 2;
                            context.font = 'bold ' + fontSize + 'px sans-serif';
                            valueLines.forEach(function(valueLine, lineIndex) {{
                                context.fillText(valueLine, x, firstLineY + lineIndex * lineHeight);
                            }});
                        }});
                        context.restore();
                    }}
                }}]
            }});
        }}
    </script>
</body>
</html>"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    csv_file = 'expenses.csv'
    output_file = 'expenses_dashboard.html'
    
    print(f"Reading expenses from {csv_file}...")
    expenses = read_expenses(csv_file)
    
    print(f"Found {len(expenses)} expense entries")
    
    print(f"Generating HTML report: {output_file}...")
    generate_html(expenses, output_file)
    
    print(f"✓ Dashboard created successfully: {output_file}")
    
    # Display summary
    total, category_totals = calculate_summary(expenses)
    print(f"\nTotal Expenses: ₹{total:,.0f}")
    print("\nCategory Breakdown:")
    for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: ₹{amount:,.0f}")

if __name__ == '__main__':
    main()
