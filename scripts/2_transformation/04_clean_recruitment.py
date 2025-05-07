from pathlib import Path
import pandas as pd

# 1. Localiza el directorio del script y la raíz del proyecto
script_dir   = Path(__file__).resolve().parent
project_root = script_dir.parent.parent

# 2. Define rutas de entrada y salida
data_raw   = project_root / 'data' / 'raw'
data_clean = project_root / 'data' / 'cleaned'
data_clean.mkdir(parents=True, exist_ok=True)

# 3. Ruta al CSV de Recruitment
file_path = data_raw /'recruitment_data.csv'
print("Leyendo fichero de Recruitment en:", file_path.resolve())
print("¿Existe realmente?", file_path.exists())

df_recruitment = pd.read_csv(file_path)


# 4. Renombrar columnas a snake_case
df_recruitment.columns = (
    df_recruitment.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_', regex=False)
        .str.replace('-', '_', regex=False)
        .str.replace('/', '_', regex=False)
)

# 5. Conversión de fechas
for col in ['application_date', 'date_of_birth']:
    if col in df_recruitment.columns:
        df_recruitment[col] = pd.to_datetime(df_recruitment[col], errors='coerce')

# 6. Manejo de nulos
print("\nMissing values before imputation:")
print(df_recruitment.isnull().sum())

# Imputar desired_salary con la media
if 'desired_salary' in df_recruitment.columns:
    df_recruitment['desired_salary'].fillna(df_recruitment['desired_salary'].mean(), inplace=True)

# Rellenar status faltante como 'Unknown'
if 'status' in df_recruitment.columns:
    df_recruitment['status'].fillna('Unknown', inplace=True)

print("\nMissing values after imputation:")
print(df_recruitment.isnull().sum())

# 7. Inspección rápida post-limpieza
print("\n■ Shape post-cleaning:", df_recruitment.shape)
print(df_recruitment.dtypes)
print(df_recruitment.head())

# 8. Guardar CSV limpio
output_path = data_clean / 'recruitment_clean.csv'
df_recruitment.to_csv(output_path, index=False)
print(f"\nCleaned Recruitment saved to:\n  {output_path}")



