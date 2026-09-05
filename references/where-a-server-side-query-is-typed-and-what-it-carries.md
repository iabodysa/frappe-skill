# Where a server-side query is typed, and what it carries

A read answers to the session it is typed into, and both contexts a developer proves a query in —
`bench console` and `bench execute` — hand it Administrator, who is exempted from the DocType
permission, from User Permissions and from every permlevel before any of the three is consulted. So
a query proved at the console has been proved against nothing. The identical line inside a
whitelisted method answers to a real user, a real User Permission and a real permlevel.


| Where the line is typed | The user it answers to | What rewrites that user |
|---|---|---|
| `bench console` | Administrator | nothing |
| `bench execute` | Administrator | nothing |
| a whitelisted method on a request | the session user | `frappe.set_user`, and a Server Script's own entry read |
| a Server Script | the session user, read once at entry | nothing after that read |
| a Query Report | the session user for the two run checks; the row filter takes a user as an ARGUMENT | whatever the caller passes as that argument |
| a background job | the user who queued it | the scheduler, which queues as Administrator |
| a controller method | whatever the caller's session already is | its caller — it has no context of its own |
| a Web Form insert | Guest, where `login_required` allows it | the `anonymous` setting, which forces Guest |

## Settled by

| what it settles | leaf |
|---|---|
| where the permission code lives and why Administrator skips it | `knowledge/permission/accessor.md` |
| the Administrator exemption before the check | `knowledge/permission/permlevel.md` |
| the hook an API call never reaches, and the falsy return | `knowledge/permission/hooks.md` |
| the condition and its empty-value admission | `knowledge/permission/user_permission.md` |
| the user arriving as an argument to `run` | `knowledge/desk/row-scope.md` |
| the console session and its rollback at exit | `knowledge/bench/site-commands.md` |
| what the scheduler queues as | `knowledge/job/scheduler.md` |
| the user a queued job carries | `knowledge/job/enqueue.md` |
| the Server Script that answers above the whitelist check | `knowledge/api/whitelisted-method.md` |
| the insert that runs with `ignore_permissions` | `knowledge/web/form-permissions.md` |
| which call drops which check, once the user is settled | `references/the-checked-and-unchecked-spelling-of-a-read-and-a-write.md` |
