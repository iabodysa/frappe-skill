---
name: week-boundary
description: get_first_day_of_week and get_last_day_of_week resolve the boundary from System Settings first_day_of_the_week, defaulting to Sunday, not from Python's Monday-based weekday().
triggers: ["get_first_day_of_week", "get_last_day_of_week", "get_week_start_offset_days", "get_first_day_of_the_week", "get_start_of_week_index", "Weekday", "first day of week setting", "week boundary calculation", "my weekly report is off by one day", "the week starts on monday but it should start on sunday", "why does my week range not match the one the system uses", "this week and last week are shifted by a day in my totals", "the numbers only look wrong on sunday and are fine the rest of the week", "weekly totals are correct midweek but break on the edge day", "is the first day of the week a setting or is it fixed", "i changed the first day of the week in settings and my code ignored it", "the same week gives two different date ranges in two places", "how do i get the start and end of the week the right way", "my hand written week calculation disagrees with the built in report", "a record lands in the wrong week bucket at the weekend"]
product: frappe
---

# Week Boundary

## paths

frappe/utils/data.py — get_first_day_of_week, get_last_day_of_week, get_week_start_offset_days, get_first_day_of_the_week, get_start_of_week_index, Weekday

## rules

MUST call get_first_day_of_week(dt) and get_last_day_of_week(dt) for a weekly boundary, because they read System Settings first_day_of_the_week through get_first_day_of_the_week, defaulting to Sunday when unset.
NEVER compute a week start with today minus timedelta(days=today.weekday()); Python's weekday() is Monday-based and disagrees with the framework's Sunday default silently, and disagrees differently again on any site where an administrator changed the setting.
MUST expect the mismatch to show only at the week boundary, never in the middle of a week, so a weekly schedule computed by hand looks correct on every check that lands mid-week and misjudges "this week" only on the edge day.

## values

default first_day_of_the_week: Sunday
weekday enum: Sunday 0, Monday 1, Tuesday 2, Wednesday 3, Thursday 4, Friday 5, Saturday 6
resolution chain: get_first_day_of_week, get_week_start_offset_days, get_start_of_week_index, get_first_day_of_the_week, System Settings

## how

The framework's week is a setting, not a constant, so any arithmetic that hardcodes an offset from Python's own weekday() computes a different week from the one the framework computes wherever the setting is non-default — and even on a default site, Python's Monday-anchored weekday() does not agree with the framework's Sunday default without an offset applied by hand. Use the helpers; they take one import and they already read the site's own answer.
