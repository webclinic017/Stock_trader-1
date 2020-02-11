from enum import Enum

class CommandURLs(Enum):
    ADD = "/addFunds"
    QUOTE = "/getQuote"
    BUY = "/buyStock"
    COMMIT_BUY = "/commitBuy"
    CANCEL_BUY = "/cancelBuy"
    SELL = "/sellStock"
    COMMIT_SELL = "/commitSell"
    CANCEL_SELL = "/cancelSell"
    SET_BUY_AMOUNT = "/setBuyAmount"
    CANCEL_SET_BUY = "/cancelSetBuy"
    SET_BUY_TRIGGER = "/setBuyTrigger"
    SET_SELL_AMOUNT = "/setSellAmount"
    SET_SELL_TRIGGER = "/setSellTrigger"
    CANCEL_SET_SELL = "/cancelSetSell"
    DUMPLOG = "/dumpLog"
    DISPLAY_SUMMARY = "/displaySummary"

