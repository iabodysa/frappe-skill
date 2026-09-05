---
name: changelog-popup
description: get_change_log_for_app collects every file in the major-version folder whose parsed version falls on the half-open interval from the installed version to the target version, sorts them newest first, and requires no file named for the minor series head.
triggers: ["get_change_log_for_app", "what's new popup after update", "change log for app", "how do i make the what is new window appear after an update", "the release notes window never shows up for users after upgrading", "why did users see notes from several old releases all at once", "does the notes file have to be named a certain way for it to show", "where do i put the text people see after an upgrade", "the update message shows notes the customer already read", "how do i write release notes for people who skipped a few versions", "nothing appeared after the update even though i added the notes", "which of my notes are people guaranteed to see when they upgrade"]
product: frappe
---

# The change_log popup

## paths

frappe/utils/change_log.py — get_change_log_for_app

## rules

MUST expect every file inside a matching `v<major>` folder to be a candidate note, kept when `from_version < version <= to_version` and dropped otherwise; the filename is parsed, never matched against a required pattern like `v<major>_<minor>_0.md`.
NEVER require a `v<major>_<minor>_0.md` file to exist for a minor series' notes to show; the popup has no such rule and demanding the file demands something the framework never checked for.
MUST expect a site upgrading across several point releases to see every one of their notes at once, sorted newest first, because `from_version` comes from the site's own `last_known_versions` and can be several releases behind.
MUST write each change note to stand alone rather than as a diff from the previous release, since a site that skipped releases receives all of them together on one upgrade.

## how

The version being shipped is the only note every upgrading site is guaranteed to see, because it is the only one certain to satisfy `version <= to_version` on a fresh upgrade; anything about a `.0` head file describes a convention some apps follow, never a check the popup performs.
