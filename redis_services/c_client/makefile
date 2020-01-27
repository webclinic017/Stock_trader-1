client: client.c quoteCacheClient.c userDBClient.c eventDBClient.c
	gcc client.c quoteCacheClient.c userDBClient.c eventDBClient.c -Ihiredis -lhiredis -o client

test: client.c quoteCacheClient.c quoteCacheTests.c userDBClient.c userDBTests.c eventDBClient.c eventDBClientTests.c
	gcc -Ihiredis -lhiredis client.c quoteCacheClient.c userDBClient.c quoteCacheTests.c userDBTests.c eventDBClient.c eventDBClientTests.c -o test