#include "hiredis.h"
#include "auditLogDBClient.h"
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "client.h"
#include <uuid/uuid.h>

void freeAuditLogEntryField(AuditLogEntryField * dataField) {
    assert(dataField != NULL);
    assert(dataField -> field != NULL);
    assert(dataField -> value != NULL);
    free(dataField -> field);
    free(dataField -> value);
    // note: (dataField -> next) should not be freed here
    free(dataField);
}

void freeAuditLogEntry(AuditLogEntry * auditLogEntry) {
    assert(auditLogEntry != NULL);
    assert(auditLogEntry -> commandType != NULL);
    free((char *) auditLogEntry -> commandType);
    AuditLogEntryField * field = auditLogEntry -> head;

    while (field != NULL) {
        AuditLogEntryField * nextField = field -> next;
        freeAuditLogEntryField(field);
        field = nextField;
    }
    free(auditLogEntry);
}

void freeAuditLogListNode(AuditLogListNode * node) {
    assert(node -> curr);
    freeAuditLogEntry(node -> curr);
    free(node);
}

void freeAuditLogList(AuditLogList * list) {
    assert(list -> head);
    AuditLogListNode * curr = list -> head;
    while (curr != NULL) {
        AuditLogListNode * next = curr -> next;
        freeAuditLogListNode(curr);
        curr = next;
    }
    free(list);
}

AuditLogEntryField * initAuditEntryField(char * field, char * value) {
    AuditLogEntryField * entryField = malloc(sizeof(AuditLogEntryField));
    entryField -> field = malloc(sizeof(field));
    entryField -> value = malloc(sizeof(value));
    strcpy(entryField -> field, field);
    strcpy(entryField -> value, value);

    entryField -> next = NULL;
    return entryField;
}

int nextAuditLogEntryId() {
    redisReply * reply = redisCommand(c, "GET auditLogUUID");
    int id = 0;
    if (reply -> str != NULL) {
        id = atoi(reply -> str);
    }
    char * setCommand = malloc(20);
    memset(setCommand, 0, 20);
    sprintf(setCommand, "SET auditLogUUID %d", id + 1);
    redisCommand(c, setCommand);
    free(setCommand);
    reply = redisCommand(c, "GET auditLogUUID");
    return id;
}

AuditLogEntry * initEmptyAuditLogEntry(const char * commandType, int entryId) {
    AuditLogEntry * auditLogEntry = malloc(sizeof(AuditLogEntry));
    auditLogEntry -> numFields = 0;
    auditLogEntry -> head = NULL;
    auditLogEntry -> tail = NULL;
    char * emptyString = malloc(1);
    emptyString[0] = 0;
    if (commandType != NULL) {
        auditLogEntry -> commandType = malloc(sizeof(commandType));
        strcpy((char *)auditLogEntry -> commandType, commandType);
    } else {
        auditLogEntry -> commandType = malloc(sizeof(1));
        strcpy((char *)auditLogEntry -> commandType, emptyString);
    }
    if (entryId > 0) {
        auditLogEntry -> entryId = entryId;
    } else {
        auditLogEntry -> entryId = nextAuditLogEntryId();
    }
    free(emptyString);

    return auditLogEntry;
}

AuditLogListNode * initEmptyAuditLogListNode() {
    AuditLogListNode * node = malloc(sizeof(AuditLogListNode));
    node -> prev = NULL;
    node -> curr = NULL;
    node -> next = NULL;
    return node;
}

AuditLogList * initEmptyAuditLogList() {
    AuditLogList * list = malloc(sizeof(AuditLogList));
    list -> size = 0;
    list -> head = NULL;
    list -> tail = NULL;
    return list;
}

