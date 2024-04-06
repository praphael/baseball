const apiHost="localhost:5000"
const baseURL="http://"+apiHost

function makeRequestObj(method, body, bodyType="json", authToken="") {
    let contentType = "json"
    if (bodyType == "text")
        contentType = "text/plain";

    let req = { method: method, 
                headers: { 'Content-Type': contentType, 
                           'Authorization' : authToken
                         },
                mode: 'cors' };
    if (method == 'POST') {
        req.body = "";
        if (body != null && body != undefined)
            req.body = JSON.stringify(body);
    }
        
    return req;
}

async function doRequest(route, method, body, bodyType, responseType, authToken, errHandler) {
    try {
        const requrl = baseURL + route;
        // console.log("doRequest(): fetching '", requrl, "'", " body='", body, "'");
        const response = await fetch(requrl, makeRequestObj(method, body, bodyType, authToken));
        const status = response.status;
        // console.log(`doRequest(${route}): status= `, status);
        if (response.ok) {
            let r = null;
            if(responseType == "json")
                r = await response.json();
            else r = await response.text();
            return r;
        } else {
            const error = await response.text();
            errHandler({route, status, error});
        }
    } catch (error) {
        console.error(`'${route}' fetch error: ${error}`);
        const status = null
        errHandler({route, status, error});
    }
    return null;
}

function handleRequestError({route, status, errMsg}) {
    console.log("ERROR route: ", route, "status: ", status, " error: ", errMsg);
    //alert(route, " failed status ", status, " \nerror message:\n", errMsg);
}

export {doRequest, handleRequestError, makeRequestObj };

