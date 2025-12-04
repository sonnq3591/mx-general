import pandas as pd
from datetime import time, timedelta

def get_period_info(hour, minute):
    """Determine period_id, period_name, and is_peak based on time"""
    if (hour == 6 or (hour >= 7 and hour <= 9)) or (hour == 9 and minute <= 55):
        return 1, "Morning Peak", "TRUE"
    elif (hour >= 10 and hour <= 13) or (hour == 13 and minute <= 55):
        return 2, "Midday", "FALSE"
    elif (hour >= 14 and hour <= 19) or (hour == 19 and minute <= 55):
        return 3, "Evening Peak", "TRUE"
    else:
        return 4, "Night", "FALSE"

# Generate 288 time slots (5-minute intervals)
slots = []
slot_id = 1

for hour in range(24):
    for minute in range(0, 60, 5):
        start_time = time(hour, minute, 0)
        
        # Calculate end time (5 minutes later)
        end_minute = minute + 5
        end_hour = hour
        if end_minute >= 60:
            end_minute = 0
            end_hour = (hour + 1) % 24
        end_time = time(end_hour, end_minute, 0)
        
        # Create slot label
        slot_label = f"{hour:02d}:{minute:02d}-{end_hour:02d}:{end_minute:02d}"
        
        # Get period information
        period_id, period_name, is_peak = get_period_info(hour, minute)
        
        slots.append({
            'slot_id': slot_id,
            'slot_start_time': start_time.strftime('%H:%M:%S'),
            'slot_end_time': end_time.strftime('%H:%M:%S'),
            'slot_label': slot_label,
            'hour': hour,
            'minute_start': minute,
            'period_id': period_id,
            'period_name': period_name,
            'is_peak': is_peak
        })
        
        slot_id += 1

# Create DataFrame
dim_time_slot = pd.DataFrame(slots)

# Save to CSV
dim_time_slot.to_csv('dim_time_slot.csv', index=False)

# Validation
print("=" * 80)
print("VALIDATION REPORT")
print("=" * 80)

print(f"\nTotal row count: {len(dim_time_slot)} (expected: 288)")

print("\n--- First 5 rows ---")
print(dim_time_slot.head(5).to_string(index=False))

print("\n--- Last 5 rows ---")
print(dim_time_slot.tail(5).to_string(index=False))

print("\nCount by period_name:")
period_counts = dim_time_slot['period_name'].value_counts().sort_index()
for period, count in period_counts.items():
    print(f"  {period}: {count}")

print(f"\nCount of is_peak=TRUE: {(dim_time_slot['is_peak'] == 'TRUE').sum()} (expected: 120)")

slot_1 = dim_time_slot[dim_time_slot['slot_id'] == 1].iloc[0]
slot_288 = dim_time_slot[dim_time_slot['slot_id'] == 288].iloc[0]
print(f"\nslot_id 1 starts at: {slot_1['slot_start_time']} ✓")
print(f"slot_id 288 starts at: {slot_288['slot_start_time']} ✓")

print("\n" + "=" * 80)
print("CSV file 'dim_time_slot.csv' created successfully!")
print("=" * 80)