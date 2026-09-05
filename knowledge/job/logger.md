---
name: logger
description: A logger built by frappe.logger() defaults to WARNING on a dev server and ERROR everywhere else, so .info and .debug calls emit nothing until set_log_level is called.
triggers: ["get_logger", "set_log_level", "default_log_level", "frappe logger not printing", "log level warning vs error", "nothing shows up in my log file at all", "my log lines never appear even though the code runs", "why are my info messages missing from the log", "logging works on my machine but writes nothing on the live site", "i cannot tell whether that branch ran because there is no log line", "how do i turn on more detailed logging", "my debug messages are silently dropped", "where do i write something so an operator can actually see it later", "the log file is empty after the job finished", "warnings appear locally but not in production"]
product: frappe
---

# Logger

## paths

frappe/utils/logger.py — get_logger, set_log_level, default_log_level

## rules

MUST call frappe.utils.logger.set_log_level before an .info or .debug call can emit anything, because get_logger sets every logger to frappe.log_level or default_log_level, and log_level is only ever populated by set_log_level.
MUST expect default_log_level to be WARNING when frappe._dev_server is set and ERROR otherwise, so an .info call emits nowhere in production, and a .warning call emits nowhere outside a dev server.
MUST call frappe.log_error for anything an operator or a maintainer must see later, because it writes an Error Log row regardless of the logger's level.
NEVER read the absence of a log line as proof a branch did not run; a logger whose level is above the call's discards it after paying its arguments, and produces nothing to check against.

## values

default_log_level: WARNING on a dev server, ERROR otherwise
raised by: frappe.utils.logger.set_log_level(level), which also resets frappe.loggers
durable channel regardless of level: frappe.log_error

## how

get_logger sets every logger's level from frappe.log_level, and nothing populates frappe.log_level except an explicit call to set_log_level. So an .info or .debug call is not weak logging, it is discarded logging until that call is made in the app's own startup or in site config — the call itself succeeds and costs its arguments, and the only symptom is an absence indistinguishable from the branch never running. Where the record must survive, use frappe.log_error, which is unconditional on level.
