import pandas as pd
df = pd.read_csv('ipl_2025_deliveries.csv')


if 'total_runs' not in df.columns:
    df['total_runs'] = df['runs_of_bat'] + df['extras']

if 'is_wicket' not in df.columns:
    df['is_wicket'] = df['wicket_type'].notnull().astype(int)

df['innings'] = df['innings'].astype(int)




