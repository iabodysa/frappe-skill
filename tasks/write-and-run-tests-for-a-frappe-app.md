# Task — write and run tests for a Frappe app

## Where the test goes and what finds it

Which rules bind a Frappe test?
MUST settle them before the first assertion.
`references/writing-tests-the-frappe-way.md`

Which directory does the runner read the test from, and what does the app's own hook cover?
MUST place the file where discovery looks, and MUST expect the before-tests hook to fire for the app under test alone.
`knowledge/bench/runner.md`

## Whether the run's exit code can be trusted

Does a failing suite end the process red?
MUST set the CI variable, because the runner exits at zero without it and a red run is recorded as green.
`knowledge/bench/runner.md`

## The records the test needs

Where do the test's records come from?
MUST build the record in the test when it has to change, because the shipped fixture is built once per site and an edited file is never read again.
`knowledge/bench/records.md`

## What the database does between tests

When does the write disappear?
MUST NOT rely on a clean table between two tests of one class, because the rollback is queued for after the last of them.
`knowledge/bench/rollback.md`

What does a bare rollback in the code under test discard?
MUST name a savepoint when only part of the work is to be undone.
`knowledge/document/transaction.md`

## Asserting a refusal and holding state

Which exception does a framework refusal raise?
MUST assert the specific subclass, because every refusal is a subclass of one class and asserting the base passes for the wrong reason.
`knowledge/bench/case.md`

Which helper changes a setting, a hook or the user for the block?
MUST import the module-level helper rather than call a method on the case, and MUST expect the user helper to restore the user the block was entered with.
`knowledge/bench/case.md`

## Side effects the test must not let out

Does mail leave the test site?
MUST check the mute and the suspend flag, because a refused row keeps its unsent status and every later flush picks it up.
`knowledge/job/email-queue.md`

Does a webhook fire from the code under test?
MUST read the delivery as enqueued and MUST expect the test flag alone to run it inline.
`knowledge/api/webhook.md`

Does a background job run, and when?
MUST set the after-commit flag, because the job is handed to a worker before the enqueueing transaction commits.
`knowledge/job/enqueue.md`

Does a scheduled entry run against a paused site?
MUST call the entry point that reads the pause flags, because calling the inner one runs the jobs of a paused site.
`knowledge/job/scheduler.md`

A method named in the hooks stopped resolving — what happens to its row?
MUST remove the hooks line, because the row is deleted only when the method string is gone from hooks.
`knowledge/job/scheduled-type.md`

Is the log line emitted at all?
MUST raise the logger's level before asserting on its output.
`knowledge/job/logger.md`
