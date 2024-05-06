import pandas as pd
from openai import OpenAI
import json

client = OpenAI()

csv_file = 'player_data.csv'


def reset_database():
    headers = ['Vorname', 'Nachname', 'Lieblingsdrink', 'Lieblingshobby', 'Branche']
    # Create an empty DataFrame with the specified headers
    df = pd.DataFrame(columns=headers)
    # Write this DataFrame to CSV, replacing any existing file
    df.to_csv(csv_file, index=False)
    print("Database has been reset. Current data:", df)


def add_player(vorname, nachname, lieblingsdrink, lieblingshobby, branche):
    new_player = pd.DataFrame({
        'Vorname': [vorname],
        'Nachname': [nachname],
        'Lieblingsdrink': [lieblingsdrink],
        'Lieblingshobby': [lieblingshobby],
        'Branche': [branche]
    })
    try:
        # Try to read the existing CSV file
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        # If the file does not exist, start with a new DataFrame
        df = new_player
    else:
        # Concatenate the new player data with existing DataFrame
        df = pd.concat([df, new_player], ignore_index=True)

    # Save the updated DataFrame back to the CSV file
    df.to_csv(csv_file, index=False)
    print("Player added. Current players in the database:")
    print(df)


def read_players():
    try:
        return pd.read_csv(csv_file)
    except FileNotFoundError:
        return pd.DataFrame()

def generate_teams():
    df = read_players()
    if df.empty:
        return "No players to generate teams."

    # Convert dataframe to a string list of players
    players_info = df.apply(lambda x: f"{x['Vorname']} {x['Nachname']}, likes {x['Lieblingsdrink']} and {x['Lieblingshobby']}, works in {x['Branche']}.", axis=1).tolist()
    num_players = len(players_info)
    player_descriptions = ' '.join(players_info)

    # Construct the messages for the chat API
    messages = [
        {"role": "system", "content": f"""You are a Team Matching assistant. You will create teams of minimum 3 and maximum 4 people from a list of {num_players} players.
        Make sure that the numbers match up and no one has to play alone! 
        Match the players based on their interests and background. 
        Generate a humorous or meaningful reason for why these players fit well within a team and come up with a creative team name. 
        Keep in mind that these teams will play bowling, so it might make sense to include some pun about it in combinatoin with the users attrirubtes.
        Return a JSON with the following: Team Names, Players First and Lastname, Reason for Matching. The reason should only be one sentence
        The JSON should be structured as an array of objects called teams with the ojbect per team(array) : team_name(object), players (array) first_name(key in the players object), last_name(key in the players object), matching_reason(key in the team arrray index)
        Additionally follow this very important instructions
        INSTRUCTION 1
        These are special players :
        - Marco Szeidenleder
        - Adam Butz 
        - Hannah Klenk
        It is extremely important that these players play in different Teams and are not assigned to the same team. 
        So each of them needs to be in a separate Team! They cannot share a team. THIS IS CRUCIAL!
        INSTRUCTION 2
        Each player can only play in one Team 
        INSTRUCTION 3
        Every player in the list needs to be added to a team. Don't forget anyone
        INSTRUCTION 4
        No Team can only have a single player. 
        INSTRUCTION 5
        The minimum Size of a Team is 3!! this means there must be a least three players in one team!
        Instruction 6
        The maximum Size of a Team is 4, this means there must be no more than four players in one team!
        Instruction 7
        The reason you provide needs to make sense. Try do find something all the players in this specific team have in 
        common but avoid inventing anything and never contradict the player's provided data. Try to make it sound fun and elaborated.
        FOLLOW THESE INSTRUCTION WITH HIGH ATTENTION AND DETAIL. FOLLOW EVERY STEP AND BE CAUTIOUS TO NOT MAKE ANY MISTAKES!"""},
        {"role": "user", "content": f"Here are the players: {player_descriptions}."}

    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            response_format={"type": "json_object"}
        )
        result = completion.choices[0].message
        teams_json_string = result.content
        teams = json.loads(teams_json_string)
        print(teams)
        return teams
    except Exception as e:
        return f"Failed to generate teams due to an API error: {str(e)}"



def generate_logo(team_name, reason):
    try:
        response = client.images.generate(
            prompt=f"""A team logo for '{team_name}' inspired by their spirit of {reason}. 
            It should have a modern 3d look and b funny. The sport is bowling. Don't include any text in the image """,
            n=1,
            size="256x256"
        )
        print(response)
        return response.data[0].url
    except Exception as e:
        print(f"Error generating logo: {str(e)}")
        return None
