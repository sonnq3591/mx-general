import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Load prerequisite files
dim_aircraft = pd.read_csv('dim_aircraft.csv')
dim_time_slot = pd.read_csv('dim_time_slot.csv')

# Create aircraft lookup
aircraft_lookup = dim_aircraft.set_index('aircraft_id').to_dict('index')

# Airlines with revenue-based weights
airlines = [
    ('EY', 'Etihad Airways', 62.36),
    ('G9', 'Air Arabia Abu Dhabi', 8.79),
    ('W6', 'Wizz Air Abu Dhabi', 7.99),
    ('6E', 'IndiGo', 5.53),
    ('IX', 'Air India Express', 2.98),
    ('QR', 'Qatar Airways', 1.99),
    ('PK', 'Pakistan International Airlines', 1.27),
    ('QP', 'Akasa Air', 1.27),
    ('SV', 'Saudi Arabian Airlines', 0.96),
    ('MS', 'EgyptAir', 0.75),
    ('XY', 'flynas', 0.71),
    ('GF', 'Gulf Air', 0.65),
    ('O3', 'SF Airlines', 0.62),
    ('RJ', 'Royal Jordanian', 0.59),
    ('TK', 'Turkish Airlines', 0.59),
    ('SU', 'Aeroflot', 0.56),
    ('FC', 'Florida Coastal Airlines', 0.50),
    ('BG', 'Biman Bangladesh Airlines', 0.44),
    ('AI', 'Air India', 0.37),
    ('UL', 'SriLankan Airlines', 0.37),
    ('ME', 'Middle East Airlines', 0.34),
    ('BS', 'British International Helicopters', 0.34)
]

# Origins
origins = ['LHR', 'CDG', 'FRA', 'SIN', 'HKG', 'BKK', 'JFK', 'DEL', 'MUM', 'CAI', 'JNB', 'NRT', 'ICN', 'DXB', 'KWI']

# Peak period time ranges for arrival distribution
time_periods = [
    (6, 10, 0.30),   # Morning Peak
    (10, 14, 0.20),  # Midday
    (14, 20, 0.35),  # Evening Peak
    (20, 6, 0.15)    # Night (wraps midnight)
]

def get_aircraft_for_airline(airline_code):
    """Select aircraft based on airline rules"""
    widebody_ids = [1, 2, 3, 4, 5, 6]  # A380, B777, B747, A350, B787, A330
    narrowbody_ids = [7, 8, 9, 10]     # A321, A320, B737, E190
    
    if airline_code == 'EY':
        if random.random() < 0.60:
            return random.choice(widebody_ids)
        else:
            return random.choice([7, 8])  # A321, A320
    elif airline_code in ['G9', 'W6', '6E', 'QP']:
        return random.choice([7, 8])  # A320, A321
    elif airline_code == 'QR':
        if random.random() < 0.80:
            return random.choice(widebody_ids)
        else:
            return random.choice(narrowbody_ids)
    else:
        if random.random() < 0.50:
            return random.choice(widebody_ids)
        else:
            return random.choice(narrowbody_ids)

def generate_arrival_time():
    """Generate arrival time based on peak period distribution"""
    period_start, period_end, _ = random.choices(
        [(p[0], p[1], p[2]) for p in time_periods],
        weights=[p[2] for p in time_periods],
        k=1
    )[0]
    
    if period_end < period_start:  # Night period wraps
        if random.random() < 0.5:
            hour = random.randint(period_start, 23)
        else:
            hour = random.randint(0, period_end - 1)
    else:
        hour = random.randint(period_start, period_end - 1)
    
    minute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    return hour, minute

