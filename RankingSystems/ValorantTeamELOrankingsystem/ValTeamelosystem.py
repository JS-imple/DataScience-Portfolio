import pandas as pd
import numpy as np

# Load the CSV
Valorant_matches_not_sorted = pd.read_csv("results20231007.csv", index_col=0)
Valorantmatches = Valorant_matches_not_sorted.reset_index()

# Sort with the most recent at the bottom
Valorantmatches = Valorantmatches.sort_index(ascending=False)

# Create unique Event IDs
unique_events = Valorantmatches[['Event']].drop_duplicates().reset_index(drop=True)

unique_events['Event_id'] = range(1, len(unique_events) + 1)
Valorantmatches = Valorantmatches.merge(unique_events, on='Event')

# Drop unnecessary columns
Valorantmatches.drop(columns=["Date", "Link", "Time", 'Status', 'Match In Event'], inplace=True)

# Initialize Elo ratings
initial_elo = 1000
elo_ratings = {}
k_factor = 40
peak_elo_ratings = {}

# Function to calculate the expected score
def expected_score(elo_a, elo_b):
    return 1 / (1 + 10**((elo_b - elo_a) / 400))

# Function to update Elo ratings
def update_elo(winner_elo, loser_elo, k_factor):
    expected_win = expected_score(winner_elo, loser_elo)
    new_winner_elo = winner_elo + k_factor * (1 - expected_win)
    new_loser_elo = loser_elo + k_factor * (0 - (1 - expected_win))
    return round(new_winner_elo, 2), round(new_loser_elo, 2)

# Create unique match IDs
Valorantmatches['cc_match'] = np.arange(1, len(Valorantmatches) + 1)

# Add columns for Elo ratings
Valorantmatches['Team_1_elo_start'] = 0.0  # float
Valorantmatches['Team_2_elo_start'] = 0.0  # float
Valorantmatches['Team_1_elo_end'] = 0.0    # float
Valorantmatches['Team_2_elo_end'] = 0.0    # float

# Calculate Elo ratings for each match
for index, row in Valorantmatches.iterrows():
    Team_1 = row['Team 1']
    Team_2 = row['Team 2']

    # Initialize Elo ratings if Teams are encountered for the first time
    if Team_1 not in elo_ratings:
        elo_ratings[Team_1] = initial_elo
    if Team_2 not in elo_ratings:
        elo_ratings[Team_2] = initial_elo

    # Get starting Elo ratings
    Team_1_elo_start = elo_ratings[Team_1]
    Team_2_elo_start = elo_ratings[Team_2]

    # Record starting Elo ratings
    Valorantmatches.at[index, 'Team_1_elo_start'] = Team_1_elo_start
    Valorantmatches.at[index, 'Team_2_elo_start'] = Team_2_elo_start

    # Update Elo based on the 'Match winner' column
    if row['Match Winner'] == row['Team 1']:  # Team 1 wins
        new_Team1_elo, new_Team2_elo = update_elo(Team_1_elo_start, Team_2_elo_start, k_factor)
    elif row['Match Winner'] == row['Team 2']:  # Team 2 wins (Team 1 loses)
        new_Team1_elo, new_Team2_elo = update_elo(Team_1_elo_start, Team_2_elo_start, -k_factor)
    else:  # In case of a draw or undefined winner
        new_Team1_elo, new_Team2_elo = update_elo(Team_1_elo_start, Team_2_elo_start, 0)  # No change in Elo

    if Team_1 not in peak_elo_ratings or new_Team1_elo > peak_elo_ratings[Team_1]:
        peak_elo_ratings[Team_1] = new_Team1_elo
    if Team_2 not in peak_elo_ratings or new_Team2_elo > peak_elo_ratings[Team_2]:
        peak_elo_ratings[Team_2] = new_Team2_elo

    # Record updated Elo ratings
    Valorantmatches.at[index, 'Team_1_elo_end'] = new_Team1_elo
    Valorantmatches.at[index, 'Team_2_elo_end'] = new_Team2_elo

    # Update Elo ratings in the dictionary
    elo_ratings[Team_1] = new_Team1_elo
    elo_ratings[Team_2] = new_Team2_elo

