# Knowing your answer is right

Four ways stand behind any statement about a framework you did not write, and they rank by what each
one observes: run the code, read the installed source, ask this store, or trust what you remember.
Only the first watches the framework act, and only the last leaves no evidence anyone can weigh.

## paths

tools/symbol_check.py — check, named, path_lines, controls

## rules

MUST run the code where a run is cheap and safe, because a run is the only one of the four that
observes behaviour rather than a claim about it.
MUST read the installed source where a run cannot reach the path in question, and MUST name the file
the reading came from.
MUST treat a store answer as a claim carrying a citation, and MUST open the file it cites.
NEVER answer from memory alone while the installed source is reachable.
MUST read a passing symbol_check as proof that a name exists in the file it names, and NEVER as
proof of what that symbol does, what it returns, or when it runs.
MUST ask what would have to be true for an answer to be wrong before acting on it, and MUST settle
that question with a run or a source read.

## values

| Way of knowing | What it proves | What it cannot prove | When it shows itself wrong |
|---|---|---|---|
| run the code | the behaviour on this input, this data, this installed version | the behaviour on an input, a version or a branch the run never took | on the next run |
| read the installed source | what the code says, unconditionally and right now | what the code does at runtime — a hook, a decorator, an override or a call site each rewrite it | on the next open of the file |
| ask this store | what a past read recorded, and the file it says it read | that the record still matches the tree, or that the read behind it was correct | only when someone opens the file it cites |
| trust what you remember | nothing the reader can check | anything — it is the claim the other three exist to test | never, on its own |

## how

Reading the source reads the instruction the framework will follow, which is not the same as
watching it followed: a decorator wraps the function, a hook runs before it, a subclass overrides it,
and the file being read never shows the site that calls it. A store answer is one of the first two
derived on a tree that may since have moved, which is why the citation and not the sentence around
it is the part worth checking first.

`symbol_check` is that gap in miniature. It resolves each `## paths` line against the installed tree
and looks for each named symbol anywhere in the file's text — a plain substring search, so a symbol
sitting in a comment, a string or an unrelated class satisfies it exactly as a definition would. Its
three controls feed the checker a symbol that is not there and a file that is not there, and all
three must fire before the real run counts for anything, because a detector that never fires reads
every leaf as clean. A pass therefore licenses one belief: this name is somewhere in that file. It
is the floor a citation clears before it is worth reading, never the ceiling that makes it correct.
