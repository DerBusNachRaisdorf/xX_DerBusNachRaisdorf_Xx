/**
 * @file bifo.h
 * @brief A connor-compliant fifo abstraction
 */

#ifndef MLVN_BIFO_H
#define MLVN_BIFO_H

#include <stddef.h>
#include <stdlib.h>
#include <unistd.h>

#ifdef __cplusplus
    extern "C" {
#endif

typedef enum m_BIFOSide {
    M_BIFO_SERVER = 0x00,
    M_BIFO_CLIENT = 0x01
} m_BIFOSide;

typedef struct m_BIFO m_BIFO;

m_BIFO *m_bifo_create(m_BIFOSide side, const char *name, const char *path);

void m_bifo_destroy(m_BIFO *bifo);

ssize_t m_bifo_read(m_BIFO *bifo, void *buf, size_t count);

ssize_t m_bifo_write(m_BIFO *bifo, const void *buf, size_t count);

#ifdef __cplusplus
    }
#endif

#endif /* MLVN_BIFO_H */
