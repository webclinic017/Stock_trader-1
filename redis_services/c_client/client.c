#include "hiredis.h"
#include <stdlib.h>
#include "quoteCacheTests.h"
#include "userDBTests.h"
#include "eventDBClientTests.h"
#include "transactionDBClientTests.h"

redisContext *c = NULL;

char * redisServerIp = "127.0.0.1";
int redisServerPort = 6379;

void openConnection() {
    c  = redisConnect(redisServerIp, redisServerPort);
    if (c == NULL || c->err) {
        if (c) {
            printf("%d\n", c->err);
            printf("Error: %s\n", c->errstr);
            redisFree(c);
            c = NULL;
        } else {
            printf("Can't allocate redis context\n");
        }
    }
}

void closeConnection() {
    if (c != NULL) {
        redisFree(c);
        c = NULL;
    }
}

int main(int argc, char **argv) {
    runQuoteCacheTests();
    runUserDBTests();
    runEventDBTests();
    runTransactionDBTests();
}