#include "hiredis.h"
#include "transactionDBClient.h"
#include <string.h>
#include <stdlib.h>

void freeTransactionDataField(transactionDataField * dataField) {

}

void freetransactionLog(transactionLog * transObj) {

}

void freetransactionLogList(transactionLogList * list) {
    transactionListNode * curr = list -> head;
    transactionListNode * next;
    while (curr != NULL) {
        next = curr -> next;
        freeTransactionLogListNode(curr);
        curr = next;
    }
    free(list);
}

void freeTransactionLogListNode(transactionLogListNode * node) {
    if (node == NULL) {
        freetransactionLog(node -> data);
        if (node -> next != NULL) {
            freetransactionLog(node -> next -> data);
        }
        if (node -> prev != NULL) {
            freetransactionLog(node -> prev -> data);
        }
        free(node);
    }
}

transactionDataField * initTransactionDataField() {

}

transactionLog * initEmptyTransactionLog() {

}

transactionLogList * initEmptyTransactionLogList() {
    transactionLogList * list = malloc(sizeof(transactionLogList));
    list -> size = 0;
    list -> head = NULL;
    list -> tail = NULL;
    return list;
}

transactionLog * buildTransactionLogFromRedisReply(redisReply * reply) {

}

void addDataFieldToTransactionLog(transactionLog * log, transactionDataField * dataField){

}

void addTransactionLogToList(transactionLogList * logList, transactionLog * log) {
    transactionLogListNode * node = malloc(sizeof(transactionLogListNode));
    node -> data = log;
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

char * addtransactionDataFieldToRedisCommand(char * commandStr, transactionDataField * dataField) {
    char * fieldname = dataField -> field;
    char * value = dataField -> value;
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

char * persistTransactionLogs(redisContext * c, transactionLogsList * logs) {
    transactionLog * transaction;
    for (int i = 0; i < logs -> numFields; ++i) {
        log = logs[i];
        //if (transaction -> transactionId == NULL || transaction -> username == NULL) {
        //    printf("Error: invalid transaction object (transactionId or username fields are NULL)\n");
        //    return NULL;
        //}
        //char * username_transactionId = coallesceUsernameAndTransactionId(transaction -> username, transaction -> transactionId);
        //char * commandRedis = "HSET";
        //char * keyname = "username_transactionId";
        //int commandStrLen = sizeof(commandRedis) + 1 + sizeof(keyname) + 1 + sizeof(username_transactionId) + 1;
        //char * commandStr = malloc(commandStrLen);
        //memset(commandStr, 0, commandStrLen);
        //sprintf(commandStr, "%s %s %s ", commandRedis, keyname, username_transactionId);

        //char * dtsCommand = malloc(2);
        //memset(dtsCommand, 0, 2);
        //sprintf(dtsCommand, "%d", transaction -> command);
        //commandStr = addFieldToSetCommand(commandStr, "command", dtsCommand);
        //free(dtsCommand);

        //commandStr = addFieldToSetCommand(commandStr, "crytokey", transaction -> cryptokey);
        //commandStr = addFieldToSetCommand(commandStr, "stockSymbol", transaction -> stockSymbol);

        //char * amountStr;
        //int amountStrLen = 20;
        //amountStr = malloc(amountStrLen);
        //memset(amountStr, 0, amountStrLen);
        //sprintf(amountStr, "%d", transaction -> amount);
        //commandStr = addFieldToSetCommand(commandStr, "amount", amountStr);
        //free(amountStr);

        //redisReply * reply = redisCommand(c, commandStr);
        //freeReplyObject(reply);
        //return commandStr;
    }
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

transactionLog * getTransactionLog(redisContext * c, char * username, char * transactionId) {
    char * username_transactionId = coallesceUsernameAndTransactionId(username, transactionId);
    redisReply * reply = redisCommand(c, "HGETALL %s", username_transactionId);
    return buildTransactionLogFromRedisReply(reply);
}

transactionLogList * getAllUserTransactionLogs(redisContext * c, char * username) {
    return redisScan(c, "SCAN %d MATCH %s_**", username);
};

transactionLogList * getAllTransactionLogs(redisContext * c){
    return redisScan(c, "SCAN %d MATCH **_**", NULL);
};