AuditLogEntry * buildAuditLogEntryFromRedisArrayReply(redisReply * reply, char * username_entryId) {
    char * _username_entryId = malloc(sizeof(username_entryId));
    strcpy(_username_entryId, username_entryId);
    size_t numElements = reply -> elements;
    AuditLogEntry * entry;
    if (numElements > 0) {
        strtok(_username_entryId, "_");
        char * username = malloc(sizeof(_username_entryId));
        strcpy(username, _username_entryId);
        int entryId = atoi(strtok(NULL, "_"));
        char * commandType = malloc(sizeof(reply -> element[1] -> str));
        strcpy(commandType, reply -> element[1] -> str);
        entry = initEmptyAuditLogEntry(commandType, entryId);

        for (int i = 3; i < reply -> elements; i += 2) {
            AuditLogEntryField * dataField = initAuditEntryField(reply -> element[i - 1] -> str, reply -> element[i] -> str);
            addDataFieldToAuditLogEntry(entry, dataField);
        }
    } else {
        entry = initEmptyAuditLogEntry(NULL, -1);
    }
    free(_username_entryId);
    return entry;
}

void addDataFieldToAuditLogEntry(AuditLogEntry * entry, AuditLogEntryField * dataField) {
    if (entry -> head == NULL) {
        entry -> head = dataField;
        entry -> tail = dataField;
    } else {
        entry -> tail -> next = dataField;
        entry -> tail = dataField;
    }
    entry -> numFields = entry -> numFields + 1;
}

void addAuditLogEntryToList(AuditLogList * logList, AuditLogEntry * entry) {
    AuditLogListNode * entryNode = initEmptyAuditLogListNode();
    entryNode -> curr = entry;
    if (logList -> head == NULL) {
        logList -> head = entryNode;
        logList -> tail = entryNode;
    } else {
        logList -> tail -> next = entryNode;
        entryNode -> prev = logList -> tail;
        logList -> tail = entryNode;
    }
    logList -> size = (logList -> size) + 1;
}

char * joinUsernameAndEntryId(char * username, int entryId) {
    char * username_entryId = malloc(1);
    username_entryId[0] = 0;
    strcat(username_entryId, username);
    strcat(username_entryId, "_");
    char * buffer = malloc(10);
    memset(buffer, 0, 10);
    sprintf(buffer, "%d", entryId);
    strcat(username_entryId, buffer);
    free(buffer);
    return username_entryId;
}

redisReply * putAuditLogEntry(redisContext * c, AuditLogEntry * entry, const char * username) {
    
    // build up log hash key as coallescence of username and entry id
    size_t username_entryIdLen = sizeof(username) + 1 + sizeof(entry -> entryId);

    char * username_entryId = malloc(username_entryIdLen);
    memset(username_entryId, 0, sizeof(username));
    strcpy(username_entryId, username);
    strcat(username_entryId, "_");
    char * buffer = malloc(10);
    memset(buffer, 0, 10);
    sprintf(buffer, "%d", entry -> entryId);
    strcat(username_entryId, buffer);
    free(buffer);

    // add log hash key to params string
    char * params = malloc(username_entryIdLen);
    memset(params, 0, username_entryIdLen);
    strcpy(params, username_entryId);

    // add each entry data field to params string
    strcat(params, " commandType");
    strcat(params, " \"");
    strcat(params, entry -> commandType);
    strcat(params, "\" ");

    AuditLogEntryField * curr = entry -> head;
    while (curr != NULL) {
        int numBytesToAppend = sizeof(curr -> field) + 2 + sizeof(curr -> value) + 2 + sizeof(curr -> next);
        int numBytesParams = sizeof(params);
        char * additionalParam = malloc(numBytesToAppend);
        strcat(additionalParam, curr -> field);
        strcat(additionalParam, " \"");
        strcat(additionalParam, curr -> value);
        strcat(additionalParam, "\" ");
        params = realloc(params, numBytesParams + numBytesToAppend);
        strcat(params, additionalParam);
        free(additionalParam);
        curr = curr -> next;
    }
    printf("%s\n", params);
    redisReply * reply = redisCommand(c, "HSET %s", params);

    free(params);
    printf("TRACE..B..\n");
    return reply;
}

