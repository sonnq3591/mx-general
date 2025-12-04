import pandas as pd

# Define aircraft data from ABC Ground operations
data = {
    'aircraft_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'aircraft_series': ['A380', 'B777', 'B747', 'A350', 'B787', 'A330', 'A321', 'A320', 'B737', 'E190'],
    'aircraft_category': ['Widebody', 'Widebody', 'Widebody', 'Widebody', 'Widebody', 'Widebody', 'Narrowbody', 'Narrowbody', 'Narrowbody', 'Narrowbody'],
    'fleet_count': [10, 3, 4, 3, 3, 1, 11, 14, 3, 5],
    'fleet_pct': [17.5, 5.3, 7.0, 5.3, 5.3, 1.8, 19.3, 24.6, 5.3, 8.8],
    'typical_pax': [496, 350, 400, 300, 280, 260, 200, 180, 162, 100],
    'typical_cargo_kg': [15000, 12000, 14000, 10000, 9000, 8000, 3500, 2500, 2000, 1000],
    'typical_bags': [645, 455, 520, 390, 364, 338, 260, 234, 211, 130],
    'uld_positions': [38, 32, 36, 28, 24, 22, 10, 7, 6, 3],
    'is_active': ['TRUE'] * 10
}

# Create DataFrame
dim_aircraft = pd.DataFrame(data)

# Save to CSV
dim_aircraft.to_csv('dim_aircraft.csv', index=False, float_format='%.1f')

# Validation
print("=" * 80)
print("VALIDATION REPORT")
print("=" * 80)
print(f"\nTotal row count: {len(dim_aircraft)} (expected: 10)")

print("\n--- All 10 rows ---")
print(dim_aircraft.to_string(index=False))

print(f"\nSum of fleet_count: {dim_aircraft['fleet_count'].sum()} (expected: 57)")
print(f"Sum of fleet_pct: {dim_aircraft['fleet_pct'].sum():.1f}% (expected: ~100%)")
print(f"Count of Widebody: {(dim_aircraft['aircraft_category'] == 'Widebody').sum()} (expected: 6)")
print(f"Count of Narrowbody: {(dim_aircraft['aircraft_category'] == 'Narrowbody').sum()} (expected: 4)")

max_fleet = dim_aircraft[dim_aircraft['fleet_count'] == dim_aircraft['fleet_count'].max()]
print(f"Aircraft with highest fleet_count: {max_fleet['aircraft_series'].iloc[0]} ({max_fleet['fleet_count'].iloc[0]} units) ✓")
print(f"All is_active = TRUE: {(dim_aircraft['is_active'] == 'TRUE').all()} ✓")

print("\n" + "=" * 80)
print("CSV file 'dim_aircraft.csv' created successfully!")
print("=" * 80)