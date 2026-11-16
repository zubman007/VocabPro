# Statistics and language architecture — 2026-11-16

## Findings and implementation

The statistics controller calculates pandas datasets through `BackgroundTask`.
`StatisticsCache` already invalidates by file revision, date and calculation
options. Chart construction is staggered on the Tk thread, with a loading cover.
The table already paginates to 25 rows. Tab selection hides existing frames; it
does not rebuild the page. These mechanisms were retained.

The scroll profile identified repeated canvas mutations, not pandas calculations
or Matplotlib figure draws. Moving the scroll interior triggers Configure events;
the background handler then requested painting of visible panels. Even unchanged
panels issued coords, itemconfigure and tag commands. Tk processed those commands
and native repainting synchronously. The fix:

- Return from the backdrop painter when viewport, content height and texture
  revision are unchanged. Children still observe their own Configure events.
- Return from a panel painter when its image key, canvas offset and revision are
  unchanged. CTk `_draw` explicitly invalidates this guard so theme, hover and
  native rounded-corner redraws still work.
- Configure the scrolling region only when its dimensions change.
- Retain a chart's figure and hover cache for equal datasets, title, placement
  and UI language. Each host retains just its current dataset; changing data
  releases the previous chart. TkAgg toplevel callbacks are explicitly removed.

No Pillow image processing, statistics calculations or full figure rendering is
introduced into the scroll handler. Tk and Matplotlib remain on the UI thread;
moving them to the statistics worker would be unsafe.

## Conjugation data and new indicators

CSV has ID, source/target text, free-form Description, six current forms
(`s1`…`m3`), `R` (S/F sequence for the whole record) and `LR` (last attempt).
A record can represent a particular tense of a verb. A failure records a failed
whole round; correction after reveal does not add a success. Repeated failed
confirmations can add failures. Therefore accuracy measures recorded confirmations,
not unique sessions or first-attempt success.

Added to the existing Conjugation section:

- Practised and unpractised record counts, based on valid S/F outcomes.
- Number of nonempty current forms across practised records. This is coverage
  of the current content, not a claim about historical per-person results.
- Up to ten records with errors ordered by whole-round accuracy, then error
  count. Table includes verb, original Description, attempts, failures and
  percentage accuracy. It uses the existing searchable, sortable table component.

Computations run in the existing background pipeline and share its cache.
The trailing-success chart and original totals remain available.
No historical data is fabricated. Description mixes tense and other qualifiers;
there is no trustworthy structured tense or regularity column. LR alone cannot
reconstruct calendar trends. Per-person accuracy, exact mistakes, response times,
tense comparison and regularity comparison have deliberately not been inferred.

For those future metrics, collect a versioned event with course ID, record ID,
structured tense ID (when available), timestamp, per-person result, reveal status
and elapsed active answer time. Start its history at opt-in/rollout, distinguish
it from legacy totals, and commit events with progress rather than as unrelated
writes. Recording verbatim wrong answers is optional and needs a retention rule.

## Language dependency map

| Area | Current contract and implication |
| --- | --- |
| Preferences | Learned by, first/second language, second-language enabled; test probabilities indexed by the legacy slot |
| Vocabulary | One `<source>_<target>_voc.csv`; language names are column names; progress belongs to this course |
| Editor | Explicit source/target columns, course-specific tags/synonyms and audio; extra columns are not a multilingual editing UI |
| Practice | Target prompt and source answer; no reverse-direction or arbitrary answer-language selector |
| Statistics | Selects active learning language; vocabulary and conjugation are course-specific, grammar currently target-specific |
| Import/export | CSV schemas and filenames carry legacy names; backups preserve original CSV bytes; no N-language interchange contract |
| Translation | UI catalogs keyed by language codes, with English fallback; distinct from dictionary translations |
| Speech/dictionary | Providers have different capability subsets; adding a language to the registry must not imply API support |
| Persistence | Audio paths, tag catalogs, synonym IDs, grammar theory and preference names depend on existing naming |

Implemented a central registry of stable language IDs and lossless legacy-name
adapters in `app/shared/languages.py`. `LanguagePair` identifies source and target
languages without language1/language2 fields. These are course roles, not a fixed
question/answer direction. AppContext resolves both ISO codes
and legacy names to exactly the existing paths. UI translation uses that same
registry. Practice resolves testing probabilities by language identity through
the preference adapter, instead of directly indexing the caller's language slot.
`RuntimePreferences.language_pairs` exposes active pairs through this model.

