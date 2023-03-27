#include <queue>
#include <string>
#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <bits/stdc++.h>
#include <sqlite3.h>

using namespace std;

struct UploadedFile {
    int id;
    std::string filename;
};

class SecureFileUploader {
public:
    SecureFileUploader(const std::string& db_path);

    std::pair<std::string, int> upload_file(const std::string& file);
    std::pair<std::vector<UploadedFile>, int> get_uploaded_files();
    std::string manage_access_controls(int file_id, const std::map<std::string, bool>& permissions);
    std::pair<std::string, int> delete_file(int file_id);

private:
    std::vector<UploadedFile> uploaded_files;
    std::map<int, std::map<std::string, bool>> access_controls;
    std::queue<std::string> pdf_queue;
    std::queue<std::string> nlp_queue;
    std::mutex pdf_mutex;
    std::mutex nlp_mutex;
    std::mutex uploaded_files_mutex;
    std::mutex access_controls_mutex;
    std::condition_variable pdf_cv;
    std::condition_variable nlp_cv;
    sqlite3* conn;
    std::atomic<bool> stop_processing;
    // private member functions
    void process_pdf_queue() {
        while (true) {
            std::string file;
            {
                std::unique_lock<std::mutex> lock(pdf_mutex);
                pdf_cv.wait(lock, [this] { return !pdf_queue.empty() || stop_processing; });
                if (stop_processing && pdf_queue.empty()) {
                    return;
                }
                file = pdf_queue.front();
                pdf_queue.pop();
            }
            // Process the PDF file here
            // ...
        }
    }
    void process_nlp_queue() {
        while (true) {
            std::string file;
            {
                std::unique_lock<std::mutex> lock(nlp_mutex);
                nlp_cv.wait(lock, [this] { return !nlp_queue.empty() || stop_processing; });
                if (stop_processing && nlp_queue.empty()) {
                    return;
                }
                file = nlp_queue.front();
                nlp_queue.pop();
            }
            // Process the PDF file here
            // ...
        }
    }

};

SecureFileUploader::SecureFileUploader(const std::string& db_path) {
    sqlite3_open(db_path.c_str(), &conn);
    sqlite3_exec(conn, "CREATE TABLE IF NOT EXISTS uploaded_files (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL)", nullptr, nullptr, nullptr);
    sqlite3_exec(conn, "CREATE TABLE IF NOT EXISTS access_controls (file_id INTEGER NOT NULL, permission TEXT NOT NULL, PRIMARY KEY (file_id, permission), FOREIGN KEY (file_id) REFERENCES uploaded_files (id))", nullptr, nullptr, nullptr);
}

