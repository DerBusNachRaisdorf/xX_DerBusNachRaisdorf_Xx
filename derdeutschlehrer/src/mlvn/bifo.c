#include <mlvn/bifo.h>

#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

struct m_BIFO {
    int fd_send, fd_recv;
};

m_BIFO *m_bifo_create(m_BIFOSide side, const char *name, const char *path)
{
    m_BIFO *bifo = NULL;
    size_t server_filename_len, client_filename_len;
    char  *server_filename,    *client_filename;

    server_filename_len = snprintf(NULL, 0, "%s/%s.server", path, name) + 1;
    client_filename_len = snprintf(NULL, 0, "%s/%s.client", path, name) + 1;
    server_filename     = malloc(server_filename_len);
    client_filename     = malloc(client_filename_len);
    if (server_filename == NULL || client_filename == NULL) {
        goto cleanup;
    }
    snprintf(server_filename, server_filename_len, "%s/%s.server", path, name);
    snprintf(client_filename, client_filename_len, "%s/%s.client", path, name);

    /* create fifos if they do not already exist. */
    mkfifo(server_filename, 0666);
    mkfifo(client_filename, 0666);

    bifo = malloc(sizeof(*bifo));
    if (bifo == NULL) {
        goto cleanup;
    }

    int server_fd = open(server_filename, O_RDWR);
    int client_fd = open(client_filename, O_RDWR);

    if (side == M_BIFO_SERVER) {
        bifo->fd_send = server_fd;
        bifo->fd_recv = client_fd;
    } else {
        bifo->fd_send = client_fd;
        bifo->fd_recv = server_fd;
    }

cleanup:
    free(server_filename);
    free(client_filename);

    return bifo;
}

void m_bifo_destroy(m_BIFO *bifo)
{
    close(bifo->fd_send);
    close(bifo->fd_recv);
    free(bifo);
}

ssize_t m_bifo_read(m_BIFO *bifo, void *buf, size_t count)
{
    return read(bifo->fd_recv, buf, count);
}

ssize_t m_bifo_write(m_BIFO *bifo, const void *buf, size_t count)
{
    return write(bifo->fd_send, buf, count);
}
