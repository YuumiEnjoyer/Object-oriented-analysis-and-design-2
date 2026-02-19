#ifndef DOWNLOADER_HPP
#define DOWNLOADER_HPP

#include <string>
#include "models.hpp"

bool download(const RawBook& book, const std::string& destination_path);

#endif // DOWNLOADER_HPP
