from typing import Dict, List

class FileUploader:
    
    def upload_file(self, file_contents: bytes, file_name: str, file_location: str, access_control: Dict[str, List[str]]) -> str:
        """
        Upload a file to the server
        """
        pass
    
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
