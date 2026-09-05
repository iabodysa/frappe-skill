# Frappe is shorter than you wrote it

Name the call the framework already ships before writing one, and read the swap as a behaviour
change until proved otherwise. The long form is written for two reasons: the reader met the call in
one use and never looked for a second, or a solution that worked elsewhere blocked the one present
here. Both are found by asking what the framework calls the concept, never by reading the hand code.

| What you were about to write | The call that already does it | What changes |
|---|---|---|
| one `get_value` per field | `frappe.db.get_value` with a list of fields | one query instead of many |
| `len(frappe.get_all(...))` | `frappe.db.count` | the rows are never built |
| an order-by-then-take-one read | `frappe.get_last_doc` | a Document, not a row |
| an existence check before a delete | `frappe.delete_doc` with `ignore_missing` | the link check still runs |
| loading a Single to read one field | `frappe.db.get_single_value` | no Document is constructed |
| a hand-built desk URL | `frappe.utils.get_url_to_form` | the site's own host and route |
| `", ".join(...)` for a message | `frappe.utils.comma_and` | the conjunction is translated |
| `round()` on a currency amount | `frappe.utils.fmt_money` | the currency's own precision and symbol |
| copying fields onto a new document | `frappe.copy_doc` | the no-copy fields are dropped for you |
| a full `save` to change one field | `doc.db_set` | `validate` and `before_save` are skipped, `on_change` is not |

`db_set` is the swap that is not always safe, because the short form drops a check the long form
ran, and a swap that drops a check is a defect however much shorter it reads.

## Settled by

| what it settles | leaf |
|---|---|
| what `db_set` skips and what it still runs | `knowledge/document/db-set.md` |
| the checked and the unchecked call for every read and write | `knowledge/permission/accessor.md` |
| what `frappe.format` returns, and the `inline` argument | `knowledge/desk/formatters.md` |
| what `copy_doc` clears, and everything outside the tables it drops | `knowledge/document/copy.md` |
| what `force` skips, and the live reference a forced delete leaves | `knowledge/document/delete-doc.md` |
| what `get_value` returns, and the cache `count` answers from | `knowledge/document/read-shortcuts.md` |
| what `fmt_money` reads first, and the quoted key `comma_and` never matches | `knowledge/job/format-helpers.md` |
| the three wrappers whose behaviour differs from the stdlib call | `knowledge/job/stdlib-wrappers.md` |
| the setting a week boundary is resolved from, rather than `weekday()` | `knowledge/job/week-boundary.md` |
| the day it returns, and the wildcard that re-exports it | `knowledge/job/get-last-day.md` |
| the single join, and the users it filters out | `knowledge/job/get-users-with-role.md` |
| the rendered template it returns rather than a plain string | `knowledge/job/render-address.md` |
| which QR package the bench actually ships | `knowledge/job/qrcode.md` |
| what each of the three caches scopes to, and what none of them expresses | `knowledge/job/cache-decorators.md` |
