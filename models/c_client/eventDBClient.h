#include "hiredis.h"
#include <stdlib.h>
#include <uuid/uuid.h>
#include "baseTypes.h"

enum eventStatus {
    PENDING,
    READY,
    FULFILLED
};

typedef struct MoneyAmount {
    int dollars;
    int cents;
} MoneyAmount;

typedef struct eventObject {
    unsigned char * eventId;
    enum commandType type;
    char * username;
    char * stockSymbol;
    MoneyAmount * moneyAmount;
    enum eventStatus status;
} eventObject;

eventObject * buildEventObject(redisReply * reply, uuid_t eventId);
eventObject * buildEmptyEventObject();
int setEvent(redisContext * c, uuid_t eventId, char * stockSymbol, MoneyAmount * targetAmount, enum commandType type, char * username);
eventObject * getEvent(redisContext * c, uuid_t eventId);
void updateEventStatus(redisContext * c, uuid_t eventId, enum eventStatus status);
void removeEvent(redisContext * c, uuid_t eventId);
void freeEventObject(eventObject * e);
MoneyAmount * initMoneyAmount(int dollars, int cents);