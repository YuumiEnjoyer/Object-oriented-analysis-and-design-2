#ifndef UTILS_HPP
#define UTILS_HPP

#include <string>
#include <thread>
#include <functional>

// Утилиты для работы с потоками и GUI
class ThreadHelper {
public:
    template<typename Func>
    static void run_in_thread(Func&& func) {
        std::thread t(std::forward<Func>(func));
        t.detach();
    }
};

#endif // UTILS_HPP
