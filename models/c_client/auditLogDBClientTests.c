#include "hiredis.h"
#include "client.h"
#include "auditLogDBClient.h"
#include <assert.h>
#include <string.h>
#include <stdlib.h>

char * auditLogEntry_username;
int entryId;
char * username_entryId;

void clearDBState() {
    redisCommand(c, "FLUSHDB");
}

// buildAuditLogEntryFromRedisArrayReply()
void buildAuditLogEntryFromRedisArrayReply_emptyRedisReply_emptyReturn() {
    redisReply * reply = redisCommand(c, "HGETALL MATCH someNonExistentMatchPattern");
    AuditLogEntry * entry = buildAuditLogEntryFromRedisArrayReply(reply, "bogusPattern");

    assert(entry != NULL);
    assert(entry -> numFields == 0);
    assert(entry -> head == NULL);
    assert(entry -> tail == NULL);
    assert(strcmp(entry -> commandType, "") == 0);
    freeReplyObject(reply);
    freeAuditLogEntry(entry);
}
void buildAuditLogEntryFromRedisArrayReply_nonemptyRedisReply_auditLogEntryReturned() {
    clearDBState();
    freeReplyObject(redisCommand(c, "HSET %s commandType %s field1 %s field2 %s field3 %s", username_entryId, "userCommand", "val1", "val2", "val3"));

    redisReply * reply = redisCommand(c, "HGETALL %s", username_entryId);
    AuditLogEntry * entry = buildAuditLogEntryFromRedisArrayReply(reply, username_entryId);

    assert(entry != NULL);
    assert(entry -> numFields == 3);
    assert(entry -> entryId == entryId);
    assert(strcmp(entry -> head -> field, "field1") == 0);
    assert(strcmp(entry -> head -> value, "val1") == 0);
    assert(strcmp(entry -> head -> next -> field, "field2") == 0);
    assert(strcmp(entry -> head -> next -> value, "val2") == 0);
    assert(strcmp(entry -> tail -> field, "field3") == 0);
    assert(strcmp(entry -> tail -> value, "val3") == 0);
    freeReplyObject(reply);

    freeAuditLogEntry(entry);

    clearDBState();
}

// addDataFieldToAuditLogEntry()
void addDataFieldToAuditLogEntry_validDataField_dataFieldSuccessfullyAdded() {
    AuditLogEntry * entry = initEmptyAuditLogEntry("userCommand", -1);
    AuditLogEntryField * dataField = initAuditEntryField("field1", "val1");

    assert(entry -> numFields == 0);
    addDataFieldToAuditLogEntry(entry, dataField);
    assert(entry -> numFields == 1);
    assert(strcmp(entry -> head -> field, "field1") == 0);
    assert(strcmp(entry -> head -> value, "val1") == 0);
    assert(entry -> head == entry -> tail);
    assert(entry -> head -> next == NULL);
    freeAuditLogEntry(entry);
}

// addAuditLogEntryToList()
void addAuditLogEntryToList_emptyList_auditLogListHasNewEntryAsOnlyEntry() {
    AuditLogList * logList = initEmptyAuditLogList();
    AuditLogEntry * entry1 = initEmptyAuditLogEntry("userCommand", -1);
    addAuditLogEntryToList(logList, entry1);
    assert(logList != NULL);
    assert(logList -> size == 1);
    assert(logList -> head -> curr == entry1);
    freeAuditLogList(logList);
}

void addAuditLogEntryToList_1EntryInList_auditLogListHas2EntriesIncludingNewEntryAtListTail() {
    AuditLogList * logList = initEmptyAuditLogList();
    AuditLogEntry * entry1 = initEmptyAuditLogEntry("userCommand", -1);
    AuditLogEntry * entry2 = initEmptyAuditLogEntry("accountTransaction", -1);
    addAuditLogEntryToList(logList, entry1);
    addAuditLogEntryToList(logList, entry2);
    assert(logList != NULL);
    assert(logList -> size == 2);
    assert(logList -> head -> curr == entry1);
    assert(logList -> head -> next -> curr == logList -> tail -> curr);
    assert(logList -> tail -> curr == entry2);
    freeAuditLogList(logList);
}

