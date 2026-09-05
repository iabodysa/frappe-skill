# What it costs, measured

`SKILL.md` is the only unavoidable per-session cost, about 3,400 tokens. Leaves are read one at a
time; the index is grepped, never opened.

It is not a compression argument. Measured when the store held 187 leaves, a leaf is 3x LARGER than
the source lines it cites — the saving is not in the bytes of the fact, it is in not reading the
file the fact sits in. Head to head against a guarded grep plus the files it points at, the store
cost 2.2x to 3.9x less across 13 sampled questions, and cost MORE on 3 of those 13. On a question
whose answer sits in one small file you can already name, `grep` wins and you should use it.

The argument that survives is not a ratio. For 6 of those 13 questions a guarded grep for the
question's own words returned ZERO hits — `autoname not called`, `patch stamped`,
`lucide icon frappe-ui`. Every zero is a phrase; every hit was an identifier the asker already knew.
A grep finds what you can already name. This store is for the question you cannot yet name, and the
retry that costs you — grep again with different words, and again — appears in no ratio above.

