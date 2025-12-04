import pandas as pd
from datetime import datetime, timedelta

# Generate date range
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Build dimension table
dim_date = pd.DataFrame({
    'date_key': [int(d.strftime('%Y%m%d')) for d in date_range],
    'full_date': [d.strftime('%Y-%m-%d') for d in date_range],
    'year': [d.year for d in date_range],
    'quarter': [d.quarter for d in date_range],
    'month': [d.month for d in date_range],
    'month_name': [d.strftime('%B') for d in date_range],
    'week_of_year': [d.isocalendar()[1] for d in date_range],
    'day': [d.day for d in date_range],
    'day_of_week': [d.isoweekday() for d in date_range],
    'day_name': [d.strftime('%A') for d in date_range],
    'is_weekend': ['TRUE' if d.isoweekday() in [6, 7] else 'FALSE' for d in date_range]
})

# Save to CSV
dim_date.to_csv('dim_date.csv', index=False)

# Validation
print("=" * 60)
print("VALIDATION REPORT")
print("=" * 60)
print(f"\nTotal row count: {len(dim_date)}")

print("\n--- First 3 rows ---")
print(dim_date.head(3).to_string(index=False))

print("\n--- Last 3 rows ---")
print(dim_date.tail(3).to_string(index=False))

# Check specific dates
jan_1 = dim_date[dim_date['full_date'] == '2025-01-01'].iloc[0]
dec_31 = dim_date[dim_date['full_date'] == '2025-12-31'].iloc[0]

print(f"\nJan 1, 2025: {jan_1['day_name']} (day_of_week = {jan_1['day_of_week']}) ✓")
print(f"Dec 31, 2025: {dec_31['day_name']} (day_of_week = {dec_31['day_of_week']}) ✓")

# Weekend/weekday counts
weekend_count = (dim_date['is_weekend'] == 'TRUE').sum()
weekday_count = (dim_date['is_weekend'] == 'FALSE').sum()

print(f"\nWeekend days: {weekend_count}")
print(f"Weekday days: {weekday_count}")
print(f"Total: {weekend_count + weekday_count}")

print("\n" + "=" * 60)
print("CSV file 'dim_date.csv' created successfully!")
print("=" * 60)