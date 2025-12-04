import pandas as pd
import numpy as np
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Load prerequisite files
dim_flight = pd.read_csv('dim_flight.csv')
dim_aircraft = pd.read_csv('dim_aircraft.csv')
dim_equipment = pd.read_csv('dim_equipment.csv')
dim_station = pd.read_csv('dim_station.csv')
dim_time_slot = pd.read_csv('dim_time_slot.csv')

# Create aircraft ULD lookup
aircraft_uld = dim_aircraft.set_index('aircraft_id')['uld_positions'].to_dict()

# Station preferences
widebody_stations = [7, 8, 10]  # 632, 641, 647
narrowbody_stations = [1, 3, 4]  # 661, 668, 699
storage_stations = [1, 3, 4, 5, 6, 7, 8, 9, 10]  # Exclude station 2

def assign_station(aircraft_category):
    """Assign station based on aircraft category"""
    if aircraft_category == 'Widebody':
        preferred = widebody_stations
    else:
        preferred = narrowbody_stations
    
    if random.random() < 0.70:
        return random.choice(preferred)
    else:
        return random.choice(storage_stations)

def calculate_allocation(qty_required):
    """Calculate allocation with shortage distribution"""
    rand = random.random()
    if rand < 0.85:
        return qty_required
    elif rand < 0.95:
        return max(0, qty_required - random.randint(1, 2))
    else:
        return max(0, qty_required - random.randint(2, 4))

def get_risk_level(shortage_qty):
    """Determine risk level from shortage"""
    if shortage_qty == 0:
        return "OK"
    elif shortage_qty == -1:
        return "LOW"
    elif shortage_qty >= -3:
        return "MEDIUM"
    else:
        return "HIGH"

def calculate_slot(arrival_slot_id, offset_min, offset_max=None):
    """Calculate slot with wrapping"""
    if offset_max is None:
        slot = arrival_slot_id + offset_min
    else:
        slot = arrival_slot_id - random.randint(offset_min, offset_max)
    
    # Wrap around
    if slot < 1:
        slot += 288
    elif slot > 288:
        slot -= 288
    
    return slot

# Generate demand records
demands = []
demand_id = 1

