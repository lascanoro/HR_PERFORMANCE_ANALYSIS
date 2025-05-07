from pathlib import Path
import pandas as pd


script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
data_raw = project_root / 'data' / 'raw'

files = [p.name for p in data_raw.iterdir() if p.is_file()]
print("Files in data/raw:", files)

# Load each table into a DataFrame (adjust names if they differ)
df_employee               = pd.read_csv(data_raw / 'employee_data.csv')
df_engagement_survey      = pd.read_csv(data_raw / 'employee_engagement_survey_data.csv')
df_recruitment            = pd.read_csv(data_raw / 'recruitment_data.csv')
df_training_development   = pd.read_csv(data_raw / 'training_and_development_data.csv')

# Initial inspection
print("\n■ dimensions of each table")
print(f"Employee:                     {df_employee.shape}")
print(f"Engagement Survey:            {df_engagement_survey.shape}")
print(f"Recruitment:                  {df_recruitment.shape}")
print(f"Training & Development:       {df_training_development.shape}")


###Employee Data
print("\n■ First 5 rows of Employee:")
print(df_employee.head())

print("\n■ Data types of Employee:")
print(df_employee.dtypes)

print("\n■ Null values in Employee:")
print(df_employee.isnull().sum())

#Engagement Survey Data
print("\n■ Dimensions of Engagement Survey:")
print(df_engagement_survey.shape)

print("\n■ First 5 rows of Engagement Survey:")
print(df_engagement_survey.head())

print("\n■ Data types of Engagement Survey:")
print(df_engagement_survey.dtypes)

##Recruitment Data
print("\n■ Dimensions of Recruitment:")
print(df_recruitment.shape)

print("\n■ First 5 rows of Recruitment:")
print(df_recruitment.head())

print("\n■ Data types of Recruitment:")
print(df_recruitment.dtypes)

#Training & Development Data
print("\n■ Dimensions of Training & Development:")
print(df_training_development.shape)

print("\n■ First 5 rows of Training & Development:")
print(df_training_development.head())
print("\n■ Data types of Training & Development:")
print(df_training_development.dtypes)

           

