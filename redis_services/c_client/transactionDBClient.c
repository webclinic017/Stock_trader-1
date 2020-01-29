#include "hiredis.h"
#include "transactionDBClient.h"
#include <string.h>
#include <stdlib.h>

void freeTransactionObject(transactionObject * transObj) {
    if (transObj != NULL) {
        if (transObj -> transactionId != NULL) {
            free(transObj -> transactionId);
        }
        if (transObj -> cryptokey != NULL) {
            free(transObj -> cryptokey);
        }
        if (transObj -> username != NULL) {
            free(transObj -> username);
        }
        if (transObj -> stockSymbol != NULL) {
            free(transObj -> stockSymbol);
        }
        free(transObj);
    }
}

void addFieldToTransactionObject(transactionObject * transObj, char * field, char * value) {
    if (strcmp(field, "cryptokey") == 0) {
        transObj -> cryptokey = value;
    } else if (strcmp(field, "stockSymbol") == 0) {
        transObj -> stockSymbol = value;
    } else if (strcmp(field, "amount") == 0) {
        transObj -> amount = atoi(value);
    } else if (strcmp(field, "command") == 0) {
        transObj -> command = atoi(value);
    }
    else {
        // do nothing: field is not defined by transactionObject data type
    }
}

transactionArgs * buildEmptyArgsObject() {
    transactionArgs * args = malloc(sizeof(transactionArgs));
    enum transactionArgsType type;
    redisReply * reply = NULL;
    args -> transactionId = NULL;
    args -> username = NULL;
    args -> username_transactionId = NULL;
    args -> cryptokey = NULL;
    args -> stockSymbol = NULL;
    args -> command = NONE;
    args -> amount = 0;
    return args;
}

void freeArgsObject(transactionArgs * args) {
    if (args != NULL) {
        if (args -> reply != NULL) {
            freeReplyObject(args -> reply);
        }
        if (args -> transactionId != NULL) {
            free(args -> transactionId);
        }
        if (args -> username != NULL) {
            free(args -> username);
        }
        if (args -> cryptokey != NULL) {
            free(args -> cryptokey);
        }
        if (args -> stockSymbol != NULL) {
            free(args -> stockSymbol);
        }
        free(args);
    }
}

transactionObject * buildTransactionObject(transactionArgs * args) {
    transactionObject * transObj = malloc(sizeof(transactionObject));
    transObj -> transactionId = NULL;
    transObj -> username = NULL;
    transObj -> command = NONE;
    transObj -> cryptokey = NULL;
    transObj -> stockSymbol = NULL;
    transObj -> amount = 0;
    if (args != NULL) {
        if (args -> type == REDIS_REPLY && args -> reply != NULL) {
            int lenUsernameTransactionId = sizeof(args -> username_transactionId);
            char * buffer = malloc(lenUsernameTransactionId);
            memset(buffer, 0, lenUsernameTransactionId);
            strcpy(buffer, args -> username_transactionId);

            char * username = strtok(buffer, "_");
            transObj -> username = malloc(sizeof(username));
            strcpy(transObj -> username, username);
            free(buffer);
            buffer = malloc(lenUsernameTransactionId);
            memset(buffer, 0, lenUsernameTransactionId);

            strcpy(buffer, args -> username_transactionId);
            strtok(buffer, "_");
            char * transactionId = strtok(NULL, "_");
            transObj -> transactionId = malloc(sizeof(transactionId));
            strcpy(transObj -> transactionId, transactionId);

            redisReply * reply = args -> reply;
            int numReplyElements = reply -> elements;
            char * field;
            char * value;

            for (int i = 1; i < numReplyElements; i += 2) {
                field = (reply -> element)[i - 1] -> str;
                value = (reply -> element)[i] -> str;
                addFieldToTransactionObject(transObj, field, value);
            }
        } else if (args -> type == FINE_GRAINED_ARGS) {
            transObj -> transactionId = malloc(sizeof(args -> transactionId));
            strcpy(transObj -> transactionId, args -> transactionId);
            transObj -> username = malloc(sizeof(args -> username));
            strcpy(transObj -> username,  args -> username);
            transObj -> command = args -> command;
            transObj -> cryptokey = malloc(sizeof(args -> cryptokey));
            strcpy(transObj -> cryptokey, args -> cryptokey);
            transObj -> stockSymbol = malloc(sizeof(args -> stockSymbol));
            strcpy(transObj -> stockSymbol, args -> stockSymbol);
            transObj -> amount = args -> amount;
        }
        freeArgsObject(args);
    }

    return transObj;
}

transactionList * newTransactionList() {
    transactionList * list = malloc(sizeof(transactionList));
    list -> size = 0;
    list -> head = NULL;
    list -> tail = NULL;
    return list;
}

void freeTransactionList(transactionList * list) {
    transactionListNode * curr = list -> head;
    transactionListNode * next;
    while (curr != NULL) {
        next = curr -> next;
        freeTransactionNode(curr);
        curr = next;
    }
    free(list);
}

void freeTransactionNode(transactionListNode * node) {
    if (node == NULL) {
        freeTransactionObject(node -> data);
        if (node -> next != NULL) {
            freeTransactionObject(node -> next -> data);
        }
        if (node -> prev != NULL) {
            freeTransactionObject(node -> prev -> data);
        }
        free(node);
    }
}

void addTransactionToList(transactionList * list, transactionObject * transObj) {
    transactionListNode * node = malloc(sizeof(transactionListNode));
    node -> data = transObj;
    node -> next = NULL;
    node -> prev = NULL;
    if (list -> head == NULL) {
        list -> head = node;
        list -> tail = node;
    } else {
        list -> tail -> next = node;
        node -> prev = (list -> tail);
        list -> tail = node;
    }
    list -> size = (list -> size)++;
}