def get_Team_info(Team_name, elo_ratings, Valorantmatches, initial_elo=1000):
    # Check if the Team exists in the Elo ratings dictionary
    if Team_name in elo_ratings:
        elo = elo_ratings[Team_name]
    else:
        elo = initial_elo

    # Find all matches where the Team appeared as either Team_1 or Team_2
    Team_matches = Valorantmatches[(Valorantmatches['Team_1'] == Team_name) | 
                                (Valorantmatches['Team_2'] == Team_name)]
    
    # Return Elo rating and their matches
    if not Team_matches.empty:
        print(f"{Team_name}'s current Elo rating: {elo}\n")
        print(f"{Team_name}'s matches:")
        return Team_matches[['event', 'Team_1', 'Team_2', 'result', 'Team_1_elo_start', 'Team_2_elo_start','Team_1_elo_end','Team_2_elo_end']]
    else:
        return f"{Team_name} has no recorded matches."
    
# Export to CSV
Valorantmatches.to_csv('Valorantmatches_with_elo.csv', index=False)
'''
# Find the Team with the highest Elo
highest_elo_Team = max(elo_ratings, key=elo_ratings.get)
highest_elo_value = elo_ratings[highest_elo_Team]
print(f"The Team with the highest Elo is {highest_elo_Team} with an Elo of {highest_elo_value}.")

#find the Team with the lowest elo
lowest_elo_Team = min(elo_ratings, key= elo_ratings.get)
lowest_elo_value = elo_ratings[lowest_elo_Team]
print(f"The Team with the highest Elo is {lowest_elo_Team} with an Elo of {lowest_elo_value}")
'''
'''
top_50_Teams = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)[:50]
top_50_df = pd.DataFrame(top_50_Teams, columns=['Team', 'Elo Rating'])
top_50_df.to_csv('top_50_Teams_elo.csv', index=False)

all_Teams = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)
all_Teams_df = pd.DataFrame(all_Teams, columns=['Team', 'Elo Rating'])
all_Teams_df.to_csv('all_Teams_elo.csv', index=False)

peak_elo = sorted(peak_elo_ratings.items(), key = lambda x: x[1], reverse = True)
peak_elo_df = pd.DataFrame(peak_elo, columns=['Team', 'Peak Elo'])
peak_elo_df.to_csv('peak_elo.csv', index=False)
'''
'''
Team_name = "GEN.G"
def get_Team_info(Team_name, elo_ratings, Valorantmatches):
    # Use the correct column names here
    Team_matches = Valorantmatches[(Valorantmatches['Team 1'] == Team_name) |
                                    (Valorantmatches['Team 2'] == Team_name)]
    Team_matches.to_csv(f'{Team_name}_matches.csv', index=False)
    return Team_matches

Team_matches = Valorantmatches[(Valorantmatches['Team 1'] == Team_name) | 
                                (Valorantmatches['Team 2'] == Team_name)]

Team_info = get_Team_info(Team_name, elo_ratings, Valorantmatches)
print(Team_info)
'''
import pandas as pd

# Assuming Valorantmatches DataFrame is already defined

# Team name to filter
team_name = "Bilibili Gaming"

# Stripping spaces and making the comparison case-insensitive
Valorantmatches['Team 1'] = Valorantmatches['Team 1'].str.strip().str.lower()
Valorantmatches['Team 2'] = Valorantmatches['Team 2'].str.strip().str.lower()
team_name_lower = team_name.lower()

# Filtering for matches involving Gen.G
team_matches = Valorantmatches[
    (Valorantmatches['Team 1'] == team_name_lower) | 
    (Valorantmatches['Team 2'] == team_name_lower)
]

# Selecting only relevant columns: team names and ending Elo ratings
results_with_elo = team_matches[['Team 1', 'Team 2', 'Team_1_elo_end', 'Team_2_elo_end', 'Match Winner']]

# If the match is won by Gen.G, display their ending Elo
results_with_elo['Gen.G Ending Elo'] = results_with_elo.apply(
    lambda row: row['Team_1_elo_end'] if row['Team 1'].lower() == team_name_lower else row['Team_2_elo_end'], axis=1
)

# Dropping the original Elo columns for clarity
results_with_elo = results_with_elo[['Team 1', 'Team 2', 'Gen.G Ending Elo', 'Match Winner']]

# Display the results
print(results_with_elo)

# Optionally, export the results to a CSV file
results_with_elo.to_csv('Bilibili_Gaming_results_with_elo.csv', index=False)
print("Results with ending Elo for Gen.G have been exported to 'gen_g_results_with_elo.csv'.")
