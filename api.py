from typing import Dict, List

class FileUploader:
    
    def upload_file(self, file_contents: bytes, file_name: str, file_location: str, access_control: Dict[str, List[str]]) -> str:
        """
        Upload a file to the server
        """
        extension = file_name.split()
        if extension[-1] == "txt":
            return "File uploaded Successfully"
        
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
        for file in self.uploaded_files:
            if file["id"] == file_id:
                return {"message": f"File {file_id} deleted successfully."}, 200
        return {"error": f"File {file_id} not found."}, 404

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
    def ingest_feed(self, feed_url):
        # TODO: Retrieve the feed from the given URL,
        # parse the feed data, and store the results
        # in a database for later retrieval
        if(not feed_url):
            return "Invalid request"
        else:
            return "Feed ingested successfully."

    def retrieve_feed(self, start_date, end_date):
        # TODO: Retrieve all feed items from the database
        # that fall within the given date range, and return
        # them in a structured format
        if not source:
            return "Empty Date"
        else:
            return [
            {"title": "Article 1", "content": "This is article 1.", "source": "CNN"},
            {"title": "Article 2", "content": "This is article 2.", "source": "BBC"}
            ]

