#include "baseTypes.h"
#include "hiredis.h"

typedef struct stockQuote {
    enum recordExists status;
    char * stockName;
    int quote;
} stockQuote;

stockQuote * buildStockQuoteObject(char * stockName, int quote);
stockQuote * cacheQuote(redisContext * c, char * stockName, int quote);
void removeQuote(redisContext * c, char * stockName);
stockQuote * getQuote(redisContext * c, char * stockName);
void freeQuoteObject(stockQuote * quote);