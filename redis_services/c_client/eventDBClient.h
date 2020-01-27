#include "hiredis.h"
#include <stdlib.h>
#include <uuid/uuid.h>

enum eventType {
    BUY,
    SELL
};

enum eventStatus {
    PENDING,
    READY,
    FULFILLED
};

typedef struct eventObject {
    unsigned char * eventId;
    enum eventType type;
    char * username;
    char * stockSymbol;
    int targetAmount;
    enum eventStatus status;
} eventObject;

eventObject * buildEventObject(redisReply * reply, uuid_t eventId);
eventObject * buildEmptyEventObject();
int setEvent(redisContext * c, uuid_t eventId, char * stockSymbol, int targetAmount, enum eventType type, char * username);
eventObject * getEvent(redisContext * c, uuid_t eventId);
void updateEventStatus(redisContext * c, uuid_t eventId, enum eventStatus status);
void removeEvent(redisContext * c, uuid_t eventId);
void freeEventObject(eventObject * e);