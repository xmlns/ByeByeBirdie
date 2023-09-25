# ByeByeBirdie

ByeByeBirdie is a Twitter bot that tweets or DMs a custom message to users who unfollow you. It uses Tweepy, Pyodbc, and Schedule modules to interact with the Twitter API, store the followers data in a SQL Server memory-optimized table, and run the bot periodically.

## Installation

To install ByeByeBirdie, you need to have Python 3 and pip installed on your system. You also need to have a Twitter developer account and a SQL Server database.

- Clone or download this repository to your local machine.
- Install the required modules using pip:

`pip install tweepy pyodbc schedule`

- Create a memory-optimized table in your SQL Server database with the following schema:

```sql
CREATE TABLE Followers ( screen_name VARCHAR(50) NOT NULL, user_id BIGINT NOT NULL, CONSTRAINT PK_Followers PRIMARY KEY NONCLUSTERED HASH (screen_name, user_id) WITH (BUCKET_COUNT = 1000000) ) WITH (MEMORY_OPTIMIZED = ON) ON FG_MemoryOptimized_Users
```

# Usage
To run ByeByeBirdie, simply execute the script.py file using Python:

`python script.py`

The bot will start by getting the current followers of each user who follows the bot and storing them in the memory-optimized table. It will also post a tweet to request a custom message from each user who follows the bot. The user needs to reply to the tweet with their custom message and include #byebyebirdie in their reply.

The bot will then check for unfollowers every hour and tweet or DM them with their custom message, depending on their privacy settings. The bot will also update the memory-optimized table with the new followers for each user.

# Contributing
If you want to contribute to ByeByeBirdie, feel free to fork this repository and make a pull request. You can also open an issue if you find any bugs or have any suggestions.

# License
ByeByeBirdie is licensed under the MIT License. See the LICENSE file for more details.
