from typing import Dict, List, Any
import sqlite3
import os

class FileUploader:
    def __init__(self, db_path):
        self.uploaded_files = []
        self.access_controls = {}
        self.conn = sqlite3.connect(db_path)

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

    def upload_file(self, file):
        if not file:
            return {"error": "No file uploaded."}, 400

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO uploaded_files (filename) VALUES (?)", (file,))
        self.conn.commit()

        self.uploaded_files.append({"id": cursor.lastrowid, "filename": file})
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

    def analyze_text(self, text: str, type:str) -> Dict[str, Any]:
        if text:
            if type in ["sen","ner"]:
                # Analyze the text and get the results
                sentiment = 0.7
                positive = 0.6
                negative = 0.4
                topics = ["politics", "activism", "health"]
                entities = {"New Delhi": "CITY", "Narendra Modi": "PERSON"}

                # Store the results in the database
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO text_analysis (text, type, sentiment, positive, negative, topics, entities)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (text, type, sentiment, positive, negative, str(topics), str(entities)))
                self.conn.commit()

                # Return the results
                return {
                    "sentiment": {"polarity": sentiment, "positive": positive, "negative": negative},
                    "topics": topics,
                    "entities": entities
                }
        else:
            return "Invalid input"

    def get_results(self, name: str):
        """
        Retrieve results
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
                "sentiment": {"polarity": sentiment, "positive": positive, "negative": negative},
                "topics": eval(topics),
                "entities": eval(entities)
            }
        else:
            return "Result not found"


class NewsFeedAPI:
    
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
   
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
        if(not title or not content or not source):
            return "Invalid request"
        else:
            self.cursor.execute('''
                INSERT INTO articles (title, content, source)
                VALUES (?, ?, ?);
            ''', (title, content, source))
            self.conn.commit()
            return "Article ingested successfully."

    def retrieve_feed(self, start_date, end_date):
        if not start_date:
            return "Empty Date"
    
        cursor = self.conn.execute("SELECT title, content, created_at FROM articles WHERE created_at BETWEEN ? AND ?", (start_date + " 00:00:00", end_date + " 23:59:59"))
        rows = cursor.fetchall()

        results = []
        for row in rows:
            result = {"title": row[0], "content": row[1], "created_at": row[2]}
            results.append(result)

        return results


