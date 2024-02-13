import pandas as pd
import time
from datetime import datetime, timedelta

teams = [
    'ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 
    'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 
    'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 
    'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO',
    'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'
    ]

column_headers = ['Date', 'H/A', 'Opp', 'W/L', 'P', 'OppP', 'FG', 'FGA', 'FG%', '3P',
       '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'TRB', 'AST', 'STL', 'BLK',
       'TOV', 'PF', 'ORtg', 'DRtg', 'Pace', 'FTr', '3PAr', 'TS%', 'TRB%',
       'AST%', 'STL%', 'BLK%', 'OeFG%', 'OTOV%', 'OORB%', 'OFT/FGA', 'DeFG%',
       'DTOV%', 'DDRB%', 'DFT/FGA']


import requests
from bs4 import BeautifulSoup

for team in teams:
    #this is so our requests dont get timed out
    print(team)
    time.sleep(5)
    
    #GET current df
    df = pd.read_csv('./data/' + team + '.csv')
    df = df.drop(df.columns[[0]],axis = 1)

    #create a new df
    new_df = pd.DataFrame(columns=column_headers)

    #get data of most recent entry in the .csv
    most_recent_date = df.iloc[df.shape[0] - 1]['Date']
    most_recent_date_object = datetime.strptime(most_recent_date, '%Y-%m-%d').date()

    #GET normal data not advanced
    URL = 'https://www.basketball-reference.com/teams/' + team + '/2024/gamelog/'
    page = requests.get(URL)
    delay = page.headers.get("Retry-After", "None")

    if delay != "None":
        d = datetime.now()
        d = d + timedelta(0, int(delay))
        print("Try again at : ")
        print(d)
        break
    
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find("table")

    table_body = table.find('tbody')

    rows = table_body.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        #make sure this column is a new column not in the dataset
        if len(cols) < 2:
            continue
        date = cols[1]
        date_object = datetime.strptime(date, '%Y-%m-%d').date()
        if date_object <= most_recent_date_object:
            continue
        
        
        #sanitize this col
        cols.pop(0)
        cols[1] = 'A' if cols[1] == '@' else 'H'
        cols.pop(22)
        cols = cols[:22]

        #add to the df
        column_head = ['Date', 'H/A', 'Opp', 'W/L', 'P', 'OppP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF']
        new_df = pd.concat([new_df,pd.DataFrame([cols], columns=column_head)])

    #GET advanced data not normal
    URL = 'https://www.basketball-reference.com/teams/' + team + '/2024/gamelog-advanced/'
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find("table")
    
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]

        #make sure this column is a new column not in the dataset
        if len(cols) < 2:
            continue
        date = cols[1]
        date_object = datetime.strptime(date, '%Y-%m-%d').date()
        if date_object <= most_recent_date_object:
            continue
        
        
        #sanitize this col
        cols.pop(0)
        cols.pop(1)
        cols.pop(1)
        cols.pop(1)
        cols.pop(13)
        cols.pop(17)
        cols.pop(1)
        cols.pop(1)
        cols.pop(0)
        
        #add to the df
        column_head = ['ORtg', 'DRtg', 'Pace', 'FTr', '3PAr', 'TS%', 'TRB%',
       'AST%', 'STL%', 'BLK%', 'OeFG%', 'OTOV%', 'OORB%', 'OFT/FGA', 'DeFG%',
       'DTOV%', 'DDRB%', 'DFT/FGA']

        #find index of date
        new_df.loc[new_df['Date'] == date, column_head] = cols

    #add new_df to df
    df = pd.concat([df, new_df])
    

    #save to .csv
    df.to_csv("./data/" + team + ".csv")


#Calculates current_team_data.csv
dataset_df = pd.DataFrame()

