
lb_socket = new WebSocket("ws://127.0.0.1:44421");
let session_id = "";

lb_socket.onopen = function(e) {
    // alert("Connection established");
    console.log("Connection established")
};

lb_socket.onmessage = function(event) {
    // alert(`Data received from server: ${event.data}`);
    let response_cmd;
    let response;
    try {
        response = JSON.parse(event.data);
        response_cmd = response["Command"];
        console.log(response);
    }
    catch(error) {
        console.log(event.data);
        return;
    }
    switch(response_cmd) {
        case "LOGIN":
            // Check for success before switching over to new page
            if (response["Succeeded"] === true) {
                // update_username(response["userid"]);
                session_id = response["session"];
                window.location.href = 'day_trader';
            }
            else {
                console.log(response["Succeeded"]);
            }
        break;
        case "ADD":
            update_balance(response);
        break;
        case "QUOTE":
            update_quote(response);
        break;
        case "BUY":
            console.log(`${response["Command"]}: Succeeded=${response["Succeeded"]}`);
        break;
        case "COMMIT_BUY":
            console.log(`${response["Command"]}: Succeeded=${response["Succeeded"]}`);
        break;
        case "CANCEL_BUY":
            console.log(`${response["Command"]}: Succeeded=${response["Succeeded"]}`);
        break;
        case "SELL":
            console.log(`${response["Command"]}: Succeeded=${response["Succeeded"]}`);
        break;
        case "COMMIT_SELL":
            console.log(`${response["Command"]}: Succeeded=${response["Succeeded"]}`);
        break;
        case "CANCEL_SELL":
            console.log(`${response["Command"]}: Succeeded=${response["Succeeded"]}`);
        break;
        case "SET_BUY_AMOUNT":
            console.log(`${response["Command"]}: Succeeded=${response["Succeeded"]}`);
        break;
        case "CANCEL_SET_BUY":
            console.log(`${response["Command"]}: Succeeded=${response["Succeeded"]}`);
        break;
        case "SET_BUY_TRIGGER":
            console.log(`${response["Command"]}: Succeeded=${response["Succeeded"]}`);
        break;
        case "SET_SELL_AMOUNT":
            console.log(`${response["Command"]}: Succeeded=${response["Succeeded"]}`);
        break;
        case "CANCEL_SET_SELL":
            console.log(`${response["Command"]}: Succeeded=${response["Succeeded"]}`);
        break;
        case "SET_SELL_TRIGGER":
            console.log(`${response["Command"]}: Succeeded=${response["Succeeded"]}`);
        break;
        case "DISPLAY_SUMMARY":
            console.log(`${response["Command"]}: Succeeded=${response["Succeeded"]}`);
        break;
        default:
            console.log(`Unknown server response:${response}`)
    }
};

lb_socket.onclose = function(event) {
  if (event.wasClean) {
      // alert(`Connection closed cleanly, code=${event.code} reason=${event.reason}`);
      console.log(`Connection closed cleanly, code=${event.code} reason=${event.reason}`)
  } else {
      console.log("Connection died");
      // alert('Connection died');
  }
};

lb_socket.onerror = function(error) {
    alert(`${error.message}`);
};

function login() {
    event.preventDefault(); //stops page from resetting/reloading
    let username = document.getElementById("username");
    let password = document.getElementById("password");
    let parcel = {
        Command: "LOGIN",
        userid: username.value,
        password: password.value
    };
    lb_socket.send(JSON.stringify(parcel));
    username.value = "";
    password.value = "";
}

function add() {

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
        amount: add_field.value,
        session: session_id
    };
    // $.post("addFunds", parcel, function (response) {update_balance(response);}, "json");
    // if (true) {
    //     console.log(JSON.stringify(parcel));
    // }
    lb_socket.send(JSON.stringify(parcel));
    add_field.value = "";
}

function buy_stock() {
    event.preventDefault(); //stops page from resetting/reloading
    let currentUser = document.getElementById("userId");
    let stock_symbol = document.getElementById("symbol_buy");
    let buy_amount = document.getElementById("buy_amount");
    if (stock_symbol.value.length < 1 || stock_symbol.value.length > 3) {
        alert("1-3 character stock symbol required");
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
        amount: buy_amount.value,
        session: session_id
    };
    // $.post("buyStock", parcel, function (data) {
    //     console.log(data);
    // }, "json");
    lb_socket.send(JSON.stringify(parcel));
    stock_symbol.value = "";
    buy_amount.value = "";
}

