/* UNIX stuff */
#include <unistd.h>
#include <dlfcn.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <semaphore.h>
#include <errno.h>

#include <stdio.h>
#include <stdlib.h>

#define SEM_NAME "/deutschlehrer_sem"
#define SEM_PERMS (S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP)
#define INITIAL_VALUE 1

int main()
{
    sem_t *semaphore;
        semaphore = sem_open(SEM_NAME, O_CREAT | O_EXCL, SEM_PERMS, INITIAL_VALUE);

    if (semaphore == SEM_FAILED) {
        perror("sem_open(3) error");
        semaphore = sem_open(SEM_NAME, O_RDWR);
    }
    if (semaphore == SEM_FAILED) {
        perror("sem_open(3) error");
        exit(-1);
    }

    int val = 1;
    sem_getvalue(semaphore, &val);
    while (val < 1) {
        sem_post(semaphore);
        sem_getvalue(semaphore, &val);
    }
}