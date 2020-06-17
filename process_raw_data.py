import json
import os

def get_sleeper_data(username):
    '''
    Gets the rosters and player info for the given user's league and place
    data into json files located in the working directory
    '''
    # Get user data to get the user id
    os.system('wget -q -O {0}.json "https://api.sleeper.app/v1/user/{0}"'.format(username))
    
    # Extract user id from user info to get the league id
    user_id = ''
    with open(username + '.json') as fp:
        user_data = json.load(fp)
        user_id = user_data['user_id']
    
    # Gets all of user's leagues for their ids
    os.system('wget -q -O 2020.json "https://api.sleeper.app/v1/user/{0}/leagues/nfl/2020"'.format(user_id))
    
    # Extract the first league id for rosters
    league_id = ''
    with open('2020.json') as fp:
        league_data = json.load(fp)
        league_id = league_data[0]['league_id']
    
    # Gets the rosters for the given league id
    os.system('wget -q -O rosters.json "https://api.sleeper.app/v1/league/{0}/rosters"'.format(league_id))
    
    # Gets the user in the given league
    os.system('wget -q -O users.json "https://api.sleeper.app/v1/league/{0}/users"'.format(league_id))
    
    # Gets the matchups for each week for the given league
    # Regular season goes from week 1 to 13
    for week in range(1,14):
        os.system('wget -q -O week{0}.json "https://api.sleeper.app/v1/league/{1}/matchups/{0}"'.format(week,league_id))
    
    # Gets player data and id for all of the nfl
    os.system('wget -q -O nfl.json "https://api.sleeper.app/v1/players/nfl"')
        
def create_team_data():
    # Import the leaugue and player data into a dictionary
    league_info = {}
    with open("2020.json", 'r') as fp:
        league_info = json.load(fp)
    players = {}
    with open("nfl.json", 'r') as fp:
        players = json.load(fp)
    users = {}
    with open("users.json", 'r') as fp:
        users = json.load(fp)
    rosters = {}
    with open("rosters.json", 'r') as fp:
        rosters = json.load(fp)
    schedule = {}
    for week in range(1,14):
        with open("week{}.json".format(week), 'r') as fp:
            schedule[week] = json.load(fp)
       
    # Get the number of league members
    num_members = league_info[0]['total_rosters']
    
    member_data = {}
    for i in range(num_members):
        # Get the name of the team
        display_name = users[i]['display_name']
        # Get the sleeper id of the team
        user_id = users[i]['user_id']
        # Get the numberical roster data and id for the team
        roster_list = []
        roster_id = 0
        for roster in rosters:
            if roster['owner_id'] == user_id:
                roster_list = roster['players']
                roster_id = roster['roster_id']
        # Add the names for the roster
        roster_data = {}
        for player in roster_list:
            # Assign the names to players or team acronym for defenses
            if player.isdigit():
                player_name  = players[player]['full_name']
            else:
                player_name = player
            roster_data[player_name] = players[player]
        # Get the weekly matchups
        weeks = {}
        matchup_ids = {}
        for week in range(1,14):
            for team in schedule[week]:
                if team['roster_id'] == roster_id:
                    weeks[week] = team
                    matchup_ids[week] = team['matchup_id']
        # Assign the data to a new dictionary
        member_data[user_id] = {}
        member_data[user_id]['name'] = display_name
        member_data[user_id]['roster_id'] = roster_id
        member_data[user_id]['roster'] = roster_data
        member_data[user_id]['weeks'] = weeks
        member_data[user_id]['matchup_ids'] = matchup_ids

    # Make a weekly matchup dictionary based on user ids
    schedule = {}
    for user_id, user_data in member_data.items():
        for week, week_matchup_id in user_data['matchup_ids'].items():
            # Find the opponent
            for oppnt_user_id, oppnt_user_data in member_data.items():
                if (oppnt_user_data['matchup_ids'][week] == week_matchup_id) and \
                (user_id != oppnt_user_id):
                    schedule[week] = oppnt_user_id
        # Assign the weekly schedule to the member dictionary
        member_data[user_id]['schedule'] = schedule

    with open('team_data.json', 'w') as f:
        json.dump(member_data, f)


#%%
if __name__ == '__main__':
    username = 'SteveBush'
    # If new data required. Get it from sleeper
    if not os.path.exists(username + '.json'):
        get_sleeper_data('SteveBush')

    # Place all of the retrieved data into a usable format
    create_team_data()