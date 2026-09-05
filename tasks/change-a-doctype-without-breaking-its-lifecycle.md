# Task — change a DocType and keep its lifecycle intact

## The rule and where it runs

Where does a check on a saved document go?
MUST write it in the controller's `validate`, because the position in the save order decides whether the check never fires or throws before the framework's own message.
`knowledge/document/save.md`

An app handler, a wildcard handler and a controller override all claim the same event — which one carries the decision?
MUST address the handler to the DocType by name, and MUST NOT let a wildcard entry or a second override own the outcome.
`knowledge/document/hooks.md`

Which declaration is the right place for the change?
MUST choose the entry from the declared hook surface before writing a handler at all.
`references/the-files-an-app-is-made-of-and-what-each-one-declares.md`

## The name

How does the record get its name?
MUST set exactly one naming route, because the first step that produces a name ends the sequence and every later step is skipped in silence.
`knowledge/document/autoname.md`

What does taking a series number cost a concurrent insert?
MUST keep the transaction that takes a number short, because the lock on the counter row is held until that transaction commits.
`knowledge/document/naming-series.md`

Where does the file have to sit for the name to resolve to a class?
MUST place the module and the controller on the derived path before naming anything.
`references/choosing-a-naming-rule-and-keeping-the-tests-off-its-counter.md`

## The fields

Which field property does the server actually enforce?
MUST express the rule with a property the server checks, and MUST NOT move it into a `depends_on`, which only the browser reads.
`knowledge/document/validation.md`

Can a Time field's default decide what an insert stores?
MUST set the value in code when the insert time is not the wanted value.
`knowledge/document/defaults.md`

Will a mandatory Select ever be empty?
MUST validate the chosen option in the controller, because the mandatory check cannot refuse a Select whose options open with a real value.
`knowledge/desk/select.md`

Where does a company default on the field come from?
MUST resolve it through the framework helper, because the user default is read before the Global Defaults field and a hand resolver that skips either step reads a different value.
`knowledge/document/get-default-company.md`

## Reshaping the table

Is a field rename one change or two?
MUST ship the JSON edit and the rename patch together, and MUST order the patch before the schema pass.
`knowledge/document/rename-doc.md`, `knowledge/document/rename-field.md`

When does the schema hook fire?
MUST change the DocType JSON in the same commit as the index the hook is meant to create.
`knowledge/document/doctype-update-hook.md`

Does a unique index refuse a duplicate on an optional column?
MUST make the column mandatory when uniqueness has to hold.
`knowledge/document/unique-index.md`

Can a savepoint hold the schema change back?
MUST run the DDL outside any savepoint the patch means to roll back.
`knowledge/document/transaction.md`

## Submit, cancel and workflow

What does a second submit request do?
MUST guard the submit against a concurrent one at the database, because the action is chosen from the docstatus each request read for itself.
`knowledge/document/submit.md`

Which checks run on the write that cancels?
MUST NOT put a rule the cancel has to obey in `validate`, because the cancel save skips that path entirely.
`knowledge/document/cancel.md`

What does saving a Workflow do to documents that already exist?
MUST expect the state field to be written into every document of the type, on every save of the Workflow.
`knowledge/document/doctype.md`

What is left behind when a transition is removed?
MUST clear the open action rows the removed transition owned, because a document reaching a state twice produces none.
`knowledge/document/action.md`

What clears an open action row after a state change made outside the lifecycle?
MUST NOT expect a hard delete or an out-of-lifecycle write to clear it, because one native path clears the row and no log setting trims it.
`knowledge/document/workflow-action-orphans.md`

## Writing without going through save

Does a direct field write escape the handlers?
MUST expect `before_change` and `on_change` to run anyway, so a write chosen to dodge a handler still reaches it.
`knowledge/document/db-set.md`

What does a bare rollback discard?
MUST name a savepoint when only part of the request is to be undone.
`knowledge/document/transaction.md`

Which spelling of the write is the checked one?
MUST pick the accessor deliberately, because every read and every write ships in a checked form and an unchecked one.
`knowledge/permission/accessor.md`, `references/the-checked-and-unchecked-spelling-of-a-read-and-a-write.md`

## Querying the changed DocType

What does the query builder check before it returns rows?
MUST apply the permission at a layer the query builder does not, and MUST read a dict in the fields list as a child-table request.
`knowledge/document/read.md`

Is there a native call for the loop about to be written?
MUST name the native form before writing the loop.
`references/frappe-is-shorter-than-you-wrote-it.md`

## What the desk shows afterwards

Will the new DocType or report appear where users look?
MUST add the link to the Workspace child table, because nothing is listed automatically and an empty roles table shows the Workspace to everyone.
`knowledge/desk/workspace.md`

Which indicator does the list view pick?
MUST set the indicator deliberately when the default precedence picks the wrong one.
`knowledge/job/list-indicator-precedence.md`

How do users learn the change happened?
MUST write the note into the major-version folder the popup reads.
`knowledge/document/changelog-popup.md`