def calculate_slot_id(hour, minute):
    """Calculate slot_id from time"""
    return (hour * 12) + (minute // 5) + 1

# Generate flights
flights = []
flight_id = 1

# Date range: March 1 to August 31, 2025
start_date = datetime(2025, 3, 1)
end_date = datetime(2025, 8, 31)
current_date = start_date

while current_date <= end_date:
    date_key = int(current_date.strftime('%Y%m%d'))
    
    # Random flights per day (75-85)
    num_flights = random.randint(75, 85)
    
    # Track used flight numbers per airline
    used_flight_numbers = {airline[0]: set() for airline in airlines}
    
    for _ in range(num_flights):
        # Select airline
        airline_code, airline_name, _ = random.choices(
            [(a[0], a[1], a[2]) for a in airlines],
            weights=[a[2] for a in airlines],
            k=1
        )[0]
        
        # Generate unique flight number
        while True:
            flight_num = random.randint(100, 9999)
            if flight_num not in used_flight_numbers[airline_code]:
                used_flight_numbers[airline_code].add(flight_num)
                break
        
        flight_number = f"{airline_code}{flight_num}"
        
        # Select aircraft
        aircraft_id = get_aircraft_for_airline(airline_code)
        aircraft_info = aircraft_lookup[aircraft_id]
        
        # Generate arrival time
        hour, minute = generate_arrival_time()
        arrival_time = f"{hour:02d}:{minute:02d}:00"
        arrival_slot_id = calculate_slot_id(hour, minute)
        
        # Select origin
        origin_airport = random.choice(origins)
        
        # Calculate passengers (70-95% load)
        load_factor = random.uniform(0.70, 0.95)
        estimated_pax = int(aircraft_info['typical_pax'] * load_factor)
        
        # Calculate bags (1.2-1.5 per pax)
        bags_per_pax = random.uniform(1.2, 1.5)
        estimated_bags = int(estimated_pax * bags_per_pax)
        
        # Cargo (39% have actual data)
        has_cargo_data = random.random() < 0.39
        if has_cargo_data:
            cargo_factor = random.uniform(0.30, 0.80)
            cargo_kg = round(aircraft_info['typical_cargo_kg'] * cargo_factor, 1)
        else:
            cargo_kg = 0.0
        
        flights.append({
            'flight_id': flight_id,
            'flight_number': flight_number,
            'airline_code': airline_code,
            'airline_name': airline_name,
            'aircraft_id': aircraft_id,
            'aircraft_series': aircraft_info['aircraft_series'],
            'aircraft_category': aircraft_info['aircraft_category'],
            'origin_airport': origin_airport,
            'date_key': date_key,
            'arrival_time': arrival_time,
            'arrival_slot_id': arrival_slot_id,
            'estimated_pax': estimated_pax,
            'estimated_bags': estimated_bags,
            'cargo_kg': cargo_kg,
            'has_cargo_data': 'TRUE' if has_cargo_data else 'FALSE',
            'is_active': 'TRUE'
        })
        
        flight_id += 1
    
    current_date += timedelta(days=1)

# Create DataFrame
dim_flight = pd.DataFrame(flights)

# Sort by date_key, then arrival_time
dim_flight = dim_flight.sort_values(['date_key', 'arrival_time']).reset_index(drop=True)
dim_flight['flight_id'] = range(1, len(dim_flight) + 1)

# Save to CSV
dim_flight.to_csv('dim_flight.csv', index=False, float_format='%.1f')

# Validation
print("=" * 80)
print("VALIDATION REPORT")
print("=" * 80)

print(f"\nTotal row count: {len(dim_flight):,}")
print(f"Date range: {dim_flight['date_key'].min()} to {dim_flight['date_key'].max()}")
days = (end_date - start_date).days + 1
print(f"Number of days: {days}")
print(f"Average flights per day: {len(dim_flight) / days:.1f}")

# Airline distribution
print("\nTop 5 airlines by flight count:")
airline_dist = dim_flight['airline_code'].value_counts().head(5)
for code, count in airline_dist.items():
    name = next(a[1] for a in airlines if a[0] == code)
    pct = count / len(dim_flight) * 100
    print(f"  {code} ({name}): {count:,} ({pct:.1f}%)")

# Aircraft category
widebody_pct = (dim_flight['aircraft_category'] == 'Widebody').sum() / len(dim_flight) * 100
narrowbody_pct = (dim_flight['aircraft_category'] == 'Narrowbody').sum() / len(dim_flight) * 100
print(f"\nAircraft category split:")
print(f"  Widebody: {widebody_pct:.1f}%")
print(f"  Narrowbody: {narrowbody_pct:.1f}%")

# Cargo data
cargo_pct = (dim_flight['has_cargo_data'] == 'TRUE').sum() / len(dim_flight) * 100
print(f"\nhas_cargo_data distribution:")
print(f"  TRUE: {cargo_pct:.1f}%")
print(f"  FALSE: {100 - cargo_pct:.1f}%")

# Sample rows
print("\n--- First 5 rows ---")
print(dim_flight.head(5).to_string(index=False))

print("\n--- Last 5 rows ---")
print(dim_flight.tail(5).to_string(index=False))

print("\n" + "=" * 80)
print("CSV file 'dim_flight.csv' created successfully!")
print("=" * 80)