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

# Define a default message to use when someone unfollows
default_message = "Hey, I noticed you unfollowed me. Was it something I said?"

# A connection string to connect to SQL Server and use a memory-optimized table
conn_str = "Driver={ODBC Driver 18 for SQL Server};Server=your_server;Database=your_database;Trusted_Connection=yes;"

# Define a function to check for unfollowers and tweet or DM them with the default message
def check_unfollowers():
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
        # Select the user_id from the memory-optimized table for the user
        cursor.execute("SELECT user_id FROM Followers WHERE screen_name = ?", screen_name)
        # Fetch all records and convert them into a set of integers
        previous_followers = set(int(row[0]) for row in cursor.fetchall())
        # Find the difference between the previous and current followers, which are the unfollowers
        unfollowers = previous_followers - current_followers
        # Loop through the unfollowers and tweet or DM them with the default message
        for user_id in unfollowers:
            try:
                # Get the user object by id
                unfollower = api.get_user(user_id)
                # Get their screen name
                unfollower_screen_name = unfollower.screen_name
                # Check if they have protected their tweets
                if unfollower.protected:
                    # If yes, send them a direct message
                    api.send_direct_message(user_id, default_message)
                    # Log the action
                    logging.info(f"Sent a DM to @{unfollower_screen_name} with the message: {default_message}")
                else:
                    # If no, tweet at them
                    api.update_status(f"@{unfollower_screen_name} {default_message}")
                    # Log the action
                    logging.info(f"Tweeted at @{unfollower_screen_name} with the message: {default_message}")
            except tweepy.TweepError as e:
                # Handle any errors
                logging.error(e)
        # Delete all records from the memory-optimized table for the user
        cursor.execute("DELETE FROM Followers WHERE screen_name = ?", screen_name)
        # Insert the current followers into the memory-optimized table for the user
        for user_id in current_followers:
            cursor.execute("INSERT INTO Followers (screen_name, user_id) VALUES (?, ?)", screen_name, user_id)
        # Commit the changes and close the connection
        conn.commit()
        conn.close()

# Schedule the function to run periodically
schedule.every().hour.do(check_unfollowers)

# Run the function once at the start
check_unfollowers()

# Keep the program running
while True:
    schedule.run_pending()
    time.sleep(1)