void addAuditLogEntryToList_3EntriesInList_auditLogListHas4EntriesIncludingNewEntryAtListTail(){
    AuditLogList * logList = initEmptyAuditLogList();
    AuditLogEntry * entry1 = initEmptyAuditLogEntry("userCommand", -1);
    AuditLogEntry * entry2 = initEmptyAuditLogEntry("accountTransaction", -1);
    AuditLogEntry * entry3 = initEmptyAuditLogEntry("quoteServer", -1);
    AuditLogEntry * entry4 = initEmptyAuditLogEntry("userCommand", -1);

    addAuditLogEntryToList(logList, entry1);
    addAuditLogEntryToList(logList, entry2);
    addAuditLogEntryToList(logList, entry3);
    addAuditLogEntryToList(logList, entry4);

    assert(logList != NULL);
    assert(logList -> size == 4);
    assert(logList -> head -> curr == entry1);
    assert(logList -> head -> next -> curr == entry2);
    assert(logList -> head -> next -> next -> next -> curr == logList -> tail -> curr);
    assert(logList -> tail -> curr == entry4);
    freeAuditLogList(logList);
}

// putAuditLogEntry()
void putAuditLogEntry_entryDoesNotExistInDB_newLogEntryIsPersisted() {
    clearDBState();
    AuditLogEntry * entry1 = initEmptyAuditLogEntry("userCommand", -1);
    printf("TRACE1\n");
    putAuditLogEntry(c, entry1, auditLogEntry_username);
    printf("TRACE2\n");
    AuditLogList * logList = initEmptyAuditLogList();
    addAuditLogEntryToList(logList, getAuditLogEntry(c, auditLogEntry_username, entry1 -> entryId));
    assert(logList != NULL);
    assert(logList -> size == 1);
    assert(logList -> head -> curr == logList -> tail -> curr);
    assert(logList -> tail -> curr -> entryId == entry1 -> entryId);
    freeAuditLogList(logList);
    clearDBState();
}
void putAuditLogEntry_entryExistsInDB_logEntryIsUpdatedWithNewFieldValues() {
    clearDBState();
    AuditLogList * logList = initEmptyAuditLogList();
    AuditLogEntry * entry1 = initEmptyAuditLogEntry("userCommand", entryId);
    addDataFieldToAuditLogEntry(entry1, initAuditEntryField("field1", "initial_val"));
    putAuditLogEntry(c, entry1, auditLogEntry_username);
    addDataFieldToAuditLogEntry(entry1, initAuditEntryField("field1", "updated_val"));
    putAuditLogEntry(c, entry1, auditLogEntry_username);
    assert(logList != NULL);
    assert(logList -> size == 1);
    assert(strcmp(logList -> head -> curr -> head -> field, "field1") == 0);
    assert(strcmp(logList -> head -> curr -> head -> value, "updated_val") == 0);
    assert(logList -> head -> curr == logList -> tail -> curr);
    assert(logList -> tail -> curr == entry1);

    freeAuditLogList(logList);
    clearDBState();
}

// getAuditLogEntry()
void getAuditLogEntry_doesntExistInDB_emptyAuditLogEntryIsReturned() {
    clearDBState();
    char * emptyString = malloc(1);
    emptyString[0] = 0;
    AuditLogEntry * entry = getAuditLogEntry(c, auditLogEntry_username, entryId);
    assert(entry != NULL);
    assert(strcmp((char*)entry -> commandType, emptyString) == 0);
    assert(entry -> entryId == -1);
    assert(entry -> head == entry -> tail);
    assert(entry -> tail == NULL);
    free(emptyString);
    clearDBState();
    freeAuditLogEntry(entry);
}
void getAuditLogEntry_existsInDB_entryIsReturned() {
    clearDBState();
    AuditLogEntry * entry = initEmptyAuditLogEntry("userCommand", -1);
    addDataFieldToAuditLogEntry(entry, initAuditEntryField("field1", "val1"));
    putAuditLogEntry(c, entry, auditLogEntry_username);
    AuditLogEntry * entryFromDB = getAuditLogEntry(c, auditLogEntry_username, entryId);
    assert(entryFromDB != NULL);
    assert(strcmp(entryFromDB -> commandType, entry -> commandType) == 0);
    assert(entryFromDB -> entryId == entry -> entryId);
    assert(strcmp(entryFromDB -> head -> field, entry -> head -> field) == 0);
    assert(strcmp(entryFromDB -> head -> value, entry -> head -> value) == 0);
    clearDBState();
    freeAuditLogEntry(entry);
    freeAuditLogEntry(entryFromDB);
}

