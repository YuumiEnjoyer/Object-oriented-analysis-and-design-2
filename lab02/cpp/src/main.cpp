#include <iostream>
#include <gtkmm.h>
#include <memory>
#include "db_proxy.hpp"
#include "downloader.hpp"
#include "models.hpp"
#include "utils.hpp"

const std::string DB_PATH = "../storage/books.db";
const std::string DOWNLOAD_PATH = "../storage/downloads/";

class BookApp : public Gtk::Window {
private:
    Glib::RefPtr<Gtk::Builder> builder;

    Gtk::Box* books_container;

    std::unique_ptr<IDB> db;

    struct BookWidget {
        Gtk::Frame* frame;
        Gtk::Button* download_button;
    };

    std::map<int, BookWidget> book_widgets;

public:
    BookApp();
    virtual ~BookApp() = default;

protected:
    void add_book();
    void load_books_from_db();
    void add_book_to_ui(const RawBook& book);
    void download_book(const RawBook& book, Gtk::Button* button);
    void on_download_button_clicked(const RawBook& book, Gtk::Button* button);
};

BookApp::BookApp() {
    std::filesystem::create_directories(DOWNLOAD_PATH);
    db = std::make_unique<DBProxy>(DB_PATH);

    set_title("Библиотека книг");
    set_default_size(600, 500);

    auto top_box = Gtk::make_managed<Gtk::Box>(Gtk::Orientation::HORIZONTAL, 5);
    top_box->set_margin(10);

    auto scrolled_window = Gtk::make_managed<Gtk::ScrolledWindow>();
    scrolled_window->set_vexpand(true);
    scrolled_window->set_margin(10);

    books_container = Gtk::make_managed<Gtk::Box>(Gtk::Orientation::VERTICAL, 2);
    books_container->set_margin(5);

    scrolled_window->set_child(*books_container);

    auto main_box = Gtk::make_managed<Gtk::Box>(Gtk::Orientation::VERTICAL);
    main_box->append(*top_box);
    main_box->append(*scrolled_window);

    set_child(*main_box);

    load_books_from_db();
}

void BookApp::load_books_from_db() {
    try {
        auto books = db->get_all_books();
        for (const auto& book : books) {
            add_book_to_ui(book);
        }
    } catch (const std::exception& e) {
        std::cout << "Ошибка загрузки книг: " << e.what() << std::endl;
    }
}

void BookApp::add_book_to_ui(const RawBook& book) {
    auto frame = Gtk::make_managed<Gtk::Frame>();
    auto box = Gtk::make_managed<Gtk::Box>(Gtk::Orientation::HORIZONTAL, 5);
    box->set_margin(5);

    std::string book_info = book.author + " - " + book.title;
    auto label = Gtk::make_managed<Gtk::Label>(book_info);
    label->set_halign(Gtk::Align::START);
    label->set_hexpand(true);
    box->append(*label);

    auto download_button = Gtk::make_managed<Gtk::Button>();
    if (book.downloaded) {
        download_button->set_label("Скачано");
        download_button->set_sensitive(false);
    } else {
        download_button->set_label("Скачать");
        download_button->signal_clicked().connect(
            sigc::bind(sigc::mem_fun(*this, &BookApp::on_download_button_clicked), book, download_button)
        );
    }

    box->append(*download_button);
    frame->set_child(*box);
    books_container->append(*frame);

    BookWidget widget{frame, download_button};
    book_widgets[book.id] = widget;
}

void BookApp::on_download_button_clicked(const RawBook& book, Gtk::Button* button) {
    ThreadHelper::run_in_thread([this, book, button]() {
        download_book(book, button);
    });
}

void BookApp::download_book(const RawBook& book, Gtk::Button* button) {
    Glib::signal_idle().connect_once([button]() {
        button->set_sensitive(false);
        button->set_label("Скачивание...");
    });

    try {
        auto fresh_book = db->get_book_by_id(book.id);
        if (fresh_book && fresh_book->downloaded) {
            Glib::signal_idle().connect_once([button]() {
                button->set_label("Скачано");
                button->set_sensitive(false);
            });
            return;
        }

        std::string full_path = DOWNLOAD_PATH + book.get_path();
        if (::download(book, full_path)) {
            db->update_download_status(book.id, true);

            Glib::signal_idle().connect_once([button]() {
                button->set_label("Скачано");
                button->set_sensitive(false);
                std::cout << "Книга успешно скачана!\n";
            });
        } else {
            Glib::signal_idle().connect_once([button]() {
                button->set_sensitive(true);
                button->set_label("Скачать");
                std::cout << "Не удалось скачать книгу\n";
            });
        }
    } catch (const std::exception& e) {
        Glib::signal_idle().connect_once([button, e]() {
            button->set_sensitive(true);
            button->set_label("Скачать");
            std::cout << "Ошибка при скачивании: " << e.what() << std::endl;
        });
    }
}

int main(int argc, char* argv[]) {
    auto app = Gtk::Application::create("org.example.bookapp");

    return app->make_window_and_run<BookApp>(argc, argv);
}
