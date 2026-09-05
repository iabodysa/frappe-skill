---
name: dashboard-chart
description: A Custom chart is served by a Dashboard Chart Source pair of files in a module folder, and every chart answer is stored under one shared key chart-data:<name> that ignores the user and the filters.
triggers: ["DashboardChart", "cache_source", "generate_and_cache_results", "chart-data", "no_cache", "refresh", "last_synced_on", "chart_type", "Custom", "source", "DashboardChartSource", "get_config", "source_name", "timeseries", "frappe.dashboards.chart_sources", "get_permission_query_conditions", "has_permission", "check_required_field", "check_document_type", "validate_custom_options", "get_group_by_chart_config", "get_heatmap_chart_config", "Cannot edit Standard charts", "Invalid Filter Value", "You cannot create a dashboard chart from single DocTypes", "dashboard chart stale", "custom dashboard chart source", "get_settings", "get_filters_for_chart_type", "frappe.dom.eval", "export_to_files", "IMPORTABLE_DOCTYPES", "add_fetch", "xIsSeries", "chart source js not loading", "dashboard chart source file", "chart filters custom source", "the chart shows the same numbers no matter which filter i pick", "two users see identical chart numbers even though their data is different", "why does changing the date range not change the chart?", "the chart numbers are old and never update", "the chart still shows yesterday's totals", "how do i force the chart to recalculate?", "the chart is visible to me as admin but nobody else can see it", "regular users get an empty dashboard while mine looks fine", "my own chart throws an error instead of drawing anything", "the chart has no filter controls of its own", "it tells me i cannot edit this chart", "the timestamp says it synced but the numbers did not move"]
product: frappe
---

# Dashboard Chart

## paths

frappe/desk/doctype/dashboard_chart/dashboard_chart.py — DashboardChart, on_update, validate, check_required_field, check_document_type, validate_custom_options, get_permission_query_conditions, has_permission, get_chart_config, get_heatmap_chart_config, get_group_by_chart_config
frappe/utils/dashboard.py — cache_source, generate_and_cache_results, sync_dashboards, make_records_in_module
frappe/desk/doctype/dashboard_chart_source/dashboard_chart_source.py — DashboardChartSource, get_config, on_update
frappe/desk/doctype/dashboard_chart_source/dashboard_chart_source.json — source_name, module, timeseries
frappe/public/js/frappe/widgets/chart_widget.js — frappe.dashboards.chart_sources, ChartWidget.get_settings, get_source_doctype
frappe/public/js/frappe/utils/dashboard_utils.js — get_filters_for_chart_type
frappe/desk/doctype/dashboard_chart/dashboard_chart.js — add_fetch
frappe/modules/export_file.py — export_to_files, write_document_file
frappe/model/sync.py — IMPORTABLE_DOCTYPES, get_doc_files, sync_for
frappe/modules/import_file.py — import_doc

## rules

