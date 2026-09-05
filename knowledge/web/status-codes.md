---
name: status-codes
description: get_context picks a portal page's status by the exception it raises — Redirect, PermissionError or PageDoesNotExistError — and every other exception renders ErrorPage.
triggers: ["get_response", "handle_exception", "get_response_without_exception_handling", "NotPermittedPage", "NotFoundPage", "RedirectPage", "cache_html", "Invalid Sidebar JSON at", "portal page 404 vs 403", "web page status code exception", "my page shows a blank record instead of saying it does not exist", "the missing item page stays empty even after i added the item", "why does my page report success when there is nothing to show", "i want a visitor who is not allowed in to be sent to the login screen", "how do i show a proper access denied page instead of my own message", "the refusal message i wrote never reaches the user", "how do i send someone from one page to another address", "my test sees a rendered error page instead of the real error", "why can i not catch the error my page raises inside a test", "the login link forgets where the user was trying to go"]
product: frappe
---

# Status codes

## paths

frappe/website/serve.py — get_response, handle_exception, get_response_without_exception_handling
frappe/website/page_renderers/not_permitted_page.py — NotPermittedPage
frappe/website/page_renderers/not_found_page.py — NotFoundPage
frappe/website/page_renderers/redirect_page.py — RedirectPage
frappe/website/utils.py — cache_html

## rules

MUST raise frappe.PermissionError from a `www` page's get_context instead of rendering your own refusal template; NotPermittedPage already answers 403, prints the exception's own text and points a Login button at `/login?redirect-to=` the requested path.
MUST raise frappe.PageDoesNotExistError for a record that is not there, and NEVER return an empty context; a page that renders with no record answers 200 and that 200 is stored in the `website_page` cache under its path and language.
MUST call frappe.redirect from get_context to send the user elsewhere; it raises frappe.Redirect and RedirectPage carries the status code the exception holds.
MUST expect the login link to drop the redirect for a path under `/app`.
MUST call get_response_without_exception_handling when a test has to see the exception itself; get_response turns every exception into a rendered page.

## values

frappe.Redirect: RedirectPage, at the status code on the exception
frappe.PermissionError: NotPermittedPage, 403, exception text, Login button
frappe.PageDoesNotExistError: NotFoundPage
any other exception: ErrorPage

## how

A portal page does not set a status; it raises one. Three exception classes are the whole vocabulary,
and anything outside them is read as a crash. So the shape of a `www` controller is a get_context
that gathers what it needs and raises the moment a precondition fails, rather than one that returns a
context describing a failure.

Write the refusal as the exception's message, because that string is what the user reads on the
403 page. A hand-built refusal template costs you the status code, the message and the login
redirect, and gains nothing.

The 404 matters more than it looks: a missing record rendered as an empty page is a 200, and a 200 is
cached. The next request gets the empty page even after the record exists.
