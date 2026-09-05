---
name: use-list
description: data is a running list rather than one page of rows, because the fetch replaces it only while start is zero and appends on every other start.
triggers: ["useList data not paging", "list append vs replace", "the list keeps getting longer every time i load more instead of showing one page", "why do i see duplicate rows after refreshing the list", "loading the next page adds the rows on top of the old ones", "i asked for twenty rows and now there are sixty on screen", "the same record shows up twice in the table", "refreshing after page two doubles everything", "how do i show numbered pages instead of a load more button", "going back a page does not remove the rows i already had", "why does my table grow forever as i scroll", "the row count on screen does not match the page size i set", "how do i refresh a paginated list without repeating rows"]
product: frappe-ui
---

# useList

## paths

src/data-fetching/useList/useList.ts — useList, next, previous, execute, updateRow, removeRow, insert, setValue, delete
src/data-fetching/idbStore.ts — idbStore
src/data-fetching/useList/listStore.ts — listStore

## rules

MUST expect the fetch handler to assign the returned rows over `data` only while `start` is 0, and to spread the previous rows and the returned rows into a new array on every other start.
MUST expect no deduplication by `name` on that append.
MUST read `data` as a running list: after two `next()` calls at a limit of 20, it holds 60 rows.
MUST slice `data` by start and limit to render one page, or refetch from a start of 0, which is the only branch that replaces the array.
MUST expect `next()` to add the limit to `start` and `previous()` to subtract it with a floor of 0, and MUST expect either to call `execute()` itself only while `refetch` is false.
MUST expect `fetch` and `reload` to be the same function as `execute`, which resets neither start nor the accumulated rows, so a reload past the first page appends a second copy of the rows already held.
MUST reset start to 0, or route the refresh through `updateRow` and `removeRow`, to refresh a paginated list without duplication.
MUST expect a cache key to write each result to IndexedDB and to read one back into the cached response at construction.

## values

replaces when: `start` is 0
appends when: `start` above 0
next: start plus limit
previous: start minus limit, floored at 0
fetch and reload: aliases of `execute`
returned writers: `updateRow`, `removeRow`, `insert`, `setValue`, `delete`

## how

Pagination here is designed for the load-more pattern, not for numbered pages: `start` moves what the request asks for while `data` keeps everything that has arrived. Nothing in the name says so, and the same array is what a page-based table would bind to, so a numbered pager built on it grows without bound and looks like a duplicate-rows bug in the backend.

Choose the shape before choosing the composable. For load-more, bind `data` and call `next()`. For numbered pages, drive `start` yourself and slice, or refetch from zero on each page change.
