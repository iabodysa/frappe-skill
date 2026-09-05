---
name: frappe-request
description: An exc in a 2xx body is printed to the console and the call resolves, and the status on a thrown error is read off the body text so it is always undefined.
triggers: ["frappeRequest", "transformRequest", "transformResponse", "transformError", "call", "request", "frappe-ui request error status", "exc in 2xx response body", "the call worked but i got nothing back", "my request returns success and the data is undefined", "why does a failed server call still look like it succeeded", "the server threw an error and my catch block never ran", "nothing is caught when the backend raises halfway through", "how do i catch a server side failure that comes back as a 200", "i see a red error printed in the console but the code carries on", "the console shows a traceback and my page acts like everything is fine", "the status code on the error object is always undefined", "i cannot tell a permission failure from a server crash in my error handler", "how do i read the http status code of a failed call", "my retry on server errors never triggers because the status is missing"]
product: frappe-ui
---

# frappeRequest

## paths

src/utils/frappeRequest.js — frappeRequest, transformRequest, transformResponse, transformError
src/utils/call.js — call
src/utils/request.js — request
src/utils/config.ts — getConfig

## rules

MUST expect `transformResponse` to branch on `response.ok` before it reads the payload.
MUST expect a `data.exc` on a 2xx response to be parsed into a collapsed console group and nothing else — no throw, no rejection, no mark on the resolved value.
MUST expect that branch to return `data.message`, which is commonly `undefined` when the server raised after answering.
MUST read `data.exc` yourself before trusting a resolved value where the endpoint can raise late; a `try`/`catch` around the call never fires.
MUST expect the whole body, not `data.message`, to be returned when it carries `docs` or when the url is the login endpoint.
MUST expect `_server_messages` to be handed to `getConfig('serverMessagesHandler')` or to `options.onServerMessages`, and to be dropped when neither is set.
NEVER read `error.status` on an error thrown by this fetcher: the non-ok branch assigns it from the body text, which has no `status`, so it is always `undefined`.
MUST read `error.response.status` for the HTTP status, and MUST expect `exc_type`, `exc` and `messages` to be the usable fields.
MUST expect `call` to set `status` correctly from the fetch response, so the defect belongs to `frappeRequest` alone.
MUST expect every resource error to travel this path in an app that sets `resourceFetcher` to `frappeRequest`.

## values

request default method: POST
url rewrite: a url starting with neither `/` nor `http` is prefixed with `/api/method/`
headers: Accept and Content-Type json, `X-Frappe-Site-Name` from the hostname, `X-Frappe-CSRF-Token` from `window.csrf_token`
2xx with exc: console group, then `return data.message`
non-2xx fields: `exc_type`, `exc`, `response`, `status` undefined, `messages`
messages fallback: `_error_message`, else `Internal Server Error`

## how

The fetcher treats the HTTP status as the whole answer, and Frappe does not always agree with it: a whitelisted method that raises after the response has begun answers 200 with an `exc` in the body. So a caller that only writes a `catch` block has no coverage for a real class of server failures, and the failure shows up as `undefined` where data was expected.

When a status code is what a `catch` block needs to branch on — a 403 into a login route, a 5xx into a retry — read it from `error.response`. Reading it from `error.status` compiles, runs, never matches, and leaves a branch that looks tested.