MUST ship a Custom chart as three files under `<module>/dashboard_chart_source/<scrubbed name>/` — a `.json` naming the Dashboard Chart Source, a `.js` that assigns into frappe.dashboards.chart_sources under the source name, and a `.py` whose `get` is whitelisted; get_config opens exactly that path and nothing else is looked up.
MUST decorate a Custom source's `get` with cache_source and declare `chart_name`, `chart`, `no_cache`, `filters`, `from_date`, `to_date`, `timespan`, `time_interval` and `heatmap_year` in its signature, because generate_and_cache_results calls the function with all of those keywords by name.
MUST read `chart-data:<chart name>` as one value for the whole site: the key carries the chart name only, so a chart rendered with different filters or by different users serves whichever answer was computed first.
MUST pass `refresh` or `no_cache` on any call whose answer must be current; without one, cache_source returns the stored value and never calls the function.
NEVER expect an edit to a filter, a report or a source to refresh a chart on its own; only DashboardChart.on_update deletes the cache key, so a change made anywhere but that document's own save leaves the old numbers on screen.
NEVER read `last_synced_on` as the age of what is displayed; generate_and_cache_results writes it when it computes, and the cached branch returns without touching it.
MUST expect validate to skip check_required_field and check_document_type when chart_type is Custom or Report, so a Custom chart saves with `document_type` empty and get_permission_query_conditions then hides it from every user who is not System Manager.
MUST put a role row on a chart that must reach a user its `document_type` does not; has_permission tries the `roles` child table first and the DocType read check only when that table is empty.
MUST expect a Custom chart to be excluded by get_permission_query_conditions for every non-System-Manager user, because the query names only the chart types Count, Sum, Average, Group By and Report.
NEVER build a chart on a Single DocType; check_document_type throws "You cannot create a dashboard chart from single DocTypes".
MUST set developer_mode before editing a chart whose `is_standard` is set; validate throws "Cannot edit Standard charts" otherwise, and on_update exports the record back to its module folder when it is set.
MUST expect the source `.js` to be fetched and evaluated at render rather than bundled: get_settings calls the whitelisted get_config, which opens `<module path>/dashboard_chart_source/<scrubbed name>/<scrubbed name>.js` with a plain open() and returns its text for frappe.dom.eval. There is no hooks entry and no build step, and a missing or misnamed file raises out of that call instead of drawing an empty chart.
MUST have the source `.js` assign into `frappe.dashboards.chart_sources[<source name>]` at eval time, because get_settings reads that key back immediately after the eval and uses it as the widget's settings — the object it assigns supplies `method` and `filters`.
MUST declare `filters` on that object for a Custom chart to have any filter controls of its own; get_filters_for_chart_type evaluates the source config a second time to read `.filters`, and no other chart_type can declare filters that are not a report's or a DocType's fields.
MUST set `timeseries` on the Dashboard Chart Source record before creating charts from it: dashboard_chart.js copies it onto the chart with add_fetch on `source`, and the chart reads its own copy for xIsSeries and for the date arguments, so a chart created before the flag was set keeps the old value.
NEVER save a Dashboard Chart Source on a site whose app folder must not change; on_update calls export_to_files unconditionally and the only thing that stops it is frappe.flags.in_import — there is no developer_mode check and no "Cannot edit Standard" throw the way there is on Dashboard Chart.
MUST expect migrate to replace the source record from the app folder: `("desk", "dashboard_chart_source")` is in IMPORTABLE_DOCTYPES, so sync_for re-imports the JSON and import_doc deletes the existing document before inserting it.

## values

cache key: chart-data:<chart name>, one per chart, no user and no filter in the key
cache cleared by: DashboardChart.on_update only
cache bypassed by: no_cache, or refresh truthy
chart_type values: Count, Sum, Average, Group By, Custom, Report
Custom chart data call: the method named in frappe.dashboards.chart_sources[source]
Report chart data call: frappe.desk.query_report.run
built-in chart data call: frappe.desk.doctype.dashboard_chart.dashboard_chart.get
source files: <module>/dashboard_chart_source/<name>/<name>.json, .js, .py
filter always appended: document_type docstatus < 2
source config route: frappe.desk.doctype.dashboard_chart_source.dashboard_chart_source.get_config, read from disk, run through frappe.dom.eval
source object keys read by the client: method, filters
timeseries: set on the source, fetched onto the chart, never re-read from the source after that
source export stopped by: frappe.flags.in_import only
source on migrate: JSON re-imported, existing record deleted then inserted
has_permission order: System Manager, then the roles table, then report_name, then document_type

## how

Two independent checks decide whether a chart works, and they run at different moments. The first is the source: a Custom chart is only a name until a JS file registers that name into frappe.dashboards.chart_sources and a Python file beside it exposes a whitelisted `get`. The JS is never bundled: the widget asks the server for the file by source name and evals the text it gets back, so what connects them is the path get_config builds and nothing else, and a file that is absent or that assigns under a different key leaves the widget with no settings while the document saves cleanly.

The second is the pair get_permission_query_conditions and has_permission, and they do not agree. The list query names five chart types and Custom is not one of them, so a Custom chart is invisible in the Dashboard Chart list to anyone below System Manager even though has_permission would allow the document. Reaching a Custom chart from a dashboard therefore depends on the roles table, which is the first branch has_permission tries.

The cache is the part that reads as a bug. cache_source keys on the chart name alone, so the first computation wins for everyone and for every filter set until the chart document itself is saved. A dashboard that shows one number to two users, or that keeps showing yesterday after the report behind it changed, is this key and not the query. The three ways out are `refresh`, `no_cache`, and re-saving the chart.
