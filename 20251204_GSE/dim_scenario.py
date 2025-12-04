import pandas as pd

# Define scenario data
data = {
    'scenario_id': [1, 2, 3, 4, 5],
    'scenario_name': [
        'Baseline',
        'Add 10 Dollies Stn 621',
        'Add 20 Trolleys Stn 608',
        'Redistribute from 647',
        'Peak Demand +20%'
    ],
    'scenario_type': ['Baseline', 'Capacity', 'Capacity', 'Redistribution', 'Demand'],
    'description': [
        'Current operations with existing equipment allocation',
        'Add 10 pallet dollies to high-traffic Station 621',
        'Add 20 baggage trolleys to baggage handling area',
        'Move surplus equipment from Station 647 to 621 & 632',
        'Simulate 20% increase in peak period demand'
    ],
    'parameter_changed': [
        'None',
        'capacity_pallet_dolly',
        'capacity_baggage_trolley',
        'redistribution_rule',
        'demand_multiplier'
    ],
    'parameter_value': [
        'None',
        'Station 621: +10 units',
        'Station 608: +20 units',
        '647 to 621: 5, 647 to 632: 5',
        'Peak periods: 1.2x'
    ],
    'is_baseline': ['TRUE', 'FALSE', 'FALSE', 'FALSE', 'FALSE'],
    'is_active': ['TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE']
}

# Create DataFrame
dim_scenario = pd.DataFrame(data)

# Save to CSV
dim_scenario.to_csv('dim_scenario.csv', index=False)

# Validation
print("=" * 80)
print("VALIDATION REPORT")
print("=" * 80)
print(f"\nTotal row count: {len(dim_scenario)}")

print("\n--- All rows ---")
print(dim_scenario.to_string(index=False))

print(f"\nRows with is_baseline = TRUE: {(dim_scenario['is_baseline'] == 'TRUE').sum()} (expected: 1) ✓")
print(f"All is_active = TRUE: {(dim_scenario['is_active'] == 'TRUE').all()} ✓")

print("\n" + "=" * 80)
print("CSV file 'dim_scenario.csv' created successfully!")
print("=" * 80)