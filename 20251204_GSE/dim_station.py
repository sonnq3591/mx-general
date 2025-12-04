import pandas as pd

# Define station data from document
data = {
    'station_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'stand_number': ['661', '678', '668', '699', '621', '625', '632', '641', '643', '647'],
    'stand_name': [
        'Stand 661',
        'Stand 678',
        'Stand 668',
        'Stand 699',
        'Stand 621',
        'Stand 625',
        'Stand 632',
        'Stand 641',
        'Stand 643',
        'Stand 647'
    ],
    'description': [
        'Area fully occupied with empty container racks',
        'Area marked for bus staging',
        'Baggage area for small dollies staging',
        'OSS baggage, OAL empty containers, lashing belts, blankets',
        'Space available for 16 pallet dollies',
        'Space shared with cargo',
        'Space available for 39 pallet dollies',
        'Space available for 43 pallet dollies',
        'Space available for 16 pallet dollies',
        'Space available for 49 pallet dollies'
    ],
    'capacity_13c': [50, 0, 238, 80, 0, 50, 0, 0, 0, 0],
    'capacity_14p': [0, 0, 0, 0, 16, 10, 39, 43, 16, 49],
    'capacity_20ft': [0, 0, 0, 0, 0, 5, 5, 5, 0, 10],
    'capacity_26o': [0, 0, 0, 100, 20, 30, 40, 45, 25, 50],
    'capacity_40ft': [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    'capacity_26c': [0, 0, 0, 50, 10, 15, 20, 25, 12, 30],
    'is_storage_location': ['TRUE', 'FALSE', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE'],
    'is_active': ['TRUE'] * 10
}

# Create DataFrame
dim_station = pd.DataFrame(data)

# Calculate total capacity
dim_station['total_capacity'] = (
    dim_station['capacity_13c'] +
    dim_station['capacity_14p'] +
    dim_station['capacity_20ft'] +
    dim_station['capacity_26o'] +
    dim_station['capacity_40ft'] +
    dim_station['capacity_26c']
)

# Save to CSV
dim_station.to_csv('dim_station.csv', index=False)

# Validation
print("=" * 80)
print("VALIDATION REPORT")
print("=" * 80)
print(f"\nTotal row count: {len(dim_station)} (expected: 10)")

print("\n--- All 10 rows ---")
print(dim_station.to_string(index=False))

print(f"\nSum of capacity_13c: {dim_station['capacity_13c'].sum()} (expected: 418)")
print(f"Sum of capacity_14p: {dim_station['capacity_14p'].sum()} (expected: 173)")
print(f"Sum of capacity_26o: {dim_station['capacity_26o'].sum()} (expected: 310)")
print(f"Count of is_storage_location=TRUE: {(dim_station['is_storage_location'] == 'TRUE').sum()} (expected: 9)")
print(f"station_id sequential 1-10: {list(dim_station['station_id'])} ✓")

print("\n" + "=" * 80)
print("CSV file 'dim_station.csv' created successfully!")
print("=" * 80)