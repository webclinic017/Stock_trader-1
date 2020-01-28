#include <stdlib.h>
#include <string.h>
#include "hiredis.h"
#include "client.h"
#include "quoteCacheClient.h"
#include "quoteCacheTests.h"
#include <assert.h>

char * stockName = "someStock";
int quote = 300;

void cacheQuote_quoteShouldBeCached() {
    removeQuote(c, stockName);
    stockQuote * sq = cacheQuote(c, stockName, quote);
    assert(sq != NULL);
    assert(sq -> stockName != NULL);
    assert(sq -> quote != 0);

    int nameResult = strcmp(sq -> stockName, stockName);
    int quoteResult = sq -> quote == quote;
    assert(nameResult == 0);
    assert(quoteResult == 1);

    freeQuoteObject(sq);
}

void cacheQuote_shouldOverwriteExistingQuote() {
    removeQuote(c, stockName);
    int updatedQuote = quote + 1;
    stockQuote * sq = cacheQuote(c, stockName, quote);
    assert(sq != NULL);
    assert(sq -> stockName != NULL);
    assert(sq -> quote != 0);
    int nameResult = strcmp(sq -> stockName, stockName);
    int quoteResult = sq -> quote == quote;
    assert(nameResult == 0);
    assert(quoteResult == 1);

    freeQuoteObject(sq);

    sq = cacheQuote(c, stockName, updatedQuote);
    assert(sq != NULL);
    assert(sq -> stockName != NULL);
    assert(sq -> quote != 0);

    nameResult = strcmp(sq -> stockName, stockName);
    quoteResult = sq -> quote == updatedQuote;
    assert(nameResult == 0);
    assert(quoteResult == 1);

    freeQuoteObject(sq);
}

void getQuote_shouldGetQuote() {
    removeQuote(c, stockName);
    freeQuoteObject(cacheQuote(c, stockName, quote));
    stockQuote * sq = getQuote(c, stockName);
    assert(sq != NULL);
    assert(sq -> status == EXISTS);
    assert(sq -> stockName != NULL);
    assert(sq -> quote != 0);
    int nameResult = strcmp(sq -> stockName, stockName);
    int quoteResult = sq -> quote == quote;
    
    assert(nameResult == 0);
    assert(quoteResult == 1);

    freeQuoteObject(sq);
}

void getQuote_shouldNotGetQuote() {
    removeQuote(c, stockName);
    stockQuote * sq = getQuote(c, stockName);
    assert(sq != NULL);
    assert(sq -> status == NOT_EXISTS);
    assert(sq -> stockName != NULL);
    assert(sq -> quote == 0);
    int nameResult = strcmp(sq -> stockName, stockName);
    assert(nameResult == 0);
    freeQuoteObject(sq);
}

void removeQuote_shouldRemoveExistingQuote() {
    stockQuote * sq = cacheQuote(c, stockName, quote);
    assert(sq != NULL);
    assert(sq -> stockName != NULL);
    assert(sq -> quote != 0);
    int nameResult = strcmp(sq -> stockName, stockName);
    int quoteResult = sq -> quote == quote;
    assert(nameResult == 0);
    assert(quoteResult == 1);

    freeQuoteObject(sq);

    removeQuote(c, stockName);
    sq = getQuote(c, stockName);

    assert(sq != NULL);
    assert(sq -> status == NOT_EXISTS);

    nameResult = strcmp(sq -> stockName, stockName);
    quoteResult = sq -> quote == 0;
    assert(nameResult == 0);
    assert(quoteResult == 1);

    freeQuoteObject(sq);
}

void runQuoteCacheTests() {
    openConnection();
    cacheQuote_quoteShouldBeCached();
    cacheQuote_shouldOverwriteExistingQuote();
    getQuote_shouldGetQuote();
    getQuote_shouldNotGetQuote();
    removeQuote_shouldRemoveExistingQuote();
    removeQuote(c, stockName);
    closeConnection();
}