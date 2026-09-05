---
name: web-template
description: A standard Web Template renders the .html file sitting beside its exported JSON and never the template field in the database, and clearing the standard check deletes that folder from the app.
triggers: ["WebTemplate", "WebTemplate.render", "WebTemplate.get_template", "get_template_path", "get_template_folder", "create_template_file", "export_to_files", "import_from_files", "Web Template Field", "Web Page Block", "web_template_values", "get_web_blocks_html", "extract_script_and_style_tags", "web_block", "web_blocks", "Enable developer mode to create a standard Web Template", "Web Template is not specified", "web_block.html", "web_template_type", "Component", "Section", "Navbar", "Footer", "page builder block", "add a section to a web page", "custom web template", "web template html file", "web template fields", "the markup box is empty even though the block renders fine", "why does the saved record show no html at all", "where did the markup go after i saved it", "my source files disappeared from the app after i unticked a box", "the change history shows deleted files and i only clicked around in the admin screen", "deleting the record also deleted the folder inside my app", "my edits to the block fields are gone after the update run", "why do my field changes get wiped every time i update the site", "after renaming a field the saved blocks come out blank", "the value i typed into the block never reaches the markup", "my script inside the block runs only once for several blocks", "the style i put in the block ended up somewhere else on the page", "the markup change shows right away but the field change does not"]
product: frappe
---

# Web Template

## paths

frappe/website/doctype/web_template/web_template.py — WebTemplate.validate, WebTemplate.before_save, WebTemplate.on_update, WebTemplate.on_trash, WebTemplate.export_to_files, WebTemplate.import_from_files, WebTemplate.create_template_file, WebTemplate.get_template_folder, WebTemplate.get_template_path, WebTemplate.get_template, WebTemplate.render
frappe/website/doctype/web_template/web_template.json — template, fields, standard, type, module
frappe/website/doctype/web_template_field/web_template_field.json — label, fieldname, fieldtype, reqd, options, default
frappe/website/doctype/web_page_block/web_page_block.py — WebPageBlock, web_template, web_template_values, css_class, hide_block, section_id
frappe/website/doctype/web_page/web_page.py — get_web_blocks_html, extract_script_and_style_tags
frappe/utils/jinja_globals.py — web_block, web_blocks
frappe/modules/export_file.py — write_document_file, create_folder
frappe/modules/import_file.py — import_doc, load_code_properties
frappe/model/sync.py — IMPORTABLE_DOCTYPES, get_doc_files, sync_for
frappe/website/utils.py — clear_cache

## rules

MUST read `standard` as the switch that decides WHERE the markup lives: render calls get_template(self.standard), and the standard branch opens `<module>/web_template/<scrubbed name>/<scrubbed name>.html` from disk on every render while the non-standard branch reads the `template` Code field out of the database.
NEVER expect the `template` field of a standard record to hold anything; export_to_files blanks it before it writes the JSON, the field is hidden by `eval:!doc.standard`, and WebTemplate declares no get_code_fields, so load_code_properties never puts the HTML back on import.
MUST set developer_mode before saving a record with `standard` checked; validate throws "Enable developer mode to create a standard Web Template" for every caller except a patch.
NEVER clear the `standard` check to test something. before_save calls import_from_files, which reads the HTML into the database field and then rmtree's the whole template folder out of the app — the JSON and the HTML are both gone from the working tree.
NEVER delete a standard Web Template on a developer_mode site; on_trash rmtree's its folder, so the record and the app's source files go together.
MUST expect the app folder to win on migrate: `("website", "web_template")` is in IMPORTABLE_DOCTYPES, so sync_for re-imports every standard `<name>.json`, and import_doc DELETES the existing record before inserting — a Desk edit to the fields child table of a standard template is lost, and a site-created template that shares a standard template's name is replaced by it.
MUST give every Web Template Field row a `label`; validate scrubs the label into `fieldname` only when fieldname is empty, and the fieldtype is limited to Attach Image, Check, Data, Int, Link, Select, Small Text, Text, Markdown Editor, Section Break, Column Break and Table Break.
NEVER rename a fieldname after blocks exist. Web Page Block stores its answers as a JSON string in the `web_template_values` Code field rather than as columns, so a renamed field leaves the old key in every saved block and the template reads the new name as undefined with no error.
MUST expect the values dict to contain itself: render does `values.update({"values": values})`, so `{{ heading }}` and `{{ values.heading }}` both resolve and either spelling works in any template.
MUST put a `<script>` or `<style>` a template needs inside the template itself and expect it to MOVE. get_web_blocks_html renders each block, then extract_script_and_style_tags pulls those tags out with BeautifulSoup and keys them by web_template name, so the code runs once per page however many blocks use the template, and it no longer sits where the block sits.
NEVER rely on on_update to refresh a page. It clears the website cache only for Web Pages whose `published` is 1 and that reference the template through a Web Page Block, so an unpublished page and any page that pulls the template through the `web_block` Jinja helper keep their cached HTML.
MUST read an immediate change to the rendered markup as the file and a stale change as the record: get_web_blocks_html fetches the Web Template through frappe.get_cached_doc, so an edit to the `.html` shows on the next request while an edit to `fields` or `type` waits for a cache clear.
MUST pass a template name to the `web_block` Jinja global to place a template outside the page builder; web_blocks throws "Web Template is not specified" when the name is missing, and every option other than `template` and `values` is merged onto the synthetic Web Page Block.
MUST set `type` to one of Component, Section, Navbar or Footer, because get_web_blocks_html passes it to `templates/includes/web_block.html` as `web_template_type` and the wrapper markup is chosen from it — it is not a label.

## values

standard 1: markup read from <module>/web_template/<scrubbed name>/<scrubbed name>.html
standard 0: markup read from the `template` Code field
export trigger: before_save, developer_mode only, standard checked
import trigger: before_save, developer_mode only, standard cleared after being set
on_trash: rmtree of the template folder, developer_mode and standard only
code field loading on import: none — WebTemplate declares no get_code_fields
migrate: JSON re-imported, existing record deleted then inserted
field types: Attach Image, Check, Data, Int, Link, Select, Small Text, Text, Markdown Editor, Section Break, Column Break, Table Break
block storage: Web Page Block.web_template_values, one JSON string
render context: every field by name, plus `values` pointing at the same dict
type values: Component, Section, Navbar, Footer
cache cleared by on_update: published Web Pages that link the template through a block

## how

The record is two records wearing one name. A site-authored template is a row: the Jinja lives in a Code field, editing it in the Desk is the whole workflow, and nothing touches the filesystem. A standard template is a folder: the row exists to carry the field list and the type, the Jinja lives in an `.html` beside the JSON, and the row's own `template` column is permanently empty by design. Reading the column and concluding the template is empty is the standard mistake; read `standard` first.

The two conversions are destructive in one direction only. Checking `standard` writes files. Clearing it reads the files back into the database and then removes the folder — a `git status` after an idle click in the Desk shows deleted source. Deleting the record does the same removal. Neither asks, and neither is reversible from the Desk, so treat the check box on a developer_mode bench as an edit to the working tree.

The block is a form the template declares. Fields on the Web Template become inputs on every Web Page Block that picks it, and the answers are stored as one JSON blob per block, so the schema lives in one place and the data lives in hundreds of unvalidated copies. Adding a field is safe; renaming or retyping one is a silent data migration nobody runs.

Scripts and styles inside a template are pulled out and deduplicated per template name, which is what makes a template reusable on one page and what breaks any script that assumed it sits next to its own markup. Write the script to find its block by a selector, never by position.
