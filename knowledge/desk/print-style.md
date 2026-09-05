---
name: print-style
description: A Print Style is one CSS blob appended after the standard print sheet for the whole site, its disabled flag stops nothing, and the same blob is injected into the Desk document head at boot so an unscoped selector restyles the app.
triggers: ["Print Style", "get_print_style", "get_font", "load_print_css", "print_css", "boot.print_css", "for_legacy", "PrintStyle", "export_module_json", "print_style_name", "standard", "disabled", "preview", "print_style", "get_html_and_style", "read_options_from_html", "get_print_format_styles", "prepare_header_footer", "PrintFormatGenerator", "build_context", "IMPORTABLE_DOCTYPES", "ignore_values", "Standard Print Style cannot be changed. Please duplicate to edit.", "Classic", "Modern", "Monochrome", "Redesign", "print style css not applied", "custom css for print format", "my print css leaked into the desk", "change print font frappe", "print style vs print format css", "my printing css wrecked the look of the whole application", "after i saved a style lists and forms across the app changed font and spacing", "why does styling meant for printouts affect the screens too", "i turned the style off and it is still being applied everywhere", "disabling it did nothing it still shows up on printouts", "the web font i pointed at never loads on the printed page", "how do i change the font used when printing", "margins and page size are respected in the pdf but not in the preview", "the preview and the downloaded file do not look the same", "there is no way to pick a different look in the print preview screen", "my css changes were wiped after an upgrade and the old version came back", "how do i make my styling survive a migration"]
product: frappe
---

# Print Style

## paths

frappe/www/printview.py — get_print_style, get_font, get_context, get_html_and_style, get_rendered_template, get_print_format_doc
frappe/printing/doctype/print_style/print_style.py — PrintStyle, validate, on_update, export_doc
frappe/printing/doctype/print_style/print_style.json — print_style_name, disabled, standard, css, preview
frappe/printing/doctype/print_settings/print_settings.json — print_style, print_style_preview, font, font_size
frappe/templates/styles/standard.css — font, font_size
frappe/www/printview.html — print_style, print-format-gutter, print-format
frappe/boot.py — load_print_css
frappe/public/js/frappe/desk.js — load_bootinfo
frappe/public/js/frappe/dom.js — frappe.dom.set_style
frappe/printing/page/print/print.js — get_print_html, setup_print_format_dom, set_style
frappe/utils/pdf.py — read_options_from_html, get_print_format_styles, prepare_header_footer, toggle_visible_pdf
frappe/utils/weasyprint.py — PrintFormatGenerator.build_context, get_main_html
frappe/templates/print_format/print_format.html — print_style, css
frappe/model/sync.py — IMPORTABLE_DOCTYPES
frappe/modules/import_file.py — ignore_values, import_file_by_path, import_doc
frappe/modules/utils.py — export_module_json
frappe/desk/search.py — search_widget

## rules

MUST read a Print Style as CSS only, chosen once for the whole site, and a Print Format as the body plus its own CSS chosen per DocType; get_print_style concatenates the standard sheet, then the Print Style, then the Print Format, so a Print Format rule wins every tie.
NEVER read `disabled` on a Print Style as a switch that stops its CSS; get_print_style tests `frappe.db.exists` alone, so a disabled style still renders while it is the Print Settings default or the `style` argument, and the flag only drops the row out of the Link picker through search_widget's disabled filter.
MUST scope every selector under `.print-format`; desk.js passes `frappe.boot.print_css` — the standard sheet plus the default Print Style — to frappe.dom.set_style at Desk boot, so a bare `td`, `label` or `h2` rule restyles every list, form and dialog in the session.
MUST spell a font pull as `@import url(...)`; get_print_style moves only that regex to the top of the sheet, and a quoted `@import "…"` stays below the standard rules where the browser discards it.
MUST expect a rule written on the bare `.print-format` selector to change wkhtmltopdf's command line rather than only its CSS; read_options_from_html lifts margin, page-size, page-width, page-height, orientation and header-spacing out of it, and that reaches the PDF alone, never the browser preview.
NEVER put those geometry properties under a descendant selector expecting the same effect; get_print_format_styles accepts `.print-format` only as a whole entry in the selector list, so `.print-format > div` and `.print-format p` are read as ordinary CSS.
MUST expect a Print Style scoped under `.print-format` to match nothing in a Print Format Builder Beta format; templates/print_format/print_format.html emits `print_style.css` but wraps the body in `.section` and `.column` with no `.print-format` element anywhere.
MUST set Print Settings `print_style` for a weasyprint format rather than passing `style`; PrintFormatGenerator.build_context reads the setting directly, so the `?style=` parameter is ignored there, and it calls `frappe.get_doc`, so a setting naming a deleted style raises DoesNotExistError instead of the legacy path's silent skip.
NEVER look for a style picker in the Desk print view; print.js calls `frappe.www.printview.get_html_and_style` with no `style` argument, so the preview always renders the Print Settings default and only a hand-built `/printview?style=` URL selects another.
MUST expect the Desk head and the Desk print preview to disagree when Print Settings names no style; load_print_css falls back to the literal `"Redesign"` while get_print_style with an empty style appends no Print Style CSS at all.
NEVER expect a Google Font named on Print Settings to reach anything built from the boot CSS; load_print_css passes `for_legacy=True` and get_font returns the default stack before it reads the setting.
MUST duplicate a standard style before editing it; validate throws "Standard Print Style cannot be changed. Please duplicate to edit." whenever `standard` is 1 and developer_mode is off.
MUST expect a save with `standard` 1 under developer_mode to write `<app>/printing/print_style/<name>/<name>.json` through export_module_json, and to write nothing at all when developer_mode is off.
MUST expect `bench migrate` to delete and re-insert every standard Print Style, carrying only `disabled` across from the site row; sync.py lists `("printing", "print_style")` in IMPORTABLE_DOCTYPES and import_doc copies the ignore_values fields off the old document before frappe.delete_doc.
MUST raise `modified` in the app's JSON to make migrate pick up a CSS change; import_file_by_path skips a non-DocType whose stored `modified` is not older than the file's, and Print Style carries no migration_hash.

