# slack_fantasy_baseball_bot
Fantasy Baseball Bot that fetches updates on players from Rotowire.

## What is this?
This is a slack bot that fetches the latest fantasy baseball information from Rotowire, both when requested and when big news breaks.

## How does it work?
The bot currently has two functionalities:

1. Fetching player fantasy news
2. Posting fantasy updates

The first functionality can be activated by typing in "@[Bot Username] get news about [Player Name]". The bot will then return the latest fantasy update about that player from Rotowire.

![Rotowire Player Update](https://i.imgur.com/pnQj4JL.png)

The second functionality is automatic - the bot posts the latest top fantasy update from [Rotowire's top news page](https://www.rotowire.com/baseball/news.php?view=top) when it is available.

![Rotowrite Automatic Update](https://i.imgur.com/l2uffxg.png)

## How do I set it up?

1. Go [HERE](https://api.slack.com/apps?new_app=1) and set up a new bot. Set the "Development Slack Workspace" to the desired workplace.
2. Under the sidebar, go to "Bot Users", input an appropriate name for the bot (like "Fantasy Baseball Bot"). Click "save changes".
3. Under the sidebar, click on "Install App" and copy the Bot User OAuth Access Token. Then, paste it between the single quotes in the code in the line ``slack_client = SlackClient('')``
4. Get the channel ID you want messages sent to. Go to your Slack workspace with your web browser (i.e. "slackworkspace.slack.com") and then click on the channel you want it sent to. Grab the code from the end of the URL - "slackworkspace.slack.com/messages/CHANNELCODE/" - and then paste it between the single quotes in the code in the line ``Channel_id = ''``
5. (Optional) if you have emojis of team logos in your slack, set ``enable_emojis = False`` to ``enable_emojis = True`` and fill out the ``emoji_map_b`` list with the names of the emojis corresponding to the team codes in ``emoji_map_a`` list. For example, the first code in the ``emoji_map_a`` list is ``'ARI'``, so the first element in ``emoji_map_b`` should be the code for the emoji that corresponds to the Diamondbacks logo. ``emoji_map_b`` is already filled with the values for the emojis from my personal slack.
6. Start the bot and invite it to the channels where you want this functionality. Congratulations! Your bot is now online.

## This code looks familiar...

Most of the code I took from Matt Makai's [tutorial on building a Slack bot](https://www.fullstackpython.com/blog/build-first-slack-bot-python.html). This is my first slack bot, so I apologize in advance if I'm not following proper practice.

## I have a question that wasn't addressed here!

Contact me on twitter (@John_Edwards_) and I'll help you out!
