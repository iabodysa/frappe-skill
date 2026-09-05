---
name: naming-series
description: A series number is taken under a FOR UPDATE lock on one tabSeries row and that lock is held until the inserting transaction commits, so every insert sharing a resolved prefix is serialised for the whole of its transaction.
triggers: ["NamingSeries", "NamingSeries.validate", "NamingSeries.get_prefix", "NamingSeries.get_preview", "NamingSeries.update_counter", "getseries", "parse_naming_series", "revert_series_if_last", "set_name_by_naming_series", "get_default_naming_series", "has_custom_parser", "InvalidNamingSeriesError", "Special Characters except", "Invalid name type (integer) for varchar name column", "Please set the document name", "naming series counter lock", "series number skipped", "saving new records is very slow when many people create them at once", "everyone waits when two people add a record at the same moment", "why do new documents take so long to save under load", "i keep getting a deadlock error when several test runs go together", "the transaction was aborted because another one was doing the same thing", "numbers are being skipped in my document numbering", "the counter jumped and left a gap in the sequence", "my numbering format was rejected when i tried to save it", "it says special characters are not allowed in my numbering format", "the preview number is not the number the record actually ended up with", "only the first block of hashes gets filled and the rest stay empty", "how do i stop one long save from blocking everyone else's new records"]
product: frappe
---

# Naming series

## paths

frappe/model/naming.py — NamingSeries, NamingSeries.validate, NamingSeries.get_prefix, NamingSeries.get_preview, NamingSeries.update_counter, getseries, parse_naming_series, revert_series_if_last, set_name_by_naming_series, get_default_naming_series, has_custom_parser, InvalidNamingSeriesError

## rules

MUST expect every insert sharing one resolved prefix to run one transaction at a time, because getseries selects the tabSeries row with for_update and no code releases that lock before the transaction ends.
MUST keep validate, child row writes and every doc_events handler that runs after naming short, because the series row stays locked for the rest of the transaction and not for the increment alone.
MUST name documents in the same order in every worker, or expect the database to abort one transaction with a deadlock on tabSeries when two transactions take two series in opposite orders.
MUST split a contended series with a date or fieldname part, because parse_naming_series builds the counter key from the prefix resolved for that document and each resolved value gets its own tabSeries row.
MUST put a dot before the # placeholders, because NamingSeries.validate throws InvalidNamingSeriesError when the series carries no dot, carries a character outside word characters, hyphen, space, slash, dot, # and braces, or carries a # with no .# ahead of it.
NEVER expect a second run of # in one series to consume a second number; parse_naming_series fills the first run and leaves every later one empty.
MUST expect revert_series_if_last to take the same for_update lock on the same row, so the rollback path contends exactly as the allocation path does.
NEVER read a preview as an allocation; get_preview parses the series with a counter that never touches tabSeries.

## values

counter table: tabSeries, column current, one row per resolved prefix
allocation: select current where name = key for update, then UPDATE tabSeries SET current = current + 1, or INSERT current = 1 when the row is absent
lock held: from naming near the start of insert until the whole transaction commits or rolls back
key: everything parse_naming_series resolved before the first # part
parts: YY, YYYY, MM, DD, WW, timestamp, a fieldname on the document, {fieldname}, and any part a naming_series_variables hook parses
digits: the length of the # run, zero padded
missing #: NamingSeries appends .##### to the series
set_name_by_naming_series: appends .##### to doc.naming_series, and falls back to the first non-empty naming series option when the field is empty
empty naming_series with no option: frappe.throw of "Naming Series mandatory"
revert: decrements only when tabSeries.current equals the number parsed out of the name
update_counter: inserts the row at 0 when absent, then sets current outright

## how

A series is a counter in a table, not a sequence in the database, so its cost is a row lock rather than an allocation. The lock is taken when the document is named, which is near the start of insert, and it is an ordinary transactional lock — it lives until commit. Everything the insert does afterwards runs inside that window, so the throughput of a series is not the speed of the increment but the length of the slowest transaction that uses it.

That gives two failures with one cause. Inserts on one prefix queue behind each other, and a slow hook in one of them stalls every other insert of that prefix. Transactions that take more than one series can deadlock, because the lock order is whatever order each transaction happened to name its documents in; several test suites against one site produce this by inserting overlapping doctypes in different orders.

Change the key, because the lock is taken per key. Read the series as a key generator: parse_naming_series resolves every part before the first # and that resolved string is the row. A flat prefix is one row for the whole site; a prefix carrying a year, a month or a fieldname is one row per value, and contention drops to the writers that share that value. Choose the part by what the readers of the name expect to see, then check whether it also splits the traffic.

Ask what the name must survive before reaching for a series at all. A series buys a readable, ordered, gap-averse identifier and charges a shared lock for it. A document nothing but a join reads does not need that identifier and should not pay that lock.
