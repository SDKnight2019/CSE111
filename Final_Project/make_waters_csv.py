import csv

INPUT_FILE = 'raw_waters.txt'
OUTPUT_FILE = 'waters_list.csv'

def parse_raw(input_path: str, output_path: str):

    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['name', 'location_desc', 'county', 'size'])

        for line in infile:
            line = line.strip()
            if not line:
                continue
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
