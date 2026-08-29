#include <string_view>

int main() {
    const std::string_view value = "cpp";
    return value.size() == 3 ? 0 : 1;
}