std::pair<std::string, int> SecureFileUploader::upload_file(const std::string& file) {
    if (file.empty()) {
        return std::make_pair("No file uploaded.", 400);
    }

    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(conn, "INSERT INTO uploaded_files (filename) VALUES (?)", -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, file.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_step(stmt);
    int file_id = sqlite3_last_insert_rowid(conn);
    sqlite3_finalize(stmt);

    std::unique_lock<std::mutex> lock(uploaded_files_mutex);
    uploaded_files.push_back({file_id, file});
    lock.unlock();

    {
        std::lock_guard<std::mutex> lock(pdf_mutex);
        pdf_queue.push(file);
    }
    pdf_cv.notify_one();

    {
        std::lock_guard<std::mutex> lock(nlp_mutex);
        nlp_queue.push(file);
    }
    nlp_cv.notify_one();

    return std::make_pair("Uploaded file successfully.", 200);
}

std::pair<std::vector<UploadedFile>, int> SecureFileUploader::get_uploaded_files() {
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(conn, "SELECT * FROM uploaded_files", -1, &stmt, nullptr);
    std::vector<UploadedFile> uploaded_files;
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        int id = sqlite3_column_int(stmt, 0);
        const unsigned char* filename = sqlite3_column_text(stmt, 1);
        uploaded_files.push_back({id, std::string(reinterpret_cast<const char*>(filename))});
    }
    sqlite3_finalize(stmt);
    return {uploaded_files, 200};
}
std::string SecureFileUploader::manage_access_controls(int file_id, const std::map<std::string, bool>& permissions) {
    if (permissions.empty()) {
        return "Permission map is empty.";
    }
    
    std::vector<std::string> allowed_permissions = {"read", "write", "execute"};
    for (auto const& p : permissions) {
        if (std::find(allowed_permissions.begin(), allowed_permissions.end(), p.first) == allowed_permissions.end()) {
            return "Invalid permission: " + p.first;
        }
    }
    
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(conn, "SELECT * FROM uploaded_files WHERE id=?", -1, &stmt, nullptr);
    sqlite3_bind_int(stmt, 1, file_id);
    if (sqlite3_step(stmt) != SQLITE_ROW) {
        return "File not found.";
    }

    sqlite3_prepare_v2(conn, "DELETE FROM access_controls WHERE file_id=?", -1, &stmt, nullptr);
    sqlite3_bind_int(stmt, 1, file_id);
    sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    
    sqlite3_prepare_v2(conn, "INSERT INTO access_controls (file_id, permission) VALUES (?, ?)", -1, &stmt, nullptr);
    for (auto const& p : permissions) {
        if (p.second) {
            sqlite3_bind_int(stmt, 1, file_id);
            sqlite3_bind_text(stmt, 2, p.first.c_str(), -1, SQLITE_TRANSIENT);
            sqlite3_step(stmt);
            sqlite3_reset(stmt);
        }
    }
    sqlite3_finalize(stmt);
    
    return "Access controls updated!";
}
std::pair<std::string, int> SecureFileUploader::delete_file(int file_id) {
    auto file = std::find_if(uploaded_files.begin(), uploaded_files.end(), [file_id](const UploadedFile& f) { return f.id == file_id; });
    if (file == uploaded_files.end()) {
        return {"File not found", 404};
    }

    // Remove the file from the database
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(conn, "DELETE FROM uploaded_files WHERE id=?", -1, &stmt, nullptr);
    sqlite3_bind_int(stmt, 1, file_id);
    int res = sqlite3_step(stmt);
    if (res != SQLITE_DONE) {
        return {"Failed to delete file", 500};
    }
    sqlite3_finalize(stmt);

    // Remove the file from the uploaded_files vector
    uploaded_files.erase(file);

    return {"File deleted!", 200};
}


class TextNLPAnalysis {
public:

    std::string db_file_;
    std::queue<std::string> nlp_queue_;
    std::queue<std::string> pdf_queue_;
    std::thread nlp_thread_;
    std::thread pdf_thread_;
    std::mutex nlp_mutex_;
    std::mutex pdf_mutex_;
    std::condition_variable nlp_cv_;
    std::condition_variable pdf_cv_;
    TextNLPAnalysis() = default;
    
    TextNLPAnalysis(std::string db_file) : db_file_(db_file) {
        create_table();
    }

    void create_table() {
        sqlite3 *db;
        char *error_message = nullptr;
        int result = sqlite3_open(db_file_.c_str(), &db);
        if (result != SQLITE_OK) {
            fprintf(stderr, "Error opening database: %s\n", sqlite3_errmsg(db));
            sqlite3_close(db);
            return;
        }
        const char *sql_stmt = "CREATE TABLE IF NOT EXISTS text_analysis ("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "text TEXT,"
                               "sentiment_polarity REAL,"
                               "sentiment_subjectivity REAL,"
                               "topics TEXT,"
                               "entities TEXT)";
        result = sqlite3_exec(db, sql_stmt, nullptr, nullptr, &error_message);
        if (result != SQLITE_OK) {
            fprintf(stderr, "Error creating table: %s\n", error_message);
            sqlite3_free(error_message);
        }
        sqlite3_close(db);
    }
    void add_to_nlp_queue(std::string text) {
        std::unique_lock<std::mutex> lock(nlp_mutex_);
        nlp_queue_.push(text);
        nlp_cv_.notify_one();
    }

    void add_to_pdf_queue(std::string file_path) {
        std::unique_lock<std::mutex> lock(pdf_mutex_);
        pdf_queue_.push(file_path);
        pdf_cv_.notify_one();
    }

    void analyze_nlp() {
        while (true) {
            std::unique_lock<std::mutex> lock(nlp_mutex_);
            nlp_cv_.wait(lock, [this](){return !nlp_queue_.empty();});
            std::string text = nlp_queue_.front();
            nlp_queue_.pop();
            lock.unlock();
            if (text.empty()) {
                break;
            }
            auto analysis = analyze_text(text);
            save_to_db(text, analysis);
        }
    }

