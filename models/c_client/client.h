#include "hiredis.h"

redisContext *c;

char * redisServerIp;
int redisServerPort;
void openConnection();
void closeConnection();