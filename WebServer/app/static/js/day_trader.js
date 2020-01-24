
function checkSubmit(e) {
   if(e && e.keyCode == 13) {
      document.forms[0].submit();
   }
}

function add() {
    event.preventDefault(); //stops page from resetting/reloading
    let currentUser = document.getElementById("userId");
    let add_field = document.getElementById("addFunds");
    if (add_field.value.length === 0 || parseFloat(add_field.value) <= 0) {
        alert("Positive amount required");
        add_field.value = "";
        return false;
    }
    if (currentUser.value.length === 0) {
        alert("userId required");
        return false;
    }
    let parcel = {
        Command: "ADD",
        userid: currentUser.value,
        amount: add_field.value
    };
    $.post("addFunds", parcel, function (data) {console.log(data);}, "json");
    update_balance(parseFloat(add_field.value));
    add_field.value = "";
}

function buy_stock() {
    event.preventDefault(); //stops page from resetting/reloading
    let currentUser = document.getElementById("userId");
    let stock_symbol = document.getElementById("symbol_buy");
    let buy_amount = document.getElementById("buy_amount");
    if (stock_symbol.value.length !== 3) {
        alert("3 character stock symbol required");
        return false;
    }
    if (buy_amount.value.length === 0 || parseFloat(buy_amount.value) <= 0) {
        alert("Positive amount required");
        buy_amount.value = "";
        return false;
    }
    let parcel = {
        Command: "BUY",
        userid: currentUser.value,
        StockSymbol: stock_symbol.value,
        amount: buy_amount.value
    };
    $.post("buyStock", parcel, function (data) { console.log(data); }, "json");
    stock_symbol.value = "";
    buy_amount.value = "";
}

function sell_stock() {
    event.preventDefault(); //stops page from resetting/reloading
    let currentUser = document.getElementById("userId");
    let stock_symbol = document.getElementById("symbol_sell");
    let sell_amount = document.getElementById("sell_amount");
    if (stock_symbol.value.length !== 3) {
        alert("3 character stock symbol required");
        return false;
    }
    if (sell_amount.value.length === 0 || parseFloat(sell_amount.value) <= 0) {
        alert("Positive amount required");
        sell_amount.value = "";
        return false;
    }
    let parcel = {
        Command: "SELL",
        userid: currentUser.value,
        StockSymbol: stock_symbol.value,
        amount: sell_amount.value
    };
    $.post("sellStock", parcel, function (data) { console.log(data); }, "json");
    stock_symbol.value = "";
    sell_amount.value = "";
}

function get_quote() {
    event.preventDefault(); //stops page from resetting/reloading
    let currentUser = document.getElementById("userId");
    let stock_symbol = document.getElementById("getQuote");
    if (stock_symbol.value.length !== 3) {
        alert("3 character stock symbol required");
        return false;
    }
    let parcel = {
        userid: currentUser.value,
        StockSymbol: stock_symbol.value
    };
    $.post("getQuote", parcel, function (data) { console.log(data); }, "json");
    stock_symbol.value = "";
}

function buy_trigger() {
    event.preventDefault(); //stops page from resetting/reloading
    let currentUser = document.getElementById("userId");
    let stock_symbol = document.getElementById("symbol_buy_trigger");
    let target_price = document.getElementById("targetPrice_buy");
    if (stock_symbol.value.length !== 3) {
        alert("3 character stock symbol required");
        return false;
    }
    if (target_price.value.length === 0 || parseFloat(target_price.value) <= 0) {
        alert("Positive amount required");
        target_price.value = "";
        return false;
    }
    let parcel = {
        Command: "SET_BUY_TRIGGER",
        userid: currentUser.value,
        StockSymbol: stock_symbol.value,
        amount: target_price.value
    };
    $.post("buyTrigger", parcel, function (data) { console.log(data); }, "json");
    stock_symbol.value = "";
    target_price.value = "";
}

function sell_trigger() {
    event.preventDefault(); //stops page from resetting/reloading
    let currentUser = document.getElementById("userId");
    let stock_symbol = document.getElementById("symbol_sell_trigger");
    let target_price = document.getElementById("targetPrice_sell");
    if (stock_symbol.value.length !== 3) {
        alert("3 character stock symbol required");
        return false;
    }
    if (target_price.value.length === 0 || parseFloat(target_price.value) <= 0) {
        alert("Positive amount required");
        target_price.value = "";
        return false;
    }
    let parcel = {
        Command: "SET_SELL_TRIGGER",
        userid: currentUser.value,
        StockSymbol: stock_symbol.value,
        amount: target_price.value
    };
    $.post("sellTrigger", parcel, function (data) { console.log(data); }, "json");
    stock_symbol.value = "";
    target_price.value = "";
}

function get_logs(admin = false) {
    event.preventDefault(); //stops page from resetting/reloading
    let parcel = {
            Command: "DUMPLOG",
            filename: "dumplog.txt"
    };
    if (admin){
        parcel.add("userid", document.getElementById("userId").value);
    }
    $.post("getLogFile", parcel, function (data) { console.log(data); }, "json");
}

function update_balance(valToAdd) {
    if (valToAdd == null || valToAdd < 0) return;
    let balance_field = document.getElementById("accountBalance");
    balance_field.textContent = (parseFloat(balance_field.textContent) + valToAdd).toString();
}
