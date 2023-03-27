from typing import Dict, List, Any, Union
import sqlite3
import feedparser
import sqlite3
import threading
import queue

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

        # Initialize queues and threads
        self.analysis_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.threads = []
        self.max_threads = 5
        self.is_processing = False

    def analyze_text(self, text: str, type:str) -> Union[str, None]:
        """
        Add the text analysis to the queue
        """
        print("Analyzing text:", text, type)
        if text:
            if type in ["sen","ner"]:
                # Add the analysis to the queue
                self.analysis_queue.put((text, type))
                
                # If not already processing, start processing the queue
                if not self.is_processing:
                    self.start_processing()
            else:
                return "Invalid type"
        else:
            return "Invalid input"


    def start_processing(self):
        """
        Start processing the analysis queue using threads
        """
        print("Starting processing")
        self.is_processing = True
        while not self.analysis_queue.empty():
            # Start a new thread for each analysis
            if len(self.threads) < self.max_threads:
                t = threading.Thread(target=self.process_text_analysis)
                self.threads.append(t)
                t.start()

        # Wait for all threads to complete before stopping processing
        for t in self.threads:
            t.join()

        self.is_processing = False

    def process_text_analysis(self):
        """
        Process the text analysis from the queue
        """
        print("Processing text analysis")
        while not self.analysis_queue.empty():
            text, type = self.analysis_queue.get()
            if text:
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

                # Add the results to the result queue
                self.result_queue.put((text, type))

        # Remove the thread from the list of threads
        self.threads.remove(threading.current_thread())
    
    def process(self) -> None:
        if not self.is_processing:
            self.is_processing = True
            while not self.input_queue.empty():
                text, type = self.input_queue.get()
                results = self._process_text(text, type)
                for result in results:
                    self.result_queue.put(result)
            self.is_processing = False

    def get_results(self) -> Dict[str, Any]:
        """
        Retrieve results from the result queue
        """
        if not self.is_processing:
            results = []
            while not self.result_queue.empty():
                text, type = self.result_queue.get()
                result = self._get_result_from_db(text)
                results.append(result)
            return results
        else:
            return "Processing in progress"

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
        self.queue = queue.Queue()
        #self.thread = threading.Thread(target=self._process_articles)
        #self.thread.start()
    
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
            self.queue.put((title, content, source))
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
    
    # def _process_articles(self):
    #     while True:
    #         title, content, source = self.queue.get()
    #         self.cursor.execute('''
    #             INSERT INTO articles (title, content, source)
    #             VALUES (?, ?, ?);
    #         ''', (title, content, source))
    #         self.conn.commit()
    #         self.queue.task_done()