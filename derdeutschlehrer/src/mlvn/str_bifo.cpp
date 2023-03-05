#include <mlvn/str_bifo.hpp>
#include <iostream>

namespace mlvn {

    StrBIFO::StrBIFO(StrBIFOSide side, const std::string name, const std::string path)
    {
        m_bufsz = 2048;
        m_buf = (char *)malloc(m_bufsz);        
        m_bifo = m_bifo_create(static_cast<m_BIFOSide>(side), name.c_str(), path.c_str());
    }

    StrBIFO::~StrBIFO()
    {
        m_bifo_destroy(m_bifo);
    }

    void StrBIFO::write(const std::string msg)
    {
        size_t length = msg.size();
        std::cout << "sending " << length << " bytes!\n"; 
        m_bifo_write(m_bifo, &length, sizeof(size_t));
        m_bifo_write(m_bifo, msg.c_str(), msg.size());
    }

    std::string StrBIFO::read()
    {
        size_t length;
        m_bifo_read(m_bifo, (void *)&length, sizeof(size_t));
        std::cout << "receiving " << length << " bytes!\n"; 

        if (length >= m_bufsz) {
            m_bufsz = length + 1;
            char *new_buf = (char *)realloc(m_buf, m_bufsz);
            if (new_buf == NULL) {
                exit(-1);
            }
            m_buf = new_buf;
        }        

        m_bifo_read(m_bifo, (void *)m_buf, length);
        m_buf[length] = '\0';
        return std::string(m_buf);
    }
}