    void analyze_pdf() {
        while (true) {
            std::unique_lock<std::mutex> lock(pdf_mutex_);
            pdf_cv_.wait(lock, [this](){return !pdf_queue_.empty();});
            std::string file_path = pdf_queue_.front();
            pdf_queue_.pop();
            lock.unlock();
            if (file_path.empty()) {
                break;
            }
            std::string text = extract_text_from_pdf(file_path);
            auto analysis = analyze_text(text);
            save_to_db(text, analysis);
        }
    }

    void start_analysis() {
        nlp_thread_ = std::thread(&TextNLPAnalysis::analyze_nlp, this);
        pdf_thread_ = std::thread(&TextNLPAnalysis::analyze_pdf, this);
    }

    void stop_analysis() {
        add_to_nlp_queue("");
        add_to_pdf_queue("");
        nlp_thread_.join();
        pdf_thread_.join();
    }

    std::map<std::string, std::any> analyze_text(std::string text) {
        // Implementation of analyze_text
        std::map<std::string, std::any> result;
        // ... some analysis code ...
        return result;
    }

    std::string extract_text_from_pdf(std::string file_path) {
        // Implementation of extract_text_from_pdf
        std::string result;
        // ... some code to extract text from PDF ...
        return result;
    }

    std::map<std::string, std::string> get_visualization_data(std::string text) {
        // Implementation of get_visualization_data
        std::map<std::string, std::string> result;
        // ... some code to generate visualization data ...
        return result;
    }

    std::vector<std::map<std::string, std::string>> extract_entities(std::string text) {
        // Implementation of extract_entities
        std::vector<std::map<std::string, std::string>> result;
        // ... some code to extract entities ...
        return result;
    }

    void save_to_db(std::string text, std::map<std::string, std::any> analysis) {
        // Implementation of save_to_db
        // ... some code to save analysis to database ...
    }

    std::vector<std::tuple<int, std::string, double, double, std::string, std::string>> get_from_db(std::string text) {
        // Implementation of get_from_db
        std::vector<std::tuple<int, std::string, double, double, std::string, std::string>> result;
        // ... some code to retrieve analysis from database ...
        return result;
    }
};

struct Article {
    string title;
    string content;
    string source;
};

class NewsFeedIngester {
public:
    NewsFeedIngester(const string& db_file);
    ~NewsFeedIngester();

    void start_workers();
    void stop_workers();

    vector<Article> get_articles_by_source(const string& source, int limit);
    string ingest_article(const string& title, const string& content, const string& source);
    vector<Article> filter_news_articles(const vector<Article>& news_articles, const string& source);

private:
    sqlite3* db_;
    sqlite3* conn;
    sqlite3_stmt* stmt;
    queue<Article> pdf_queue_;
    queue<Article> nlp_queue_;
    vector<thread> pdf_threads_;
    vector<thread> nlp_threads_;
    atomic_bool stop_threads_;
    mutex pdf_mutex_;
    mutex nlp_mutex_;
    condition_variable pdf_cv_;
    condition_variable nlp_cv_;

    void create_articles_table();
    void process_pdf_queue();
    void process_nlp_queue();
};

NewsFeedIngester::NewsFeedIngester(const string& db_file) : stop_threads_{false} {
    int rc = sqlite3_open(db_file.c_str(), &db_);
    if (rc != SQLITE_OK) {
        std::cerr << "Cannot open database: " << sqlite3_errmsg(db_) << std::endl;
        sqlite3_close(db_);
        std::exit(1);
    }
    create_articles_table();
}

NewsFeedIngester::~NewsFeedIngester() {
    stop_threads_ = true;
    pdf_cv_.notify_all();
    nlp_cv_.notify_all();
    for (auto& t : pdf_threads_) {
        t.join();
    }
    for (auto& t : nlp_threads_) {
        t.join();
    }
    sqlite3_close(db_);
}

void NewsFeedIngester::create_articles_table() {
    char* errmsg = nullptr;
    int rc = sqlite3_exec(db_, R"(
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT NOT NULL
        );
    )", nullptr, nullptr, &errmsg);
    if (rc != SQLITE_OK) {
        std::cerr << "Cannot create articles table: " << errmsg << std::endl;
        sqlite3_free(errmsg);
        std::exit(1);
    }
    std::cout << "Table 'articles' created successfully!" << std::endl;
}

