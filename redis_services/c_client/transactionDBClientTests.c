#include "transactionDBClient.h"
#include "client.h"
#include "hiredis.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>

transactionArgs * transactionArgsForTesting() {
    transactionArgs * args = buildEmptyArgsObject();
    args -> type = FINE_GRAINED_ARGS;
    args -> reply = NULL;

    args -> transactionId = malloc(sizeof("transaction1"));
    strcpy(args -> transactionId, "transaction1");

    args -> username = malloc(sizeof("user1"));
    strcpy(args -> username, "user1");

    args -> command = BUY;

    args -> cryptokey = malloc(sizeof("cryptokey123"));
    strcpy(args -> cryptokey, "cryptokey123");

    args -> stockSymbol = malloc(sizeof("someStock"));
    strcpy(args -> stockSymbol, "someStock");

    args -> amount = 100;
    return args;
}

void buildTransactionObject_successfullyBuildFromArgs() {
    transactionArgs * args = transactionArgsForTesting();
    transactionObject * transObj = buildTransactionObject(args);
    args = transactionArgsForTesting(); // args was freed in buildTransactionObject() function call
    assert(transObj != NULL);
    assert(strcmp(transObj -> transactionId, args -> transactionId) == 0);
    assert(strcmp(transObj -> username, args -> username) == 0);
    assert(transObj -> command == args -> command);
    assert(strcmp(transObj -> cryptokey, args -> cryptokey) == 0);
    assert(strcmp(transObj -> stockSymbol, args -> stockSymbol) == 0);
    assert(transObj -> amount == args -> amount);
    freeArgsObject(args);
    freeTransactionObject(transObj);
}

void newTransactionList_emptyTransactionListIsCreated() {
    transactionObject * transObj = buildTransactionObject(NULL);
    assert(transObj != NULL);
    assert(transObj -> transactionId == NULL);
    assert(transObj -> username == NULL);
    freeTransactionObject(transObj);
}

void buildTransactionObject_successfullyBuildFromReply() {
    transactionArgs * args = buildEmptyArgsObject();
    char * username_transactionId = "user1_transaction1";
    enum commandType command = SELL;
    char * cryptokey = "cryptokey123";
    char * stockSymbol = "someStock";
    int amount = 100;
    redisCommand(c, "DEL %s", username_transactionId);
    redisReply * reply = redisCommand(c, "HSET %s command %d cryptokey %s stockSymbol %s amount %d", username_transactionId, command, cryptokey, stockSymbol, amount);
    assert(reply -> integer == 4);
    freeReplyObject(reply);
    args -> reply = redisCommand(c, "HGETALL %s", username_transactionId);
    args -> type = REDIS_REPLY;
    args -> username_transactionId = malloc(sizeof(username_transactionId));
    strcpy(args -> username_transactionId, username_transactionId);
    transactionObject * transObj = buildTransactionObject(args);

    assert(strcmp(transObj -> transactionId, "transaction1") == 0);
    printf("%s\n", transObj -> username);
    assert(strcmp(transObj -> username, "user1") == 0);
    assert(transObj -> command == command);
    assert(strcmp(transObj -> cryptokey, cryptokey) == 0);
    assert(strcmp(transObj -> stockSymbol, stockSymbol) == 0);
    assert(transObj -> amount == amount);
    freeTransactionObject(transObj);
}

void addTransactionToList_threeNewItemsAreAddedToList() {

}

void addFieldToSetCommand_correctCommandIsBuilt() {

}

void newTransactionLog_newTransactionLogIsPersisted() {

}

void getTransactionLog_returnMatchingUserTransactionLogs() {

}

void getAllTransactionLogs_returnAllTransactionLogs() {

}

void runTransactionDBTests() {
    openConnection();
    //buildTransactionObject_successfullyBuildFromArgs();
    //newTransactionList_emptyTransactionListIsCreated();
    buildTransactionObject_successfullyBuildFromReply();
    addTransactionToList_threeNewItemsAreAddedToList();
    addFieldToSetCommand_correctCommandIsBuilt();
    newTransactionLog_newTransactionLogIsPersisted();
    getTransactionLog_returnMatchingUserTransactionLogs();
    getAllTransactionLogs_returnAllTransactionLogs();
    closeConnection();
}