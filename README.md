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

For a module that focuses on users, their documents, and searches, a document database would be the better choice over a traditional SQL database. Here's why:

* Flexibility: Document databases like MongoDB, CouchDB, or RavenDB are designed to store unstructured data, making them a good fit for document-based use cases. This makes them an ideal choice for a module that involves working with documents that may not have a fixed schema.

* Performance: Document databases are designed for high performance and scalability. They use a distributed architecture that allows them to easily scale horizontally by adding more servers. This makes them ideal for applications that need to handle a large volume of data and traffic.

* Querying: Document databases offer powerful query capabilities that allow developers to retrieve data based on complex criteria. This makes them an excellent choice for applications that need to perform ad-hoc queries or search operations.

* Integration: Document databases can integrate easily with modern web frameworks and languages like Node.js, Ruby on Rails, or Python, making them an ideal choice for web applications.

* Cost: Document databases are generally less expensive to operate than traditional SQL databases because they require less infrastructure and support to manage. This is particularly true when scaling horizontally, which is much easier and less expensive with a document database.

In summary, for a module that focuses on users, their documents, and searches, a document database would be the better choice because of its flexibility, performance, querying capabilities, integration, and cost-effectiveness.






