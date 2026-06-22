import os
import glob
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_CLEAN_PATH = os.path.join(DATA_DIR, 'storage_clean_train.csv')

def process_balanced_storage_dataset():
    print("⏳ Scanning your data/ directory for extracted Kaggle storage data shards...")
    
    # 1. Broad recursive search to find any nested storage data CSV files from the zip
    all_csv_files = glob.glob(os.path.join(DATA_DIR, '**', '*.csv'), recursive=True)
    
    # Filter out files belonging to other pillars or our final output target
    target_files = [
        f for f in all_csv_files 
        if 'storage_clean' not in f 
        and 'power' not in f 
        and 'compute' not in f 
        and 'metadata' not in f
    ]
    
    if not target_files:
        raise FileNotFoundError(
            f"No raw storage CSV files found inside '{DATA_DIR}'. "
            "Make sure you completely extracted the Kaggle zip archive into your data folder!"
        )
        
    print(f"📦 Discovered {len(target_files)} relevant data pieces. Beginning ingestion and consolidation...")
    
    compiled_records = []
    
    # 2. Extract and match keys to fulfill our live Prometheus metrics schema contract
    for path in target_files:
        try:
            # First, scan headings to find columns flexibly regardless of capitalization variations
            sample_df = pd.read_csv(path, nrows=5)
            col_mapping = {}
            
            for col in sample_df.columns:
                col_lower = col.lower()
                if 'smart_5' in col_lower or 'smart5' in col_lower:
                    col_mapping[col] = 'storage_smart_5'
                elif 'smart_197' in col_lower or 'smart197' in col_lower:
                    col_mapping[col] = 'storage_smart_197'
                elif 'smart_198' in col_lower or 'smart198' in col_lower:
                    col_mapping[col] = 'storage_smart_198'
                # 🟢 Natively matches 'failure', 'is_failed', or 'failed' columns from raw Backblaze logs
                elif 'fail' in col_lower:
                    col_mapping[col] = 'failure'

            # Ensure all core properties are present in this slice before running heavy reads
            required_keys = ['storage_smart_5', 'storage_smart_197', 'storage_smart_198', 'failure']
            reverse_mapping = {v: k for k, v in col_mapping.items()}
            
            if all(rk in reverse_mapping for rk in required_keys):
                actual_cols_to_use = [reverse_mapping[rk] for rk in required_keys]
                
                # Load only the critical columns needed
                df = pd.read_csv(path, usecols=actual_cols_to_use)
                df = df.rename(columns=col_mapping)
                
                # Drop rows missing critical telemetry data attributes
                df = df.dropna(subset=required_keys)
                compiled_records.append(df[required_keys])
            else:
                print(f"⚠️ Column missing in {os.path.basename(path)}. Found keys map to: {list(col_mapping.values())}")
        except Exception as e:
            print(f"⚠️ Skipping block {os.path.basename(path)} due to read/parse error: {e}")

    if not compiled_records:
        raise ValueError("Could not find any rows containing a valid matching schema contract inside the files!")

    # 3. Combine the distinct tables into one comprehensive historical baseline dataset
    print("\n🔄 Merging records and formatting data types...")
    final_df = pd.concat(compiled_records, ignore_index=True)
    
    # Cast variables securely to shield matrix tracking arrays during XGBoost cross-validation loops
    for sc in ['storage_smart_5', 'storage_smart_197', 'storage_smart_198']:
        final_df[sc] = pd.to_numeric(final_df[sc], errors='coerce').fillna(0).astype(float)
    final_df['failure'] = final_df['failure'].astype(int)
    
    # 4. Save the balanced clean data down for train.py execution
    final_df.to_csv(OUTPUT_CLEAN_PATH, index=False)
    print(f"🟢 Success! Combined and normalized {len(final_df)} samples total.")
    print(f"🏁 Final clean output saved to: {OUTPUT_CLEAN_PATH}\n")

if __name__ == "__main__":
    process_balanced_storage_dataset()