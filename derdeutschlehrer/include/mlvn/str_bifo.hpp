#include <string>
#include <mlvn/bifo.h>

namespace mlvn {
    enum class StrBIFOSide {
        SERVER = 0x00,
        CLIENT = 0x01
    };

    /**
     * @brief Simple connor-compliant FIFO abstraction layer
     */
    class StrBIFO {
    public:
        StrBIFO(StrBIFOSide side, const std::string name, const std::string path = "/tmp");
        virtual ~StrBIFO();

        void write(const std::string msg);
        std::string read();

        size_t buffer_size() const { return m_bufsz; }

    private:
        m_BIFO *m_bifo;
        size_t m_bufsz;
        char *m_buf;
    };
}