import tweepy
import time
import schedule
import pyodbc
import logging

# Configure logging to write to a file named "unfollowers.log"
logging.basicConfig(filename="C:\\Users\\amogh\\Desktop\\byebyebirdie.log'", level=logging.INFO, format="%(asctime)s %(message)s")

# Authenticate to Twitter
auth = tweepy.OAuthHandler("CONSUMER_KEY", "CONSUMER_SECRET")
auth.set_access_token("ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")

# Create API object
api = tweepy.API(auth)

# Get the screen name of the bot account
bot_screen_name = api.me().screen_name

# Create a dictionary to store the followers of each user who follows the bot
followers_dict = {}

# Create a dictionary to store the custom messages for each user who follows the bot
messages_dict = {}

# Define a hashtag to use for getting the user's input
hashtag = "#byebyebirdie"

# A connection string to connect to SQL Server and use a memory-optimized table
conn_str = "Driver={ODBC Driver 18 for SQL Server};Server=your_server;Database=your_database;Trusted_Connection=yes;"

# Define a function to get the followers of each user who follows the bot and update the dictionary and the table
def get_followers():
    global followers_dict, messages_dict
    # Loop through the users who follow the bot
    for user in tweepy.Cursor(api.followers, screen_name=bot_screen_name).items():
        # Get the screen name of the user
        screen_name = user.screen_name
        # Get the current followers of the user
        current_followers = set(api.friends_ids(screen_name))
        # Connect to SQL Server using pyodbc
        conn = pyodbc.connect(conn_str)
        # Create a cursor object to execute queries
        cursor = conn.cursor()
        # Delete all records from the memory-optimized table for the user
        cursor.execute("DELETE FROM Followers WHERE screen_name = ?", screen_name)
        # Insert the current followers into the memory-optimized table for the user
        for user_id in current_followers:
            cursor.execute("INSERT INTO Followers (screen_name, user_id) VALUES (?, ?)", screen_name, user_id)
        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        # Update the dictionary with the current followers for the user
        followers_dict[screen_name] = current_followers
        # Check if the user has already provided a custom message 
        if screen_name not in messages_dict:
            # If not, post a tweet to request a custom message 
            tweet = api.update_status(f"Hello @{screen_name}, thank you for following @{bot_screen_name}. Please reply to this tweet with your custom message that you want me to use when someone unfollows you, and include {hashtag} in your reply.")
            # Get the tweet ID 
            tweet_id = tweet.id
            # Wait for the user's reply 
            reply = None
            while not reply:
                # Check if there is any new reply to the tweet 
                for status in tweepy.Cursor(api.search, q=f"to:{bot_screen_name} {hashtag}", since_id=tweet_id).items():
                    if status.in_reply_to_status_id == tweet_id:
                        # Get the text of the reply 
                        reply = status.text
                        break
                # Wait for 10 seconds before checking again 
                time.sleep(10)
            # Store the custom message in the dictionary 
            messages_dict[screen_name] = reply

# Define a function to check for unfollowers and tweet or DM them with their custom message
def check_unfollowers():
    global followers_dict, messages_dict
    # Loop through the users who follow the bot
    for user in tweepy.Cursor(api.followers, screen_name=bot_screen_name).items():
        # Get the screen name of the user
        screen_name = user.screen_name
        # Get the previous followers of the user from the dictionary
        previous_followers = followers_dict[screen_name]
        # Get the current followers of the user and update the dictionary and the table
        current_followers = set(api.friends_ids(screen_name))
        # Find the difference between the previous and current followers
        unfollowers = previous_followers - current_followers
        # Update the dictionary with the current followers for the user
        followers_dict[screen_name] = current_followers
        # If there are any unfollowers, tweet or DM them with their custom message and log it to a file 
        if unfollowers:
            # Get the custom message from the dictionary 
            message = messages_dict[screen_name]
            # Check if the user prefers to tweet or DM their message 
            if tweet_preference:
                # Post their tweet 
                api.update_status(message)
            else:
                # Send their DM to them 
                api.send_direct_message(screen_name, message)
            # Log their message to a file 
            logging.info(message)

# Call the get_followers function for the first time to initialize the dictionary and the table 
get_followers()

# Schedule the check_unfollowers function to run every day at noon using schedule 
schedule.every().day.at("12:00").do(check_unfollowers)

# Run pending scheduled jobs using a while loop and time.sleep() 
while True:
    schedule.run_pending()
    time.sleep(60)
