from pathlib import Path
import pandas as pd

# 1. Localiza el directorio del script y la raíz del proyecto
script_dir   = Path(__file__).resolve().parent
project_root = script_dir.parent.parent

# 2. Define rutas de entrada y salida
data_raw   = project_root / 'data' / 'raw'
data_clean = project_root / 'data' / 'cleaned'
data_clean.mkdir(parents=True, exist_ok=True)

# 3. Busca el CSV de Engagement Survey por patrón (más robusto que un nombre fijo)
engagement_files = list(data_raw.glob('*engagement*survey*.csv'))
if not engagement_files:
    raise FileNotFoundError(f"No encontré ningún CSV de Engagement Survey en:\n  {data_raw}")
file_path = engagement_files[0]
print("Usando fichero de Engagement Survey:", file_path)

# 4. Carga del CSV crudo en df_engagement_survey
df_engagement_survey = pd.read_csv(file_path)

# 5. Renombrar columnas a snake_case
df_engagement_survey.columns = (
    df_engagement_survey.columns
      .str.strip()
      .str.lower()
      .str.replace(' ', '_', regex=False)
      .str.replace('-', '_', regex=False)
      .str.replace('/', '_', regex=False)
)

# 6. Conversión de fechas
df_engagement_survey['survey_date'] = pd.to_datetime(
    df_engagement_survey['survey_date'],
    format='%d-%m-%Y',
    errors='coerce'
)

# 7. Manejo de nulos
print("\nValores nulos antes de imputación:")
print(df_engagement_survey.isnull().sum())
for col in ['engagement_score', 'satisfaction_score', 'work_life_balance_score']:
    if df_engagement_survey[col].isna().any():
        df_engagement_survey[col].fillna(df_engagement_survey[col].mean(), inplace=True)
print("\nValores nulos después de imputación:")
print(df_engagement_survey.isnull().sum())

# 8. Inspección rápida post-limpieza
print("\n■ Dimensiones post-limpieza:", df_engagement_survey.shape)
print(df_engagement_survey.dtypes)
print(df_engagement_survey.head())

# 9. Guardar CSV limpio
output_path = data_clean / 'engagement_survey_clean.csv'
df_engagement_survey.to_csv(output_path, index=False)
print(f"\nEngagement Survey limpio guardado en:\n  {output_path}")


