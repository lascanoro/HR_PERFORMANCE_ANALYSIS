from pathlib import Path
import pandas as pd

# 1. Locate the script directory and project root
script_dir   = Path(__file__).resolve().parent
project_root = script_dir.parent.parent

# 2. Define raw & clean data paths
data_raw   = project_root / 'data' / 'raw'
data_clean = project_root / 'data' / 'cleaned'
data_clean.mkdir(parents=True, exist_ok=True)

# 3. Point to the Training & Development CSV
file_path = data_raw / 'training_and_development_data.csv'
print(f"Reading Training & Development file from: {file_path}")
if not file_path.exists():
    raise FileNotFoundError(f"File not found: {file_path}")

# 4. Load into df_training_development
df_training_development = pd.read_csv(file_path)

# 5. Rename columns to snake_case
df_training_development.columns = (
    df_training_development.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_', regex=False)
        .str.replace('-', '_', regex=False)
        .str.replace('/', '_', regex=False)
)

# 6. Convert date columns
# Assuming ‘training_date’ column exists
if 'training_date' in df_training_development.columns:
    df_training_development['training_date'] = pd.to_datetime(
        df_training_development['training_date'],
        errors='coerce'
    )

# 7. Handle missing values
print("\nMissing values before imputation:")
print(df_training_development.isnull().sum())

# Example imputations:
# - If 'training_outcome' is missing, fill with 'Unknown'
if 'training_outcome' in df_training_development.columns:
    df_training_development['training_outcome'].fillna('Unknown', inplace=True)

# - If 'training_duration(days)' missing, fill with median
col_duration = 'training_duration(days)'
if col_duration in df_training_development.columns and df_training_development[col_duration].isna().any():
    median_dur = df_training_development[col_duration].median()
    df_training_development[col_duration].fillna(median_dur, inplace=True)

print("\nMissing values after imputation:")
print(df_training_development.isnull().sum())

# 8. Quick post-cleaning inspection
print("\n■ Shape post-cleaning:", df_training_development.shape)
print(df_training_development.dtypes)
print(df_training_development.head())

# 9. Save cleaned CSV
output_path = data_clean / 'training_and_development_clean.csv'
df_training_development.to_csv(output_path, index=False)
print(f"\nCleaned Training & Development saved to:\n  {output_path}")