---
name: autoname
description: Naming runs a fixed sequence of steps and the first one that sets a name ends it, so an autoname string that matches no naming rule leaves the name empty and the document is given a random hash without an error.
triggers: ["set_new_name", "set_name_from_naming_options", "set_naming_from_document_naming_rule", "is_autoincremented", "_set_amended_name", "_field_autoname", "_prompt_autoname", "_format_autoname", "make_autoname", "validate_name", "patch_old_naming_expressions", "Doctype", "Special Characters except", "Invalid name type (integer) for varchar name column", "Please set the document name", "doctype naming rule", "autoname format", "my records get random letters and numbers instead of the pattern i set", "the record id came out as a meaningless string of characters", "why is the number not following the format i configured", "i set the name in my own code before saving but it gets thrown away", "the name i assign in my function does not stick", "why does my custom naming code have no effect at all", "the naming pattern is wrong and nothing shows an error anywhere", "it tells me a field is required when i try to save a new record", "it keeps asking me to set the document name", "i changed the naming setting on the type and it reverted after saving"]
product: frappe
---

# Autoname

## paths

frappe/model/naming.py — set_new_name, set_name_from_naming_options, set_naming_from_document_naming_rule, is_autoincremented, _set_amended_name, _field_autoname, _prompt_autoname, _format_autoname, make_autoname, validate_name
frappe/core/doctype/doctype/doctype.py — patch_old_naming_expressions

## rules

MUST declare one naming rule per DocType, because set_new_name runs each later branch only while doc.name is empty.
NEVER set doc.name inside before_naming and expect it to survive; set_new_name resets doc.name to None unless meta.autoname is prompt or frappe.flags.in_import is set.
MUST expect set_naming_from_document_naming_rule to set the name before the controller autoname method runs, and that method to set it before set_name_from_naming_options runs.
MUST expect an autoname string that starts with none of field:, naming_series:, prompt or format: and carries no # to leave doc.name empty, so make_autoname("hash", doc.doctype) names the document and nothing raises.
MUST assert frappe.ValidationError for an empty field: source and MUST match the message on the field label, because set_name_from_naming_options calls frappe.throw with no exc, so frappe.MandatoryError is never raised.
MUST set autoname and let the DocType save settle naming_rule, because patch_old_naming_expressions rewrites naming_rule from autoname on every validate.
NEVER read the absence of an error as proof that the naming rule declared is the one that named the document.

## values

set_new_name order: before_naming, doc.name = None, is_autoincremented, _set_amended_name, issingle, set_naming_from_document_naming_rule, controller autoname, set_name_from_naming_options, make_autoname hash, validate_name
returns early: is_autoincremented, _set_amended_name once it sets a name
autoname string prefixes: field:, naming_series:, prompt, format:, any string carrying #
dispatch: if/elif on autoname.lower(), first match only
hash name: ten characters — one trace-id character, three deciseconds in base32, seven random base32 characters
field: with an empty value: frappe.throw of "{0} is required" on the field label, so frappe.ValidationError
prompt with an empty name: frappe.throw of "Please set the document name"
Document Naming Rule: read for the doctype, disabled 0, ordered by priority desc, first rule that sets a name wins
Document Naming Rule skipped for: log_types, DOCTYPES_FOR_DOCTYPE, DefaultValue, Patch Log
naming_rule options: "", Set by user, Autoincrement, By fieldname, By "Naming Series" field, Expression, Expression (old style), Random, By script
autoname starting with format:: naming_rule becomes Expression (old style) and an alert msgprint says the usage is discouraged
amended_from set: _set_amended_name suffixes the source name unless Amended Document Naming Settings or Document Naming Settings selects Default Naming

## how

Naming is a sequence, not a table of options. Each branch after the reset runs only while the name is still empty, so declaring two naming rules does not combine them — it disables the second, and the second's absence is announced nowhere. That is why the useful question is never whether autoname is set but which call set the name. Read set_new_name downward and stop at the first call that could produce a value for this document.

The reset at the top is the part that surprises. before_naming runs first and can compute anything, but the name it writes is thrown away immediately unless the DocType is a prompt DocType or the write is an import. Use before_naming to prepare the fields the later naming rule reads, never to name.

The autoname string itself is a prefix dispatch on a lowercased string with no final else, so a typo in the prefix is not a configuration error — it is a document with a hash name. The failure looks like a naming feature that was never enabled rather than a value that was rejected, so check the produced name, not the declaration.

Choose by what the name must survive. A name a person reads aloud or files by needs a series or a format. A name only a join uses is better as a hash or an autoincrement, because a series is one shared counter and a shared counter serialises everyone writing behind it.
