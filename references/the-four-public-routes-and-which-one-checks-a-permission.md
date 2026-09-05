# The four public routes, and which one checks a permission

One of the four checks a DocType permission — the record route, and only while the DocType's
`allow_guest_to_view` is 0. The Web Form route checks a login, per record, and never the target
DocType's `create`. A file under `www/` is checked by nothing at all. A whitelisted call checks that
the function is on the whitelist and that the verb matches, which is not a permission.

| Route | Who answers it | What is checked before your code runs |
|---|---|---|
| a record of a `has_web_view` DocType | the document renderer | the publish field, then `allow_guest_to_view` OR the document permission OR a website permission |
| a Web Form | the Web Form renderer, then the record's own `get_context` | published, then a login, and only where the URL names a record |
| a file under `www/` or `templates/pages/` | the template renderer | nothing |
| `@frappe.whitelist()` at `/api/method` | the request handler | the whitelist and the HTTP verb |

The path is offered to the renderers in a fixed order and the FIRST one answering `can_render` takes
it, so a published Web Form owns its route before any file at that path is looked at. Inside the Web
Form, the insert runs with `ignore_permissions`, so `login_required` is the only condition between a
Guest and a new document of that DocType.

## Settled by

| what it settles | leaf |
|---|---|
| the fixed order and the first renderer that answers | `knowledge/web/routing.md` |
| the reversed walk for a page file and the forward walk for an asset | `knowledge/web/page-files.md` |
| the insert with `ignore_permissions` | `knowledge/web/form-permissions.md` |
| the four Check fields and the two that reach the write | `knowledge/web/form-settings.md` |
| the declared field a missing key blanks | `knowledge/web/form-write.md` |
| the four exceptions a portal page can answer with | `knowledge/web/status-codes.md` |
| the environment built with no extensions | `knowledge/web/jinja.md` |
| the whitelist, the verb, and the Server Script above them | `knowledge/api/whitelisted-method.md` |
| where v1 and v2 answer | `knowledge/api/rest-routes.md` |
| what the document permission consults | `knowledge/permission/accessor.md` |
| the guest check read ahead of any permission | `knowledge/web/document-page.md` |
| the controller method read instead of the hooks, and the default refusal | `knowledge/permission/website-permission.md` |
