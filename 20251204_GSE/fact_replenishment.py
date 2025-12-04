import pandas as pd
import numpy as np
from datetime import datetime
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Load prerequisite data
fact_station_stock = pd.read_csv('fact_station_stock.csv')
dim_station = pd.read_csv('dim_station.csv')

# Create station coordinates lookup
station_coords = {}
for _, row in dim_station.iterrows():
    station_coords[row['station_id']] = (row['location_x'], row['location_y'])

def calculate_distance(from_id, to_id):
    """Calculate Euclidean distance between stations in km"""
    x1, y1 = station_coords[from_id]
    x2, y2 = station_coords[to_id]
    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2) / 30  # Scale to km
    return round(distance, 1)

def get_priority(shortage_qty):
    """Determine priority based on shortage severity"""
    if shortage_qty <= -4:
        return "HIGH"
    elif shortage_qty <= -2:
        return "MEDIUM"
    else:
        return "LOW"

def get_status(date_key):
    """Determine status based on date"""
    reference_date = 20250601
    if date_key < reference_date:
        rand = random.random()
        if rand < 0.60:
            return "Completed"
        elif rand < 0.90:
            return "Approved"
        else:
            return "Recommended"
    else:
        return "Recommended"

# Generate replenishment records
replenishments = []
replenishment_id = 1

# Group by date, period, equipment to find shortage/surplus matches
grouped = fact_station_stock.groupby(['date_key', 'period_id', 'equipment_id'])

for (date_key, period_id, equipment_id), group in grouped:
    # Find shortages and surpluses
    shortages = group[group['shortage_qty'] < 0].copy()
    surpluses = group[group['surplus_qty'] > 0].copy()
    
    if len(shortages) == 0 or len(surpluses) == 0:
        continue
    
    # Sort by severity
    shortages = shortages.sort_values('shortage_qty')
    surpluses = surpluses.sort_values('surplus_qty', ascending=False)
    
    # Match surplus to shortage
    surplus_dict = {row['station_id']: row['surplus_qty'] for _, row in surpluses.iterrows()}
    
    for _, shortage_row in shortages.iterrows():
        to_station_id = shortage_row['station_id']
        needed = abs(shortage_row['shortage_qty'])
        
        # Only generate replenishment for ~30% of shortages (to get target volume)
        if random.random() > 0.30:
            continue
        
        # Find best surplus station (closest with available surplus)
        best_from = None
        best_distance = float('inf')
        
        for from_station_id, available in surplus_dict.items():
            if available <= 0 or from_station_id == to_station_id:
                continue
            
            distance = calculate_distance(from_station_id, to_station_id)
            if distance < best_distance:
                best_distance = distance
                best_from = from_station_id
        
        if best_from is None:
            continue
        
        # Determine quantity to move
        qty_to_move = min(needed, surplus_dict[best_from])
        if qty_to_move == 0:
            continue
        
        # Update surplus
        surplus_dict[best_from] -= qty_to_move
        
        # Calculate distance and time
        distance_km = calculate_distance(best_from, to_station_id)
        estimated_time_min = max(2, min(15, int(np.ceil(distance_km * 4))))
        
        # Determine priority
        priority = get_priority(shortage_row['shortage_qty'])
        
        # Determine trigger reason
        rand = random.random()
        if rand < 0.70:
            trigger_reason = "Shortage"
        elif rand < 0.90:
            trigger_reason = "Balance"
        else:
            trigger_reason = "Preventive"
        
        # Determine status
        status = get_status(date_key)
        
        replenishments.append({
            'replenishment_id': replenishment_id,
            'from_station_id': best_from,
            'to_station_id': to_station_id,
            'date_key': date_key,
            'before_period_id': period_id,
            'equipment_id': equipment_id,
            'scenario_id': 1,
            'qty_to_move': qty_to_move,
            'distance_km': distance_km,
            'estimated_time_min': estimated_time_min,
            'priority': priority,
            'trigger_reason': trigger_reason,
            'status': status,
            'is_active': 'TRUE'
        })
        
        replenishment_id += 1

# Create DataFrame
fact_replenishment = pd.DataFrame(replenishments)

# Sort by date_key, before_period_id, priority
priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
fact_replenishment['priority_sort'] = fact_replenishment['priority'].map(priority_order)
fact_replenishment = fact_replenishment.sort_values(
    ['date_key', 'before_period_id', 'priority_sort']
).reset_index(drop=True)
fact_replenishment = fact_replenishment.drop('priority_sort', axis=1)

# Update replenishment_id to be sequential after sorting
fact_replenishment['replenishment_id'] = range(1, len(fact_replenishment) + 1)

# Save to CSV
fact_replenishment.to_csv('fact_replenishment.csv', index=False, float_format='%.1f')

# Validation
print("=" * 80)
print("VALIDATION REPORT")
print("=" * 80)

print(f"\nTotal row count: {len(fact_replenishment):,}")
print(f"Date range: {fact_replenishment['date_key'].min()} to {fact_replenishment['date_key'].max()}")
print(f"Average per day: {len(fact_replenishment) / 365:.1f}")

# Priority distribution
print("\nPriority distribution:")
priority_dist = fact_replenishment['priority'].value_counts()
for priority in ['HIGH', 'MEDIUM', 'LOW']:
    count = priority_dist.get(priority, 0)
    pct = count / len(fact_replenishment) * 100
    print(f"  {priority}: {count:,} ({pct:.1f}%)")

# Trigger reason distribution
print("\nTrigger reason distribution:")
trigger_dist = fact_replenishment['trigger_reason'].value_counts()
for reason in ['Shortage', 'Balance', 'Preventive']:
    count = trigger_dist.get(reason, 0)
    pct = count / len(fact_replenishment) * 100
    print(f"  {reason}: {count:,} ({pct:.1f}%)")

# Status distribution
print("\nStatus distribution:")
status_dist = fact_replenishment['status'].value_counts()
for status in ['Completed', 'Approved', 'Recommended']:
    count = status_dist.get(status, 0)
    pct = count / len(fact_replenishment) * 100
    print(f"  {status}: {count:,} ({pct:.1f}%)")

# Averages
print(f"\nAverage qty_to_move: {fact_replenishment['qty_to_move'].mean():.1f}")
print(f"Average distance_km: {fact_replenishment['distance_km'].mean():.1f}")

# Top station pairs
print("\nTop 3 most common from_station → to_station pairs:")
fact_replenishment['pair'] = fact_replenishment['from_station_id'].astype(str) + ' → ' + fact_replenishment['to_station_id'].astype(str)
top_pairs = fact_replenishment['pair'].value_counts().head(3)
for pair, count in top_pairs.items():
    print(f"  Station {pair}: {count:,} times")

# Sample rows
print("\n--- First 5 rows ---")
print(fact_replenishment.drop('pair', axis=1).head(5).to_string(index=False))

print("\n--- Last 5 rows ---")
print(fact_replenishment.drop('pair', axis=1).tail(5).to_string(index=False))

print("\n" + "=" * 80)
print("CSV file 'fact_replenishment.csv' created successfully!")
print("=" * 80)