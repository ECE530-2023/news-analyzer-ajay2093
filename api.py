from typing import Dict, List
import sqlite3
import feedparser



class FileUploader:
    def __init__(self):
        # Connect to the SQLite database
        self.conn = sqlite3.connect('file_data.db')
        
        # Create a table to store information about the uploaded files
        self.conn.execute('''CREATE TABLE IF NOT EXISTS uploaded_files
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             file_name TEXT NOT NULL,
                             file_location TEXT NOT NULL,
                             access_control TEXT,
                             file_size INTEGER NOT NULL,
                             upload_date TEXT NOT NULL)''')
        self.conn.commit()

    def upload_file(self, file_contents: bytes, file_name: str, file_location: str, access_control: Dict[str, List[str]]) -> str:
        """
        Upload a file to the server
        """
        extension = file_name.split()
        if extension[-1] == "txt":
            # Insert the file information into the database
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO uploaded_files (file_name, file_location, access_control, file_size, upload_date) VALUES (?, ?, ?, ?, ?)", (file_name, file_location, str(access_control), len(file_contents), str(datetime.now())))
            self.conn.commit()

            return "File uploaded Successfully"
        else:
            return "This file format is not supported"
    
    def retrieve_file(self, file_name: str, file_location: str, user_id: str) -> bytes:
        """
        Retrieve a file from the server
        """
        pass
    
    def delete_file(self, file_name: str, file_location: str, user_id: str) -> None:
        """
        Delete a file from the server
        """
        pass

class TextNLP:
    
    def analyze_text(self, text: str, type:str) -> Dict[str, any]:
        if text:
            if type in ["sen","ner"]:
                return {
                    "sentiment": {"polarity": 0.7, "positive": 0.6, "negative": 0.4},
                    "topics": ["politics", "activism", "health"],
                    "entities": {"New Delhi": "CITY", "Narendra Modi": "PERSON"}
                }
        else:
            return "Invalid input"

    def get_results(self, name: str):
        """
        Retrieve results
        """
        return {
    "language": "en",
    "sentences": [
        {
        "text": {
            "content": "Enjoy your vacation!",
            "beginOffset": 0
        },
        "sentiment": {
            "magnitude": 0.8,
            "score": 0.8
        }
        }
    ]
    }

class NewsFeedAPI:
    
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_articles_table()
   

    def create_news_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS feed_data
                     (title TEXT, link TEXT, published TEXT)''')
        
    
    def ingest_feed(self, feed_url):
        # TODO: Retrieve the feed from the given URL,
        # parse the feed data, and store the results
        # in a database for later retrieval
        if(not feed_url):
            return "Invalid request"
        
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            title = entry.title
            link = entry.link
            published = entry.published
            self.cursor.execute("INSERT INTO feed_data VALUES (?, ?, ?)", (title, link, published))

    def retrieve_feed(self, start_date, end_date):
        # TODO: Retrieve all feed items from the database
        # that fall within the given date range, and return
        # them in a structured format
        if not start_date:
            return "Empty Date"
        
        cursor = self.conn.execute("SELECT title, link, published FROM feed_data WHERE published BETWEEN ? AND ?", (start_date, end_date))
        rows = self.cursor.fetchall()

        self.conn.close()

        results = []
        for row in rows:
            result = {"title": row[0], "link": row[1], "published": row[2]}
            results.append(result)

        return results