import os
import glob
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_PATH = os.path.join(DATA_DIR, 'storage_new_raw.csv')

print("⏳ Scanning your extracted Kaggle folder for year-by-year CSV slices...")

# Look for all .csv files matching the internal name convention inside the dataset folder
# Change 'Battery_DataSet' match logic to find your unzipped hard drive folders instead
csv_files = glob.glob(os.path.join(DATA_DIR, '**', '*ST4000DM000*.csv'), recursive=True)

if not csv_files:
    # Fallback to catch all generic csv structures if folders are named differently
    csv_files = [f for f in glob.glob(os.path.join(DATA_DIR, '**', '*.csv'), recursive=True) if 'storage_clean' not in f and 'power' not in f and 'compute' not in f and 'metadata' not in f]

if not csv_files:
    raise FileNotFoundError("Could not find any raw year CSV files inside the data directory! Make sure you extracted the zip completely.")

print(f"📦 Found {len(csv_files)} data shards. Merging tables...")

combined_df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
combined_df.to_csv(OUTPUT_PATH, index=False)

print(f"🟢 Success! Combined {len(combined_df)} total records into a balanced file tracking block.")
print(f"🏁 Saved location: {OUTPUT_PATH}")