## values

concatenation order: templates/styles/standard.css rendered, then Print Style css, then any `@import url(...)` moved to the top, then Print Format css
default: Print Settings `print_style`
overrides the default: `style` on `/printview`, `style` on get_html_and_style
ignores the override: PrintFormatGenerator, the weasyprint path behind Print Format Builder Beta
boot.print_css: `get_print_style(print_settings.print_style or "Redesign", for_legacy=True)`
for_legacy=True: font forced to `Inter, "Helvetica Neue", Helvetica, Arial, "Open Sans", sans-serif`
font precedence otherwise: Print Format font, then Print Settings font, then the default stack
lifted into the PDF command line: margin-top, margin-bottom, margin-left, margin-right, page-size, page-width, page-height, orientation, header-spacing
lifted from: a rule whose selector list contains `.print-format` as a whole entry
kept from the site on migrate: disabled
standard styles: Classic, Modern, Monochrome, Redesign
autoname: field:print_style_name, unique
write permission: System Manager

## how

The record holds one Code field and nothing else that renders. get_print_style builds the sheet in three moves: it renders `templates/styles/standard.css` against Print Settings, appends the Print Style's `css` verbatim, and appends the Print Format's `css` after that. Position is the whole mechanism — the Print Style beats the standard sheet at equal specificity because it comes later, and loses to the Print Format for the same reason. The `@import` move runs between the second and third step, which is why a font import in a Print Style survives and the identical line in a Print Format does not.

Where that sheet lands is the part that surprises. The standalone print view drops it into a `<style>` in the head of printview.html, and the wkhtmltopdf PDF is that same page rendered through the same route, so preview and PDF agree. The Desk print view renders the format into an iframe and scopes the sheet there. But desk.js also injects the boot copy into the main Desk document at load, unscoped, for the life of the tab. So an unscoped rule in a Print Style is a site-wide Desk restyle that appears on pages nobody was printing, and the defect is diagnosed on the wrong page.

The two PDF generators do not read the record the same way. wkhtmltopdf takes the finished HTML and parses the style tags back out, treating a bare `.print-format` rule as a source of page geometry, so a margin written there silently moves the paper and changes nothing in the browser preview. weasyprint never sees that HTML: PrintFormatGenerator fetches the Print Style document itself from Print Settings, renders its CSS into a different template with a different DOM, and never loads `standard.css` at all. A style tuned against the legacy `.print-format` tree is therefore inert under the beta builder, and the `style` parameter that switches the legacy view is not consulted.

`standard` and `disabled` both read as switches and neither is. `standard` decides where the record is written on save and whether migrate will overwrite it, not who may print with it; developer_mode is the condition, so on a production site the working shape is always a duplicate with `standard` unset. `disabled` is preserved across migrate precisely because it is a site-side choice, yet the print path never reads it — it only hides the row from the Print Settings link search. Disabling the style that is already the default changes nothing on the page.
