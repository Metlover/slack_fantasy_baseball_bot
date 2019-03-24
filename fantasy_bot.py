import re
import time
from slackclient import SlackClient
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

#Much of the code for this bot comes from the template here: https://www.fullstackpython.com/blog/build-first-slack-bot-python.html

slack_client = SlackClient('') #Put your bot user Oath token here. If you're confused about what that is, see the readme.
enable_emojis = True #If you enable this, you need to list in order the emojis corresponding to each team code below, as well as a free agent emoji (usually the :baseball: emoji).
channel_id = '' #Put the channel ID where you want fantasy updates posted automatically. If you're confused about what this is and where to find it, see the readme.

emoji_map_a = ['ARI','ATL','BAL','BOS','CHC','CIN','CLE','COL','CWS','DET','HOU','KC\"','LAA','LAD','MIA','MIL','MIN','NYM','NYY','OAK','PHI','PIT','SD\"','SEA','SF\"','STL','TB\"','TEX','TOR','WAS','FA\"']
#these codes should be the text that corresponds to each teams' emoji in your workspace. These are currently the ones that mine uses.
emoji_map_b = ['dbacks','atl-logo','orioles','redsox','cubs','reds','indians','rockies','whitesox','tigers','astros','royals','angels','dodgers','marlins','brewers','twins','mets','yankees','athletics','phillies','pirates','padres','sea-logo','sf-logo','cardinals','rays','rangers','bluejays','nationals','baseball']

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "get news about " #users use this command after '@'ing the bot to get it to return the latest fantasy update for a player.
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

url = 'https://www.rotowire.com/baseball/news.php?view=top' #latest fantasy baseball news from Rotowire
player_map_url = 'https://www.smartfantasybaseball.com/PLAYERIDMAPCSV' #Player ID map to directly fetch Rotowire news
roto_player_url = 'https://www.rotowire.com/baseball/player.php?id=' #Base player URL to fetch Rotowire news

#grabs player id map from smart fantasy baseball for matching names with Rotowire IDs
#You'll need to restart the bot sparsely as new players are added to the ID map, maybe once a year
data = pd.read_csv(player_map_url) #reads in playerID map - a little slow, obviously, but the issue is that
data['PLAYERNAME'] = data['PLAYERNAME'].str.lower()
data.set_index("PLAYERNAME", inplace=True)

def initial_news_list(): #grabs an initial list of news when the bot is first started
    site = requests.get(url)
    soup = BeautifulSoup(site.content,'html.parser')
    news_updates = soup.findAll("div", {"class": "news-update"})
    news_lists = []
    for item in news_updates: #iterates through items in the list and creates dictionary of news items
        newSoup = BeautifulSoup(str(item),'html.parser')
        player_name = newSoup.find("a", {"class": "news-update__player-link"}).get_text()
        team_code = str(newSoup)[str(newSoup).find("alt")+5:str(newSoup).find("alt")+8]
        time_code = newSoup.find("div", {"class": "news-update__timestamp"}).get_text()
        news = newSoup.find("div", {"class": "news-update__news"}).get_text()
        headline = newSoup.find("div", {"class": "news-update__headline"}).get_text()
        myDict = {"Name":player_name,"Team":team_code,"Date":time_code,"News":news,"Headline":headline}
        news_lists.append(myDict)
    return(news_lists)

def latest_news(): #grabs the latest piece of news from the top of the news list
    site = requests.get(url)
    soup = BeautifulSoup(site.content,'html.parser')
    latest_news_item = soup.findAll("div", {"class": "news-update"})[1]
    newSoup = BeautifulSoup(str(latest_news_item),'html.parser')
    player_name = newSoup.find("a", {"class": "news-update__player-link"}).get_text()
    team_code = str(newSoup)[str(newSoup).find("alt")+5:str(newSoup).find("alt")+8]
    time_code = newSoup.find("div", {"class": "news-update__timestamp"}).get_text()
    news = newSoup.find("div", {"class": "news-update__news"}).get_text()
    headline = newSoup.find("div", {"class": "news-update__headline"}).get_text()
    myDict = {"Name":player_name,"Team":team_code,"Date":time_code,"News":news,"Headline":headline}
    return(myDict)

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Ask me to \"*{}*\" on a player.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        player_name = command[command.find(EXAMPLE_COMMAND) + len(EXAMPLE_COMMAND):] #grabs player name
        try:
            roto_id = int(data["ROTOWIREID"].loc[player_name.lower()]) #finds location of player name in dataframe and fetches rotowire ID
            #fetches player values from rotowire
            player_url = roto_player_url + str(roto_id)
            site = requests.get(player_url)
            soup = BeautifulSoup(site.content,'html.parser')
            team_code = str(soup)[str(soup).find("href=\"/baseball/team.php?team=")+30:str(soup).find("href=\"/baseball/team.php?team=")+33]
            headline = soup.find("div", {"class": "news-update__headline"}).get_text()
            time_stamp = soup.find("div", {"class": "news-update__timestamp"}).get_text()
            news_blurb = soup.find("div", {"class": "news-update__news"}).get_text()
            player_name = soup.find("div", {"class": "p-card__player-name"}).get_text()
            #sends information to slack chat
            if(enable_emojis):
                attachment = json.dumps([{"title": player_name + ' :' + emoji_map_b[emoji_map_a.index(team_code)] + ": — " + headline,
                    "text": time_stamp + ' — ' + news_blurb,
                    "mrkdwn_in": [
                        "text",
                        "pretext"
                        ]}])
            else:
                attachment = json.dumps([{"title": player_name + ' — ' + headline,
                    "text": time_stamp + ' — ' + news_blurb,
                    "mrkdwn_in": [
                        "text",
                        "pretext"
                        ]}])
            slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                attachments=attachment
                )
        except: #if the name doesn't fit or there's some other error, this message is posted
            slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                text= "Sorry, I couldn't find anything about that player!"
            )

if __name__ == "__main__": #main function
    if slack_client.rtm_connect(with_team_state=False):
        print("Fantasy bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        news = initial_news_list()
        while True:
            try:
                latest_news_item = latest_news()
                if not any(d['News'] == latest_news_item['News'] for d in news):
                    if(enable_emojis):
                        attachment = json.dumps([{"title": latest_news_item["Name"] + ' :' + emoji_map_b[emoji_map_a.index(latest_news_item["Team"])] + ": — " + latest_news_item["Headline"],
                            "text": latest_news_item["Date"] + ' — ' + latest_news_item["News"],
                            "mrkdwn_in": [
                                "text",
                                "pretext"
                                ]}])
                    else:
                        attachment = json.dumps([{"title": latest_news_item["Name"] + ' — ' + latest_news_item["Headline"],
                            "text": latest_news_item["Date"] + ' — ' + latest_news_item["News"],
                            "mrkdwn_in": [
                                "text",
                                "pretext"
                                ]}])
                    slack_client.api_call(
                        "chat.postMessage",
                        channel=channel_id,
                        attachments=attachment
                        )
                    news.append(latest_news_item)
                command, channel = parse_bot_commands(slack_client.rtm_read())
                if command:
                    handle_command(command, channel)
                time.sleep(RTM_READ_DELAY)
            except WebSocketConnectionClosedException:
                slack_client.rtm_connect()
    else:
        print("Connection failed. Exception traceback printed above.")
