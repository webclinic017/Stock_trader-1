#include "auditLogDBClient.h"

int transaction_num = 0;
typedef enum ResponseCode {
    SUCCESS,
    ERROR
};

typedef struct Response {
    enum ResponseCode code;
    const char * serializedData;
} Response;

typedef struct UserCommand {
    const char * username;
    const char * serializedData;
} UserCommand;

Response initResponse();
UserCommand initUserCommand(const char * username, const char * serializedData);

int getCurrentTransactionNum();
int getNextTransactionNum();
Response insertLog(AuditLogEntry * entry);
Response getLogs(UserCommand * data);
Response logDumplog(UserCommand * data);