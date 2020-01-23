#include "hiredis.h"
#include <string.h>
#include <stdlib.h> 

redisContext *c;

enum cacheRequestStatus {
    NOT_CACHED,
    CACHED
};

typedef struct stockQuote {
    enum cacheRequestStatus status;
    char * stockName;
    char * quote;
} stockQuote;

char * redisServerIp = "127.0.0.1";
int redisServerPort = 6379;

void openConnection() {
    c  = redisConnect(redisServerIp, redisServerPort);
    if (c == NULL || c->err) {
        if (c) {
            printf("%d\n", c->err);
            printf("Error: %s\n", c->errstr);
            // handle error
        } else {
            printf("Can't allocate redis context\n");
        }
    }
}

void closeConnection() {
    if (c != NULL) {
        redisFree(c);
    }
}

char * cacheQuote(char * stockName, int quote) {
    if (c == NULL) {
        printf("ERROR: must open client connection to redis server before invoking cacheQuote()");
        return NULL;
    }

    redisReply *reply = redisCommand(c,"SET %s %d", stockName, quote);
    char * result = NULL;
    if (reply != NULL) {
        result = reply->str;
    }
    
    freeReplyObject(reply);
    return result;
}

stockQuote * getQuote(char * stockName) {
    if (c == NULL) {
        printf("ERROR: must open client connection to redis server before invoking getQuote()");
        return NULL;
    }

    redisReply *reply;
    reply = redisCommand(c, "GET %s", stockName);
    stockQuote * result;
    if (reply != NULL) {
        result -> stockName = stockName;
        result -> quote = malloc(sizeof(reply->str));
        strcpy(result->quote, reply->str);
        freeReplyObject(reply);
        result -> status = CACHED;
    } else {
        result -> status = NOT_CACHED;
        result -> stockName = stockName;
        result -> quote = NULL;
    }
    return result;
}

int main(int argc, char **argv) {
    openConnection();
    cacheQuote("someStock", 300);
    stockQuote * quote = getQuote("someStock");
    printf("status: %d\n", quote -> status);
    printf("%s: $%s\n", quote -> stockName, quote -> quote);
    closeConnection();
}