#include "client.h"
#include "userDBClient.h"
#include <assert.h>
#include <string.h>

char * username = "somebody";
int amount = 1000;

void addNewUser_newUserSuccessfullyAdded() {
    removeUser(c, username);
    User * newUser = addNewUser(c, username);
    assert(newUser != NULL);
    int usernameResult = strcmp(newUser -> username, username);
    assert(usernameResult == 0);
    assert(newUser -> amount == 0);
    freeUserObject(newUser);
    removeUser(c, username);
}

void addUserAmount_shouldAddAmountToExistingAmount() {
    removeUser(c, username);
    User * user = addNewUser(c, username);
    assert(user != NULL);
    int usernameResult = strcmp(user -> username, username);
    int initialAmount = 0;
    assert(usernameResult == 0);
    assert(user -> amount == initialAmount);
    freeUserObject(user);

    user = addUserAmount(c, username, amount);
    assert(user != NULL);
    usernameResult = strcmp(user -> username, username);
    assert(usernameResult == 0);
    assert(user -> amount == initialAmount + amount);
    freeUserObject(user);

    user = addUserAmount(c, username, amount);
    assert(user != NULL);
    usernameResult = strcmp(user -> username, username);
    assert(usernameResult == 0);
    int currAmount = initialAmount + 2 * amount;
    assert(user -> amount == currAmount);
    freeUserObject(user);
}

void subtractUserAmount_shouldSubtractUserAmount() {
    removeUser(c, username);
    int initialAmount = 1000;
    User * user = addUserAmount(c, username, initialAmount);
    assert(user != NULL);
    int usernameResult = strcmp(user -> username, username);
    assert(usernameResult == 0);
    assert(user -> amount == initialAmount);
    freeUserObject(user);

    int amountToSubtract = 100;
    user = subtractUserAmount(c, username, amountToSubtract);
    assert(user != NULL);
    usernameResult = strcmp(user -> username, username);
    assert(usernameResult == 0);
    assert(user -> amount == initialAmount - amountToSubtract);
    freeUserObject(user);
    removeUser(c, username);
}

void getUser_shouldGetNonExistentUser() {
    User * user = getUser(c, username);
    assert(user != NULL);
    assert(user -> status == NOT_EXISTS);
    freeUserObject(user);
}

void runUserDBTests() {
    openConnection();
    addNewUser_newUserSuccessfullyAdded();
    addUserAmount_shouldAddAmountToExistingAmount();
    subtractUserAmount_shouldSubtractUserAmount();
    getUser_shouldGetNonExistentUser();
    removeUser(c, username);
    closeConnection();
}