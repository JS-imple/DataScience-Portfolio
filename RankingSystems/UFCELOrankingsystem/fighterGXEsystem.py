import numpy as np
import pandas as pd

# Load the CSV
ufcfights_not_sorted = pd.read_csv("ufcfights.csv", index_col=0)
ufcfights = ufcfights_not_sorted.reset_index()


# Sort by index in descending order
ufcfights = ufcfights.sort_index(ascending=False)

# Create unique event IDs
unique_events = ufcfights[['event']].drop_duplicates().reset_index(drop=True)
unique_events['event_id'] = range(1, len(unique_events) + 1)
ufcfights = ufcfights.merge(unique_events, on='event')

# Clean up KO and Sub methods
ufcfights['method'] = ufcfights['method'].apply(lambda x: 'KO' if 'KO' in x else ('SUB' if 'SUB' in x else x))

# Drop unnecessary columns
ufcfights.drop(columns=["round", "time"], inplace=True)

# Elo system update for the method (KO or SUB gets an adjusted K-factor)
def get_k_factor(method, base_k=40):
    if method == 'KO' or method == 'SUB':
        return base_k * 1.15  # Increase K by 15% for KO or submission
    else:
        return base_k  # Default to base K for other outcomes

# Initialize Elo ratings and other configurations
initial_elo = 1000
elo_ratings = {}
base_k_factor = 40
peak_elo_ratings = {}

# Function to calculate the expected score in the Elo system
def expected_score(elo_a, elo_b):
    return 1 / (1 + 10**((elo_b - elo_a) / 400))

# Function to update Elo ratings based on the result
def update_elo(winner_elo, loser_elo, k_factor):
    expected_win = expected_score(winner_elo, loser_elo)
    new_winner_elo = winner_elo + k_factor * (1 - expected_win)
    new_loser_elo = loser_elo + k_factor * (0 - (1 - expected_win))
    return round(new_winner_elo, 2), round(new_loser_elo, 2)

# Create unique match IDs for tracking
ufcfights['cc_match'] = np.arange(1, len(ufcfights) + 1)

# Add columns for Elo ratings
ufcfights['fighter_1_elo_start'] = 0
ufcfights['fighter_2_elo_start'] = 0
ufcfights['fighter_1_elo_end'] = 0
ufcfights['fighter_2_elo_end'] = 0

# Calculate Elo ratings for each match
for index, row in ufcfights.iterrows():
    fighter_1 = row['fighter_1']
    fighter_2 = row['fighter_2']

    # Initialize Elo ratings if the fighters are encountered for the first time
    if fighter_1 not in elo_ratings:
        elo_ratings[fighter_1] = initial_elo
    if fighter_2 not in elo_ratings:
        elo_ratings[fighter_2] = initial_elo

    # Get starting Elo ratings
    fighter_1_elo_start = elo_ratings[fighter_1]
    fighter_2_elo_start = elo_ratings[fighter_2]

    # Adjust the K-factor based on the fight method
    fight_method = row["method"]
    current_k = get_k_factor(fight_method, base_k_factor)

    # Record starting Elo ratings
    ufcfights.at[index, 'fighter_1_elo_start'] = fighter_1_elo_start
    ufcfights.at[index, 'fighter_2_elo_start'] = fighter_2_elo_start

    # Update Elo ratings based on the result
    if row['result'] == 'win':  # Fighter 1 wins
        new_fighter1_elo, new_fighter2_elo = update_elo(fighter_1_elo_start, fighter_2_elo_start, current_k)
    elif row["result"] == 'draw':  # Draw
        new_fighter1_elo, new_fighter2_elo = update_elo(fighter_1_elo_start, fighter_2_elo_start, current_k / 2)
    else:  # No contest
        new_fighter1_elo, new_fighter2_elo = fighter_1_elo_start, fighter_2_elo_start

    # Update peak Elo ratings if necessary
    if fighter_1 not in peak_elo_ratings or new_fighter1_elo > peak_elo_ratings[fighter_1]:
        peak_elo_ratings[fighter_1] = new_fighter1_elo
    if fighter_2 not in peak_elo_ratings or new_fighter2_elo > peak_elo_ratings[fighter_2]:
        peak_elo_ratings[fighter_2] = new_fighter2_elo

    # Record updated Elo ratings
    ufcfights.at[index, 'fighter_1_elo_end'] = new_fighter1_elo
    ufcfights.at[index, 'fighter_2_elo_end'] = new_fighter2_elo

    # Update Elo ratings in the dictionary
    elo_ratings[fighter_1] = new_fighter1_elo
    elo_ratings[fighter_2] = new_fighter2_elo

# Function to retrieve fighter information and Elo history
def get_fighter_info(fighter_name, elo_ratings, ufcfights, initial_elo=1000):
    # Check if the fighter exists in the Elo ratings dictionary
    if fighter_name in elo_ratings:
        elo = elo_ratings[fighter_name]
    else:
        elo = initial_elo

    # Find all matches where the fighter appeared as either fighter_1 or fighter_2
    fighter_matches = ufcfights[(ufcfights['fighter_1'] == fighter_name) | 
                                (ufcfights['fighter_2'] == fighter_name)]
    
    # Return Elo rating and their matches
    if not fighter_matches.empty:
        print(f"{fighter_name}'s current Elo rating: {elo}\n")
        print(f"{fighter_name}'s matches:")
        return fighter_matches[['event', 'fighter_1', 'fighter_2', 'result', 
                                'fighter_1_elo_start', 'fighter_2_elo_start',
                                'fighter_1_elo_end', 'fighter_2_elo_end']]
    else:
        return f"{fighter_name} has no recorded matches."

# Sort and save the current Elo ratings to a CSV file
all_fighters = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)
all_fighters_df = pd.DataFrame(all_fighters, columns=['Fighter', 'Elo Rating'])
all_fighters_df.to_csv('k_factor_adjust_current.csv', index=False)

# Sort and save the peak Elo ratings to a CSV file
peak_elo = sorted(peak_elo_ratings.items(), key=lambda x: x[1], reverse=True)
peak_elo_df = pd.DataFrame(peak_elo, columns=['Fighter', 'Peak Elo'])
peak_elo_df.to_csv('peak_elo.csv', index=False)