char * addFieldToSetCommand(char * commandStr, char * fieldname, char * value) {
    char space = ' ';
    int newCommandStrLen = sizeof(commandStr) + 1 + sizeof(fieldname) + 1 + sizeof(value) + 1;
    char * newCommandStr = malloc(newCommandStrLen);
    memset(newCommandStr, 0, newCommandStrLen);
    int i, k = 0;
    for (k = 0; k < sizeof(commandStr); ++k) {
        newCommandStr[i] = commandStr[k];
        i++;
    }
    newCommandStr[i] = space;
    for (k = 0; k < sizeof(fieldname); ++k) {
        newCommandStr[i] = fieldname[k];
        i++;
    }
    newCommandStr[i] = space;
    for (k = 0; k < sizeof(fieldname); ++k) {
        newCommandStr[i] = value[k];
        i++;
    }
    newCommandStr[i] = space;
    free(commandStr);
    return newCommandStr;
}

char * coallesceUsernameAndTransactionId(char * username, char * transactionId) {
    int sizeUsername = sizeof(username);
    int sizeTransactionId = sizeof(transactionId);
    int sizeUsername_transactionId = sizeUsername + 1 + sizeTransactionId;
    char * username_transactionId = malloc(sizeUsername_transactionId);
    memset(username_transactionId, 0, sizeUsername_transactionId);
    int i, k = 0;
    for (k = 0; k < sizeUsername; ++k) {
        username_transactionId[i] = username[k];
        i++;
    }
    for (k = 0; k < sizeTransactionId; ++k) {
        username_transactionId[i] = transactionId[k];
        i++;
    }
    return username_transactionId;
}

char * newTransactionLog(redisContext * c, transactionObject * transaction) {
    if (transaction -> transactionId == NULL || transaction -> username == NULL) {
        printf("Error: invalid transaction object (transactionId or username fields are NULL)\n");
        return NULL;
    }
    char * username_transactionId = coallesceUsernameAndTransactionId(transaction -> username, transaction -> transactionId);
    char * commandRedis = "HSET";
    char * keyname = "username_transactionId";
    int commandStrLen = sizeof(commandRedis) + 1 + sizeof(keyname) + 1 + sizeof(username_transactionId) + 1;
    char * commandStr = malloc(commandStrLen);
    memset(commandStr, 0, commandStrLen);
    sprintf(commandStr, "%s %s %s ", commandRedis, keyname, username_transactionId);

    char * dtsCommand = malloc(2);
    memset(dtsCommand, 0, 2);
    sprintf(dtsCommand, "%d", transaction -> command);
    commandStr = addFieldToSetCommand(commandStr, "command", dtsCommand);
    free(dtsCommand);

    commandStr = addFieldToSetCommand(commandStr, "crytokey", transaction -> cryptokey);
    commandStr = addFieldToSetCommand(commandStr, "stockSymbol", transaction -> stockSymbol);

    char * amountStr;
    int amountStrLen = 20;
    amountStr = malloc(amountStrLen);
    memset(amountStr, 0, amountStrLen);
    sprintf(amountStr, "%d", transaction -> amount);
    commandStr = addFieldToSetCommand(commandStr, "amount", amountStr);
    free(amountStr);

    redisReply * reply = redisCommand(c, commandStr);
    freeReplyObject(reply);
    return commandStr;
}

transactionList * redisScan(redisContext * c, char * scanCommand, char * username) {

    // TODO: revisit what this function is doing, based on new understanding of redis' SCAN command

    int cursor = 0;
    int failSafe = 1000000;
    transactionObject * transObj;
    redisReply * reply;
    if (username != NULL) {
        reply = redisCommand(c, scanCommand, cursor, username);
    } else {
        reply = redisCommand(c, scanCommand, cursor);
    }
    transactionArgs * args = buildEmptyArgsObject();
    args -> type = REDIS_REPLY;
    args -> reply = reply;
    transObj = buildTransactionObject(args);

    transactionList * transactions = newTransactionList();
    addTransactionToList(transactions, transObj);
    
    while (reply -> integer > 0 && (failSafe--) > 0) {
        args = buildEmptyArgsObject();
        if (username != NULL) {
            args -> reply = redisCommand(c, scanCommand, cursor, username);
        } else {
            args -> reply = redisCommand(c, scanCommand, cursor);
        }
        transObj = buildTransactionObject(args);
        char * username_transactionId = reply -> element[1] -> str;
        args -> username_transactionId = malloc(sizeof(username_transactionId));
        strcpy(args -> username_transactionId, username_transactionId);
        transactionArgs * args = buildEmptyArgsObject();
        addTransactionToList(transactions, transObj);
    }
    return transactions;
}

transactionObject * getTransactionLog(redisContext * c, char * username, char * transactionId) {
    transactionArgs * args = buildEmptyArgsObject();
    args -> type = REDIS_REPLY;
    char * username_transactionId = coallesceUsernameAndTransactionId(username, transactionId);
    args -> reply = redisCommand(c, "HGETALL %s", username_transactionId);
    args -> username_transactionId = malloc(sizeof(username_transactionId));
    strcpy(args -> username_transactionId, username_transactionId);
    return buildTransactionObject(args);
}

transactionList * getAllUserTransactionLogs(redisContext * c, char * username) {
    return redisScan(c, "SCAN %d MATCH %s_**", username);
};

transactionList * getAllTransactionLogs(redisContext * c) {
    return redisScan(c, "SCAN %d MATCH **_**", NULL);
};