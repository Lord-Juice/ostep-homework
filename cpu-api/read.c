#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <unistd.h>

void wait_or_die() {
    int rc = wait(NULL);
    assert(rc > 0);
}

int fork_or_die() {
    int rc = fork();
    assert(rc >= 0);
    return rc;
}

int main(int argc, char *argv[]) {
    // process a
    if (fork_or_die() == 0) {
        sleep(7);
        // process b
        exit(0);
    }
    wait_or_die();
    if (fork_or_die() == 0) {
        sleep(6);
        // process c
        exit(0);
    }
    wait_or_die();
    if (fork_or_die() == 0) {
        sleep(5);
        // process d
        exit(0);
    }
    wait_or_die();
    if (fork_or_die() == 0) {
        sleep(3);
        // process e
        exit(0);
    }
    wait_or_die();
    return 0;
}

