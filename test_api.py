import api
class TestFileUploader:
    
    def test_upload_file(self):
        uploader = FileUploader()
        file_contents = b"example file contents"
        file_name = "example_file.txt"
        file_location = "/example/path/"
        access_control = {"users": ["user1", "user2"], "groups": ["group1"]}
        
        result = uploader.upload_file(file_contents, file_name, file_location, access_control)
        
        assert result == "File uploaded successfully"
        
