import sqlite3
from contextlib import closing

def init_db(db_path):
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        # Table to store threads with their player lists, waitlists, backups, and streamers
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threads (
                thread_id INTEGER PRIMARY KEY,
                player_list TEXT,
                waitlist TEXT,
                backups TEXT,
                streamers TEXT,
                original_content TEXT 
            )
        ''')
        conn.commit()



# Helper function to execute queries
def query_db(db_path, query, args=(), one=False):
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()  # Create the cursor outside of the `with` statement
        cursor.execute(query, args)
        conn.commit()
        rv = cursor.fetchall()
        return (rv[0] if rv else None) if one else rv

# Function to store or update the thread info in the database
def update_thread_db(db_path, thread_id, players, waitlist, backups, streamers, original_content):
    player_str = ",".join(players)
    waitlist_str = ",".join(waitlist)
    backups_str = ",".join(backups)
    streamers_str = ",".join(streamers)

    existing_thread = query_db(db_path, 'SELECT thread_id FROM threads WHERE thread_id = ?', (thread_id,), one=True)
    if existing_thread:
        query_db(db_path, 'UPDATE threads SET player_list = ?, waitlist = ?, backups = ?, streamers = ?, original_content = ? WHERE thread_id = ?', 
                  (player_str, waitlist_str, backups_str, streamers_str, original_content, thread_id))
    else:
        query_db(db_path, 'INSERT INTO threads (thread_id, player_list, waitlist, backups, streamers, original_content) VALUES (?, ?, ?, ?, ?, ?)', 
                  (thread_id, player_str, waitlist_str, backups_str, streamers_str, original_content))

# Function to retrieve thread info from the database
def get_thread_info(db_path, thread_id):
    result = query_db(db_path, 'SELECT player_list, waitlist, backups, streamers, original_content FROM threads WHERE thread_id = ?', (thread_id,), one=True)
    if result:
        players = result[0].split(',') if result[0] else []
        waitlist = result[1].split(',') if result[1] else []
        backups = result[2].split(',') if result[2] else []
        streamers = result[3].split(',') if result[3] else []
        original_content = result[4] if result[4] else ""
        return players, waitlist, backups, streamers, original_content
    return [], [], [], [], ""
