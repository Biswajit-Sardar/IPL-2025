import pandas as pd
df = pd.read_csv('ipl_2025_deliveries.csv')


if 'total_runs' not in df.columns:
    df['total_runs'] = df['runs_of_bat'] + df['extras']

if 'is_wicket' not in df.columns:
    df['is_wicket'] = df['wicket_type'].notnull().astype(int)

df['innings'] = df['innings'].astype(int)

if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
else:
    df['date'] = None

df['cumulative_runs'] = df.groupby(['match_id', 'innings'])['total_runs'].cumsum()
df['cumulative_wickets'] = df.groupby(['match_id', 'innings'])['is_wicket'].cumsum()

innings_summary = df.groupby(['match_id', 'innings', 'batting_team', 'bowling_team']).agg(
    total_score=('cumulative_runs', 'max'),
    wickets_lost=('cumulative_wickets', 'max'),
    venue=('venue', 'first'),
    date=('date', 'first')
).reset_index()

match_data = innings_summary.pivot_table(
    index=['match_id', 'venue', 'date'],
    columns='innings',
    values=['batting_team', 'bowling_team', 'total_score', 'wickets_lost'],
    aggfunc='first'
)

match_data.columns = [f'{col[0]}_{col[1]}' for col in match_data.columns]
match_data = match_data.reset_index()

rename_dict = {
    'batting_team_1': 'Team_1_Batting_First',
    'bowling_team_1': 'Team_2_Bowling_First',
    'batting_team_2': 'Team_2_Batting_Second',
    'bowling_team_2': 'Team_1_Bowling_Second',
    'total_score_1': 'Score_1',
    'total_score_2': 'Score_2',
    'wickets_lost_1': 'Wickets_1',
    'wickets_lost_2': 'Wickets_2'
}

match_data.rename(columns=rename_dict, inplace=True)

required_cols = [
    'Score_1', 'Score_2', 'Wickets_1', 'Wickets_2',
    'Team_1_Batting_First', 'Team_2_Batting_Second'
]

for col in required_cols:
    if col not in match_data.columns:
        match_data[col] = None

def determine_winner(row):
    s1, s2 = row['Score_1'], row['Score_2']
    t1, t2 = row['Team_1_Batting_First'], row['Team_2_Batting_Second']

    if pd.isna(s1) or pd.isna(s2):
        return 'Unknown'  

    if s2 > s1:
        return t2
    elif s1 > s2:
        return t1
    else:
        return 'Tie'

match_data['winner'] = match_data.apply(determine_winner, axis=1)


final_match_df = match_data[
    ['match_id', 'date', 'venue',
     'Team_1_Batting_First', 'Team_2_Batting_Second',
     'Score_1', 'Score_2', 'Wickets_1', 'Wickets_2', 'winner']
]


output_file = 'ipl_2025_cleaned_data.csv'
final_match_df.to_csv(output_file, index=False)


