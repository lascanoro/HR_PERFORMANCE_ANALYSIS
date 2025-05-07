from pathlib import Path
import pandas as pd
import numpy as np



script_dir   = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
data_clean   = project_root / 'data' / 'cleaned'
reports_dir  = project_root / 'reports'
reports_dir.mkdir(parents=True, exist_ok=True)


df_emp = pd.read_csv(data_clean / 'employee_data_clean.csv')

#Convert date columns to datetime
for col in ['startdate','exitdate','dob']:
    df_emp[col] = pd.to_datetime(df_emp[col], errors='coerce')

# Map performance_score (text) to a numeric scale, including 'PIP'
perf_mapping = {
    'PIP':                1,
    'Needs Improvement':  2,
    'Fully Meets':        3,
    'Exceeds':            4,
    'Outstanding':        5
}
df_emp['performance_score_num'] = df_emp['performance_score'].map(perf_mapping)
unmapped = df_emp.loc[df_emp['performance_score_num'].isna(), 'performance_score'].unique()
if len(unmapped) > 0:
    print("⚠️ Valores de performance_score no mapeados:", unmapped)

# Ensure numeric types
df_emp['performance_score_num'] = pd.to_numeric(df_emp['performance_score_num'], errors='coerce')
df_emp['current_rating']        = pd.to_numeric(df_emp['current_rating'],    errors='coerce')

# Calculate experience in years
today = pd.Timestamp.today()
df_emp['experience_years'] = (
    (df_emp['exitdate'].fillna(today) - df_emp['startdate'])
    .dt.days
    .div(365)
    .round(2)
)

# Descriptive statistics
descr = df_emp[['performance_score_num','current_rating']].describe().T
descr['iqr'] = descr['75%'] - descr['25%']
print("=== Descriptive stats (performance_score_num & current_rating) ===\n", descr, "\n")
descr.to_csv(reports_dir / '03_performance_rating_stats.csv')

# Analysis by groups (experience, department, gender)
bins   = [0, 2, 5, 10, np.inf]
labels = ['0-2','3-5','6-10','>10']
df_emp['exp_group'] = pd.cut(df_emp['experience_years'], bins=bins, labels=labels)

for col in ['exp_group','departmenttype','gendercode']:
    if col not in df_emp.columns:
        continue
    grp = (
        df_emp
        .groupby(col)['performance_score_num']
        .agg(['mean','median','std','count'])
        .round(2)
        .sort_values('mean', ascending=False)
    )
    print(f"--- Performance por {col} ---\n", grp, "\n")
    grp.to_csv(reports_dir / f'03_perf_by_{col}.csv')

# # Detection of outliers (IQR)
ps    = df_emp['performance_score_num'].dropna()
Q1, Q3 = ps.quantile([0.25,0.75])
IQR    = Q3 - Q1
lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
outliers = df_emp[(df_emp['performance_score_num'] < lower) | (df_emp['performance_score_num'] > upper)]
print(f"Outliers (<{lower:.1f} or >{upper:.1f}): {outliers.shape[0]} registros")
outliers[['emp_id','performance_score','performance_score_num']].to_csv(
    reports_dir / '03_outliers_performance.csv', index=False
)

#  Load and clean Training & Development for merging
df_trn = pd.read_csv(data_clean / 'training_and_development_clean.csv')
print("Columns in df_trn before rename:", df_trn.columns.tolist())
if 'training_duration(days)' in df_trn.columns:
    df_trn = df_trn.rename(columns={'training_duration(days)': 'training_duration_days'})
print("Columns in df_trn after rename:", df_trn.columns.tolist())

#Correlation matrix
df_rec = pd.read_csv(data_clean / 'recruitment_clean.csv')
df_stats = (
    df_emp[['emp_id','performance_score_num','current_rating']]
    .merge(
        df_rec[['applicant_id','desired_salary']],
        how='left', left_on='emp_id', right_on='applicant_id'
    )
    .merge(
        df_trn[['employee_id','training_duration_days']],
        how='left', left_on='emp_id', right_on='employee_id'
    )
)
cols_corr = ['performance_score_num','current_rating','desired_salary','training_duration_days']
corr = df_stats[cols_corr].corr().round(2)
print("=== Matriz de correlación ===\n", corr, "\n")
corr.to_csv(reports_dir / '03_correlation_matrix.csv')


print("▶︎ Fase 3 completada.")

