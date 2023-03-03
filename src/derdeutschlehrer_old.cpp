#include <limits.h>
#include <string>
#include <vector>
#include <unordered_map>
#include <iostream>
#include <fstream>
#include <ctype.h>
#include <sstream>
#include <chrono>
#include <string.h>

#include <unistd.h>
#include <dlfcn.h>

#ifndef OPTIMIZATION_LEVEL
    #define OPTIMIZATION_LEVEL 1
#endif

#define USE_ADVANCED_EDIT_DISTANCE true

template <typename T>
class Matrix {
public:
    Matrix(size_t rows, size_t cols)
        : m_rows(rows), m_cols(cols)
    {
        m_data = new T[rows * cols];
    }

    ~Matrix()
    {
        delete[] m_data;
    }

    T *operator[](size_t row)
    {
        return m_data + (row * m_cols);
    }

    T &at(size_t row, size_t col)
    {
        return m_data[row * m_cols + col];
    }

    void fill(T value)
    {
        for (size_t i = 0; i < m_rows * m_cols; ++i) {
            m_data[i] = value;
        }
    }

private:
    size_t m_rows, m_cols;
    T *m_data;
};

template <typename T>
T min3(T a, T b, T c)
{
    T ab = a < b ? a : b;
    return ab < c ? ab : c;
}

int edit_distance(const std::string &word1, const std::string &word2)
{
    size_t word1_len = word1.size();
    size_t word2_len = word2.size();

    Matrix<int> cache(word1_len + 1, word2_len + 1);
    cache.fill(INT_MAX);
    for (size_t j = 0; j < word1_len + 1; ++j) {
        cache.at(j, word2_len) = word1_len - j;
    }
    for (size_t i = 0; i < word2_len + 1; ++i) {
        cache.at(word1_len, i) = word2_len - i;
    }

    for (ssize_t i = word1_len - 1; i >= 0; --i) {
        for (ssize_t j = word2_len - 1; j >= 0; --j) {
#if USE_ADVANCED_EDIT_DISTANCE
            if (word1[i] == word2[j]) {
                cache.at(i, j) = cache.at(i+1, j+1);
            } else if (tolower(word1[i]) == tolower(word2[j])) {
                cache.at(i, j) = 1 + min3(
                    cache.at(i+1, j), cache.at(i, j+1), cache.at(i+1, j+1));
            } else {
                cache.at(i, j) = 2 + min3(
                    cache.at(i+1, j), cache.at(i, j+1), cache.at(i+1, j+1));
            }
#else
            if (word1[i] == word2[j]) {
                cache.at(i, j) = cache.at(i+1, j+1);
            } else {
                cache.at(i, j) = 1 + min3(
                    cache.at(i+1, j), cache.at(i, j+1), cache.at(i+1, j+1));
            }
#endif /* USE_ADVANCED_EDIT_DISTANCE */
        }
    }

    return cache.at(0, 0);
}

std::string str_tolower(const std::string &str)
{
    std::string res = "";
    for (const char c : str) {
        res += tolower(c);
    }
    return res;
}

enum class WordType {
    NONE,
    WORD,
    NOISE
};

struct WordInfo {
    WordInfo(WordType type, std::string val, bool begin, bool cap)
        : type(type), value(val), isBeginningOfSenctence(begin), capitalize(cap) {}

    WordType type;
    std::string value;
    std::string correction;
    bool isBeginningOfSenctence;
    bool capitalize;
};

std::vector<WordInfo> str_words(const std::string &str)
{
    std::vector<WordInfo> res;
    std::string cur_word = "";
    WordType cur_type = WordType::NONE;
    bool cur_is_beginning_of_sentence = true;
    bool capitalize = true;
    for (const char c : str) {
        switch (c) {
            case '.': case ',': case ':': case ';':
            case '-': case '_': case '!': case '?':
            case ' ': case '\t':
                if (cur_type == WordType::WORD) {
                    res.emplace_back(cur_type, cur_word, cur_is_beginning_of_sentence, capitalize);
                    cur_word = "";
                    cur_type = WordType::NONE;
                    cur_is_beginning_of_sentence = false;
                    capitalize = false;
                    break;
                }
            case '0': case '1': case '2': case '3': case '4':
            case '5': case '6': case '7': case '8': case '9':
                if (cur_type == WordType::NONE) {
                    cur_type = WordType::NOISE;
                }
                break;
            default:
                if (isalpha(c) && cur_type != WordType::WORD) {
                    res.emplace_back(cur_type, cur_word, cur_is_beginning_of_sentence, capitalize);
                    cur_word = "";
                    cur_type = WordType::WORD; 
                }
                break;
        }
        if (c == '.' || c == '!' || c == '?' || c == ':' || c == ';' ) {
            cur_is_beginning_of_sentence = true;
            capitalize = true;
        }
        if (c == '"' || c =='\'') {
            cur_is_beginning_of_sentence = true;
        }
        cur_word += c;
    }
    if (cur_word != "") {
        res.emplace_back(cur_type, cur_word, cur_is_beginning_of_sentence, capitalize);
    }

    return res;
}

