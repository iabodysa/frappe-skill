# The records that carry code, and what each one runs

Six desk records are ROWS in a table rather than files in an app: Report, Print Format, Web Form,
Workspace, Dashboard Chart and Number Card. Each writes itself back into the app folder when saved,
and none of the six takes its visibility from the DocPerm rows of its own DocType — every one
carries its own check, and three of them execute code no deploy step reviewed.

| Record | What it can execute | Whose permission decides who sees it | Re-imported from disk on migrate |
|---|---|---|---|
| Report, `report_type` Script | unsandboxed python in `execute` | its own role table, then `report` on `ref_doctype` | yes |
| Report, `report_type` Query | SQL only, filtered by nothing | the same two checks | yes |
| Print Format | Jinja on the server, or the browser's template engine for a Report | the `print` right, after `read` has passed | yes |
| Web Form | a python module of its own, beside the record | `login_required`, and nothing about the target DocType | yes |
| Workspace | nothing of its own — it executes through the records it names | its roles table, empty meaning everyone | yes |
| Dashboard Chart | a Custom source module, evaluated by the browser | the DocType being charted, at read | no |
| Number Card | a whitelisted method the browser calls | derived from the method | no |

A report saved with a blank `is_standard` turns standard for Administrator in `developer_mode`,
writes its JSON and controllers into the app folder, and then refuses deletion wherever
`developer_mode` is off.

## Settled by

| what it settles | leaf |
|---|---|
| the blank `is_standard`, the write to disk, the refusal | `knowledge/desk/standard.md` |
| the Custom Role replacement and the empty table that permits | `knowledge/desk/roles.md` |
| the user arriving as an argument, and the Link-only pass | `knowledge/desk/row-scope.md` |
| the module html ahead of the field, and the browser engine | `knowledge/desk/print-format.md` |
| why `print` refuses nobody who can read | `knowledge/desk/print-permission.md` |
| the six values `execute` is unpacked to, and the Prepared Report turn | `knowledge/desk/report.md` |
| the links table, and the empty roles table | `knowledge/desk/workspace.md` |
| the insert with `ignore_permissions` | `knowledge/web/form-permissions.md` |
| the four Check fields and where each acts | `knowledge/web/form-settings.md` |
| the folders migrate re-imports, and the permanent skip | `knowledge/bench/standard-json.md` |
| the concatenation order, and the layout that drops the script | `knowledge/desk/client-script.md` |
| which report type ERPNext's own shipped suite is made of | `knowledge/desk/suite-size.md` |
