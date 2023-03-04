/**
 * @file derdeutschlehrer.cpp
 * @author your name (you@domain.com)
 * @brief 
 * @version 0.1
 * @date 2023-03-03
 * 
 * @copyright Copyright (c) 2023
 * 
 * **Changelog**
 * 03.03.2023: 
 *  - kennt jzt Anglizismen
 *  - unterstützt jzt Umlaute, dafür aber deutlich langsamer lul
 */


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
#include <locale>
#include <codecvt>
#include <unistd.h>
#include <dlfcn.h>

#ifndef     OPTIMIZATION_LEVEL
    #define OPTIMIZATION_LEVEL 1
#endif

#ifndef     USE_ADVANCED_EDIT_DISTANCE
    #define USE_ADVANCED_EDIT_DISTANCE true
#endif

#ifndef     ENABLE_RANDOM_CITES
    #define ENABLE_RANDOM_CITES true
#endif

#ifndef     MIN_CITATION_TRIGGERWORD_LENGTH
    #define MIN_CITATION_TRIGGERWORD_LENGTH 10
#endif

std::wstring str_to_wstr(const std::string &str)
{
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> converter;
    std::wstring wide = converter.from_bytes(str);
    return wide;
}

std::wstring cstr_to_wstr(const char *str)
{
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> converter;
    std::wstring wide = converter.from_bytes(str);
    return wide;
}

std::string wstr_to_str(const std::wstring &str)
{
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> converter;
    std::string narrow = converter.to_bytes(str);
    return narrow;
}

bool m_iswletter(const wchar_t c)
{
    switch (c) {
        case L'Ü': case L'ü': case L'Ä': case L'ä':
        case L'Ö': case L'ö': case L'ß':
            return true;
        default:
            return iswalpha(c);
    }
}

bool m_iswlower(const wchar_t c)
{
    switch (c) {
        case L'ü': case L'ä': case L'ö': case L'ß':
            return true;
        default:
            return iswlower(c);
    }
}

bool m_iswupper(const wchar_t c)
{
    switch (c) {
        case L'Ü': case L'Ä': case L'Ö':
            return true;
        default:
            return iswupper(c);
    }
}

wchar_t m_towlower(const wchar_t c)
{
    switch (c) {
        case L'Ü': case L'ü':
            return L'ü';
        case L'Ä': case L'ä':
            return L'ä';
        case L'Ö': case L'ö':
            return L'ö';
        case L'ß':
            return L'ß';
        default:
            return towlower(c);
    }
}

wchar_t m_towupper(const wchar_t c)
{
    switch (c) {
        case L'Ü': case L'ü':
            return L'Ü';
        case L'Ä': case L'ä':
            return L'Ä';
        case L'Ö': case L'ö':
            return L'Ö';
        case L'ß':
            return L'ß';
        default:
            return towupper(c);
    }
}

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

template <typename T>
T min2(T a, T b)
{
    return a < b ? a : b;
}

int wchar_distance_h(const wchar_t c1, const wchar_t c2)
{
    wchar_t c1_lower = m_towlower(c1), c2_lower = m_towlower(c2);
    int dist = 5;
    switch (c1_lower) {
        case L'u':
            if (c2_lower == L'ü') {
                dist = min2(dist, 2);
            }
            break;
        case L'o':
            if (c2_lower == L'ö') {
                dist = min2(dist, 2);
            }
            break;
        case L'a':
            if (c2_lower == L'ä') {
                dist = min2(dist, 2);
            }
            break;
        case L's':
            if (c2_lower == L'ß') {
                dist = min2(dist, 2);
            }
            break;
        case L'e':
            if (c2_lower == L'é') {
                dist = min2(dist, 2);
            }
            break;
    }

    if (m_iswlower(c1) != m_iswlower(c2)) {
        dist += 1;
    }

    return dist;
}

int wchar_distance(const wchar_t c1, const wchar_t c2)
{
    if (c1 == c2) {
        return 0;
    } else if (m_towlower(c1) == m_towlower(c2)) {
        return 1;
    }

    return min2(wchar_distance_h(c1, c2), wchar_distance_h(c2, c1));
}

