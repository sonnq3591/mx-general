import pandas as pd

# Define equipment data from document
data = {
    'equipment_id': [1, 2, 3, 4, 5, 6],
    'asset_code': ['13C', '14P', '20FT', '26-O', '40FT', '26-C'],
    'asset_type': [
        'LD3 Container Dolly',
        '10 FT Pallet Dolly',
        '20 FT Pallet Dolly',
        'Open Baggage Trolley',
        '40FT Pallet Dolly',
        'Closed Baggage Trolley'
    ],
    'equipment_category': ['Dolly', 'Dolly', 'Dolly', 'Trolley', 'Dolly', 'Trolley'],
    'capacity_ton': [1.6, 7.0, 14.0, 2.0, 20.0, 3.5],
    'units_in_operation': [810, 945, 60, 542, 1, 252],
    'aircraft_category': ['Narrowbody', 'Widebody', 'Widebody', 'All', 'Widebody', 'All'],
    'description': [
        'For LD3 containers on narrowbody aircraft',
        'Standard pallet dolly for widebody aircraft',
        'Large pallet dolly for heavy cargo',
        'Open trolley for bulk baggage',
        'Extra-large pallet dolly for oversized cargo',
        'Enclosed trolley for weather protection'
    ],
    'is_active': ['TRUE'] * 6
}

# Create DataFrame
dim_equipment = pd.DataFrame(data)

# Save to CSV
dim_equipment.to_csv('dim_equipment.csv', index=False, float_format='%.1f')

# Validation
print("=" * 80)
print("VALIDATION REPORT")
print("=" * 80)
print(f"\nTotal row count: {len(dim_equipment)} (expected: 6)")

print("\n--- All 6 rows ---")
print(dim_equipment.to_string(index=False))

print(f"\nSum of units_in_operation: {dim_equipment['units_in_operation'].sum()} (expected: 2610)")
print(f"Count of Dolly category: {(dim_equipment['equipment_category'] == 'Dolly').sum()} (expected: 4)")
print(f"Count of Trolley category: {(dim_equipment['equipment_category'] == 'Trolley').sum()} (expected: 2)")
print(f"All is_active = TRUE: {(dim_equipment['is_active'] == 'TRUE').all()} ✓")

print("\n" + "=" * 80)
print("CSV file 'dim_equipment.csv' created successfully!")
print("=" * 80)