void _addAuditLogEntriesFromRedisArrayReplyOfKeysToLogList(redisContext * c, AuditLogList * logList, redisReply * redisArrayReplyOfKeys) {
    redisReply * entryQueryReply;
    for (int i = 0; i < redisArrayReplyOfKeys -> elements; ++i) {
        entryQueryReply = redisCommand(c, "HGETALL %s", redisArrayReplyOfKeys -> element[i] -> str);
        addAuditLogEntryToList(logList, buildAuditLogEntryFromRedisArrayReply(entryQueryReply, redisArrayReplyOfKeys -> element[i] -> str));
        freeReplyObject(entryQueryReply);
    }
}

AuditLogList * _buildAuditLogListFromSCANCommand(redisContext * c, char * scanCommand, char * username) {
    AuditLogList * logList = initEmptyAuditLogList();
    redisReply * reply;
    if (username != NULL) {
        reply = redisCommand(c, scanCommand, 0, username);
    } else {
        reply = redisCommand(c, scanCommand, 0);
    }
    _addAuditLogEntriesFromRedisArrayReplyOfKeysToLogList(c, logList, reply -> element[1]);
    freeReplyObject(reply);
    int cursor = reply -> element[0] -> integer;
    while (cursor != 0) {
        if (username != NULL) {
            reply = redisCommand(c, scanCommand, cursor, username);
        } else {
            reply = redisCommand(c, scanCommand, cursor);
        }
        cursor = reply -> element[0] -> integer;
        _addAuditLogEntriesFromRedisArrayReplyOfKeysToLogList(c, logList, reply -> element[1]);
        freeReplyObject(reply);
    }
    return logList;
}

AuditLogEntry * getAuditLogEntry(redisContext * c, char * username, int entryId) {
    char * username_entryId = joinUsernameAndEntryId(username, entryId);
    redisReply * reply = redisCommand(c, "HGETALL %s", username_entryId);
    return buildAuditLogEntryFromRedisArrayReply(reply, username_entryId);
}

AuditLogList * getAllAuditLogEntriesOfUser(redisContext * c, char * username) {
    return _buildAuditLogListFromSCANCommand(c, "SCAN %d MATCH %s_**", username);
}

AuditLogList * getAllAuditLogEntries(redisContext * c) {
    return _buildAuditLogListFromSCANCommand(c, "SCAN %d", NULL);
}

const char * serializeAuditLogListToXML(AuditLogList * auditLogList) {
    assert(auditLogList != NULL);
    size_t numXmlBytes = 0;
    char * xmlString = "<log>";
    AuditLogListNode * node = auditLogList -> head;

    // add each log entry as an xml element to the xml string
    while (node != NULL) {
        // opening tag:
        char * logEntryOpeningTag = "<";
        strcat(logEntryOpeningTag, node -> curr -> commandType);
        strcat(logEntryOpeningTag, ">");

        strcat(xmlString, logEntryOpeningTag);

        // add each data field of the given log entry as an xml element containing the field value as child text
        AuditLogEntryField * dataField = node -> curr -> head;
        while (dataField != NULL) {
            char * fieldOpeningTag = "<";
            strcat(fieldOpeningTag, dataField -> field);
            strcat(fieldOpeningTag, ">");

            char * fieldClosingTag = "</";
            strcat(fieldClosingTag, dataField -> field);
            strcat(fieldClosingTag, ">");

            strcat(xmlString, fieldOpeningTag);
            strcat(xmlString, dataField -> value);
            strcat(xmlString, fieldClosingTag);

            dataField = dataField -> next;
        }

        // closing tag:
        char * logEntryClosingTag = "</";
        strcat(logEntryClosingTag, node -> curr -> commandType);
        strcat(logEntryClosingTag, ">");

        strcat(xmlString, logEntryClosingTag);
        node = node -> next;
    }
    strcat(xmlString, "</log>");
    return xmlString;
}