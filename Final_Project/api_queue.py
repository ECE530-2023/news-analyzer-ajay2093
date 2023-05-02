from typing import Dict, List, Any, Union
import sqlite3
import feedparser
import sqlite3
import threading
import queue
import os
import google.oauth2.credentials
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from textblob import TextBlob
import nltk
import spacy
import json

nlp = spacy.load("en_core_web_sm")
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('brown')


class FileUploader:
    def __init__(self, db_path):
        self.uploaded_files = []
        self.access_controls = {}
        self.conn = sqlite3.connect(db_path)
        self.pdf_analysis_queue = queue.Queue()
        self.nlp_analysis_queue = queue.Queue()

        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uploaded_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_controls (
                file_id INTEGER NOT NULL,
                permission TEXT NOT NULL,
                PRIMARY KEY (file_id, permission),
                FOREIGN KEY (file_id) REFERENCES uploaded_files (id)
            )
        """)

        self.conn.commit()
	
    def authenticate(self):
        credentials = self.get_credentials()
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json',
                    ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/drive.file'])
                credentials = flow.run_local_server(port=0)
            self.set_credentials(credentials)
        return credentials
    
    def get_credentials(self):
        if os.path.exists('token.json'):
            with open('token.json', 'r') as token:
                return Credentials.from_authorized_user_info(json.load(token))
        else:
            return None


    def upload_file(self, file):
        if not file:
            return {"error": "No file uploaded."}, 400

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO uploaded_files (filename) VALUES (?)", (file,))
        self.conn.commit()

        file_id = cursor.lastrowid
        self.uploaded_files.append({"id": file_id, "filename": file})
        self.pdf_analysis_queue.put(file_id)
        self.nlp_analysis_queue.put(file_id)
        return {"message": "File uploaded successfully."}, 200

    def retrieve_file(self, filename: str) -> bytes:
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT id, filename FROM uploaded_files WHERE filename=?
        """, (filename,))

        result = cursor.fetchone()

        if result:
            file_id, filename = result
            with open(filename, 'rb') as f:
                file_contents = f.read()
            return file_contents

        else:
            raise ValueError("File not found")

    def delete_file(self, file_id):
        for file in self.uploaded_files:
            if file["id"] == file_id:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM uploaded_files WHERE id=?", (file_id,))
                self.conn.commit()

                self.uploaded_files.remove(file)
                return {"message": f"File {file_id} deleted successfully."}, 200
        return {"error": f"File {file_id} not found."}, 404

    def queue_pdf_analysis(self, file_id):
        self.pdf_analysis_queue.put(file_id)

    def queue_nlp_analysis(self, file_id):
        self.nlp_analysis_queue.put(file_id)




class TextNLP:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS text_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                type TEXT NOT NULL,
                sentiment REAL,
                positive REAL,
                negative REAL,
                topics TEXT,
                entities TEXT
            )
        """)

        self.conn.commit()

        self.is_processing = False

    def analyze_text(self, text: str, type: str) -> Union[str, None]:
        """
        Analyze the text and store the results in the database
        """
        print("Analyzing text:", text, type)
        if text:
            if type in ["sen", "ner"]:
                # Analyze the text using TextBlob
                blob = TextBlob(text)
                sentiment = blob.sentiment.polarity
                positive = blob.sentiment.subjectivity
                negative = 1 - positive
                topics = [phrase for phrase, tag in blob.tags if tag.startswith("N")]
                
                # Extract noun chunks and their root tokens using spacy
                doc = nlp(text)
                # Extract entities using spacy
                entities = {}
                doc = nlp(text)
                for chunk in doc.noun_chunks:
                    root = chunk.root
                    entities[root.text] = root.pos_

                # Store the results in the database
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO text_analysis (text, type, sentiment, positive, negative, topics, entities)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (text, type, sentiment, positive, negative, str(topics), str(entities)))
                self.conn.commit()
            else:
                return "Invalid type"
        else:
            return "Invalid input"

    def process(self) -> None:
        """
        Process the text analysis
        """
        if not self.is_processing:
            self.is_processing = True
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT text, type
                FROM text_analysis
            """)
            results = cursor.fetchall()
            for text, type in results:
                result = self._get_result_from_db(text)
                #self.result_queue.put(result)
            self.is_processing = False

    def get_results(self) -> Dict[str, Any]:
        """
        Retrieve results from the database
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT text, type, sentiment, positive, negative, topics, entities
            FROM text_analysis
        """)
        results = cursor.fetchall()

        return [{"text": text, "type": type, "sentiment": {"polarity": sentiment, "positive": positive, "negative": negative},
                 "topics": eval(topics), "entities": eval(entities)} for text, type, sentiment, positive, negative, topics, entities in results]

    def _get_result_from_db(self, name: str):
        """
        Retrieve results from the database
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT text, type, sentiment, positive, negative, topics, entities
            FROM text_analysis
            WHERE text = ?
        """, (name,))
        result = cursor.fetchone()

        if result:
            text, type, sentiment, positive, negative, topics, entities = result
            return {
                "text": text,
                "type": type,
                "sentiment": {"polarity": sentiment, "positive": positive, "negative": negative},
                "topics": eval(topics),
                "entities": eval(entities)
            }
        else:
            return "Result not found"

class NewsFeedAPI:
    def __init__(self, db_file="test.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.queue = queue.Queue()

    def create_news_table(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            self.conn.commit()
        except Exception as e:
            print(f"Error creating table: {e}")
            
    def ingest_article(self, title: str, content: str, source: str) -> str:
        if not title or not content or not source:
            return "Invalid request"
        else:
            self.queue.put((title, content, source))
            print(title, content, source)
            try:
                self.cursor.execute("INSERT INTO articles (title, content, source) VALUES (?, ?, ?)", (title, content, source))
                self.conn.commit()
                return "Article ingested successfully."
            except Exception as e:
                return "Error inserting article: {e}"

    def retrieve_feed(self, source: str) -> List[Dict[str, str]]:
        if not source:
            return "Empty source"
        cursor = self.conn.execute('''
                SELECT title, content, source FROM articles
                WHERE source = ?;
            ''', (source,))
        rows = cursor.fetchall()
        articles = []
        if not rows:
            print("No articles found for source")
        for row in rows:
            articles.append({"title": row[0], "content": row[1], "source": row[2]})
        return articles
