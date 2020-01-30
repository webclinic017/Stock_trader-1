#include "baseTypes.h"
#include "hiredis.h"

typedef struct transactionDataField {
    char * field;
    char * value;
    transactionDataField * next;
} transactionDataField;

typedef struct transactionLog {
    char * transactionId;
    char * username;
    int numDataFields;
    transactionDataField * head;
    transactionDataField * tail;
} transactionLog;

typedef struct transactionLogListNode {
    struct transactionLogListNode * prev;
    struct transactionLog * log;
    struct transactionLogListNode * next;
} transactionLogListNode;

typedef struct transactionLogList {
    int size;
    struct transactionLogListNode * head;
    struct transactionLogListNode * tail;
} transactionLogList;

void freeTransactionDataField(transactionDataField * dataField)
void freetransactionLog(transactionLog * transObj);
void freetransactionLogList(transactionLogList * list);
void freeTransactionLogListNode(transactionLogListNode * node);

transactionDataField * initTransactionDataField(char * field, char * value);
transactionLog * initEmptyTransactionLog();
transactionLogList * initEmptyTransactionLogList();

transactionLog * buildTransactionLogFromRedisReply(redisReply * reply);
void addDataFieldToTransactionLog(transactionLog * log, transactionDataField * dataField);
void addTransactionLogToList(transactionLogList * logList, transactionLog * log);
char * addtransactionDataFieldToRedisCommand(char * commandStr, transactionDataField * dataField);

char * coallesceUsernameAndTransactionId(char * username, char * transactionId);

char * persistTransactionLogs(redisContext * c, transactionLogsList * logs);
transactionLogList * redisScan(redisContext * c, char * scanCommand, char * username);
transactionLog * getTransactionLog(redisContext * c, char * username, char * transactionId);
transactionLogList * getAllUserTransactionLogs(redisContext * c, char * username);
transactionLogList * getAllTransactionLogs(redisContext * c);