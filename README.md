**YouTube Channel Analytics**
        YouTube Channel Analytics is a Python application that allows users to fetch data from YouTube channels using the YouTube Data API, store it in a MySQL database, and perform various analytics queries on the data.

**Features**:
1. Fetch YouTube channel data including subscriber count, total video count, playlists, and video statistics.
2. Store fetched data in a MySQL database.
3. Execute predefined SQL queries to analyze the stored data.
4. Search for specific channel details in the database.
   
**Prerequisites**
    Before running the application, make sure you have the following installed:
                                      1.Python 3.x
                                      2.MySQL server
                                      3.Required Python packages listed in requirements.txt
**Installation**
  **Clone the repository:**
        git clone https://github.com/umaseenu25/YouTube-Channel-Analytics.git
        cd YouTube-Channel-Analytics
**Install dependencies:**
        pip install -r requirements.txt
**Set up MySQL database:**
          1.Create a MySQL database named test.
          2.Update the database connection details in the code if necessary (connect_to_database() function).
**Obtain a YouTube Data API key:**
          1.Go to the Google Developers Console.
          2.Create a new project.
          3.Enable the YouTube Data API v3 for the project.
          4.Generate an API key and replace api_key variable in the code with your API key.
**Usage**
**Run the application:**
          1.streamlit run app.py
          2.Enter a YouTube channel ID and click "Fetch and Store Data" to fetch data for a single channel.
          3.Alternatively, enter multiple YouTube channel IDs separated by commas (up to 10) and click "Data fetch and store" to fetch data for multiple channels.
          4.Use the "Select Query" dropdown to choose from predefined SQL queries, then click "Execute Query" to perform analytics on the stored data.
          5.Enter a search query in the "Search for Channel Details" field and click "Search" to search for specific channel details in the database.
**Contributing**
          Contributions are welcome! Feel free to open issues or pull requests for any improvements or new features.
**License**
This project is licensed under the MIT License - see the LICENSE file for details.