for _, flight in dim_flight.iterrows():
    flight_id = flight['flight_id']
    date_key = flight['date_key']
    arrival_slot_id = flight['arrival_slot_id']
    aircraft_category = flight['aircraft_category']
    aircraft_id = flight['aircraft_id']
    estimated_bags = flight['estimated_bags']
    cargo_kg = flight['cargo_kg']
    has_cargo_data = flight['has_cargo_data']
    
    # Get ULD positions
    uld_positions = aircraft_uld[aircraft_id]
    
    # Assign station
    station_id = assign_station(aircraft_category)
    
    # Calculate time slots
    pickup_slot_id = calculate_slot(arrival_slot_id, 3, 6)
    return_slot_id = calculate_slot(arrival_slot_id, 9)
    
    # Demand calc method
    demand_calc_method = "Cargo-based" if has_cargo_data == 'TRUE' else "Estimated"
    
    # Generate equipment demands
    if aircraft_category == 'Widebody':
        # 14P Pallet Dolly
        cargo_factor = int(np.ceil(cargo_kg / 3000)) if has_cargo_data == 'TRUE' else 2
        qty_14p = min(12, max(4, int(np.ceil(uld_positions * 0.6)) + cargo_factor))
        qty_alloc_14p = calculate_allocation(qty_14p)
        shortage_14p = qty_alloc_14p - qty_14p
        
        demands.append({
            'demand_id': demand_id,
            'flight_id': flight_id,
            'date_key': date_key,
            'arrival_slot_id': arrival_slot_id,
            'station_id': station_id,
            'equipment_id': 2,
            'qty_required': qty_14p,
            'qty_allocated': qty_alloc_14p,
            'shortage_qty': shortage_14p,
            'pickup_slot_id': pickup_slot_id,
            'return_slot_id': return_slot_id,
            'allocation_distance_km': round(random.uniform(0.3, 2.5), 1),
            'demand_calc_method': demand_calc_method,
            'risk_level': get_risk_level(shortage_14p),
            'sla_compliant': 'TRUE' if shortage_14p >= -1 else 'FALSE',
            'is_active': 'TRUE'
        })
        demand_id += 1
        
        # 26-O Open Baggage Trolley
        qty_26o = min(22, max(8, int(np.ceil(estimated_bags / 30))))
        qty_alloc_26o = calculate_allocation(qty_26o)
        shortage_26o = qty_alloc_26o - qty_26o
        
        demands.append({
            'demand_id': demand_id,
            'flight_id': flight_id,
            'date_key': date_key,
            'arrival_slot_id': arrival_slot_id,
            'station_id': station_id,
            'equipment_id': 4,
            'qty_required': qty_26o,
            'qty_allocated': qty_alloc_26o,
            'shortage_qty': shortage_26o,
            'pickup_slot_id': pickup_slot_id,
            'return_slot_id': return_slot_id,
            'allocation_distance_km': round(random.uniform(0.3, 2.5), 1),
            'demand_calc_method': demand_calc_method,
            'risk_level': get_risk_level(shortage_26o),
            'sla_compliant': 'TRUE' if shortage_26o >= -1 else 'FALSE',
            'is_active': 'TRUE'
        })
        demand_id += 1
        
        # 26-C Closed Baggage Trolley
        qty_26c = min(11, max(4, int(np.ceil(estimated_bags / 60))))
        qty_alloc_26c = calculate_allocation(qty_26c)
        shortage_26c = qty_alloc_26c - qty_26c
        
        demands.append({
            'demand_id': demand_id,
            'flight_id': flight_id,
            'date_key': date_key,
            'arrival_slot_id': arrival_slot_id,
            'station_id': station_id,
            'equipment_id': 6,
            'qty_required': qty_26c,
            'qty_allocated': qty_alloc_26c,
            'shortage_qty': shortage_26c,
            'pickup_slot_id': pickup_slot_id,
            'return_slot_id': return_slot_id,
            'allocation_distance_km': round(random.uniform(0.3, 2.5), 1),
            'demand_calc_method': demand_calc_method,
            'risk_level': get_risk_level(shortage_26c),
            'sla_compliant': 'TRUE' if shortage_26c >= -1 else 'FALSE',
            'is_active': 'TRUE'
        })
        demand_id += 1
        
    else:  # Narrowbody
        # 13C Container Dolly
        qty_13c = min(8, max(3, int(np.ceil(uld_positions * 0.8))))
        qty_alloc_13c = calculate_allocation(qty_13c)
        shortage_13c = qty_alloc_13c - qty_13c
        
        demands.append({
            'demand_id': demand_id,
            'flight_id': flight_id,
            'date_key': date_key,
            'arrival_slot_id': arrival_slot_id,
            'station_id': station_id,
            'equipment_id': 1,
            'qty_required': qty_13c,
            'qty_allocated': qty_alloc_13c,
            'shortage_qty': shortage_13c,
            'pickup_slot_id': pickup_slot_id,
            'return_slot_id': return_slot_id,
            'allocation_distance_km': round(random.uniform(0.3, 2.5), 1),
            'demand_calc_method': demand_calc_method,
            'risk_level': get_risk_level(shortage_13c),
            'sla_compliant': 'TRUE' if shortage_13c >= -1 else 'FALSE',
            'is_active': 'TRUE'
        })
        demand_id += 1
        
        # 26-O Open Baggage Trolley
        qty_26o = min(8, max(4, int(np.ceil(estimated_bags / 35))))
        qty_alloc_26o = calculate_allocation(qty_26o)
        shortage_26o = qty_alloc_26o - qty_26o
        
        demands.append({
            'demand_id': demand_id,
            'flight_id': flight_id,
            'date_key': date_key,
            'arrival_slot_id': arrival_slot_id,
            'station_id': station_id,
            'equipment_id': 4,
            'qty_required': qty_26o,
            'qty_allocated': qty_alloc_26o,
            'shortage_qty': shortage_26o,
            'pickup_slot_id': pickup_slot_id,
            'return_slot_id': return_slot_id,
            'allocation_distance_km': round(random.uniform(0.3, 2.5), 1),
            'demand_calc_method': demand_calc_method,
            'risk_level': get_risk_level(shortage_26o),
            'sla_compliant': 'TRUE' if shortage_26o >= -1 else 'FALSE',
            'is_active': 'TRUE'
        })
        demand_id += 1
        
        # 26-C Closed Baggage Trolley
        qty_26c = min(4, max(2, int(np.ceil(estimated_bags / 70))))
        qty_alloc_26c = calculate_allocation(qty_26c)
        shortage_26c = qty_alloc_26c - qty_26c
        
        demands.append({
            'demand_id': demand_id,
            'flight_id': flight_id,
            'date_key': date_key,
            'arrival_slot_id': arrival_slot_id,
            'station_id': station_id,
            'equipment_id': 6,
            'qty_required': qty_26c,
            'qty_allocated': qty_alloc_26c,
            'shortage_qty': shortage_26c,
            'pickup_slot_id': pickup_slot_id,
            'return_slot_id': return_slot_id,
            'allocation_distance_km': round(random.uniform(0.3, 2.5), 1),
            'demand_calc_method': demand_calc_method,
            'risk_level': get_risk_level(shortage_26c),
            'sla_compliant': 'TRUE' if shortage_26c >= -1 else 'FALSE',
            'is_active': 'TRUE'
        })
        demand_id += 1