int edit_distance(const std::wstring &word1, const std::wstring &word2)
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
/*
            if (word1[i] == word2[j]) {
                cache.at(i, j) = cache.at(i+1, j+1);
            } else {
                cache.at(i, j) = wchar_distance(word1[i], word2[j]) + min3(
                    cache.at(i+1, j), cache.at(i, j+1), cache.at(i+1, j+1));
            }
*/
            if (word1[i] == word2[j]) {
                cache.at(i, j) = cache.at(i+1, j+1);
            } else if (m_towlower(word1[i]) == m_towlower(word2[j])) {
                cache.at(i, j) = 1 + cache.at(i+1, j+1);
                //cache.at(i, j) = 1 + min3(
                //    cache.at(i+1, j), cache.at(i, j+1), cache.at(i+1, j+1));
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
    std::wstring wstr = str_to_wstr(str);
    std::wstring wres = L"";
    for (const wchar_t c : wstr) {
        wres += m_towlower(c);
    }
    return wstr_to_str(wres);
}

enum class WordType {
    NONE,
    WORD,
    NOISE
};

struct WordInfo {
    WordInfo(WordType type, std::wstring val, bool begin, bool cap)
        : type(type), value(val), isBeginningOfSenctence(begin), capitalize(cap) {}

    WordType type;
    std::wstring value;
    std::wstring correction;
    bool isBeginningOfSenctence;
    bool capitalize;
};