function sell_stock() {
    event.preventDefault(); //stops page from resetting/reloading
    let currentUser = document.getElementById("userId");
    let stock_symbol = document.getElementById("symbol_sell");
    let sell_amount = document.getElementById("sell_amount");
    if (stock_symbol.value.length < 1 || stock_symbol.value.length > 3) {
        alert("1-3 character stock symbol required");
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
        amount: sell_amount.value,
        session: session_id
    };
    // $.post("sellStock", parcel, function (data) {
    //     console.log(data);
    // }, "json");
    lb_socket.send(JSON.stringify(parcel));
    stock_symbol.value = "";
    sell_amount.value = "";
}

function get_quote() {
    event.preventDefault(); //stops page from resetting/reloading
    let currentUser = document.getElementById("userId");
    let stock_symbol = document.getElementById("getQuote");
    if (stock_symbol.value.length < 1 || stock_symbol.value.length > 3) {
        alert("1-3 character stock symbol required");
        return false;
    }
    let parcel = {
        Command: "QUOTE",
        userid: currentUser.value,
        StockSymbol: stock_symbol.value,
        session: session_id
    };
    // $.post("getQuote", parcel, function (response) {update_quote(response);}, "json");
    lb_socket.send(JSON.stringify(parcel));
    stock_symbol.value = "";
}

function buy_trigger() {
    event.preventDefault(); //stops page from resetting/reloading
    let currentUser = document.getElementById("userId");
    let stock_symbol = document.getElementById("symbol_buy_trigger");
    let target_price = document.getElementById("targetPrice_buy");
    if (stock_symbol.value.length < 1 || stock_symbol.value.length > 3) {
        alert("1-3 character stock symbol required");
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
        amount: target_price.value,
        session: session_id
    };
    // $.post("buyTrigger", parcel, function (data) {
    //     console.log(data);
    // }, "json");
    lb_socket.send(JSON.stringify(parcel));
    stock_symbol.value = "";
    target_price.value = "";
}

function sell_trigger() {
    event.preventDefault(); //stops page from resetting/reloading
    let currentUser = document.getElementById("userId");
    let stock_symbol = document.getElementById("symbol_sell_trigger");
    let target_price = document.getElementById("targetPrice_sell");
    if (stock_symbol.value.length < 1 || stock_symbol.value.length > 3) {
        alert("1-3 character stock symbol required");
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
        amount: target_price.value,
        session: session_id
    };
    // $.post("sellTrigger", parcel, function (data) {
    //     console.log(data);
    // }, "json");
    lb_socket.send(JSON.stringify(parcel));
    stock_symbol.value = "";
    target_price.value = "";
}

function get_logs(admin = false) {
    event.preventDefault(); //stops page from resetting/reloading
    let parcel = {
        Command: "DUMPLOG",
        filename: "dumplog.txt",
        session: session_id
    };
    if (admin) {
        parcel.add("userid", document.getElementById("userId").value);
    }
    // $.post("getLogFile", parcel, function (data) {
    //     console.log(data);
    // }, "json");
    lb_socket.send(JSON.stringify(parcel));
}

function update_balance(responseJSON) {
    // if (isNaN(responseJSON)) return; # Always blocks for some reason
    let balance_field = document.getElementById("accountBalance");
    let valToSet = parseFloat(responseJSON["amount"]) + parseFloat(balance_field.textContent);
    balance_field.textContent = valToSet.toString();
}

function update_quote(responseJSON) {
    // if (isNaN(responseJSON)) return; # Always blocks for some reason
    let quote_symbol = document.getElementById("qt_sym");
    let quote_amount = document.getElementById("qt_amt");
    quote_symbol.textContent = responseJSON["StockSymbol"];
    quote_amount.textContent = responseJSON["Quote"];
}

function update_username(name_str) {
    let currentUser = document.getElementById("userId");
    currentUser.readOnly = false;
    currentUser.textContent = name_str;
    currentUser.readOnly = true;
}
