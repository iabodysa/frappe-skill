# The checked and the unchecked call for a read and a write

Every read and every write ships as a checked call and an unchecked call that look identical from
the call site, and the permission code sits only in `DatabaseQuery` and in `Document` — never in
`frappe.db`. So the unchecked call is not a call with a check switched off; it is a call typed below
the layer where a check could exist, and nothing at the call site reads differently.

| What you typed | What is consulted | What is skipped |
|---|---|---|
| `frappe.get_list` | the DocType `read` right, permlevel, User Permissions, `permission_query_conditions` | nothing |
| `frappe.get_all` | nothing — it is `get_list` with the same argument turned off | all four |
| `frappe.qb.get_query` | nothing, and there is no argument to ask | all four |
| `frappe.db.sql`, `frappe.db.get_value`, `frappe.db.get_list` | nothing — this layer holds no permission code | all four |
| `doc.save()` | the `write` right, `validate`, the DocField properties the server enforces | nothing |
| `doc.save(ignore_permissions=True)` | `validate` and the field properties | the `write` right |
| `doc.db_set` | `before_change` and `on_change` | `validate`, `before_save`, `on_update` |
| `frappe.db.set_value` | nothing | every handler and every check |
| `doc.cancel()` | the `cancel` right | `_validate` entirely, including the workflow check |

A DocField property is the same pair in metadata: some are enforced on the server and the rest are
browser rules, so moving a controller check into `mandatory_depends_on` or `read_only_depends_on`
moves it out of every API call, patch, job and import at once.

## Settled by

| what it settles | leaf |
|---|---|
| the two calls, and where the permission code lives | `knowledge/permission/accessor.md` |
| why `get_query` has no argument to ask for a check | `knowledge/document/read.md` |
| the handlers `db_set` still reaches | `knowledge/document/db-set.md` |
| which DocField properties the server enforces | `knowledge/document/validation.md` |
| the save that skips `_validate` | `knowledge/document/cancel.md` |
| the violation that puts the old value back and saves | `knowledge/permission/permlevel.md` |
| what a bare rollback discards | `knowledge/document/transaction.md` |
| the query-condition hook whose falsy return shows every row | `knowledge/permission/hooks.md` |
| the condition that also admits an empty value | `knowledge/permission/user_permission.md` |
