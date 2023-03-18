# news-analyzer-ajay2093
news-analyzer-ajay2093 created by GitHub Classroom

Please refer uploaded PPT (Project2.ppt) for user stories and error handling

### Database Schemas

**User Schema:**
``` json
{
  "id": "<string>",
  "username": "<string>",
  "email": "<string>",
  "password": "<string>",
  "access_control": "<string>"
}
```

**Documents Schemas:**

- Secure File Uploader/Ingester:
``` json
{
    "id": "<string>",
    "file_name": "<string>",
    "file_type": "<string>",
    "file_size": "<float>",
    "date_uploaded": "<datetime>",
    "uploaded_by": "<string>",
    "access_control": {
        "viewers": [
            "<string>"
        ],
        "editors": [
            "<string>"
        ],
        "owner": "<string>"
    }
}
```

- Text NLP Analysis:
``` json
{
    "id": "<string>",
    "text_data": "<string>",
    "date_uploaded": "<datetime>",
    "uploaded_by": "<string>",
    "sentiment_analysis": {
        "polarity": "<float>",
        "subjectivity": "<float>"
    },
    "named_entities": [
        {
            "text": "<string>",
            "label": "<string>",
            "relevance": "<float>"
        }
    ]
}
```

- News Feed Ingester:
``` json
{
    "id": "<string>",
    "title": "<string>",
    "url": "<string>",
    "date_published": "<datetime>",
    "source": "<string>",
    "access_control": {
        "viewers": [
            "<string>"
        ],
        "editors": [
            "<string>"
        ],
        "owner": "<string>"
    }
}
```

### Best database for such module

- For a module that focuses on users, their documents, and searches, a document database like MongoDB may be a better fit than a traditional SQL database.

- Document databases are designed to store semi-structured data, which makes them well-suited for storing user documents and search queries. This type of database can handle a variety of document formats, including PDFs, Word documents, images, and audio files.

- In addition, document databases are flexible and schemaless, which means that they can adapt to changing data models and requirements without requiring a strict schema. This can be particularly useful in a module that involves user-generated content, where the document structure may vary from user to user.

- Document databases are also designed for high performance and scalability, making them ideal for modules that require fast query response times and the ability to handle large volumes of data. For example, if the module needs to search through thousands of user documents quickly, a document database can efficiently handle the indexing and querying needed to retrieve relevant documents.

- Finally, document databases often have built-in features that support full-text search, which can be important for a module that involves user search queries. Full-text search allows users to search for specific keywords or phrases within the content of their documents, making it easier to find relevant information.
Overall, a document database may be a better fit for a module that focuses on users, their documents, and searches because it can handle semi-structured data, is flexible and scalable, and supports full-text search.







