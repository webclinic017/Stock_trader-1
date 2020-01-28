#include "baseTypes.h"
#include "hiredis.h"

enum transactionArgsType {
    REDIS_REPLY,
    FINE_GRAINED_ARGS
};

typedef struct transactionArgs {
    enum transactionArgsType type;
    redisReply * reply;
    char * transactionId;
    char * username;
    enum commandType * command;
    char * cryptokey;
    char * stockSymbol;
    int * amount;
} transactionArgs;

typedef struct transactionListNode {
    struct transactionListNode * prev;
    struct transactionObject * data;
    struct transactionListNode * next;
} transactionListNode;

typedef struct transactionList {
    int size;
    struct transactionListNode * head;
    struct transactionListNode * tail;
} transactionList;

typedef struct transactionObject {
    char * transactionId;
    enum commandType * command;
    char * cryptokey;
    char * username;
    char * stockSymbol;
    int * amount;
} transactionObject;

void freeArgsObject(transactionArgs * args);
void freeTransactionObject(transactionObject * transObj);
void freeTransactionList(transactionList * list);
void freeTransactionNode(transactionListNode * node);
transactionObject * buildTransactionObject(transactionArgs * args);
transactionList * newTransactionList();
void addTransactionToList(transactionList * list, transactionObject * transObj);
char * addFieldToSetCommand(char * commandStr, char * fieldname, char * value);
char * newTransactionLog(redisContext * c, transactionObject * transaction);
transactionList * redisScan(redisContext * c, char * scanCommand, char * username);
transactionList * getTransactionLog(redisContext * c, char * username);
transactionList * getAllTransactionLogs(redisContext * c);