---
name: formatters
description: frappe.format returns a right-aligned div around Float, Int, Percent and Currency, so the caller gets markup rather than a number unless it passes inline.
triggers: ["frappe.form.formatters._right", "Float", "Int", "Percent", "Currency", "frappe.get_format_helper", "frappe.form.formatters._apply_custom_formatter", "frappe.form.link_formatters", "frappe.format output", "currency and percent formatting in list view", "why is my number showing html tags on the page", "the amount column prints a div instead of the value", "i formatted a number and got angle brackets on screen", "how do i get just the plain formatted number without any wrapper", "the total is printed with markup around it in my custom page", "my custom template shows raw tags where the price should be", "why does the formatted value break my layout", "the number jumps to the right side and pushes my layout around", "amount is right aligned in my own template and i never asked for that", "how do i stop the formatted currency from being wrapped in a block", "percent value renders as a chunk of text with tags in it"]
product: frappe
---

# Formatters

## paths

frappe/public/js/frappe/form/formatters.js — frappe.form.formatters._right, Float, Int, Percent, Currency, frappe.get_format_helper
frappe/public/js/frappe/form/formatters.js — frappe.form.formatters._apply_custom_formatter, frappe.form.link_formatters

## rules

MUST pass `{ inline: 1 }` as the third argument to frappe.format when the caller needs the bare number, because _right wraps the value in a right-aligned div for every fieldtype that routes through it.
NEVER write the return of frappe.format into the page with jQuery `.text()` for a numeric fieldtype; the tags appear on screen as literal characters.
NEVER write it with `.html()` inside a layout you control either; the div is a block element that the surrounding layout did not expect.
MUST read `only_value` as the other escape from _right, which Currency also honours before it calls _right.
MUST set a custom formatter through `frappe.meta.docfield_map[doctype][fieldname].formatter`, which _apply_custom_formatter reads.

## values

routed through _right: Float, Int, Percent, Currency
wrapper: a div carrying an inline right-alignment style
escapes: options.inline, options.only_value
frappe's own inline caller: frappe.get_format_helper, which passes inline 1

## how

frappe.format is two jobs in one call — turn the value into a string, and place it in a table cell. The second job is why a number comes back inside a div, and it is the job most callers outside the list view do not want. So the question to ask at a call site is not "how do I format this" but "who is laying this out": if the answer is your own template, pass inline and take the string.

The failure is visible in two different ways depending on how the string is written to the page, and neither one names the cause. Written as text the markup is on screen; written as HTML the layout shifts and the markup is invisible. Both mean the same thing — the third argument was omitted.