This is incremental preparation, not an N-language settings migration. Existing
preference fields and their disabled values remain intact. Providers still enforce
their own capability maps. No settings, dictionary, progress or audio files are
rewritten, renamed or deleted by these changes.

## Recommended next architecture (requires approval before migration)

Prefer a collection of independent courses over immediate shared multilingual
records. Store an ordered list of active languages by ID and per-course settings
keyed by `(prompt ID, answer ID)`, separately from UI language. First adapt the
legacy settings into this model in memory, then introduce a versioned course
configuration with explicit conflict rules if both formats exist. Legacy CSV
names remain behind an adapter until a separately approved storage migration.
This supports N courses without adding language3 variables. The home cards need
a wrapping grid or course selector before enabling a third course.

Selecting a study direction selects a course and its independent progress.
Missing translations exclude an item from that direction and appear as missing
content in the editor; do not substitute another language or auto-generate text.
Existing pair-specific progress must never be copied to a reverse/new pair.

One entry with translations into N languages is a materially different model:
it needs stable concept and sense IDs, translations keyed by language, explicit
links to legacy word IDs, and progress keyed by direction. Existing equal strings
must not be merged automatically (homonyms and differing senses). If that product
behavior is desired, add it after the course model, with previewable migration,
backups, idempotent conversion, validation of counts/IDs/histories and rollback.

Third-language activation and shared multilingual entries are **not implemented**
in this change. No irreversible migration has been performed.

## Validation and measurement

`python -B -m app.statistics.profile_scroll` opens statistics read-only, waits
for preparation, and profiles 100 scroll-position updates with `root.update()`.
`--baseline` substitutes the original panel/backdrop painter methods from Git
HEAD without modifying files. `--compare` measures both paths in the same window.
Run measurements without another UI test process
or user interaction. Timings include native Tk repainting and are machine,
display and focus dependent; they are not a claim of 60 FPS.

Initial diagnostic runs: median 284–357 ms per step; intermediate fix 125 ms;
final optimization run 58 ms (5.64 s total). A later baseline-method check was
144 ms (12.28 s total). Those runs overlapped parts of the test suite, so the
operation counts are stronger evidence than the exact wall-clock speedup:
the optimized scroll eliminated the hundreds of unchanged panel paints and
roughly one thousand canvas item configurations seen in the baseline.

Final controlled comparison after the tests, in the same loaded window (original
panel/backdrop painting methods versus optimized methods; all other code equal):

| 100 position updates | Original painting | Optimized painting |
| --- | ---: | ---: |
| Median per update | 87.72 ms | 42.87 ms |
| Maximum per update | 224.89 ms | 97.49 ms |
| Total | 9.431 s | 4.127 s |
| Panel paint calls | 450 | 0 |
| Canvas itemconfigure calls in profile | 1,000 | 0 |

This is about 51% lower median latency and 56% lower total time. Large position
jumps still spend most time inside native Tk event processing. Continuous 60 FPS
has not been established. The script and comparison deliberately isolate the
painting optimization, rather than attributing unrelated cache changes to it.

The new regression module checks whole-round statistics, missing/empty data,
bounded ranking, read-only CSV handling, cache invalidation and isolation, legacy
paths, language IDs, disabled-language settings, no-op surface rendering and
retention/replacement of figures. Existing tests cover worker scheduling,
chart hover pixels, tabs, scroll background memory, preferences and workflows.

Final full-suite run: **494 tests, 79 modules, zero failures, zero skips**.
After adding the legacy-CSV Conjugation window integration case, the updated
new module passed **8/8** tests (the full-suite run included its earlier seven
cases). This covers 495 distinct tests across the full run and targeted rerun.
The initial development run had two intermittent UI failures (focus-dependent
shortcut and Tk timer teardown); both modules passed on the final full run.
Tests use the repository's service and data-write guards. Existing user changes
in `sandbox.py` and `files/Spanish_gra.csv` were left untouched.

Chart-construction check in the final targeted run: equal data retained the
existing figure in **0.14 ms**, versus **47.30 ms** for changed-data construction.
This comparison excludes the subsequent raster draw; figure identity and absence
of a scheduled redraw are also asserted, rather than relying on timing alone.
