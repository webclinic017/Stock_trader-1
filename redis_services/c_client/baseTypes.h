enum recordExists {
    NOT_EXISTS,
    EXISTS
};

enum commandType {
    NONE,
    BUY,
    SELL,
    COMMIT,
    CANCEL,
    DUMPLOG,
    SET_BUY_AMOUNT,
    SET_SELL_AMOUNT,
    QUOTE
};