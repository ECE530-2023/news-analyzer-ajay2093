import api as api
import unittest

class TestFileUploader(unittest.TestCase):
    def setUp(self):
        self.api = api.FileUploader()

    def test_upload_file(self):
        uploader = api.FileUploader()
        file_contents = b"example file contents"
        file_name = "example_file.txt"
        file_location = "/example/path/"
        access_control = {"users": ["user1", "user2"], "groups": ["group1"]}
        
        result = self.api.upload_file(file_contents, file_name, file_location, access_control)
        
        self.assertEqual(result,"File uploaded successfully")
    
    def test_upload_file_none(self):
        uploader = api.FileUploader()
        file_contents = b"example file contents"
        file_name = "example_file.api"
        file_location = "/example/path/"
        access_control = {"users": ["user1", "user2"], "groups": ["group1"]}
        
        result = self.api.upload_file(file_contents, file_name, file_location, access_control)
        
        self.assertEqual(result,"This file format is not supported")

class TestTextAnalysisAPI(unittest.TestCase):
    def setUp(self):
        self.api = api.TextNLP()

    def test_analyze_text(self):
        text = "The quick brown fox jumps over the lazy dog"
        result = self.api.analyze_text(text)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn("tokens", result)
        self.assertIn("sentences", result)
        self.assertIn("entities", result)
    
    def test_empty_text(self):
        analysis = api.TextNLPAnalysis()
        response =  analysis.analyze_text("") 
        self.assertEqual(response, "Invalid input")

import unittest

class TestNewsFeedAPI(unittest.TestCase):
    def setUp(self):
        self.api = api.NewsFeedAPI()

    def test_ingest_feed(self):
        feed_url = "https://example.com/feed.xml"
        result = self.api.ingest_feed(feed_url)
        self.assertIsNotNone(result)
        self.assertEqual(result, "Feed ingested successfully")

    def test_retrieve_feed(self):
        start_date = "2023-02-01"
        end_date = "2023-02-28"
        result = self.api.retrieve_feed(start_date, end_date)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        for item in result:
            self.assertIsInstance(item, dict)
            self.assertIn("title", item)
            self.assertIn("link", item)
            self.assertIn("description", item)
            self.assertIn("pub_date", item)
            self.assertIn("categories", item)



