#include "eventDBClient.h"
#include "eventDBClientTests.h"
#include "hiredis.h"
#include "client.h"
#include <uuid/uuid.h>
#include <assert.h>
#include <string.h>

uuid_t eventId;
int targetAmount = 100;
char * stockSymbol = "someStock";
enum eventType type = BUY;

void setEvent_shouldSetEvent() {
    char * username = "someUser";
    uuid_generate(eventId);
    int result = setEvent(c, eventId, stockSymbol, targetAmount, type, username);
    assert(result == 1);
}

void getEvent_shouldGetEvent() {
    char * username = "someUser";
    eventObject * e = getEvent(c, eventId);
    assert(e != NULL);
    int sizeUuid = sizeof(uuid_t);
    for (int i = 0; i < sizeUuid; ++i) {
        assert(e -> eventId[i] == eventId[i]);
    }
    assert(e -> type == type);
    assert(strcmp(e -> username, username) == 0);
    assert(strcmp(e -> stockSymbol, stockSymbol) == 0);
    assert(e -> targetAmount == targetAmount);
    assert(e -> status == PENDING);
    freeEventObject(e);
}

void updateEvent_shouldUpdateEvent() {
    char * username = "someUser";
    enum eventStatus status = READY;
    eventObject * e = getEvent(c, eventId);
    assert(e -> status == PENDING);
    freeEventObject(e);
    updateEventStatus(c, eventId, status);
    e = getEvent(c, eventId);
    assert(e -> status == status);
    freeEventObject(e);
}

void removeEvent_shouldRemoveEvent() {
    removeEvent(c, eventId);
    eventObject * e = getEvent(c, eventId);
    assert(e -> eventId == NULL);
}

void runEventDBTests() {
    openConnection();
    setEvent_shouldSetEvent();
    getEvent_shouldGetEvent();
    updateEvent_shouldUpdateEvent();
    removeEvent_shouldRemoveEvent();
    closeConnection();
}