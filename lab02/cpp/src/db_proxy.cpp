#include "db_proxy.hpp"

DBProxy::DBProxy(const std::string& db_path) : db_path(db_path) {}

IDB& DBProxy::get_db() {
    if (!db) {
        db = std::make_unique<DB>(db_path);
    }
    return *db;
}

RawBook DBProxy::insert_book(const RawBook& book) {
    RawBook result = get_db().insert_book(book);
    cache[result.id] = result;
    return result;
}

std::optional<RawBook> DBProxy::get_book_by_id(int book_id) {
    auto it = cache.find(book_id);
    if (it != cache.end()) {
        return it->second;
    }

    auto book = get_db().get_book_by_id(book_id);
    if (book) {
        cache[book_id] = *book;
    }
    return book;
}

std::vector<RawBook> DBProxy::get_all_books() {
    return get_db().get_all_books();
}

void DBProxy::update_download_status(int book_id, bool downloaded) {
    get_db().update_download_status(book_id, downloaded);

    auto it = cache.find(book_id);
    if (it != cache.end()) {
        it->second.downloaded = downloaded;
    }
}
