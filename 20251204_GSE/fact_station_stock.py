import pandas as pd
import numpy as np

# Load prerequisite data
fact_flight_demand = pd.read_csv('fact_flight_demand.csv')
dim_station = pd.read_csv('dim_station.csv')

# Aggregate demand by station, date, period, equipment
demand_agg = fact_flight_demand.groupby(
    ['station_id', 'date_key', 'period_id', 'equipment_id']
)['qty_required'].sum().reset_index()
demand_agg.rename(columns={'qty_required': 'demand_qty'}, inplace=True)

# Create capacity mapping from dim_station
capacity_map = {}
for _, row in dim_station.iterrows():
    station_id = row['station_id']
    capacity_map[station_id] = {
        1: row['capacity_pallet_dolly'],
        2: row['capacity_container_dolly'],
        3: row['capacity_baggage_trolley']
    }

# Generate all combinations for baseline scenario
stations = list(range(1, 11))
dates = list(range(20250101, 20251232))  # All date_keys from dim_date
dates = [d for d in dates if d <= 20251231]  # Filter valid dates
periods = [1, 2, 3, 4]
equipment_types = [1, 2, 3]  # Exclude equipment_id=4 (Bulk Cart)
scenario_id = 1

# Create all combinations
stock_records = []
stock_id = 1

for date_key in dates:
    for period_id in periods:
        for station_id in stations:
            for equipment_id in equipment_types:
                # Get capacity
                capacity = capacity_map[station_id][equipment_id]
                
                # Calculate reserved and available
                reserved_outbound = int(np.floor(capacity * 0.5))
                available_inbound = capacity - reserved_outbound
                
                # Get demand (default to 0 if no demand)
                demand_row = demand_agg[
                    (demand_agg['station_id'] == station_id) &
                    (demand_agg['date_key'] == date_key) &
                    (demand_agg['period_id'] == period_id) &
                    (demand_agg['equipment_id'] == equipment_id)
                ]
                demand_qty = int(demand_row['demand_qty'].iloc[0]) if len(demand_row) > 0 else 0
                
                # Calculate allocation
                allocated_qty = min(demand_qty, available_inbound)
                
                # Calculate shortage/surplus
                gap = available_inbound - demand_qty
                shortage_qty = min(0, gap)
                surplus_qty = max(0, gap)
                
                # Calculate utilization
                if available_inbound > 0:
                    utilization_pct = min(150.0, (demand_qty / available_inbound) * 100)
                else:
                    utilization_pct = 0.0
                
                # Bottleneck flag
                bottleneck_flag = 'TRUE' if utilization_pct > 100.0 else 'FALSE'
                
                stock_records.append({
                    'stock_id': stock_id,
                    'station_id': station_id,
                    'date_key': date_key,
                    'period_id': period_id,
                    'equipment_id': equipment_id,
                    'scenario_id': scenario_id,
                    'capacity': capacity,
                    'reserved_outbound': reserved_outbound,
                    'available_inbound': available_inbound,
                    'demand_qty': demand_qty,
                    'allocated_qty': allocated_qty,
                    'shortage_qty': shortage_qty,
                    'surplus_qty': surplus_qty,
                    'utilization_pct': round(utilization_pct, 1),
                    'bottleneck_flag': bottleneck_flag,
                    'is_active': 'TRUE'
                })
                
                stock_id += 1

# Create DataFrame
fact_station_stock = pd.DataFrame(stock_records)

# Sort by date_key, period_id, station_id, equipment_id
fact_station_stock = fact_station_stock.sort_values(
    ['date_key', 'period_id', 'station_id', 'equipment_id']
).reset_index(drop=True)

# Update stock_id to be sequential after sorting
fact_station_stock['stock_id'] = range(1, len(fact_station_stock) + 1)

# Save to CSV
fact_station_stock.to_csv('fact_station_stock.csv', index=False, float_format='%.1f')

# Validation
print("=" * 80)
print("VALIDATION REPORT")
print("=" * 80)

print(f"\nTotal row count: {len(fact_station_stock):,} (expected: 43,800)")
print(f"Date range: {fact_station_stock['date_key'].min()} to {fact_station_stock['date_key'].max()}")

# Bottleneck rate
bottleneck_rate = (fact_station_stock['bottleneck_flag'] == 'TRUE').sum() / len(fact_station_stock) * 100
print(f"\nBottleneck rate: {bottleneck_rate:.1f}%")

# Average utilization by equipment
print("\nAverage utilization_pct by equipment:")
equip_names = {1: 'Pallet Dolly', 2: 'Container Dolly', 3: 'Baggage Trolley'}
for equip_id in sorted(fact_station_stock['equipment_id'].unique()):
    avg_util = fact_station_stock[fact_station_stock['equipment_id'] == equip_id]['utilization_pct'].mean()
    print(f"  equipment_id={equip_id} ({equip_names[equip_id]}): {avg_util:.1f}%")

# Stations with most bottlenecks
print("\nStations with most bottlenecks (top 3):")
bottleneck_by_station = fact_station_stock[fact_station_stock['bottleneck_flag'] == 'TRUE'].groupby('station_id').size().sort_values(ascending=False).head(3)
for station_id, count in bottleneck_by_station.items():
    pct = count / len(fact_station_stock[fact_station_stock['station_id'] == station_id]) * 100
    print(f"  station_id={station_id}: {count:,} bottlenecks ({pct:.1f}%)")

# Sample rows
print("\n--- First 5 rows ---")
print(fact_station_stock.head(5).to_string(index=False))

print("\n--- Last 5 rows ---")
print(fact_station_stock.tail(5).to_string(index=False))

print("\n" + "=" * 80)
print("CSV file 'fact_station_stock.csv' created successfully!")
print("=" * 80)