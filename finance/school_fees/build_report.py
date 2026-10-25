#!/usr/bin/env python3
"""
School Expense Report Generator
Reads school_expenses.csv and generates a beautiful HTML dashboard
"""

import pandas as pd
from jinja2 import Template
from datetime import datetime
import json
import os

def load_data(csv_file='school_expenses.csv'):
    """Load and parse the expense data"""
    df = pd.read_csv(csv_file)
    df['paid_date'] = pd.to_datetime(df['paid_date'], format='%d-%m-%Y')
    return df

def calculate_summaries(df):
    """Calculate all necessary summaries"""
    summaries = {}
    
    # Total spent
    summaries['total_spent'] = df['amount'].sum()
    
    # Paid vs Outstanding
    paid_df = df[df['payment_status'] == 'Paid']
    upcoming_df = df[df['payment_status'] == 'Upcoming']
    summaries['paid_amount'] = paid_df['amount'].sum()
    summaries['outstanding_amount'] = upcoming_df['amount'].sum()
    
    # Expense by type
    summaries['expense_by_type'] = df.groupby('expense_type')['amount'].sum().to_dict()
    
    # Total per child
    summaries['child_total'] = df.groupby('child_name')['amount'].sum().to_dict()
    
    # Monthly trend
    df['month'] = df['paid_date'].dt.strftime('%b %Y')
    summaries['monthly_trend'] = df.groupby('month')['amount'].sum().to_dict()
    
    # Per-child detailed summary
    child_summary = {}
    for child in df['child_name'].unique():
        child_df = df[df['child_name'] == child]
        child_paid = child_df[child_df['payment_status'] == 'Paid']
        child_outstanding = child_df[child_df['payment_status'] == 'Upcoming']
        
        child_summary[child] = {
            'grade': child_df['class_grade'].iloc[0],
            'total': child_df['amount'].sum(),
            'paid': child_paid['amount'].sum(),
            'outstanding': child_outstanding['amount'].sum(),
            'breakdown': child_df.groupby('expense_type')['amount'].sum().to_dict(),
            'last_payment': child_df.sort_values('paid_date', ascending=False)['paid_date'].iloc[0].strftime('%d-%b-%Y')
        }
    summaries['child_summary'] = child_summary
    
    # List of all children
    summaries['children'] = sorted(df['child_name'].unique())
    
    # Academic year (extract from data)
    summaries['academic_year'] = df['academic_year'].iloc[0] if 'academic_year' in df.columns else '2025-26'
    
    # Forecast future fees (10% increase per year till graduation)
    forecast = {}
    grade_mapping = {
        'Grade I': 1, 'Grade II': 2, 'Class 3': 3, 'Class 4': 4, 'Class 5': 5,
        'Class 6': 6, 'Class 7': 7, 'Class 8': 8, 'Class 9': 9, 'Class 10': 10,
        'Class 11': 11, 'Class 12': 12
    }
    
    for child in df['child_name'].unique():
        child_df = df[df['child_name'] == child]
        current_grade = child_df['class_grade'].iloc[0]
        current_grade_num = grade_mapping.get(current_grade, 1)
        
        # Calculate annual fees (fees + transport for current year)
        annual_fees = child_df[child_df['expense_type'].isin(['Fees', 'Transport'])]['amount'].sum()
        
        # Forecast from next year till Class 12
        years_forecast = []
        for year_offset in range(1, 13 - current_grade_num + 1):
            future_grade_num = current_grade_num + year_offset
            if future_grade_num <= 12:
                future_year = f"20{25 + year_offset}-{26 + year_offset}"
                future_grade = f"Class {future_grade_num}" if future_grade_num > 2 else f"Grade {['I', 'II'][future_grade_num - 1]}"
                projected_fees = annual_fees * (1.10 ** year_offset)
                years_forecast.append({
                    'year': future_year,
                    'grade': future_grade,
                    'amount': projected_fees
                })
        
        forecast[child] = {
            'current_grade': current_grade,
            'current_annual': annual_fees,
            'years': years_forecast,
            'total_future': sum([y['amount'] for y in years_forecast])
        }
    
    summaries['forecast'] = forecast
    
    # Prepare yearly forecast totals for chart (both children combined per year)
    all_years = set()
    yearly_totals = {}
    
    # Collect all years and sum amounts per year across both children
    for child, data in forecast.items():
        for year_data in data['years']:
            year = year_data['year']
            amount = year_data['amount']
            all_years.add(year)
            if year not in yearly_totals:
                yearly_totals[year] = 0
            yearly_totals[year] += amount
    
    # Create yearly totals list (not cumulative)
    sorted_years = sorted(list(all_years))
    yearly_data = [yearly_totals[year] for year in sorted_years]
    
    summaries['forecast_chart_data'] = yearly_data
    summaries['forecast_years'] = sorted_years
    
    return summaries

