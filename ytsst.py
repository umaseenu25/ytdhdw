import mysql.connector
import streamlit as st
import googleapiclient.discovery

# Function to establish a database connection
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="test"
    )

# YouTube API Key
api_key = 'AIzaSyABWb0ja4EjMjPPSOXJaVnOTNCbyUvFGvw'

#channel_id
channel_id = 'UC7ekJbGft4swD_3fb7MiRPw'

# Function to fetch YouTube data
def fetch_youtube_data(api_key, channel_id):
    
    youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)

    # Fetch channel data
    try:
        channel_response = youtube.channels().list(id=channel_id, part="snippet,statistics").execute()
        channel_name = channel_response["items"][0]["snippet"]["title"]
        subscription_count = channel_response["items"][0]["statistics"]["subscriberCount"]
        total_video_count = channel_response["items"][0]["statistics"]["videoCount"]
    except Exception as e:
        st.error(f"Failed to fetch YouTube data: {str(e)}")
        return None

    # Fetch playlist data
    playlist_response = youtube.playlists().list(part="snippet", channelId=channel_id, maxResults=50).execute()

    # Store channel data
    channel_data = {
        "channel_name": channel_name,
        "subscriber_count": subscription_count,
        "total_video_count": total_video_count,
        "playlists": []
    }

    # Iterate over playlists to fetch video data
    for playlist_item in playlist_response["items"]:
        playlist_id = playlist_item["id"]
        playlist_name = playlist_item["snippet"]["title"]

        # Fetch videos in the playlist
        playlist_videos_response = youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=50).execute()

        playlist_data = {
            "playlist_id": playlist_id,
            "playlist_name": playlist_name,
            "videos": []
        }

        # Iterate over videos in the playlist
        if "items" in playlist_videos_response:
            for video_item in playlist_videos_response["items"]:
                video_id = video_item["snippet"]["resourceId"]["videoId"]
                video_title = video_item["snippet"]["title"]
                video_stats_response = youtube.videos().list(part="statistics", id=video_id).execute()
        
                # Check if there are items in the response
                if "items" in video_stats_response:
                    video_stats = video_stats_response["items"][0]["statistics"]
                    likes = int(video_stats.get("likeCount", 0))
                    dislikes = int(video_stats.get("dislikeCount", 0))
                    comments = int(video_stats.get("commentCount", 0))
                else:
                    # Handle the case where no statistics are available for the video
                    likes = 0
                    dislikes = 0
                    comments = 0

                video_data = {
                    "video_id": video_id,
                    "video_title": video_title,
                    "likes": likes,
                    "dislikes": dislikes,
                    "comments": comments
                }

                playlist_data["videos"].append(video_data)
                
        channel_data["playlists"].append(playlist_data)

    return channel_data

# Function to create tables in SQL database
def create_tables(db_cursor):
    db_cursor.execute("""CREATE TABLE IF NOT EXISTS test.channels (
        id INT AUTO_INCREMENT PRIMARY KEY,
        channel_name VARCHAR(255),
        subscriber_count INT,
        total_video_count INT
    )""")

    db_cursor.execute("""CREATE TABLE IF NOT EXISTS test.playlists (
        id INT AUTO_INCREMENT PRIMARY KEY,
        channel_id INT,
        playlist_id VARCHAR(255),
        playlist_name VARCHAR(255),
        FOREIGN KEY (channel_id) REFERENCES channels(id)
    )""")

    db_cursor.execute("""CREATE TABLE IF NOT EXISTS test.videos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        playlist_id INT,
        video_id VARCHAR(255),
        video_title VARCHAR(255),
        likes INT,
        dislikes INT,
        comments INT,
        FOREIGN KEY (playlist_id) REFERENCES playlists(id)
    )""")

# Function to store data in SQL database
def store_data_in_database(data, db_cursor):
    try:
        channel_sql = "INSERT INTO test.channels (channel_name, subscriber_count, total_video_count) VALUES (%s, %s, %s)"
        channel_values = (data["channel_name"], data["subscriber_count"], data["total_video_count"])
        db_cursor.execute(channel_sql, channel_values)
        channel_id = db_cursor.lastrowid
        st.success("Data stored successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error storing data in database: {err}")


    for playlist_data in data["playlists"]:
        playlist_sql = "INSERT INTO test.playlists (channel_id, playlist_id, playlist_name) VALUES (%s, %s, %s)"
        playlist_values = (channel_id, playlist_data["playlist_id"], playlist_data["playlist_name"])
        db_cursor.execute(playlist_sql, playlist_values)
        playlist_id = db_cursor.lastrowid

        for video_data in playlist_data["videos"]:
            video_sql = "INSERT INTO test.videos (playlist_id, video_id, video_title, likes, dislikes, comments) VALUES (%s, %s, %s, %s, %s, %s)"
            video_values = (playlist_id, video_data["video_id"], video_data["video_title"], video_data["likes"], video_data["dislikes"], video_data["comments"])
            db_cursor.execute(video_sql, video_values)

# Function to search and retrieve data from SQL database
def search_database(query, db_cursor):
    sql = "SELECT * FROM test.channels WHERE channel_name LIKE %s"
    db_cursor.execute(sql, ('%' + query + '%',))
    channel_results = db_cursor.fetchall()

    sql = "SELECT * FROM test.playlists WHERE playlist_name LIKE %s"
    db_cursor.execute(sql, ('%' + query + '%',))
    playlist_results = db_cursor.fetchall()

    sql = "SELECT * FROM test.videos WHERE video_title LIKE %s"
    db_cursor.execute(sql, ('%' + query + '%',))
    video_results = db_cursor.fetchall()

    return channel_results, playlist_results, video_results

