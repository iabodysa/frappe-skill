# Who may run a report, and what it is allowed to read

Two checks decide who may RUN any report and both ask the session, never the `user` argument: the
report's own role table, then the `report` right on its `ref_doctype`. What the report may READ is
decided by `report_type` alone — a Report Builder report is filtered by the framework, a Query
Report cannot be filtered at all, and a Script Report is filtered only where its author wrote a
checked read. A print format is not a third type.

| `report_type` | What runs | How the rows are scoped |
|---|---|---|
| Report Builder | the framework's own list read | the DocType read right, permlevel, User Permissions and the query-condition hooks |
| Query Report | the SQL on the record | not at all — there is nothing between the SQL and the result |
| Script Report | `execute` in the report module, unsandboxed | only by whatever the author typed; the framework adds nothing |
| the row filter that runs after any of them | one pass over the returned rows | Link columns only, and a column whose cells are all empty is dropped |
| a Print Format on a DocType | sandboxed Jinja on the server | the `print` right, consulted only after `read` has passed |
| a Print Format on a Report | the browser's template engine | nothing on the server |

A Custom Role REPLACES a report's own role table instead of adding to it, and a report with rows on
neither table is permitted to everyone.

## Settled by

| what it settles | leaf |
|---|---|
| the Custom Role replacement and the empty table that permits | `knowledge/desk/roles.md` |
| the user as an argument, the Link-only pass, the dropped column | `knowledge/desk/row-scope.md` |
| the blank `is_standard` and the write into the app folder | `knowledge/desk/standard.md` |
| the module html ahead of the field, and the browser engine | `knowledge/desk/print-format.md` |
| why `print` refuses nobody who can read | `knowledge/desk/print-permission.md` |
| the six values `execute` is unpacked to, and the Prepared Report turn | `knowledge/desk/report.md` |
| the checked read a Script Report author has to type | `knowledge/permission/accessor.md` |
| the empty role list that permits rather than refuses | `knowledge/permission/role.md` |
