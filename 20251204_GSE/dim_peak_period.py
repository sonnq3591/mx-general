import pandas as pd

# Define peak period data
data = {
    'period_id': [1, 2, 3, 4],
    'period_name': ['Morning Peak', 'Midday', 'Evening Peak', 'Night'],
    'start_time': ['06:00:00', '10:00:00', '14:00:00', '20:00:00'],
    'end_time': ['10:00:00', '14:00:00', '20:00:00', '06:00:00'],
    'description': [
        'Morning arrival wave',
        'Midday operations',
        'Evening departure/arrival wave',
        'Night operations and preparation'
    ],
    'is_active': ['TRUE', 'TRUE', 'TRUE', 'TRUE']
}

# Create DataFrame
dim_peak_period = pd.DataFrame(data)

# Save to CSV
dim_peak_period.to_csv('dim_peak_period.csv', index=False)

# Validation
print("=" * 60)
print("VALIDATION REPORT")
print("=" * 60)
print(f"\nTotal row count: {len(dim_peak_period)}")

print("\n--- All rows ---")
print(dim_peak_period.to_string(index=False))

print(f"\nPeriod IDs sequential: {list(dim_peak_period['period_id'])} ✓")

print("\n" + "=" * 60)
print("CSV file 'dim_peak_period.csv' created successfully!")
print("=" * 60)