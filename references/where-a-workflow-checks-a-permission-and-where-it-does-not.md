# Where a workflow checks a permission, and where it does not

The transition is not the check. `apply_workflow` asks for `read` on the document and nothing more;
the write right arrives underneath it from the `save`, `submit` or `cancel` it delegates to. Three
conditions sit above that line — the role, the transition condition, and self-approval — and a plain
`save` re-runs two of them, a `submit` re-runs none and writes an approved state by itself, and a
`cancel` runs no workflow code at all.

| How the state changes | What is checked | What is skipped |
|---|---|---|
| `apply_workflow` — the Actions button, the emailed link, bulk approval | `read`, the role, the condition, self-approval, then the right the save beneath it needs | nothing on the state |
| `doc.save()` — REST `PUT`, `set_value`, Data Import, a client script, a job | `write`, the role, the condition | self-approval, and the docstatus never moves |
| `doc.submit()` with the state left alone | the `submit` right | every workflow condition — and the state is written forward |
| `doc.cancel()` | the `cancel` right | every workflow condition — the state is left where it stood |
| writing the state field directly | whatever the write path checks | self-approval, always |
| saving the Workflow record itself | nothing about any document | the state field is written into every document of its type, with no version history |

`allow_edit` on a state is read only by the desk, so it is a form rule and never a permission, and
the docstatus jumps between states are refused when the Workflow is SAVED rather than when a
document moves.

## Settled by

| what it settles | leaf |
|---|---|
| the checks on the save path, and the one that is not there | `knowledge/document/transitions.md` |
| `allow_edit` as a desk rule, and the docstatus jump refused at save | `knowledge/document/states.md` |
| one row per document and state, and the second state that produces nothing | `knowledge/document/action.md` |
| the raw write over every document on every Workflow save | `knowledge/document/doctype.md` |
| the cancel save that skips `_validate` | `knowledge/document/cancel.md` |
| the docstatus comparison that picks the action | `knowledge/document/submit.md` |
| the right each underlying write consults | `knowledge/permission/accessor.md` |
