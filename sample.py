import tweepy
import time
import schedule
import pyodbc

# Your app's API/consumer key and secret can be found under the Consumer Keys
# section of the Keys and Tokens tab of your app, under the
# Twitter Developer Portal Projects & Apps page at
# 1
consumer_key = ""
consumer_secret = ""

# Your account's (the app owner's account's) access token and secret for your
# app can be found under the Authentication Tokens section of the
# Keys and Tokens tab of your app, under the
# Twitter Developer Portal Projects & Apps page at
# 1
access_token = ""
access_token_secret = ""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# The screen name of the account to track unfollowers
screen_name = "byebye_birdie"

# A set to store the current followers of the account
current_followers = set()

# A connection string to connect to SQL Server and use a memory-optimized table
conn_str = "Driver={SQL Server};Server=your_server;Database=your_database;Trusted_Connection=yes;"

# A function to get the followers of the account and update the set and the table
def get_followers():
    global current_followers
    # Use the Cursor object to iterate through followers
    current_followers = set(tweepy.Cursor(api.followers_ids, screen_name=screen_name).items())
    # Connect to SQL Server using pyodbc
    conn = pyodbc.connect(conn_str)
    # Create a cursor object to execute queries
    cursor = conn.cursor()
    # Delete all records from the memory-optimized table
    cursor.execute("DELETE FROM Followers")
    # Insert the current followers into the memory-optimized table
    for user_id in current_followers:
        cursor.execute("INSERT INTO Followers (user_id) VALUES (?)", user_id)
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# A function to check if there are any unfollowers and tweet or DM them
def check_unfollowers():
    global current_followers
    # Get the previous followers from the set
    previous_followers = current_followers.copy()
    # Get the current followers and update the set and the table
    get_followers()
    # Find the difference between the previous and current followers
    unfollowers = previous_followers - current_followers
    # If there are any unfollowers, tweet or DM them with a message
    if unfollowers:
        # Compose a tweet or a DM with a summary of the unfollowers 
        message = f"Bye bye {len(unfollowers)} accounts. You just unfollowed @{screen_name}. You will be missed. Not."
        # Check if the user prefers to tweet or DM the message 
        if tweet_preference:
            # Post the tweet 
            api.update_status(message)
        else:
            # Send the DM to the user 
            api.send_direct_message(screen_name, message)
        # Print the message for debugging purposes 
        print(message)

# Call the get_followers function for the first time to initialize the set and the table 
get_followers()

# Schedule the check_unfollowers function to run every day at noon using schedule 
schedule.every().day.at("12:00").do(check_unfollowers)

# Run pending scheduled jobs using a while loop and time.sleep() 
while True:
    schedule.run_pending()
    time.sleep(60)