# Function to execute SQL queries and return results
def execute_query(query, db_cursor):
    try:
        db_cursor.execute(query)
        return db_cursor.fetchall()
    except mysql.connector.Error as err:
        st.error(f"Error executing SQL query: {err}")
        return None
    
# Streamlit UI
st.title(":red[YouTube Channel Analytics]")

st.subheader("Query Section")

# Database connection
conn = connect_to_database()
cursor = conn.cursor()

# Queries
queries = {
    "Names of all videos and their corresponding channels": """
        SELECT v.video_title, c.channel_name
        FROM test.videos AS v
        JOIN test.playlists AS p ON v.playlist_id = p.id
        JOIN test.channels AS c ON p.channel_id = c.id
    """,
    "Channels with the most number of videos": """
        SELECT c.channel_name, COUNT(v.video_id) AS video_count
        FROM test.channels AS c
        JOIN test.playlists AS p ON c.id = p.channel_id
        JOIN test.videos AS v ON p.id = v.playlist_id
        GROUP BY c.channel_name
        ORDER BY video_count DESC
        LIMIT 1
    """,
    "Top 10 most viewed videos and their respective channels": """
        SELECT v.video_title, c.channel_name, v.likes + v.dislikes AS views
        FROM test.videos AS v
        JOIN test.playlists AS p ON v.playlist_id = p.id
        JOIN test.channels AS c ON p.channel_id = c.id
        ORDER BY views DESC
        LIMIT 10
    """,
    "Number of comments on each video and their corresponding video names": """
        SELECT v.video_title, v.comments
        FROM test.videos AS v
    """,
    "Videos with the highest number of likes and their corresponding channel names": """
        SELECT v.video_title, c.channel_name, v.likes
        FROM test.videos AS v
        JOIN test.playlists AS p ON v.playlist_id = p.id
        JOIN test.channels AS c ON p.channel_id = c.id
        ORDER BY v.likes DESC
        LIMIT 1
    """,
    "Total number of likes and dislikes for each video and their corresponding video names": """
        SELECT v.video_title, v.likes, v.dislikes
        FROM test.videos AS v
    """,
    "Total number of views for each channel and their corresponding channel names": """
        SELECT c.channel_name, SUM(v.likes + v.dislikes) AS total_views
        FROM test.channels AS c
        JOIN test.playlists AS p ON c.id = p.channel_id
        JOIN test.videos AS v ON p.id = v.playlist_id
        GROUP BY c.channel_name
    """,
    "Names of all channels that published videos in 2022": """
        SELECT DISTINCT c.channel_name
        FROM test.channels AS c
        JOIN test.playlists AS p ON c.id = p.channel_id
        JOIN test.videos AS v ON p.id = v.playlist_id
        WHERE YEAR(v.published_at) = 2022
    """,
    "Average duration of all videos in each channel": """
        SELECT c.channel_name, AVG(v.duration) AS avg_duration
        FROM test.channels AS c
        JOIN test.playlists AS p ON c.id = p.channel_id
        JOIN test.videos AS v ON p.id = v.playlist_id
        GROUP BY c.channel_name
    """,
    "Videos with the highest number of comments and their corresponding channel names": """
        SELECT v.video_title, c.channel_name, v.comments
        FROM test.videos AS v
        JOIN test.playlists AS p ON v.playlist_id = p.id
        JOIN test.channels AS c ON p.channel_id = c.id
        ORDER BY v.comments DESC
        LIMIT 1
    """
}

# Display query options
selected_query = st.selectbox("Select Query", list(queries.keys()))

if st.button("Execute Query"):
    query_result = execute_query(queries[selected_query], cursor)
    st.table(query_result)

# Close cursor and connection
conn.commit()

# Fetch and Store Data Section
st.subheader("Fetch and Store YouTube Data")

channel_id = st.text_input("Enter YouTube Channel ID")

if st.button("Fetch and Store Data"):
    conn = connect_to_database()
    cursor = conn.cursor()
    youtube_data = fetch_youtube_data(api_key, channel_id)
    if youtube_data:
        store_data_in_database(youtube_data, cursor)
    conn.commit()

# Fetch and Store Data Section
st.subheader("Fetch and Store 10 YouTube Channel Data")

# Collect data for up to 10 different YouTube channels
channel_ids = st.text_area("Enter YouTube Channel IDs (up to 10, separated by commas)")

if st.button("Data fetch and store"):
    conn = connect_to_database()
    cursor = conn.cursor()

    channel_ids_list = channel_ids.split(",")
    for channel_id in channel_ids_list[:10]:  # Limit to 10 channels
        youtube_data = fetch_youtube_data(api_key, channel_id.strip())
        store_data_in_database(youtube_data, cursor)

    conn.commit()

# Search Database Section
st.subheader("Search Database")

search_query = st.text_input("Search for Channel Details")

if st.button("Search"):
    conn = connect_to_database()
    cursor = conn.cursor()
    channel_results, playlist_results, video_results = search_database(search_query, cursor)
    st.write("Channel Results:")
    st.write(channel_results)
    st.write("Playlist Results:")
    st.write(playlist_results)
    st.write("Video Results:")
    st.write(video_results)
    conn.commit()

cursor.close()
conn.close()