for team in teams:
    df = pd.read_csv('./data/' + team + '.csv')
        
    #calculate average over last 3 games
    wins_last_3 = df.iloc[-3:]['W/L'].value_counts().get('W', 0)
    home_last_3 = df.iloc[-3:]['H/A'].value_counts().get('H', 0)
    numerical_stats_last_3 = df.iloc[-3:,5:].mean().apply(lambda x: float("{:.2f}".format(x)))
    last_3 = numerical_stats_last_3
    last_3['W'] = wins_last_3
    last_3['H'] = home_last_3
    last_3.index = list(map(lambda n: "last_3_" + n, last_3.index.to_list()))
    
    #calculate average over last 10 games
    wins_last_10 = df.iloc[-10:]['W/L'].value_counts().get('W', 0)
    home_last_10 = df.iloc[-10:]['H/A'].value_counts().get('H', 0)
    numerical_stats_last_10 = df.iloc[-10:,5:].mean().apply(lambda x: float("{:.2f}".format(x)))
    last_10 = numerical_stats_last_10
    last_10['W'] = wins_last_10
    last_10['H'] = home_last_10
    last_10.index = list(map(lambda n: "last_10_" + n, last_10.index.to_list()))

    #calculate average over last 50 games
    wins_last_50 = df.iloc[-50:]['W/L'].value_counts().get('W', 0)
    home_last_50 = df.iloc[-50:]['H/A'].value_counts().get('H', 0)
    numerical_stats_last_50 = df.iloc[-50:,5:].mean().apply(lambda x: float("{:.2f}".format(x)))
    last_50 = numerical_stats_last_50
    last_50['W'] = wins_last_50
    last_50['H'] = home_last_50
    last_50.index = list(map(lambda n: "last_50_" + n, last_50.index.to_list()))
    #add all averages to one series
    stats = pd.concat([pd.Series([team], index=["Team"]),last_3, last_10, last_50])

    #add stats to the dataset
    dataset_df = pd.concat([dataset_df, stats.to_frame().T])

#save data
dataset_df.to_csv('./data/current_team_data.csv')


import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

months = ["october", "november", "december", "january", "february", "march", "april"]

team_dict = {
    "Los Angeles Lakers": "LAL",
    "Phoenix Suns": "PHO",
    "Houston Rockets": "HOU",
    "Boston Celtics": "BOS",
    "Washington Wizards": "WAS",
    "Atlanta Hawks": "ATL",
    "Detroit Pistons": "DET",
    "Minnesota Timberwolves": "MIN",
    "Cleveland Cavaliers": "CLE",
    "New Orleans Pelicans": "NOP",
    "Oklahoma City Thunder": "OKC",
    "Sacramento Kings": "SAC",
    "Dallas Mavericks": "DAL",
    "Portland Trail Blazers": "POR",
    "Philadelphia 76ers": "PHI",
    "Denver Nuggets": "DEN",
    "New York Knicks": "NYK",
    "Miami Heat": "MIA",
    "Toronto Raptors": "TOR",
    "Brooklyn Nets": "BRK",
    "Los Angeles Clippers": "LAC",
    "Orlando Magic": "ORL",
    "Golden State Warriors": "GSW",
    "Chicago Bulls": "CHI",
    "Memphis Grizzlies": "MEM",
    "Indiana Pacers": "IND",
    "Utah Jazz": "UTA",
    "San Antonio Spurs": "SAS",
    "Milwaukee Bucks": "MIL",
    "Charlotte Hornets": "CHO",
}

column_head = [
    "Date",
    "Time",
    "Home_Team",
    "Home_Pts",
    "Away_Team",
    "Away_Points",
]

df = pd.read_csv("./data/schedule.csv")
df = df.drop(df.columns[[0]],axis = 1)

for month in months:
    # this is so our requests dont get timed out
    #print(month)
    time.sleep(5)

    # GET data for the month
    URL = (
        "https://www.basketball-reference.com/leagues/NBA_2024_games-" + month + ".html"
    )
    page = requests.get(URL)
    delay = page.headers.get("Retry-After", "None")

    if delay != "None":
        d = datetime.now()
        d = d + timedelta(0, int(delay))
        print("Try again at : ")
        print(d)
        break

    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find("table")

    table_body = table.find("tbody")

    rows = table_body.find_all("tr")

    for row in rows:
        cols = [row.find("th").find("a")]
        cols += row.find_all("td")
        cols = [ele.text.strip() for ele in cols]

        # sanitize this col
        cols = cols[:6]

        #make date in dd/mm/yy
        cols[0] = datetime.strptime(cols[0], '%a, %b %d, %Y').strftime('%Y-%m-%d')
        #shorten team name to three letters
        cols[2] = team_dict[cols[2]] 
        cols[4] = team_dict[cols[4]] 

        formatted_date = datetime.strptime(cols[0], '%Y-%m-%d').strftime('%m/%d/%Y')
        day = int(formatted_date[0:2])
        month = int(formatted_date[3:5])
        year = int(formatted_date[6:])
        formatted_date = f"{month}/{day}/{year}"

        # update home and away team scores
        df.loc[(df['Date'] == formatted_date) & (df['Home_Team'] == cols[2]) & (df['Away_Team'] == cols[4]), "Home_Pts"] = cols[3]
        df.loc[(df['Date'] == formatted_date) & (df['Home_Team'] == cols[2]) & (df['Away_Team'] == cols[4]), "Away_Points"] = cols[5]