# Create DataFrame
fact_flight_demand = pd.DataFrame(demands)

# Sort by date_key, arrival_slot_id, flight_id
fact_flight_demand = fact_flight_demand.sort_values(
    ['date_key', 'arrival_slot_id', 'flight_id']
).reset_index(drop=True)
fact_flight_demand['demand_id'] = range(1, len(fact_flight_demand) + 1)

# Save to CSV
fact_flight_demand.to_csv('fact_flight_demand.csv', index=False, float_format='%.1f')

# Validation
print("=" * 80)
print("VALIDATION REPORT")
print("=" * 80)

print(f"\nTotal row count: {len(fact_flight_demand):,}")
print(f"Ratio to flights: {len(fact_flight_demand) / len(dim_flight):.2f}x")
print(f"Date range: {fact_flight_demand['date_key'].min()} to {fact_flight_demand['date_key'].max()}")

# Equipment distribution
print("\nEquipment distribution:")
equip_names = {1: '13C Container', 2: '14P Pallet', 4: '26-O Open Trolley', 6: '26-C Closed Trolley'}
for equip_id in sorted(fact_flight_demand['equipment_id'].unique()):
    count = (fact_flight_demand['equipment_id'] == equip_id).sum()
    pct = count / len(fact_flight_demand) * 100
    print(f"  {equip_id} ({equip_names[equip_id]}): {count:,} ({pct:.1f}%)")

# Risk level distribution
print("\nRisk level distribution:")
for level in ['OK', 'LOW', 'MEDIUM', 'HIGH']:
    count = (fact_flight_demand['risk_level'] == level).sum()
    pct = count / len(fact_flight_demand) * 100
    print(f"  {level}: {count:,} ({pct:.1f}%)")

# SLA compliance
sla_rate = (fact_flight_demand['sla_compliant'] == 'TRUE').sum() / len(fact_flight_demand) * 100
print(f"\nSLA compliance rate: {sla_rate:.1f}%")

# Average qty_required by equipment
print("\nAverage qty_required by equipment:")
for equip_id in sorted(fact_flight_demand['equipment_id'].unique()):
    avg = fact_flight_demand[fact_flight_demand['equipment_id'] == equip_id]['qty_required'].mean()
    print(f"  {equip_id} ({equip_names[equip_id]}): {avg:.1f}")

# Sample rows
print("\n--- First 5 rows ---")
print(fact_flight_demand.head(5).to_string(index=False))

print("\n--- Last 5 rows ---")
print(fact_flight_demand.tail(5).to_string(index=False))

print("\n" + "=" * 80)
print("CSV file 'fact_flight_demand.csv' created successfully!")
print("=" * 80)