// getAllAuditLogEntriesOfUser()
void getAllAuditLogEntriesOfUser_doesntExistInDB_emptyAuditLogEntryIsReturned() {
    AuditLogList * logList = getAllAuditLogEntriesOfUser(c, "someRandomUser");
    assert(logList != NULL);
    assert(logList -> size == 0);
    freeAuditLogList(logList);
}
void getAllAuditLogEntriesOfUser_existsInDB_entryIsReturned() {
    clearDBState();
    AuditLogEntry * entry1 = initEmptyAuditLogEntry("userCommand", -1);
    AuditLogEntry * entryA = initEmptyAuditLogEntry("userCommand", -1);

    putAuditLogEntry(c, entry1, auditLogEntry_username);
    putAuditLogEntry(c, entryA, "userA");

    AuditLogList * logList = getAllAuditLogEntriesOfUser(c, (char*)auditLogEntry_username);
    assert(logList != NULL);
    assert(logList -> size == 1);
    assert(logList -> head -> curr == entry1);
    freeAuditLogList(logList);
}

// getAllAuditLogEntries()
void getAllAuditLogEntries_noLogsInDB_emptyResult() {
    AuditLogList * logList = getAllAuditLogEntries(c);
    assert(logList != NULL);
    assert(logList -> size == 0);
    assert(logList -> head == NULL);
    assert(logList -> tail == NULL);
    freeAuditLogList(logList);
}
void getAllAuditLogEntries_1LogInDB_1AuditLogEntriesReturned() {
    clearDBState();
    AuditLogEntry * entry = initEmptyAuditLogEntry("userCommand", -1);
    addDataFieldToAuditLogEntry(entry, initAuditEntryField("field1", "val1"));
    AuditLogList * logList = getAllAuditLogEntries(c);
    assert(strcmp(logList -> head -> curr -> head -> field, "field1") == 0);
    assert(strcmp(logList -> head -> curr -> head -> value, "val1") == 0);
    assert(strcmp(logList -> tail -> curr -> head -> field, logList -> head -> next -> next -> curr -> head -> field) == 0);
    assert(strcmp(logList -> tail -> curr -> head -> value, logList -> head -> next -> next -> curr -> head -> value) == 0);
    clearDBState();
}
void getAllAuditLogEntries_3LogInDB_3AuditLogEntriesReturned() {
    clearDBState();
    AuditLogEntry * entry1 = initEmptyAuditLogEntry("userCommand", -1);
    addDataFieldToAuditLogEntry(entry1, initAuditEntryField("field1", "val1"));
    putAuditLogEntry(c, entry1, NULL);
    AuditLogEntry * entry2 = initEmptyAuditLogEntry("accountTransaction", -1);
    addDataFieldToAuditLogEntry(entry2, initAuditEntryField("fieldA", "valA"));
    putAuditLogEntry(c, entry2, NULL);
    AuditLogEntry * entry3 = initEmptyAuditLogEntry("quoteServer", -1);
    addDataFieldToAuditLogEntry(entry3, initAuditEntryField("fieldX", "valX"));
    putAuditLogEntry(c, entry3, NULL);

    AuditLogList * logList = getAllAuditLogEntries(c);
    assert(logList != NULL);
    assert(logList -> size == 3);
    assert(strcmp(logList -> head -> curr -> head -> field, "field1") == 0);
    assert(strcmp(logList -> head -> curr -> head -> value, "val1") == 0);
    assert(strcmp(logList -> head -> next -> curr -> head -> field, "fieldA") == 0);
    assert(strcmp(logList -> head -> next -> curr -> head -> value, "valA") == 0);
    assert(strcmp(logList -> head -> next -> next -> curr -> head -> field, "fieldX") == 0);
    assert(strcmp(logList -> head -> next -> next -> curr -> head -> value, "valX") == 0);
    assert(strcmp(logList -> tail -> curr -> head -> field, logList -> head -> next -> next -> curr -> head -> field) == 0);
    assert(strcmp(logList -> tail -> curr -> head -> value, logList -> head -> next -> next -> curr -> head -> value) == 0);
    clearDBState();
    freeAuditLogEntry(entry1);
    freeAuditLogEntry(entry2);
    freeAuditLogEntry(entry3);
}