# save to .csv
df.to_csv("./data/schedule.csv")

import pickle
import pandas as pd

#function to make prediction given home team and away team
model_file = './models/naive_bayes.sav'

# load the model from disk
model = pickle.load(open(model_file, 'rb'))
current_team_df =  pd.read_csv('./data/current_team_data.csv')
current_team_df = current_team_df.drop(current_team_df.columns[[0]],axis = 1)

def predict(home_team, away_team):
    home = current_team_df.loc[current_team_df['Team'] == home_team].iloc[0,1:]
    home.index = list(map(lambda n: "home_" + n, home.index.to_list()))

    away = current_team_df.loc[current_team_df['Team'] == away_team].iloc[0,1:]

    away.index = list(map(lambda n: "away_" + n, away.index.to_list()))
    X = pd.concat([home, away])
    X = X.to_frame().T

    #put data in form for model
    y_pred = model.predict(X)[0]
    y_pred_prob = model.predict_proba(X)[0][1 if y_pred else 0]
    #print("We predict the home team " + home_team + str(" WINS" if y_pred else " LOSES") + " with an probability of " + str(round(y_pred_prob, 2)))
    return model.predict_proba(X)[0][1]

#go through current schedule
#for any game that doesn't have a score predict the winner
#save the output in a json file for website
schedule_df = pd.read_csv("./data/schedule.csv")
schedule_df = schedule_df.drop(schedule_df.columns[[0]],axis = 1)

for i in range(schedule_df.shape[0]):
    #row has no prediction
    if pd.isna(schedule_df.iloc[i].get('Home_Pts')):
        prediction = predict(schedule_df.iloc[i,2], schedule_df.iloc[i,4])
        schedule_df.iloc[i, 6]  = round(prediction, 2)
schedule_df.to_csv("./data/schedule.csv")


#convert schedule.csv to a readble javascript object for the website
import pandas as pd
from datetime import datetime
schedule_df = pd.read_csv("./data/schedule.csv")
schedule_df = schedule_df.drop(schedule_df.columns[[0]],axis = 1)

data = {}

for i in range(schedule_df.shape[0]):
    game = {}
    game["time"] = schedule_df.iloc[i, 1] if not pd.isna(schedule_df.iloc[i, 1]) else ""
    game["homeTeam"] = schedule_df.iloc[i, 2] if not pd.isna(schedule_df.iloc[i, 2]) else ""
    game["homeTeamPoints"] = schedule_df.iloc[i, 3] if not pd.isna(schedule_df.iloc[i, 3]) else ""
    game["awayTeam"] = schedule_df.iloc[i, 4] if not pd.isna(schedule_df.iloc[i, 4]) else ""
    game["awayTeamPoints"] = schedule_df.iloc[i, 5] if not pd.isna(schedule_df.iloc[i, 5]) else ""
    game["prediction"] = schedule_df.iloc[i, 6] if not pd.isna(schedule_df.iloc[i, 6]) else ""
    

    #make it a blank list if it doesn't exist
    date = schedule_df.iloc[i, 0]
    #add zero padded days and months
    date = datetime.strptime(date, '%m/%d/%Y').strftime('%m/%d/%Y')
    if data.get(date, None) != None:
        data[date].append(game)
    else:
        data[date] = [game]

with open('./docs/data.js', "w") as file:
    file.write("const data = " + str(data))
