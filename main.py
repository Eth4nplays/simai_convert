import re
import csv

INPUT_FILE = "chart.simai"

def parse_simai(file_path):
    try:
        with open(file_path, "r") as f:
            # Clean data: remove newlines and spaces
            raw_data = "".join(f.read().split())
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return [], [], [], []

    current_bpm = 120.0
    current_division = 4.0
    current_time = 0.0
    
    times, lanes, types, durations = [], [], [], []
    
    # Split by commas (individual rhythmic steps)
    steps = raw_data.split(',')
    
    for step in steps:
        if not step:
            step_duration = (60 / current_bpm) * (4 / current_division)
            current_time += step_duration
            continue
        
        # 1. Update BPM and Division
        bpm_match = re.search(r'\((\d+(\.\d+)?)\)', step)
        if bpm_match:
            current_bpm = float(bpm_match.group(1))
            step = re.sub(r'\(.*?\)', '', step)

        div_match = re.search(r'\{(\d+)\}', step)
        if div_match:
            current_division = float(div_match.group(1))
            step = re.sub(r'\{.*?\}', '', step)

        # 2. Process Notes (separated by / for chords)
        notes_in_step = step.split('/')
        
        for note in notes_in_step:
            if not note or note == 'E': continue 
            
            # Regex to detect Area (A-E) and Lane Number (1-8)
            # Area is explicitly defined for Touch notes
            area_match = re.search(r'([ABCDE])([1-8])', note)
            
            n_type = "TAP"
            n_duration = 0
            
            if area_match:
                # If it has an Area prefix (A1, B5, E3, etc.), it is a TOUCH note
                area = area_match.group(1)
                lane_num = area_match.group(2)
                lane_str = f"{area}{lane_num}"
                n_type = "TOUCH"
            else:
                # Standard Tap/Slide/Hold (no area prefix)
                lane_match = re.search(r'([1-8])', note)
                lane_str = lane_match.group(1) if lane_match else "0"
                n_type = "TAP"

            # 3. Refine Type and Duration
            # Check for Hold/Slide duration first
            dur_match = re.search(r'\[(\d+):(\d+)\]', note)
            if dur_match:
                n_duration = (60 / current_bpm) * (4 / float(dur_match.group(1))) * float(dur_match.group(2))

            if 'h' in note:
                n_type = "HOLD" if not area_match else "TOUCH_HOLD"
            elif any(s in note for s in ['>', '<', '-', '^', 'v', 'p', 'q', 's', 'z', 'w', 'V']):
                n_type = "SLIDE"
            elif 'b' in note:
                n_type = "BREAK"

            # Append data
            times.append(round(current_time, 3))
            lanes.append(lane_str)
            types.append(n_type)
            durations.append(round(n_duration, 3))
        
        # 4. Advance time
        step_duration = (60 / current_bpm) * (4 / current_division)
        current_time += step_duration

    return times, lanes, types, durations

def save_list(filename, data):
    with open(filename, 'w', newline='') as f:
        print(filename+": ")
        print(f"{','.join(map(str, data))}")
        writer = csv.writer(f)
        for val in data:
            writer.writerow([val])
    print(f"Created {filename}")

# --- RUN ---
t, l, ty, d = parse_simai(INPUT_FILE)
if t:
    save_list("data_time.csv", t)
    save_list("data_lane.csv", l)
    save_list("data_type.csv", ty)
    save_list("data_duration.csv", d)
    print(f"\nSuccess! Exported {len(t)} notes.")