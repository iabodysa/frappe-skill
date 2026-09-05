# Where an Arabic string is allowed to live

Every source string stays English and every Arabic string goes into `<app>/translations/ar.csv` and
nowhere else, because that CSV is the only source an app owns in the merge and the only one a
`bench migrate` re-reads. A string written in Arabic inside a DocType JSON, a fixture, a workspace
or a python module is not translated — it is the source, and no language can move it.

| Where a string can be resolved | What the framework reads | What it cannot do |
|---|---|---|
| the app's `translations/<lang>.csv` | a plain dict in file order, last row wins | carry a row that is neither two nor three columns |
| a PO compiled to an MO under `sites/assets/locale` | the MO, only when it is older than the PO by mtime | notice a PO edit under an MO with a newer timestamp |
| a contextual key `source:context` | that key first, the bare source second | be selected by a field — context is part of the key |
| `_()` at call time | `local.lang` as it stands when the call runs | survive a module body, which freezes English at import |
| `_lt` | the same lookup, deferred to render | nothing — this is the form that survives a module body |
| the merged dict per language | five sources in a fixed order, country names last | keep the three highest when one of them raises |

| Layer to extract | Where the English lives |
|---|---|
| DocType label, field label, Select option, description | the DocType JSON |
| workspace title, card label, shortcut label | the Workspace record |
| report label, column label, filter label | the report JSON and its controller |
| message, title, throw and msgprint text | the controller |
| button label, dialog title, client message | the DocType JS |

## Settled by

| what it settles | leaf |
|---|---|
| the file-order dict, the last-row win, and the skipped row | `knowledge/bench/csv.md` |
| the mtime comparison that skips a recompile in silence | `knowledge/bench/gettext.md` |
| `source:context` as a key rather than a field | `knowledge/bench/context.md` |
| why a module body freezes English and `_lt` does not | `knowledge/bench/lazy.md` |
| the five sources, the order, and the suppressed failure | `knowledge/bench/merge.md` |
| the install order that lets an app row replace the framework's wording | `knowledge/bench/app-over-framework.md` |
| the dictionary the desk is handed and the portal page is not | `knowledge/bench/frontend-boundary.md` |
