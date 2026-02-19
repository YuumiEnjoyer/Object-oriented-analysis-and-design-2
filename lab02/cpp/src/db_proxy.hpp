#ifndef DB_PROXY_HPP
#define DB_PROXY_HPP

#include <unordered_map>
#include <memory>
#include "db.hpp"

class DBProxy {
private:
    std::string db_path;
    std::unique_ptr<IDB> db;
    std::unordered_map<int, RawBook> cache;

    IDB& get_db();

public:
    explicit DBProxy(const std::string& db_path);

    RawBook insert_book(const RawBook& book);
    std::optional<RawBook> get_book_by_id(int book_id);
    std::vector<RawBook> get_all_books();
    void update_download_status(int book_id, bool downloaded);
};

#endif // DB_PROXY_HPP
