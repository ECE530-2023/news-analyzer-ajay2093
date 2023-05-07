from api_queue import FileUploader,TextNLP,NewsFeedAPI
import sqlite3
import bcrypt
from auth import Authentication

class Authenticator:
    """
    Authenticator for registering and authenticating users
    """
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._create_users_table()

    def _create_users_table(self):
        """
        Create the users table if it does not exist
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT
            )
        """)
        self.conn.commit()

    def register_user(self, username: str, password: str) -> bool:
        """
        Register a new user
        """
        cursor = self.conn.cursor()
        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False

        # Hash the password and store the user credentials in the database
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        self.conn.commit()
        return True

    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticate an existing user
        """
        cursor = self.conn.cursor()
        # Get the user's password hash
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            # Check if the hashed password matches the stored hash
            return bcrypt.checkpw(password.encode(), result[0])
        return False
    
def modules():
    while True:
        print("\nChoose Module:")
        print("1. Secure File Uploader")
        print("2. Text Analyzer")
        print("3. News Feed Analyzer")
        print("4. Quit")
        choice = input("Enter your choice: ")
        if choice=="1":
            uploader = FileUploader("fileuploader.db")
            #credentials = uploader.authenticate()
            print("Authenticated with Google Drive API.")

            while True:
                print("\nMenu:")
                print("1. Upload file")
                print("2. Retrieve file")
                print("3. Delete file")
                print("4. Quit")
                choice = input("Enter your choice: ")

                if choice == "1":
                    file = input("Enter filename: ")
                    response, status = uploader.upload_file(file)
                    print(response)
                elif choice == "2":
                    filename = input("Enter filename: ")
                    try:
                        file_contents = uploader.retrieve_file(filename)
                        print("File contents:", file_contents)
                    except ValueError as e:
                        print(e)
                elif choice == "3":
                    filename = input("Enter filename: ")
                    response, status = uploader.delete_file(filename)
                    print(response)
                elif choice == "4":
                    break
                else:
                    print("Invalid choice.")
        
        elif choice=="2":
            text_nlp = TextNLP("text_analysis.db")
            while True:
                print("\nMenu:")
                print("1. Analyze Text")
                print("2. Quit")
                choice = input("Enter your choice: ")
                if choice=="1":
                    text = input("Enter the text to analyze: ")
                    text_nlp.analyze_text(text, "sen")
                    # Process the text analysis and get the results
                    text_nlp.process()
                    results = text_nlp.get_results()
                    # Print the results
                    for result in results:
                        print(result)
                elif choice=="2":
                    break
                else:
                    print("Invalid choice.")
                
        elif choice=="3":
            api = NewsFeedAPI("news.db")
            api.create_news_table()
            while True:
                print("Choose an option: ")
                print("1. Ingest an article")
                print("2. Retrieve an article by source")
                print("3. Quit")
                choice = input("Enter your choice: ")
                if choice == "1":
                    user_input = input("Enter (title, content, source): ").strip().split(',')
                    if len(user_input) == 3:
                        title, content, source = user_input
                        print(api.ingest_article(title, content, source))
                    else:
                        print("Please enter the article in correct format!")
                elif choice == "2":
                    user_input = input("Enter source: ")
                    print(user_input)
                    result = api.retrieve_feed(user_input)
                    print(result)
                else: 
                    break

        elif choice == "4":
            break
        else:
            print("Invalid choice.")

def main():
    authenticator = Authentication()
    # Register a new user
    while True:
        print("Choose the option: ")
        print("1. Register")
        print("2. Authenticate")
        print("3. Quit")
        choice = input("Enter your choice: ")
        if choice == "1":
            email = input("Enter user email: ")
            authenticator.register_user(email)
            print("User registered successfully!")
            #break
        elif choice == "2":
            # Authenticate a user
            authenticator.test()
            email = authenticator.authenticate_user()
            if email:
                print(f"User {email} authenticated successfully!")
                modules()
            else:
                print("Invalid ID token or unregistered user!")
            
        else:
            break

if __name__ == "__main__":
    main()