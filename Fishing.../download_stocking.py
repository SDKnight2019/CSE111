import requests

# URL copied from IDFG Stocking export
CSV_URL = 'https://idfg.idaho.gov/ifwis/fishingplanner/stocking/export?format=csv'
OUTPUT_FILE = 'stocking.csv'

def download_stocking_csv(url: str, out_path: str) -> None:
    """
    Download the IDFG stocking CSV from the given URL and save it locally.
    """
    resp = requests.get(url)
    resp.raise_for_status()
    with open(out_path, 'wb') as f:
        f.write(resp.content)
    print(f"Saved stocking data to {out_path}")

if __name__ == '__main__':
    download_stocking_csv(CSV_URL, OUTPUT_FILE)

