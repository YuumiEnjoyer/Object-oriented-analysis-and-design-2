#include "downloader.hpp"
#include <curl/curl.h>
#include <filesystem>
#include <iostream>
#include <fstream>

size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::ofstream* file) {
    size_t totalSize = size * nmemb;
    file->write(static_cast<char*>(contents), totalSize);
    return totalSize;
}

bool download(const RawBook& book, const std::string& destination_path) {
    CURL* curl;
    CURLcode res = CURLE_OK;

    curl = curl_easy_init();
    if (!curl) {
        return false;
    }

    // Создаем директорию если она не существует
    std::filesystem::path path(destination_path);
    std::filesystem::create_directories(path.parent_path());

    std::ofstream file(destination_path, std::ios::binary);
    if (!file.is_open()) {
        curl_easy_cleanup(curl);
        return false;
    }

    curl_easy_setopt(curl, CURLOPT_URL, book.file_url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &file);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);

    res = curl_easy_perform(curl);

    file.close();
    curl_easy_cleanup(curl);

    return res == CURLE_OK;
}
