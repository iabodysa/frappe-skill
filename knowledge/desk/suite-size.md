---
name: suite-size
description: Script Report is 89% of ERPNext's 180 standard reports, and reports per module is the number that maps to a crowded workspace, not report count or code size.
triggers: ["report_type", "Report Builder", "Query Report", "Script Report", "Custom Report", "execute", "columns", "data", "Report", "Select an account to print in account currency", "From Date must be before To Date", "how many reports does erpnext ship", "script report vs query report count", "how many reports does the accounting system actually ship with", "is my report too long compared to the normal ones", "which area has way too many reports in the sidebar", "the reports menu is a wall of links and nobody can find anything", "are we reinventing the wheel by writing our own reports", "how do i tell if a report is a near duplicate of another one", "how many of the built in reports actually draw a chart", "does having a companion javascript file mean the report has filters", "what is a normal number of reports for one business area", "our report list is out of control where do i start cutting"]
product: erpnext
---

# Report suite size

## paths

frappe/core/doctype/report/report.json — report_type, Report Builder, Query Report, Script Report, Custom Report
erpnext/accounts/report/general_ledger/general_ledger.py — execute, columns, data

## rules

MUST count Script Report as the framework's own default rather than a workaround, since 161 of ERPNext's 180 standard reports are Script Report against 13 Query Report and 6 Report Builder.
MUST expect a Script Report under 200 lines to be normal rather than lean, since the median across ERPNext, HRMS and Frappe's own Script Reports sits between 87 and 174 lines.
MUST read reports per module, not report count or code size, as the number that maps to a crowded workspace sidebar.
NEVER read a `.js` companion's existence alone as evidence of a filter; only 144 of ERPNext's 180 reports declare a `filters` array inside it.
NEVER assume a report with four or more return values renders a chart; only 31 of ERPNext's 180 return a non-empty chart as execute's fourth value, and only 6 return a non-empty report_summary as the fifth.
MUST treat a module carrying several times the median report count as the one to inspect for a report that duplicates a sibling plus one condition.

## values

erpnext report_type mix: Script Report 161, Query Report 13, Report Builder 6, total 180
script report count: erpnext 161, hrms 25, frappe 8
script report median lines: erpnext 168, hrms 174, frappe 87.5
script report mean lines: erpnext 227, hrms 211, frappe 100
erpnext reports declaring a filters array: 144 of 180
erpnext reports returning a non-empty chart: 31 of 180
erpnext reports returning a non-empty report_summary: 6 of 180
erpnext reports per module: median 7.5, Accounts 50, Stock 47, Selling 23, Manufacturing 21

## how

A count over the installed tree turns "too many reports" or "reinventing the wheel" from an opinion
into a comparison. Script Report dominates by a wide margin, so an app whose reports are all Script
Reports has reinvented nothing by that fact alone, and a report under 200 lines sits near the
framework's own median rather than below some notional standard.

The number that actually maps to what an operator meets is reports per module, because a workspace
renders one link per report regardless of how lean the code behind it is. Accounts and Stock sit far
above the median because they are the two largest domains of an ERP sold to many companies; a
single-company module carrying several times the median is the one worth opening, not the module with
the most lines of Python.

A crowded module is more often a filter away from shrinking than a deletion away: a report that
duplicates a sibling plus one condition should become that condition rather than stay a second file.
Filters and charts are declared per report, not inherited, so a `.js` file existing proves nothing
about what it declares — read the filters array and the fourth return value themselves rather than
infer either from a file's presence or a return statement's length.
