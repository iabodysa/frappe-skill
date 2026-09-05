# Theming — what survives an update

A Website Theme is a RECORD: saving it compiles SCSS to a file under the site's public files and
stores that path on the record, so the compiled CSS is a build artefact and the record is the only
thing worth shipping. Everything outside that record is overwritten by `bench build` or by the next
app update, so the question for any colour, font, logo or navbar item is which record holds it.

| What you want to change | Where the override lives | What destroys it |
|---|---|---|
| a colour or a font on the portal | `custom_scss` on a Website Theme record | nothing — it is compiled from the record |
| a rule that must win over the compiled stylesheet | `custom_overrides` on the same record | nothing; it is appended after, not merged |
| the stock stylesheet itself | an active theme REPLACES it | activating a different theme |
| a shipped standard theme | it is read-only outside `developer_mode` | editing it in `developer_mode` writes to app source |
| an asset under `apps/frappe/.../public` | nowhere — the file is generated | `bench build`, on every run |
| a navbar item | the `standard_navbar_items` hook | nothing — it is a hook, re-read on migrate |
| a logo | the ladder of settings fields, in its own order | a field set at a level the ladder reads earlier |
| anything with no record and no hook | only a patched file | the next app update |

## Settled by

| what it settles | leaf |
|---|---|
| the hooks that already declare record classes apps hand-roll | `knowledge/bench/seeds.md` |
| the compile at save, and the CSS a theme never re-saved keeps serving | `knowledge/desk/website-theme.md` |
| the order the desk title is read in, and the favicon fallback | `knowledge/desk/branding.md` |
| the save refused when a standard row drops, and the condition one dropdown ignores | `knowledge/desk/navbar.md` |
