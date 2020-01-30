#include "hiredis.h"
#include "client.h"
#include "quoteCacheClient.h"
#include <string.h>
#include <stdlib.h> 

stockQuote * buildStockQuoteObject(char * stockName, int quote) {
    stockQuote * sq = malloc(sizeof(stockQuote));
    sq -> stockName = malloc(strlen(stockName));
    strcpy(sq -> stockName, stockName);
    sq -> quote = quote;
    return sq;
}

stockQuote * cacheQuote(redisContext * c, char * stockName, int quote) {
    if (c == NULL) {
        printf("Error: must open client connection to redis server before invoking cacheQuote()\n");
        return NULL;
    }

    redisReply *reply = redisCommand(c,"SET %s %d", stockName, quote);
    stockQuote * sq = NULL;
    if (strcmp(reply -> str, "OK") == 0) {
        sq = buildStockQuoteObject(stockName, quote);
    }
    freeReplyObject(reply);
    return sq;
}

void removeQuote(redisContext * c, char * stockName) {
    if (c == NULL) {
        printf("Error: must open client connection to redis server before invoking cacheQuote()\n");
        return;
    }
    redisReply *reply = redisCommand(c,"DEL %s", stockName);
    freeReplyObject(reply);
}

stockQuote * getQuote(redisContext * c, char * stockName) {
    if (c == NULL) {
        printf("Error: must open client connection to redis server before invoking getQuote()\n");
        return NULL;
    }

    redisReply *reply;
    reply = redisCommand(c, "GET %s", stockName);
    stockQuote * result;
    if (reply != NULL && reply -> str != NULL) {
        int quote = atoi(reply -> str);
        result = buildStockQuoteObject(stockName, quote);
        freeReplyObject(reply);
        result -> status = EXISTS;
    } else {
        result = buildStockQuoteObject(stockName, 0);
        result -> status = NOT_EXISTS;
    }

    return result;
}

void freeQuoteObject(stockQuote * quote) {
    if (quote != NULL) {
        free(quote -> stockName);
        free(quote);
    }
}