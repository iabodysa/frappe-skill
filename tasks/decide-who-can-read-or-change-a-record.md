# Task — decide who can read or change a record

## Which surface is the gate

Which native surface answers this restriction?
MUST name the surface before writing any check by hand.
`references/permissions.md`

Which of them actually refuses a write?
MUST put the refusal on a DocPerm row, because the flags that look like gates only move the DocType between lists.
`knowledge/permission/docperm.md`

Which spelling of the read or the write is the one that checks?
MUST choose the accessor deliberately, because every read and every write ships in a checked form and an unchecked one, and no permission code sits in `frappe.db`.
`knowledge/permission/accessor.md`, `references/the-checked-and-unchecked-spelling-of-a-read-and-a-write.md`

## The gate is a role

Where does a role come from when no file declares it?
MUST declare the role in a fixture, because the one created on the fly carries desk access.
`knowledge/document/role-auto-created.md`

Is a list of role holders a list of users?
MUST resolve the holders through the framework call and MUST NOT count the child table, which nine parents share.
`knowledge/permission/role.md`

## The gate is a value on the row

Which primitive scopes rows to a value rather than a role?
MUST use a User Permission and MUST turn strict on when a row whose scoped field is empty has to be refused.
`knowledge/permission/user_permission.md`

Which layer enforces the condition a hook returns?
MUST return a condition the query layer can apply, and MUST read a falsy return as one hook denying, another permitting every row, and a third never reached by an API call.
`knowledge/permission/hooks.md`

Which read walks past the condition entirely?
MUST apply the scope above the query builder, which runs no permission check and offers no parameter to ask for one.
`knowledge/document/read.md`

## The gate is one field

How is a single field restricted rather than the whole row?
MUST set a permlevel and MUST NOT read a successful save as an accepted value, because the rejected value is put back and the save succeeds.
`knowledge/permission/permlevel.md`, `references/permissions.md`

## The surface is a report

Whose User Permissions scope a report's rows?
MUST declare a Link column for the scoped field, because the pass that applies the scope recognises nothing else.
`knowledge/desk/row-scope.md`

Who may run the report when its role table is empty?
MUST put rows on the report's own role table, because an empty one permits everyone and a Custom Role replaces rather than adds.
`knowledge/desk/roles.md`

Which report kind can outrun the request?
MUST expect a long Script Report to become a Prepared Report and a Query Report never to.
`knowledge/desk/report.md`

## The surface is a page, a workspace or a method

What does an empty roles table mean on a Page or a Report?
MUST fill the roles table, because empty permits instead of refusing.
`knowledge/permission/role.md`

Who sees a Workspace with no roles, and why did every DocType link vanish at once?
MUST fill the roles table, and MUST read every link disappearing for every non-Administrator user as the domain cache rather than a permission.
`knowledge/desk/workspace.md`

What does a whitelisted call check?
MUST check the DocType permission inside the method, because the route checks whitelist membership and the verb and nothing else.
`knowledge/api/whitelisted-method.md`

## The caller is unauthenticated or a portal user

What does a Guest POST carry?
MUST authenticate the payload itself on an `allow_guest` write, because the session carries no CSRF token.
`knowledge/permission/csrf.md`

Which identity does a portal visitor hold?
MUST set the user type and read the session as the portal rail rather than a desk one.
`knowledge/permission/portal_identity.md`

## A workflow or a notification stands in front of the write

Does an ignore-permissions write skip the workflow check?
MUST expect every transition check except self-approval to run on the save path, so writing the state field directly passes the one that is off.
`knowledge/document/transitions.md`

Does hiding an action refuse it?
MUST refuse the move in the transition rather than in the button the desk draws.
`knowledge/document/states.md`

Who receives a notification addressed to a role?
MUST confirm the named role holds a read permission when the Notification is written, because the resolver checks none.
`knowledge/job/notification.md`

## Hiding the surface instead of gating it

Can a DocType be hidden outright?
MUST answer concealment with DocPerm rows, because no root flag exists and a read-only DocType stays in the search index.
`knowledge/desk/hiding-a-doctype.md`
