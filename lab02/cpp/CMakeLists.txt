cmake_minimum_required(VERSION 3.16)
project(ReadliLibrary)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/vcpkg/scripts/buildsystems/vcpkg.cmake" CACHE STRING "")

find_package(unofficial-sqlite3 CONFIG REQUIRED)
find_package(CURL CONFIG REQUIRED)
find_package(unofficial-gumbo CONFIG REQUIRED)
find_package(PkgConfig)
pkg_check_modules(GTKMM REQUIRED IMPORTED_TARGET gtkmm-4.0)
find_package(cpr CONFIG REQUIRED)


add_executable(bookapp
    src/main.cpp
    src/db.cpp
    src/db_proxy.cpp
    src/downloader.cpp
)

target_link_libraries(bookapp PRIVATE
    unofficial::sqlite3::sqlite3
    CURL::libcurl
    PkgConfig::GTKMM
    unofficial::gumbo::gumbo
    cpr::cpr
)
