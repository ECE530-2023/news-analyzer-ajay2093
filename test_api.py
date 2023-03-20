import unittest
import tempfile
import os
import sqlite3
from datetime import datetime
from api import NewsFeedAPI
from api import FileUploader
from api import TextNLP


class TestFileUploader(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.file_uploader = FileUploader(self.db_path)

    def tearDown(self):
        self.file_uploader.conn.close()  # Close the database connection
        os.close(self.db_fd)
        os.unlink(self.db_path)  # Delete the database file

    def test_upload_file(self):
        resp, status_code = self.file_uploader.upload_file("test.txt")
        self.assertEqual(status_code, 200)
        self.assertEqual(resp, {"message": "File uploaded successfully."})
        self.assertEqual(len(self.file_uploader.uploaded_files), 1)

    def test_retrieve_file(self):
        self.file_uploader.upload_file("test.txt")
        file_contents = b'This is a test file'
        with open('test.txt', 'wb') as f:
            f.write(file_contents)

        retrieved_file = self.file_uploader.retrieve_file("test.txt")
        self.assertEqual(retrieved_file, file_contents)

    def test_delete_file(self):
        # Test deleting a file
        self.file_uploader.upload_file("test_file.txt")
        file_id = 1
        response, status_code = self.file_uploader.delete_file(file_id)
        self.assertEqual(status_code, 200)
        self.assertEqual(
            response, {"message": f"File {file_id} deleted successfully."})

        # Test deleting a non-existent file
        file_id = 2
        response, status_code = self.file_uploader.delete_file(file_id)
        self.assertEqual(status_code, 404)
        self.assertEqual(response, {"error": f"File {file_id} not found."})

class TestTextNLP(unittest.TestCase):
    def setUp(self):
        self.db_path = "test.db"
        self.text_nlp = TextNLP(self.db_path)

    def tearDown(self):
        self.text_nlp.conn.close()  # Close the database connection
        os.unlink(self.db_path)  # Delete the database file

    def test_analyze_text(self):
        # Test valid input
        result = self.text_nlp.analyze_text("This is a test sentence.", "sen")
        self.assertEqual(result["sentiment"]["polarity"], 0.7)
        self.assertEqual(result["sentiment"]["positive"], 0.6)
        self.assertEqual(result["sentiment"]["negative"], 0.4)
        self.assertListEqual(result["topics"], ["politics", "activism", "health"])
        self.assertDictEqual(result["entities"], {"New Delhi": "CITY", "Narendra Modi": "PERSON"})

        # Test invalid input
        result = self.text_nlp.analyze_text("", "sen")
        self.assertEqual(result, "Invalid input")

        # Test invalid type
        result = self.text_nlp.analyze_text("This is a test sentence.", "invalid_type")
        self.assertIsNone(result)

    def test_get_results(self):
        # Test valid input
        self.text_nlp.analyze_text("This is a test sentence.", "sen")
        result = self.text_nlp.get_results("This is a test sentence.")
        self.assertEqual(result["sentiment"]["polarity"], 0.7)
        self.assertEqual(result["sentiment"]["positive"], 0.6)
        self.assertEqual(result["sentiment"]["negative"], 0.4)
        self.assertListEqual(result["topics"], ["politics", "activism", "health"])
        self.assertDictEqual(result["entities"], {"New Delhi": "CITY", "Narendra Modi": "PERSON"})

        # Test invalid input
        result = self.text_nlp.get_results("Invalid text")
        self.assertEqual(result, "Result not found")


class TestNewsFeedAPI(unittest.TestCase):

    def setUp(self):
        self.db_file = ":memory:"
        self.api = NewsFeedAPI(self.db_file)
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.api.create_news_table()

    def test_ingest_article(self):
        result = self.api.ingest_article("Test Article", "This is a test article.", "Test Source")
        self.assertEqual(result, "Article ingested successfully.")
        
        result = self.api.ingest_article("", "This is a test article.", "Test Source")
        self.assertEqual(result, "Invalid request")
        
        result = self.api.ingest_article("Test Article", "", "Test Source")
        self.assertEqual(result, "Invalid request")
        
        result = self.api.ingest_article("Test Article", "This is a test article.", "")
        self.assertEqual(result, "Invalid request")

    def test_retrieve_feed(self):
        # Create some sample data in the database
        self.api.create_news_table()
        self.api.ingest_article("Article 1", "Content 1", "Source 1")
        self.api.ingest_article("Article 2", "Content 2", "Source 2")
        self.api.ingest_article("Article 3", "Content 3", "Source 3")

        # Test that retrieving feed items outside of the date range returns an empty list
        start_date = datetime(2023, 1, 1).strftime('%Y-%m-%d')
        end_date = datetime(2023, 1, 31).strftime('%Y-%m-%d')
        results = self.api.retrieve_feed(start_date, end_date)
        self.assertEqual(len(results), 0)

    def tearDown(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute("DROP TABLE IF EXISTS articles")
        self.cursor.execute("DROP TABLE IF EXISTS feed_data")
        self.conn.close()


if __name__ == '__main__':
    unittest.main()




