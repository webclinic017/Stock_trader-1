#include "baseTypes.h"
#include "hiredis.h"

typedef struct AuditLogEntryField {
    char * field;
    char * value;
    struct AuditLogEntryField * next;
} AuditLogEntryField;

typedef struct AuditLogEntry {
    int entryId;
    const char * username;
    size_t numFields;
    const char * commandType;
    struct AuditLogEntryField * head;
    struct AuditLogEntryField * tail;
} AuditLogEntry;

typedef struct AuditLogListNode {
    struct AuditLogListNode * prev;
    struct AuditLogEntry * curr;
    struct AuditLogListNode * next;
} AuditLogListNode;

typedef struct AuditLogList {
    int size;
    struct AuditLogListNode * head;
    struct AuditLogListNode * tail;
} AuditLogList;

void freeAuditLogEntryField(AuditLogEntryField * dataField);
void freeAuditLogEntry(AuditLogEntry * auditLogEntry);
void freeAuditLogListNode(AuditLogListNode * node);
void freeAuditLogList(AuditLogList * list);

AuditLogEntryField * initAuditEntryField(char * field, char * value);
AuditLogEntry * initEmptyAuditLogEntry(const char * commandType, int entryId);
AuditLogListNode * initEmptyAuditLogListNode();
AuditLogList * initEmptyAuditLogList();

int nextAuditLogEntryId();
char * joinUsernameAndEntryId(char * username, int eventId);
AuditLogEntry * buildAuditLogEntryFromRedisArrayReply(redisReply * reply, char * username_entryId);
void addDataFieldToAuditLogEntry(AuditLogEntry * entry, AuditLogEntryField * dataField);
void addAuditLogEntryToList(AuditLogList * logList, AuditLogEntry * entry);
redisReply * putAuditLogEntry(redisContext * c, AuditLogEntry * entry, const char * username);
void _addAuditLogEntriesFromRedisArrayReplyOfKeysToLogList(redisContext * c, AuditLogList * logList, redisReply * redisArrayReplyOfKeys);
AuditLogList * _buildAuditLogListFromSCANCommand(redisContext * c, char * scanCommand, char * username);
AuditLogEntry * getAuditLogEntry(redisContext * c, char * username, int entryId);
AuditLogList * getAllAuditLogEntriesOfUser(redisContext * c, char * username);
AuditLogList * getAllAuditLogEntries(redisContext * c);
const char * serializeAuditLogListToXML(AuditLogList * auditLogList);