std::string unwords(const std::vector<WordInfo> words)
{
    std::string res = "";
    for (const WordInfo &word : words) {
        if (word.correction == "" || word.value == word.correction) {
            res += word.value;
        } else {
            res += "(~~" + word.value + "~~) " + word.correction;
        }
    }
    return res;
}

std::vector<std::string> split(std::string &str)
{
    std::vector<std::string> res;
    std::stringstream sstream(str);
    std::string word;
    while (sstream >> word) {
        res.push_back(word);
    }
    return res;
}

class DerDeutschlehrer {
public:
    DerDeutschlehrer();

    std::string find_nearest_word(const std::string &word);
    std::string correct_message(const std::string &message);

private:
    void load_wordlist(std::string filename);
    void load_commonerrorlist(std::string filename);

private:
    std::vector<std::string> m_words;
    std::unordered_map<std::string, std::string> m_wordmap;
};

DerDeutschlehrer::DerDeutschlehrer()
{
    load_wordlist("wordlist-german.txt");
    load_wordlist("wordlist-german-expaneded.txt");
    load_wordlist("wordlist-german-umgangsprache.txt");
    load_wordlist("wordlist-german-anglizismen.txt");
    load_commonerrorlist("commonerrorlist-german.txt");
}

std::string DerDeutschlehrer::find_nearest_word(const std::string &word)
{
    auto it = m_wordmap.find(word);
    if (it != m_wordmap.end()) {
        return it->second;
    }
    it = m_wordmap.find(str_tolower(word));
    if (it != m_wordmap.end()) {
        return it->second;
    }

    int nearest_distance = INT_MAX;
    std::string nearest_word = "Schnellgüterwagen";
    for (const std::string &cur_word : m_words) {
        int cur_distance = edit_distance(word, cur_word);
        if (cur_distance < nearest_distance) {
            nearest_distance = cur_distance;
            nearest_word = cur_word;
        }
    }

    return nearest_word;
}

std::string DerDeutschlehrer::correct_message(const std::string &message)
{
    std::vector<WordInfo> words = str_words(message);
    bool is_correct = true;
    for (WordInfo &word : words) {
        if (word.type == WordType::WORD) {
            word.correction = find_nearest_word(word.value);
            // Anfangsbuchstabe am Satzanfang darf groß sein.
            if (!word.capitalize && word.isBeginningOfSenctence && word.value.size() != 0 &&
                word.correction[0] != word.value[0] &&
                word.correction.size() == word.value.size() &&
                word.correction[0] == tolower(word.value[0])) {
                bool isValid = true;
                for (size_t i = 1; i < word.value.size(); ++i) {
                    if (word.correction[i] != word.value[i]) {
                        isValid = false;
                        break;
                    }
                }
                if (isValid) {
                    word.correction = "";
                } else {
                    is_correct = false;
                }
            } else if (word.correction == word.value) {
                word.correction = "";
            } else if (word.correction != "") {
                is_correct = false;
                if (word.capitalize) {
                    word.correction[0] = toupper(word.correction[0]);
                }
            }
            
            if (word.capitalize && word.correction == "" && islower(word.value[0])) {
                word.correction = word.value;
                word.correction[0] = toupper(word.correction[0]);
                is_correct = false;
            }
        }
    }
    return is_correct ? "" : unwords(words);
}

void DerDeutschlehrer::load_wordlist(std::string filename)
{
    std::string word;
    std::ifstream file(filename);
    while (std::getline(file, word)) {
        std::string word_lower = str_tolower(word);

        auto it = m_wordmap.find(word);
        if (it != m_wordmap.end() && it->second == word) {
            continue;
        }
        it = m_wordmap.find(word_lower);
        if (it != m_wordmap.end() && it->second == word) {
            continue;
        }

        m_words.push_back(word);
        m_wordmap.insert(std::make_pair(word, word));
        m_wordmap.insert(std::make_pair(word_lower, word));
    }
    file.close();
}

void DerDeutschlehrer::load_commonerrorlist(std::string filename)
{
    std::string line;
    std::ifstream file(filename);
    while (std::getline(file, line)) {
        std::vector<std::string> entry = split(line);
        if (entry.size() < 2) {
            continue;
        }
        for (auto it = entry.begin(); it != entry.end() - 1; ++it) {
            m_wordmap.insert(std::make_pair(str_tolower(*it), *(entry.end() - 1)));
        }
    }
}

int main(int argc, char **argv)
{
    DerDeutschlehrer d;

    if (argc == 2) {
        std::cout << d.correct_message(argv[1]);
        return 0;
    } else if (argc == 3) {
        if (strcmp(argv[1], "benchmark") == 0) {
            std::cout << "Build with Optimization Level " << OPTIMIZATION_LEVEL << "\n";

            std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
            std::string correct = d.correct_message(argv[2]);
            std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();

            std::cout << correct << "\n";
            std::cout << "elapsed time: " << std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count() << "ms" << "\n";
            return 0;
        }
        return 1;
    }

    for (;;) {
        std::string input;
        std::cout << "> ";
        std::getline(std::cin, input);

        std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
        std::string correct = d.correct_message(input);
        std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();

        std::string response = correct == "" ? "correct" : correct;
        std::cout << "\n" << correct << "\n";

        std::cout << "elapsed time: " << std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count() << "ms" << "\n";
    }
}
