client: client.c quoteCacheClient.c userDBClient.c eventDBClient.c transactionDBClient.c
	gcc client.c quoteCacheClient.c userDBClient.c eventDBClient.c transactionDBClient.c -Ihiredis -lhiredis -o client

test: client.c quoteCacheClient.c quoteCacheTests.c userDBClient.c userDBTests.c eventDBClient.c eventDBClientTests.c transactionDBClient.c transactionDBClientTests.c
	gcc -Ihiredis -lhiredis client.c quoteCacheClient.c userDBClient.c quoteCacheTests.c userDBTests.c eventDBClient.c eventDBClientTests.c transactionDBClient.c transactionDBClientTests.c -o test