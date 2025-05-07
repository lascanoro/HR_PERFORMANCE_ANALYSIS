from pathlib import Path
import pandas as pd
import numpy as np


script_dir   = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
data_clean   = project_root / 'data' / 'cleaned'
reports_dir  = project_root / 'reports'
reports_dir.mkdir(parents=True, exist_ok=True)


df_emp = pd.read_csv(data_clean / 'employee_data_clean.csv', parse_dates=['startdate','exitdate'])
df_eng = pd.read_csv(data_clean / 'engagement_survey_clean.csv', parse_dates=['survey_date'])
df_rec = pd.read_csv(data_clean / 'recruitment_clean.csv')
df_trn = pd.read_csv(data_clean / 'training_and_development_clean.csv', parse_dates=['training_date'])


# Search for any column containing 'training_duration'
duration_cols = [c for c in df_trn.columns if 'training_duration' in c]
if not duration_cols:
    raise KeyError(f"No encontré ninguna columna de training_duration en: {df_trn.columns.tolist()}")
# Rename the first match to 'training_duration_days'
if duration_cols[0] != 'training_duration_days':
    df_trn = df_trn.rename(columns={duration_cols[0]: 'training_duration_days'})

#  Map performance_score to a numeric scale (reconstruction)
perf_mapping = {
    'PIP':                1,
    'Needs Improvement':  2,
    'Fully Meets':        3,
    'Exceeds':            4,
    'Outstanding':        5
}
df_emp['performance_score_num'] = df_emp['performance_score'].map(perf_mapping)

# Calculate experience in years
today = pd.Timestamp.today()
df_emp['experience_years'] = (
    (df_emp['exitdate'].fillna(today) - df_emp['startdate'])
    .dt.days.div(365).round(2)
)

#  Define segments
high_perf = df_emp[df_emp['performance_score_num'] >= 4]
low_perf  = df_emp[df_emp['performance_score_num'] <= 2]

def summarize_group(df_group, name):
    # Average de Engagement
    eng_avg = df_eng.groupby('employee_id')['engagement_score'] \
                    .mean().rename('avg_engagement')
    # Average Desired Salary
    rec_avg = df_rec.groupby('applicant_id')['desired_salary'] \
                    .mean().rename('avg_desired_salary')
    # Average Training Days
    trn_avg = df_trn.groupby('employee_id')['training_duration_days'] \
                    .mean().rename('avg_training_days')
    
    df = (
        df_group
        .set_index('emp_id')
        .join(eng_avg, how='left')
        .join(rec_avg, how='left')
        .join(trn_avg, how='left')
        .reset_index()
    )
    profile = {
        'segment': name,
        'count': len(df),
        'mean_experience_years': df['experience_years'].mean().round(2),
        'female_ratio': (df['gendercode']=='Female').mean().round(2),
        'mean_current_rating': df['current_rating'].mean().round(2),
        'mean_engagement_score': df['avg_engagement'].mean().round(2),
        'mean_desired_salary': df['avg_desired_salary'].mean().round(2),
        'mean_training_days': df['avg_training_days'].mean().round(2),
        'top_3_departments': df['departmenttype']
            .value_counts().nlargest(3).index.tolist()
    }
    return profile

# 7. Generate and save profiles
profiles = [
    summarize_group(high_perf, 'High Performance (>=4)'),
    summarize_group(low_perf,  'Low Performance (<=2)')
]
df_profiles = pd.DataFrame(profiles)
df_profiles.to_csv(reports_dir / '04_performance_profiles.csv', index=False)
print("✔︎ Profiles saved in 04_performance_profiles.csv")

# 8. Detail distribution High Performance
dept_high = high_perf['departmenttype'].value_counts(normalize=True).mul(100).round(1)
dept_high.to_frame('pct').to_csv(
    reports_dir / '04_high_perf_dept_distribution.csv'
)
gender_high = high_perf['gendercode'].value_counts(normalize=True).mul(100).round(1)
gender_high.to_frame('pct').to_csv(
    reports_dir / '04_high_perf_gender_distribution.csv'
)
print("✔︎ Profiles saved in 04_high_perf_*_distribution.csv")

print("▶︎ Phase 4 completed. Check the CSVs in 'reports/'")