std::vector<WordInfo> str_words(const std::string &str)
{
    std::wstring wstr = str_to_wstr(str);

    std::vector<WordInfo> res;
    std::wstring cur_word = L"";
    WordType cur_type = WordType::NONE;
    bool cur_is_beginning_of_sentence = true;
    bool capitalize = true;
    for (const wchar_t c : wstr) {
        switch (c) {
            case '.': case ',': case ':': case ';':
            case '-': case '_': case '!': case '?':
            case ' ': case '\t': case '\'':
                if (cur_type == WordType::WORD) {
                    res.emplace_back(cur_type, cur_word, cur_is_beginning_of_sentence, capitalize);
                    cur_word = L"";
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
                if (m_iswletter(c) && cur_type != WordType::WORD) {
                    res.emplace_back(cur_type, cur_word, cur_is_beginning_of_sentence, capitalize);
                    cur_word = L"";
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
    if (cur_word != L"") {
        res.emplace_back(cur_type, cur_word, cur_is_beginning_of_sentence, capitalize);
    }

    return res;
}

std::string unwords(const std::vector<WordInfo> words)
{
    std::string res = "";
    for (const WordInfo &word : words) {
        if (word.correction == L"" || word.value == word.correction) {
            res += wstr_to_str(word.value);
        } else {
            res += "(~~" + wstr_to_str(word.value) + "~~) " + wstr_to_str(word.correction);
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

#if ENABLE_RANDOM_CITES
    class EinZitat {
    public:
        EinZitat(std::string zitat="Bruda, was los?", std::string autor="Keyboard-Cat")
            : autor(autor), zitat(zitat) {}
        std::string autor, zitat;

        std::string to_string() { return "Um es mit den Worten von " + autor + " zu sagen: \n" + zitat; }
    };
#endif /* ENABLE_RANDOM_CITES */

struct CorrectionResult {
    CorrectionResult(std::string response, size_t words, size_t errors)
        : response(response), words(words), errors(errors) {}

    std::string response;
    size_t words;
    size_t errors;
};

class DerDeutschlehrer {
public:
    DerDeutschlehrer();

    std::wstring find_nearest_word(const std::wstring &word);
    CorrectionResult correct_message(const std::string &message);

    inline size_t known_words() const { return m_words.size(); }

#if ENABLE_RANDOM_CITES
    inline size_t known_citations() const { return m_cite_map.size(); }
#endif

private:
    void add_word(std::string &word);

    void load_wordlist(std::string filename);
    void load_text(std::string filename, std::string author);
    void load_commonerrorlist(std::string filename);

private:
    std::vector<std::string> m_words;
    std::unordered_map<std::string, std::string> m_wordmap;

#if ENABLE_RANDOM_CITES
    std::unordered_map<std::string, EinZitat> m_cite_map;
#endif
};

DerDeutschlehrer::DerDeutschlehrer()
{
    load_wordlist("wordlists/wordlist-german.txt");
    load_wordlist("wordlists/wordlist-german-expaneded.txt");
    load_wordlist("wordlists/wordlist-german-umgangsprache.txt");
    load_wordlist("wordlists/wordlist-german-anglizismen.txt");
    load_wordlist("wordlists/wordlist-german-insults.txt");
    load_commonerrorlist("wordlists/commonerrorlist-german.txt");
    load_text("wordlists/text-faust.txt", "Goethe");
    load_text("wordlists/text-faust2.txt", "Goethe");
    load_text("wordlists/text-faust3-chatgpt.txt", "Chat-GPT");
    load_text("wordlists/text-prometheus.txt", "Goethe");
    load_text("wordlists/text-woyzeck.txt", "Georg Büchner");
    load_text("wordlists/text-die-bruecke-am-tay.txt", "Theodor Fontane oder so");
    load_text("wordlists/text-die-buergschaft.txt", "Schiller aus der Schilleria");
    load_text("wordlists/text-linux.txt", "Richard Stallman");
    load_text("wordlists/text-kafka-das-urteil.txt", "Kafka");
    load_text("wordlists/text-kafka-die-verwandlung.txt", "Kafka");
}

std::wstring DerDeutschlehrer::find_nearest_word(const std::wstring &w_word)
{
    std::string word = wstr_to_str(w_word);

    auto it = m_wordmap.find(word);
    if (it != m_wordmap.end()) {
        return str_to_wstr(it->second);
    }
    it = m_wordmap.find(str_tolower(word));
    if (it != m_wordmap.end()) {
        return str_to_wstr(it->second);
    }

    int nearest_distance = INT_MAX;
    std::wstring nearest_word = L"Schnellgüterwagen";
    for (const std::string &cur_word : m_words) {
        std::wstring w_cur_word = str_to_wstr(cur_word);
        int cur_distance = edit_distance(w_word, w_cur_word);
        if (cur_distance < nearest_distance) {
            nearest_distance = cur_distance;
            nearest_word = w_cur_word;
        }
    }

    return nearest_word;
}

CorrectionResult DerDeutschlehrer::correct_message(const std::string &message)
{
    std::vector<WordInfo> words = str_words(message);
    size_t num_words = 0, num_errors = 0;

#if ENABLE_RANDOM_CITES
    std::string longest_cite_word = "";
#endif /* ENABLE_RANDOM_CITES */

    bool is_correct = true;
    for (WordInfo &word : words) {
        if (word.type == WordType::WORD) {
            num_words++;

            word.correction = find_nearest_word(word.value);

#if ENABLE_RANDOM_CITES
            std::string maybe_cite_word = wstr_to_str(word.correction);
            if (word.correction.size() > longest_cite_word.size() && m_cite_map.find(maybe_cite_word) != m_cite_map.end()) {
                longest_cite_word = maybe_cite_word;
            }
#endif /* ENABLE_RANDOM_CITES */

            // Anfangsbuchstabe am Satzanfang darf groß sein.
            if (!word.capitalize && word.isBeginningOfSenctence && word.value.size() != 0 &&
                word.correction[0] != word.value[0] &&
                word.correction.size() == word.value.size() &&
                word.correction[0] == m_towlower(word.value[0])) {
                bool isValid = true;
                for (size_t i = 1; i < word.value.size(); ++i) {
                    if (word.correction[i] != word.value[i]) {
                        isValid = false;
                        break;
                    }
                }
                if (isValid) {
                    word.correction = L"";
                } else {
                    is_correct = false;
                }
            } else if (word.correction == word.value) {
                word.correction = L"";
            } else if (word.correction != L"") {
                is_correct = false;
                if (word.capitalize) {
                    word.correction[0] = m_towupper(word.correction[0]);
                }
            }
            
            if (word.capitalize && word.correction == L"" && m_iswlower(word.value[0])) {
                word.correction = word.value;
                word.correction[0] = m_towupper(word.correction[0]);
                is_correct = false;
            }

            if (word.correction != L"" && word.correction != word.value) {
                num_errors++;
            }
        }
    }

    std::string response_message = is_correct ? "" : unwords(words);

#if ENABLE_RANDOM_CITES
    if (longest_cite_word.size() >= 5) {
        response_message = (is_correct ? "" : unwords(words) + "\n\nJedoch... ") + m_cite_map[longest_cite_word].to_string();
    }
#endif /* ENABLE_RANDOM_CITES */

    return CorrectionResult(response_message, num_words, num_errors);

}

void DerDeutschlehrer::add_word(std::string &word)
{
    std::string word_lower = str_tolower(word);

    auto it = m_wordmap.find(word);
    if (it != m_wordmap.end() && it->second == word) {
        return;
    }
    it = m_wordmap.find(word_lower);
    if (it != m_wordmap.end() && it->second == word) {
        return;
    }

    m_words.push_back(word);
    m_wordmap.insert(std::make_pair(word, word));
    m_wordmap.insert(std::make_pair(word_lower, word));
}

void DerDeutschlehrer::load_wordlist(std::string filename)
{
    std::string word;
    std::ifstream file(filename);
    while (std::getline(file, word)) {
        add_word(word);
    }
    file.close();
}

void DerDeutschlehrer::load_text(std::string filename, std::string author)
{
    std::string line;
    std::ifstream file(filename);

#if ENABLE_RANDOM_CITES
    std::string cur_paragraph = "";
    std::string cur_paragraph_longest_word = "";
#endif

    while (std::getline(file, line)) {

#if ENABLE_RANDOM_CITES
        if (line == "" || line == "\r") {
            if (cur_paragraph_longest_word.size() >= MIN_CITATION_TRIGGERWORD_LENGTH) {
                EinZitat zitat(cur_paragraph, author);
                m_cite_map.insert(std::make_pair(cur_paragraph_longest_word, zitat));
            }

            cur_paragraph = "";
            cur_paragraph_longest_word = "";
        } else {
            cur_paragraph += "> " + line + "\n";
        }
#endif /* ENABLE_RANDOM_CITES */

        /* process words */
        std::wstring wline = str_to_wstr(line);
        std::wstring wword = L"";
        for (size_t i = 0; i < wline.size() + 1; ++i) {
            wchar_t c = wline[i];
            if (m_iswletter(c)) {
                wword += c;
            } else {
                std::string word = wstr_to_str(wword);
                add_word(word);
                wword = L"";

#if ENABLE_RANDOM_CITES
                if (word.size() > cur_paragraph_longest_word.size() && m_cite_map.find(word) == m_cite_map.end()) {
                    cur_paragraph_longest_word = word;
                }
#endif /* ENABLE_RANDOM_CITES */
            }
        }
    }
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
        CorrectionResult result = d.correct_message(argv[1]);
        std::cout << result.response;
        std::cerr << result.errors << "/" << result.words;
        return 0;
    } else if (argc == 3) {
        if (strcmp(argv[1], "benchmark") == 0) {
            std::cout << "Build with" << (USE_ADVANCED_EDIT_DISTANCE ? "" : "out") << " Advanced Edit Distance " << "\n";

            std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
            CorrectionResult result = d.correct_message(argv[2]);
            std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();

            std::cout << result.response << "\n";
            std::cerr << result.errors << "/" << result.words << "\n";
            std::cout << "elapsed time: " << std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count() << "ms" << "\n";
            return 0;
        }
        return 1;
    }

    std::cout << "Isch kenne momentan " << d.known_words() << " Wörtahs." << std::endl;

#if ENABLE_RANDOM_CITES
    std::cout << "Isch kenne momentan " << d.known_citations() << " Zitate." << std::endl;
#endif

    for (;;) {
        std::string input;
        std::cout << "> ";
        std::getline(std::cin, input);

        std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
        CorrectionResult result = d.correct_message(input);
        std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();

        std::cout << "\n" << result.response << "\n";
        std::cerr << result.errors << "/" << result.words << "\n";

        std::cout << "elapsed time: " << std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count() << "ms" << "\n";
    }
}
