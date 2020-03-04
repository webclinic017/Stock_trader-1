#include "hiredis.h"
#include "userDBClient.h"
#include <string.h>
#include <stdlib.h>

User * getUser(redisContext * c, char * username) {
    if (c == NULL) {
        printf("Error: must open client connection to redis server before invoking getQuote()\n");
        return NULL;
    }

    redisReply *reply;
    reply = redisCommand(c, "GET %s", username);
    User * user = malloc(sizeof(User));
    user -> username = malloc(strlen(username));
    strcpy(user -> username, username);
    if (reply != NULL && reply -> str != NULL) {
        user -> amount = atoi(reply->str);
        freeReplyObject(reply);
        user -> status = EXISTS;
    } else {
        user -> status = NOT_EXISTS;
        user -> amount = 0;
    }
    return user;
}

User * addNewUser(redisContext * c, char * username) {

    if (c == NULL) {
        printf("Error: must open client connection to redis server before invoking cacheQuote()\n");
        return NULL;
    }

    redisReply *reply = redisCommand(c, "SET %s %d", username, 0);
    User * user = NULL;

    if (reply != NULL && strcmp(reply -> str, "OK") == 0) {

        user = getUser(c, username);
    }
    
    freeReplyObject(reply);
    return user;
}


User * addUserAmount(redisContext * c, char * username, int amount) {
    if (c == NULL) {
        printf("Error: must open client connection to redis server before invoking cacheQuote()\n");
        return NULL;
    }

    User * user = getUser(c, username);

    if (user == NULL || (user -> status) == NOT_EXISTS) {
        user = addNewUser(c, username);
    }
    
    int prevAmount = user -> amount;

    amount = prevAmount + amount;
    redisReply *reply = redisCommand(c,"SET %s %d", username, amount);
    freeUserObject(user);
    if (reply != NULL && strcmp(reply -> str, "OK") == 0) {
        user = getUser(c, username);
    }
    
    freeReplyObject(reply);
    return user;
}

User * subtractUserAmount(redisContext * c, char * username, int amountToSubtract) {
    return addUserAmount(c, username, -1 * amountToSubtract);
}

void removeUser(redisContext * c, char * username) {
    if (c == NULL) {
        printf("Error: must open client connection to redis server before invoking cacheQuote()\n");
        return;
    }
    redisReply *reply = redisCommand(c,"DEL %s", username);
    freeReplyObject(reply);
}

void freeUserObject(User * user) {
    free(user -> username);
    free(user);
}