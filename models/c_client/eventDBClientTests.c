#include "eventDBClient.h"
#include "eventDBClientTests.h"
#include "hiredis.h"
#include "client.h"
#include <uuid/uuid.h>
#include <assert.h>
#include <string.h>

uuid_t eventId;
char * stockSymbol = "someStock";
enum commandType type = BUY;

void setEvent_shouldSetEvent() {
    MoneyAmount * targetAmount = initMoneyAmount(100, 63);  
    char * username = "someUser";
    uuid_generate(eventId);
    int result = setEvent(c, eventId, stockSymbol, targetAmount, type, username);
    assert(result == 1);
    free(targetAmount);
}

void getEvent_shouldGetEvent() {
    MoneyAmount * targetAmount = initMoneyAmount(100, 63);
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
    assert(e -> moneyAmount -> dollars == targetAmount -> dollars);
    assert(e -> moneyAmount -> cents == targetAmount -> cents);
    assert(e -> status == PENDING);
    freeEventObject(e);
    free(targetAmount);
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