# make_waters_csv.py
"""
Parse a raw tab-delimited list of water bodies into a clean CSV.

Usage:
    1. Save your raw list (one record per line, with fields separated by tabs) to 'raw_waters.txt'.
    2. Run:
         python3 make_waters_csv.py
    3. The script will produce 'waters_list.csv' with headers: name,location_desc,county,size
"""
import csv

INPUT_FILE = 'raw_waters.txt'
OUTPUT_FILE = 'waters_list.csv'

def parse_raw(input_path: str, output_path: str):
    """
    Read the raw tab-delimited text and write a CSV with four columns.
    """
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        # Write header
        writer.writerow(['name', 'location_desc', 'county', 'size'])

        for line in infile:
            line = line.strip()
            if not line:
                continue
            # Skip header lines that start with 'Name'
            if line.lower().startswith('name'):
                continue
            parts = line.split('\t')
            if len(parts) != 4:
                print(f"Skipping malformed line: {line}")
                continue
            name, loc, county, size = [p.strip() for p in parts]
            writer.writerow([name, loc, county, size])
    print(f"Created {output_path}")

if __name__ == '__main__':
    parse_raw(INPUT_FILE, OUTPUT_FILE)