def prepare_expense_list(df):
    """Prepare expense list for table display"""
    df_sorted = df.sort_values('paid_date', ascending=False)
    expenses = []
    
    for _, row in df_sorted.iterrows():
        expenses.append({
            'child_name': row['child_name'],
            'class_grade': row['class_grade'],
            'expense_type': row['expense_type'],
            'description': row['description'],
            'amount': row['amount'],
            'paid_date': row['paid_date'].strftime('%d-%b-%Y'),
            'payment_status': row.get('payment_status', 'Paid')
        })
    
    return expenses

def generate_report(output_file='school_report.html'):
    """Main function to generate the HTML report"""
    print("🎓 School Expense Report Generator")
    print("=" * 50)
    
    # Check if data file exists
    if not os.path.exists('school_expenses.csv'):
        print("❌ Error: school_expenses.csv not found!")
        print("   Please ensure the CSV file is in the same directory.")
        return
    
    # Load data
    print("📊 Loading expense data...")
    df = load_data()
    print(f"   ✓ Loaded {len(df)} expense records")
    
    # Calculate summaries
    print("🔢 Calculating summaries...")
    summaries = calculate_summaries(df)
    print(f"   ✓ Total expenditure: ₹{summaries['total_spent']:,.2f}")
    print(f"   ✓ Children tracked: {', '.join(summaries['children'])}")
    
    # Prepare expense list
    print("📝 Preparing expense list...")
    expenses = prepare_expense_list(df)
    
    # Load template
    print("🎨 Loading HTML template...")
    with open('template.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    template = Template(template_content)
    
    # Prepare data for template
    template_data = {
        'total_spent': summaries['total_spent'],
        'paid_amount': summaries['paid_amount'],
        'outstanding_amount': summaries['outstanding_amount'],
        'expense_by_type': summaries['expense_by_type'],
        'child_total': summaries['child_total'],
        'monthly_trend': summaries['monthly_trend'],
        'child_summary': summaries['child_summary'],
        'children': summaries['children'],
        'expenses': expenses,
        'academic_year': summaries['academic_year'],
        'forecast': summaries['forecast'],
        'forecast_years': summaries['forecast_years'],
        'generated_at': datetime.now().strftime('%d-%B-%Y %I:%M %p'),
        # JSON data for charts
        'expense_by_type_json': json.dumps(summaries['expense_by_type']),
        'child_total_json': json.dumps(summaries['child_total']),
        'monthly_trend_json': json.dumps(summaries['monthly_trend']),
        'forecast_chart_json': json.dumps(summaries['forecast_chart_data']),
        'forecast_years_json': json.dumps(summaries['forecast_years'])
    }
    
    # Render template
    print("🚀 Generating HTML report...")
    html_output = template.render(**template_data)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print(f"✅ Report generated successfully!")
    print(f"   📄 Output: {output_file}")
    print(f"   💡 Open {output_file} in your browser to view the report")
    print()
    
    # Print quick summary
    print("📊 Quick Summary:")
    print(f"   • Total Budget: ₹{summaries['total_spent']:,.2f}")
    print(f"   • Paid Till Now: ₹{summaries['paid_amount']:,.2f}")
    print(f"   • Outstanding: ₹{summaries['outstanding_amount']:,.2f}")
    print()
    print("   Per-Child Breakdown:")
    for child, amount in summaries['child_total'].items():
        print(f"   • {child}: ₹{amount:,.2f}")
    print()
    print("🎉 All done! Enjoy your expense dashboard!")

if __name__ == '__main__':
    generate_report()
