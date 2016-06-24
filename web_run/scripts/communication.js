function send(method, conten_type, url, async, data, callback) {
    var x;
    if(window.XMLHttpRequest) {
        x = new XMLHttpRequest();
        
        x.open(method, url, async);

        x.onreadystatechange = function() {
            if(x.readyState === 4) {
                if(x.status === 200) {
                    var data = {
                        text: x.responseText,
                        xml: x.responseXML
                    };
                    callback.call(this, data);
                }
            }
        }

        if(method.toLowerCase() === "post") {
            //x.setRequestHeader("Content-Type", conten_type);
            x.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            //x.setRequestHeader("Content-Length", data.length);
            //x.setRequestHeader("Connection", "close");
        }

        x.send(data);
    } else {
        // ... implement code for not support XMLHttpRequest browser here ...
    }
    return x;
}
