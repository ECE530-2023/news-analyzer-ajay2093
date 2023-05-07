# news-analyzer-ajay2093
news-analyzer-ajay2093 created by GitHub Classroom

## *Added api_queue and test_api_queue for Queue and Thread implementation!
## *Added api.cpp for Queue and Thread implementation in C++!

## GO INTO FINAL PROJECT FOLDER TO ASSES MY FINAL PROJECT

[![Software Engineering Final Project](https://res.cloudinary.com/marcomontalbano/image/upload/v1683502668/video_to_markdown/images/google-drive--151ZE_nvowifXXbw2HDABf7lpIYCHHwyE-c05b58ac6eb4c4700831b2b3070cd403.jpg)](https://drive.google.com/file/d/151ZE_nvowifXXbw2HDABf7lpIYCHHwyE/view?usp=sharing "Software Engineering Final Project")


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

While a document database is a better choice for a module that focuses on unstructured data, such as user-generated documents and searches, SQL may be a better choice in certain scenarios. Here are some reasons why:

* Structured Data: If the module involves storing structured data that requires strict consistency and validation, a relational database using SQL may be a better fit. SQL databases are designed to handle data with complex relationships and dependencies, making them ideal for applications with a lot of data and strict requirements.

* Transactions: SQL databases offer transactional support, which is crucial for applications that require a high degree of data integrity. Transactions ensure that multiple database operations occur atomically, meaning they either all succeed or all fail. This ensures that data remains consistent and reduces the risk of data loss or corruption.

* Security: SQL databases offer a wide range of security features, such as access control, encryption, and auditing, making them ideal for applications that need to store sensitive information.

* Reporting: SQL databases offer robust reporting capabilities that allow developers to generate complex reports and analytics from the data. This makes them an excellent choice for applications that require advanced reporting capabilities.

* Legacy Systems: In some cases, SQL databases may be a better choice because they are a well-established technology with a large developer community and support. This is particularly true for applications that need to integrate with legacy systems that use SQL.







