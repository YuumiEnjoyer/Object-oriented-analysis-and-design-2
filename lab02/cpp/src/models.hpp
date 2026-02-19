#ifndef MODELS_HPP
#define MODELS_HPP

#include <string>
#include <filesystem>

struct RawBook {
    int id = -1;
    std::string title;
    std::string author;
    std::string file_url;
    bool downloaded = false;

    RawBook() = default;

    RawBook(int id, const std::string& title, const std::string& author,
            const std::string& file_url, bool downloaded = false)
        : id(id), title(title), author(author), file_url(file_url), downloaded(downloaded) {}

    std::string get_path() const {
        return (std::filesystem::path(author) / std::filesystem::path(title)).string();
    }
};

#endif // MODELS_HPP
