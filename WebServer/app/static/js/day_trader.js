

function add() {
    let add_field = document.getElementById("addFunds");
    if (add_field.value.length === 0) {
        alert("Positive dollar amount required");
        return false;
    }
    $.post("addFunds", {amount: add_field.value}, function (data) {
            console.log(data);
        },
        "json");
    update_balance(parseFloat(add_field.value));
    add_field.value = "";
}

function buy_stock() {
    let stock_symbol = document.getElementById("symbol_buy");
    let buy_amount = document.getElementById("buy_amount");
    if (stock_symbol.value.length !== 3) {
        alert("3 character stock symbol required");
        return false;
    }
    if (buy_amount.value.length === 0) {
        alert("Purchase amount required");
        return false;
    }
    $.post("buyStock", {symbol: stock_symbol.value, amount: buy_amount.value}, function (data) {
            console.log(data);
        },
        "json");
    stock_symbol.value = "";
    buy_amount.value = "";
}

function sell_stock() {
    let stock_symbol = document.getElementById("symbol_sell");
    let sell_amount = document.getElementById("sell_amount");
    if (stock_symbol.value.length !== 3) {
        alert("3 character stock symbol required");
        return false;
    }
    if (sell_amount.value.length === 0) {
        alert("Sell amount required");
        return false;
    }
    $.post("sellStock", {symbol: stock_symbol.value, amount: sell_amount.value}, function (data) {
            console.log(data);
        },
        "json");
    stock_symbol.value = "";
    sell_amount.value = "";
}

function get_quote() {
    let stock_symbol = document.getElementById("getQuote");
    if (stock_symbol.value.length !== 3) {
        alert("3 character stock symbol required");
        return false;
    }
    $.post("getQuote", {symbol: stock_symbol.value}, function (data) {
            console.log(data);
        },
        "json");
    stock_symbol.value = "";
}

function buy_trigger() {
    let stock_symbol = document.getElementById("symbol_buy_trigger");
    let target_price = document.getElementById("targetPrice_buy");
    if (stock_symbol.value.length !== 3) {
        alert("3 character stock symbol required");
        return false;
    }
    if (target_price.value.length === 0) {
        alert("Purchase amount required");
        return false;
    }
    $.post("buyTrigger", {symbol: stock_symbol.value, price: target_price.value}, function (data) {
            console.log(data);
        },
        "json");
    stock_symbol.value = "";
    target_price.value = "";
}

function sell_trigger() {
    let stock_symbol = document.getElementById("symbol_sell_trigger");
    let target_price = document.getElementById("targetPrice_sell");
    if (stock_symbol.value.length !== 3) {
        alert("3 character stock symbol required");
        return false;
    }
    if (target_price.value.length === 0) {
        alert("Purchase amount required");
        return false;
    }
    $.post("sellTrigger", {symbol: stock_symbol.value, price: target_price.value}, function (data) {
            console.log(data);
        },
        "json");
    stock_symbol.value = "";
    target_price.value = "";
}

function get_logs() {
    $.post("getLogFile", {}, function (data) {
            console.log(data);
        },
        "json");
}

function update_balance(valToAdd) {
    if (valToAdd == null || valToAdd < 0) return;
    let balance_field = document.getElementById("accountBalance");
    balance_field.textContent = (parseFloat(balance_field.textContent) + valToAdd).toString();
}
