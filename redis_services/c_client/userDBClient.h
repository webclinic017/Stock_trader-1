#include "baseTypes.h"

typedef struct User {
    enum recordExists status;
    char * username;
    int amount;
} User;

User * getUser(redisContext * c, char * username);
User * addNewUser(redisContext * c, char * username);
User * addUserAmount(redisContext * c, char * username, int amount);
User * subtractUserAmount(redisContext * c, char * username, int amountToSubtract);
void removeUser(redisContext * c, char * username);
void freeUserObject(User * user);