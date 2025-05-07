from pathlib import Path
import pandas as pd

script_dir   = Path(__file__).resolve().parent
project_root = script_dir.parent.parent

# 2. Define rutas de entrada y salida
data_raw   = project_root / 'data' / 'raw'
data_clean = project_root / 'data' / 'cleaned'
data_clean.mkdir(parents=True, exist_ok=True)

# 3. Carga del dataset principal
df_employee = pd.read_csv(data_raw / 'employee_data.csv')

# 4. Renombrado de columnas a snake_case
df_employee.columns = (
    df_employee.columns
      .str.strip()
      .str.lower()
      .str.replace(' ', '_', regex=False)
      .str.replace('-', '_', regex=False)
      .str.replace('/', '_', regex=False)
)
# Ajustes puntuales 
df_employee.rename(columns={
    'empid': 'emp_id',
    'ade_mail': 'ad_email',
    'performance_score': 'performance_score',
    'current_employee_rating': 'current_rating'
}, inplace=True)

# 5. Conversión de fechas a datetime
date_cols = ['startdate', 'exitdate', 'dob']
for col in date_cols:
    df_employee[col] = pd.to_datetime(df_employee[col], format='%d-%b-%y', errors='coerce')

# 6. Manejo de valores nulos
# 6.1 Marcar empleados activos
df_employee['is_active'] = df_employee['exitdate'].isna()
# 6.2 Rellenar descripción de terminación
if 'terminationdescription' in df_employee.columns:
    df_employee['terminationdescription'].fillna('Active', inplace=True)

# 7. Ajuste de tipos de datos
df_employee['locationcode']    = df_employee['locationcode'].astype(str)
df_employee['current_rating']  = df_employee['current_rating'].astype(int)

# 8. Eliminación de columnas irrelevantes
to_drop = []
for col in ['ad_email', 'terminationtype']:
    if col in df_employee.columns:
        to_drop.append(col)
if to_drop:
    df_employee.drop(columns=to_drop, inplace=True)

# 9. Inspección rápida post-limpieza
print("Dimensiones post-limpieza:", df_employee.shape)
print(df_employee.dtypes)
print(df_employee[['emp_id','startdate','exitdate','is_active','performance_score']].head())

# 10. Guardar CSV limpio
output_path = data_clean / 'employee_data_clean.csv'
df_employee.to_csv(output_path, index=False)
print(f"\nDataset limpiado guardado en:\n  {output_path}")