// serializeAuditLogListToXML()
void serializeAuditLogListToXML_emptyLog_emptyLogResult() {
    const char * expectedXML = "<log></log>";
    AuditLogList * logList = initEmptyAuditLogList();
    const char * xmlOutput = serializeAuditLogListToXML(logList);
    assert(strcmp(expectedXML, xmlOutput) == 0);
}
void serializeAuditLogListToXML_1EntryInLogList_1LogEntryInXMLResult() {
    const char * expectedXML = "<log><userCommand><field1>val1</field1><field2>val2</field2></userCommand></log>";
    AuditLogList * logList = initEmptyAuditLogList();
    AuditLogEntry * entry1 = initEmptyAuditLogEntry("userCommand", -1);
    entry1 -> commandType = "userCommand";
    addDataFieldToAuditLogEntry(entry1, initAuditEntryField("field1", "val1"));
    addDataFieldToAuditLogEntry(entry1, initAuditEntryField("field2", "val2"));
    const char * xmlOutput = serializeAuditLogListToXML(logList);
    assert(strcmp(expectedXML, xmlOutput) == 0);
}
void serializeAuditLogListToXML_3EntriesInLogList_3LogEntriesInXMLResult() {
    const char * expectedXML = "<log><userCommand><field1>val1</field1><field2>val2</field2></userCommand><accountTransaction><fieldA>valA</fieldA><fieldB>valB</fieldB></accountTransaction><quoteServer><fieldX>valX</fieldX><fieldY>valY</fieldY></quoteServer></log>";
    AuditLogList * logList = initEmptyAuditLogList();
    AuditLogEntry * entry1 = initEmptyAuditLogEntry("userCommand", -1);
    entry1 -> commandType = "userCommand";
    addDataFieldToAuditLogEntry(entry1, initAuditEntryField("field1", "val1"));
    addDataFieldToAuditLogEntry(entry1, initAuditEntryField("field2", "val2"));
    AuditLogEntry * entry2 = initEmptyAuditLogEntry("accountTransaction", -1);
    entry2 -> commandType = "accountTransaction";
    addDataFieldToAuditLogEntry(entry2, initAuditEntryField("fieldA", "valA"));
    addDataFieldToAuditLogEntry(entry2, initAuditEntryField("fieldB", "valB"));
    AuditLogEntry * entry3 = initEmptyAuditLogEntry("quoteServer", -1);
    entry3 -> commandType = "quoteServer";
    addDataFieldToAuditLogEntry(entry3, initAuditEntryField("fieldX", "valX"));
    addDataFieldToAuditLogEntry(entry3, initAuditEntryField("fieldY", "valY"));
    const char * xmlOutput = serializeAuditLogListToXML(logList);
    assert(strcmp(expectedXML, xmlOutput) == 0);
}

// driver
void runAuditLogDBTests() {
    openConnection();
    clearDBState();

    auditLogEntry_username = malloc(10);
    memset(auditLogEntry_username, 0, 10);
    strcpy(auditLogEntry_username, "user1");
    entryId = nextAuditLogEntryId();

    username_entryId = joinUsernameAndEntryId(auditLogEntry_username, entryId);

    // buildAuditLogEntryFromRedisArrayReply()
    buildAuditLogEntryFromRedisArrayReply_emptyRedisReply_emptyReturn();

    buildAuditLogEntryFromRedisArrayReply_nonemptyRedisReply_auditLogEntryReturned();

    // addDataFieldToAuditLogEntry()

    addDataFieldToAuditLogEntry_validDataField_dataFieldSuccessfullyAdded();

    // addAuditLogEntryToList()
    addAuditLogEntryToList_emptyList_auditLogListHasNewEntryAsOnlyEntry();

    addAuditLogEntryToList_1EntryInList_auditLogListHas2EntriesIncludingNewEntryAtListTail();

    addAuditLogEntryToList_3EntriesInList_auditLogListHas4EntriesIncludingNewEntryAtListTail();
    printf("trace1...\n");

    // putAuditLogEntry()
    putAuditLogEntry_entryDoesNotExistInDB_newLogEntryIsPersisted();
    printf("trace2...\n");

    putAuditLogEntry_entryExistsInDB_logEntryIsUpdatedWithNewFieldValues();

    // getAuditLogEntry()
    getAuditLogEntry_existsInDB_entryIsReturned();

    // getAllAuditLogEntriesOfUser()
    getAllAuditLogEntriesOfUser_doesntExistInDB_emptyAuditLogEntryIsReturned();
    getAllAuditLogEntriesOfUser_existsInDB_entryIsReturned();

    // getAllAuditLogEntries()
    getAllAuditLogEntries_noLogsInDB_emptyResult();
    getAllAuditLogEntries_1LogInDB_1AuditLogEntriesReturned();
    getAllAuditLogEntries_3LogInDB_3AuditLogEntriesReturned();

    // serializeAuditLogListToXML()
    serializeAuditLogListToXML_emptyLog_emptyLogResult();
    serializeAuditLogListToXML_1EntryInLogList_1LogEntryInXMLResult();
    serializeAuditLogListToXML_3EntriesInLogList_3LogEntriesInXMLResult();

    closeConnection();
    free(username_entryId);
}