void NewsFeedIngester::process_pdf_queue() {
    while (!stop_threads_) {
        Article article;
        {
            unique_lock<mutex> lock{pdf_mutex_};
            pdf_cv_.wait(lock, [this] { return !pdf_queue_.empty() || stop_threads_; });
            if (stop_threads_) {
                break;
            }
            article = pdf_queue_.front();
            pdf_queue_.pop();
        }
        // Perform PDF analysis here
        // ...
    }
}

void NewsFeedIngester::process_nlp_queue() {
    while (!stop_threads_) {
        Article article;
        {
            unique_lock<mutex> lock{nlp_mutex_};
            nlp_cv_.wait(lock, [this] { return !nlp_queue_.empty() || stop_threads_; });
            if (stop_threads_) {
                break;
            }
            article = nlp_queue_.front();
            nlp_queue_.pop();
        }
    }
}
void NewsFeedIngester::start_workers() {
    for (int i = 0; i < 5; i++) {
        std::thread t(&NewsFeedIngester::process_pdf_queue, this);
        t.detach();
    }

    for (int i = 0; i < 5; i++) {
        std::thread t(&NewsFeedIngester::process_nlp_queue, this);
        t.detach();
    }
}
string NewsFeedIngester::ingest_article(const string& title, const string& content, const string& source) {
    if (title.empty() || content.empty() || source.empty()) {
        std::scoped_lock lock{pdf_mutex_, nlp_mutex_};
        pdf_queue_.push({title, content, source});
        nlp_queue_.push({title, content, source});
        return "Invalid request";
    } else {
        string query = "INSERT INTO articles (title, content, source) VALUES (?, ?, ?);";
        sqlite3_prepare_v2(db_, query.c_str(), -1, &stmt, NULL);
        sqlite3_bind_text(stmt, 1, title.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 2, content.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 3, source.c_str(), -1, SQLITE_STATIC);
        int result = sqlite3_step(stmt);
        sqlite3_finalize(stmt);
        if (result != SQLITE_DONE) {
            return "Failed to insert article into database.";
        }
        return "Article ingested successfully.";
    }
}
vector<Article> NewsFeedIngester::get_articles_by_source(const string& source, int limit) {
    // implementation
    vector<Article> articles;
    if (source.empty()) {
        articles.emplace_back("Empty source!", "", "");
        return articles;
    }
    
    sqlite3_stmt* stmt;
    const char* query = "SELECT title, content, source FROM articles WHERE source = ? LIMIT ?;";
    int rc = sqlite3_prepare_v2(conn, query, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        articles.emplace_back("Error preparing statement", "", "");
        return articles;
    }
    
    sqlite3_bind_text(stmt, 1, source.c_str(), -1, SQLITE_STATIC);
    sqlite3_bind_int(stmt, 2, limit);
    
    while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
        string title = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
        string content = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
        string source = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
        articles.emplace_back(title, content, source);
    }
    
    if (rc != SQLITE_DONE) {
        articles.emplace_back("Error fetching data", "", "");
    }
    
    sqlite3_finalize(stmt);
    
    return articles;
}

vector<Article> NewsFeedIngester::filter_news_articles(const vector<Article>& news_articles, const string& source) {
    vector<Article> filtered_articles;
    for (const auto& article : news_articles) {
        if (article.source == source) {
            filtered_articles.push_back(article);
        }
    }
    if (filtered_articles.empty()) {
        throw std::runtime_error("Source not found");
    }
    return filtered_articles;
}


int main() {
    SecureFileUploader uploader("test.db");

    // Upload a file
    auto res = uploader.upload_file("test.pdf");
    std::cout << res.first << " Status code: " << res.second << std::endl;

    // Get uploaded files
    auto uploaded_files = uploader.get_uploaded_files().first;
    for (const auto& file : uploaded_files) {
        std::cout << "File ID: " << file.id << ", Filename: " << file.filename << std::endl;
    }

    // Manage access controls for the uploaded file
    std::map<std::string, bool> permissions = {
        {"read", true},
        {"write", false},
        {"execute", true}
    };
    std::string message = uploader.manage_access_controls(uploaded_files[0].id, permissions);
    std::cout << message << std::endl;

    // Delete the uploaded file
    res = uploader.delete_file(uploaded_files[0].id);
    std::cout << res.first << " Status code: " << res.second << std::endl;

    return 0;
}
