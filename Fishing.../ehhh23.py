# filter_waters.py
import pandas as pd
import argparse

def filter_valid_coords(input_csv: str, output_csv: str) -> None:
    """
    Reads a CSV with 'lat' and 'lon' columns and writes out only rows with valid coords.

    :param input_csv: Path to the input CSV file
    :param output_csv: Path to save the filtered CSV
    """
    df = pd.read_csv(input_csv)
    # Drop rows where lat or lon is NaN
    df_filtered = df.dropna(subset=['lat', 'lon'])
    df_filtered.to_csv(output_csv, index=False)
    print(f"Filtered {len(df_filtered)} entries into '{output_csv}'")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Filter out rows without valid coordinates.'
    )
    parser.add_argument(
        'input_csv',
        help='Input CSV file containing lat/lon columns'
    )
    parser.add_argument(
        'output_csv',
        help='Output CSV file for entries with valid coordinates'
    )
    args = parser.parse_args()
    filter_valid_coords(args.input_csv, args.output_csv)
