# What answers a permission question, and in what order

`has_permission` answers a narrower question the more it is handed: with no document it answers "any
document of this DocType", with one it layers the controller hook, `if_owner` and User Permissions
over the role rows. Roles are ADDITIVE and every right is an OR across the applicable rows, so a
narrow row can never correct a broad one. A denial is still not final — an explicit Share grants
access after the whole sequence has said no.

| Layer | What it reads | What it can do |
|---|---|---|
| Administrator | the user name | return true before anything else runs |
| DocPerm rows | `role in roles` and `permlevel == 0` | grant only; it is the only thing that refuses a write |
| `if_owner` on a granted right | the owner of the document | scope `read`, `write` and `delete`; never `create` |
| User Permission | four fields on the row | add a row condition that also admits an empty value, unless strict is on |
| permlevel above 0 | the DocPerm rows at that level | put the old value back and let the save succeed |
| `has_permission` hook | one document | deny; it cannot grant what the rows withheld |
| `permission_query_conditions` hook | the list query | subtract rows; a falsy return shows every row |
| `get_permission_query_conditions` on an API call | nothing — it is never reached there | nothing |
| Share | the Share rows | grant `read`, `write`, `share`, `submit`, `email`, `print` after a denial |

`in_create` and `read_only` are not refusals: they move a DocType between lists and stop nothing, so
concealing a DocType is a DocPerm question rather than a flag.

## Settled by

| what it settles | leaf |
|---|---|
| where the permission code lives and where it does not | `knowledge/permission/accessor.md` |
| the only row that refuses, and what `in_create` really does | `knowledge/permission/docperm.md` |
| Has Role shared by nine parents, and the empty list that permits | `knowledge/permission/role.md` |
| the four fields and the empty-value admission | `knowledge/permission/user_permission.md` |
| the silent revert, and the Administrator exemption | `knowledge/permission/permlevel.md` |
| three hooks, three paths, three readings of a falsy return | `knowledge/permission/hooks.md` |
| why concealment is a DocPerm act | `knowledge/desk/hiding-a-doctype.md` |
| the ledger write its own writer exempts from every row | `knowledge/permission/subledger.md` |
