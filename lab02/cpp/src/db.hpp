#ifndef DB_HPP
#define DB_HPP

#include <sqlite3.h>
#include <string>
#include <vector>
#include <optional>
#include "models.hpp"

class IDB {
public:
    virtual ~IDB() = default;
    virtual RawBook insert_book(const RawBook& book) = 0;
    virtual std::optional<RawBook> get_book_by_id(int book_id) = 0;
    virtual std::vector<RawBook> get_all_books() = 0;
    virtual void update_download_status(int book_id, bool downloaded) = 0;
};

class DB : public IDB {
private:
    std::string db_path;
    sqlite3* db;

    void create_tables();

public:
    explicit DB(const std::string& db_path);
    ~DB();

    RawBook insert_book(const RawBook& book) override;
    std::optional<RawBook> get_book_by_id(int book_id) override;
    std::vector<RawBook> get_all_books() override;
    void update_download_status(int book_id, bool downloaded) override;
};

#endif // DB_HPP
