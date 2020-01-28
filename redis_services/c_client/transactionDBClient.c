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
        int val;
    if (strcmp(field, "username_transactionId") == 0) {
        int valueLen = sizeof(value);
        char * buffer = malloc(valueLen);
        strtok(buffer, "_");
        transObj -> username = strtok(NULL, "_");
        transObj -> transactionId = strtok(NULL, "_");
        free(buffer);
    } else if (strcmp(field, "cryptokey") == 0) {
        transObj -> cryptokey = value;
    } else if (strcmp(field, "stockSymbol") == 0) {
        transObj -> stockSymbol = value;
    } else if (strcmp(field, "amount") == 0) {
        val = atoi(value);
        transObj -> amount = &val;
    } else if (strcmp(field, "command") == 0) {
        val = atoi(value);
        transObj -> command = (enum commandType *) &val;
    }
    else {
        // do nothing: field is not defined by transactionObject data type
    }
}

void freeArgsObject(transactionArgs * args) {
    if (args != NULL) {
        if (args -> reply != NULL) {
            free(args -> reply);
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
        if (args -> command != NULL) {
            free(args -> command);
        }
        if (args -> stockSymbol != NULL) {
            free(args -> stockSymbol);
        }
        if (args -> amount != NULL) {
            free(args -> amount);
        }
        free(args);
    }
}

transactionObject * buildTransactionObject(transactionArgs * args) {
    transactionObject * transObj = malloc(sizeof(transactionObject));
    transObj -> transactionId = NULL;
    transObj -> username = NULL;
    if (args != NULL) {
        if (args -> type == REDIS_REPLY && args -> reply != NULL) {
            redisReply * reply = args -> reply;
            int numReplyElements = reply -> elements;
            char * field;
            char * value;
            for (int i = 1; i < numReplyElements; i += 2) {
                field = (reply -> element)[i - 1] -> str;
                value = (reply -> element)[i] -> str;
                addFieldToTransactionObject(transObj, field, value);
            }
            return transObj;
        } else if (args -> type == FINE_GRAINED_ARGS) {
            transObj -> transactionId = args -> transactionId;
            transObj -> username = args -> username;
            transObj -> command = args -> command;
            transObj -> cryptokey = args -> cryptokey;
            transObj -> stockSymbol = args -> stockSymbol;
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
    freeTransactionObject(transObj);
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

char * newTransactionLog(redisContext * c, transactionObject * transaction) {
    if (transaction -> transactionId == NULL || transaction -> username == NULL) {
        printf("Error: invalid transaction object (transactionId or username fields are NULL)\n");
        return NULL;
    }
    int sizeUsername = sizeof(transaction -> username);
    int sizeTransactionId = sizeof(transaction -> transactionId);
    int sizeUsername_transactionId = sizeUsername + 1 + sizeTransactionId;
    char * username_transactionId = malloc(sizeUsername_transactionId);
    memset(username_transactionId, 0, sizeUsername_transactionId);
    int i, k = 0;
    for (k = 0; k < sizeUsername; ++k) {
        username_transactionId[i] = transaction -> username[k];
        i++;
    }
    for (k = 0; k < sizeTransactionId; ++k) {
        username_transactionId[i] = transaction -> transactionId[k];
        i++;
    }
    
    char * commandRedis = "HSET";
    char * keyname = "username_transactionId";
    int commandStrLen = sizeof(commandRedis) + 1 + sizeof(keyname) + 1 + sizeof(username_transactionId) + 1;
    char * commandStr = malloc(commandStrLen);
    memset(commandStr, 0, commandStrLen);
    sprintf(commandStr, "%s %s %s ", commandRedis, keyname, username_transactionId);

    char * dtsCommand;
    if (transaction -> command == NULL) {
        dtsCommand = "null";
    } else {
        dtsCommand = malloc(2);
        memset(dtsCommand, 0, 2);
        sprintf(dtsCommand, "%d", *(transaction -> command));
    }
    commandStr = addFieldToSetCommand(commandStr, "command", dtsCommand);
    free(dtsCommand);

    commandStr = addFieldToSetCommand(commandStr, "crytokey", transaction -> cryptokey);
    commandStr = addFieldToSetCommand(commandStr, "stockSymbol", transaction -> stockSymbol);

    char * amountStr;
    if (transaction -> amount == NULL) {
        amountStr = "null";
    }
    else {
        int amountStrLen = 20;
        amountStr = malloc(amountStrLen);
        memset(amountStr, 0, amountStrLen);
        sprintf(amountStr, "%d", *(transaction -> amount));
    }
    commandStr = addFieldToSetCommand(commandStr, "amount", amountStr);
    free(amountStr);

    redisReply * reply = redisCommand(c, commandStr);
    freeReplyObject(reply);
    return commandStr;
}

transactionList * redisScan(redisContext * c, char * scanCommand, char * username) {
    int cursor = 0;
    int failSafe = 1000000;
    transactionObject * transObj;
    redisReply * reply;
    if (username != NULL) {
        reply = redisCommand(c, scanCommand, cursor, username);
    } else {
        reply = redisCommand(c, scanCommand, cursor);
    }
    transactionArgs * args = malloc(sizeof(transactionArgs));
    args -> reply = reply;
    transObj = buildTransactionObject(args);
    transactionList * transactions = newTransactionList();
    addTransactionToList(transactions, transObj);
    
    while (reply -> integer > 0 && (failSafe--) > 0) {
        args = malloc(sizeof(transactionArgs));
        if (username != NULL) {
            args -> reply = redisCommand(c, scanCommand, cursor, username);
        } else {
            args -> reply = redisCommand(c, scanCommand, cursor);
        }
        transObj = buildTransactionObject(args);
        addTransactionToList(transactions, transObj);
        freeReplyObject(reply);
    }
    return transactions;
}

transactionList * getTransactionLog(redisContext * c, char * username) {
    char * scanCommand = "HSCAN %d MATCH %s_**";
    return redisScan(c, scanCommand, username);
};

transactionList * getAllTransactionLogs(redisContext * c) {
    return redisScan(c, "HSCAN %d", NULL);
};