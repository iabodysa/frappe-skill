---
name: get-last-day
description: get_last_day returns the day before the first day of next month, and frappe.utils re-exports it through a wildcard import.
triggers: ["get_last_day", "get_first_day", "is_last_day_of_the_month", "wildcard import of frappe.utils.data", "get_last_day utility function", "last day of next month", "how do i get the last day of the month", "what is the right way to find month end without writing my own calendar math", "my month end date is wrong in february", "my code says the month ends on the 30th when it ends on the 31st", "how do i check whether a date is the final day of its month", "the end of december comes out wrong in my date helper", "why does my hand written month end break on a leap year", "how do i get the first day of the month a few months ahead", "is there a built in helper for month start and month end", "my monthly period end is off by one day"]
product: frappe
---

# Get Last Day

## paths

frappe/utils/data.py — get_last_day, get_first_day, is_last_day_of_the_month
frappe/utils/__init__.py — wildcard import of frappe.utils.data

## rules

MUST call frappe.utils.get_last_day rather than compute month end by hand, because get_first_day(dt, 0, 1) minus one day already handles every month length and leap year.
MUST expect the wildcard import in frappe/utils/__init__.py to expose get_last_day as frappe.utils.get_last_day, not only as frappe.utils.data.get_last_day.

## how

get_last_day is get_first_day(dt, 0, 1) with a day subtracted, so month end falls out of month start rather than being computed on its own, and December is not a special case.
