#include "db.hpp"
#include <stdexcept>

DB::DB(const std::string& db_path) : db_path(db_path) {
    int rc = sqlite3_open(db_path.c_str(), &db);
    if (rc) {
        throw std::runtime_error("Can't open database: " + std::string(sqlite3_errmsg(db)));
    }
    create_tables();
}

DB::~DB() {
    if (db) {
        sqlite3_close(db);
    }
}

void DB::create_tables() {
    const char* sql = R"(
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            file_url TEXT NOT NULL,
            downloaded BOOLEAN NOT NULL DEFAULT 0
        )
    )";

    char* errMsg = nullptr;
    int rc = sqlite3_exec(db, sql, nullptr, nullptr, &errMsg);
    if (rc != SQLITE_OK) {
        std::string error = "SQL error: " + std::string(errMsg);
        sqlite3_free(errMsg);
        throw std::runtime_error(error);
    }
}

RawBook DB::insert_book(const RawBook& book) {
    const char* sql = R"(
        INSERT INTO books (title, author, file_url, downloaded)
        VALUES (?, ?, ?, ?)
    )";

    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        throw std::runtime_error("Failed to prepare statement");
    }

    sqlite3_bind_text(stmt, 1, book.title.c_str(), -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, book.author.c_str(), -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 3, book.file_url.c_str(), -1, SQLITE_STATIC);
    sqlite3_bind_int(stmt, 4, book.downloaded ? 1 : 0);

    rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) {
        sqlite3_finalize(stmt);
        throw std::runtime_error("Failed to execute insert");
    }

    int book_id = sqlite3_last_insert_rowid(db);
    sqlite3_finalize(stmt);

    RawBook result = book;
    result.id = book_id;
    return result;
}

std::optional<RawBook> DB::get_book_by_id(int book_id) {
    const char* sql = R"(
        SELECT id, title, author, file_url, downloaded
        FROM books
        WHERE id = ?
    )";

    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        return std::nullopt;
    }

    sqlite3_bind_int(stmt, 1, book_id);

    rc = sqlite3_step(stmt);
    if (rc == SQLITE_ROW) {
        RawBook book(
            sqlite3_column_int(stmt, 0),
            reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1)),
            reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2)),
            reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3)),
            sqlite3_column_int(stmt, 4) != 0
        );
        sqlite3_finalize(stmt);
        return book;
    }

    sqlite3_finalize(stmt);
    return std::nullopt;
}

std::vector<RawBook> DB::get_all_books() {
    const char* sql = R"(
        SELECT id, title, author, file_url, downloaded
        FROM books
    )";

    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        throw std::runtime_error("Failed to prepare statement");
    }

    std::vector<RawBook> books;
    while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
        RawBook book(
            sqlite3_column_int(stmt, 0),
            reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1)),
            reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2)),
            reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3)),
            sqlite3_column_int(stmt, 4) != 0
        );
        books.push_back(book);
    }

    sqlite3_finalize(stmt);
    return books;
}

void DB::update_download_status(int book_id, bool downloaded) {
    const char* sql = R"(
        UPDATE books
        SET downloaded = ?
        WHERE id = ?
    )";

    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        throw std::runtime_error("Failed to prepare statement");
    }

    sqlite3_bind_int(stmt, 1, downloaded ? 1 : 0);
    sqlite3_bind_int(stmt, 2, book_id);

    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    if (rc != SQLITE_DONE) {
        throw std::runtime_error("Failed to execute update");
    }
}
