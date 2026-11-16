# Study courses (N learning languages)

## Using the feature

Open **Settings → Languages → Study courses → Add language**. Select the new
language, enable its course and set the percentages of context and audio
questions. The remaining percentage uses ordinary translation questions.
Save settings to activate the course. At least one course must stay enabled.

Each row also has **Enable grammar**. An enabled module is ready for the
question/theory editors, even with no questions yet. A disabled module has no
home section, statistics tab/card or public practice/editor entry point. If all
courses disable grammar, its global setting, About section and shortcut groups
are hidden too.

**Enable conjugation** works independently. Enabling prepares an empty verb CSV
and a language-specific person configuration. The home section offers Repeat,
Edit and Grammatical persons. Turning this module off hides its entry points
and statistics while keeping even empty verb files and all person definitions.
See [Conjugation phase 1](conjugation-phase-1.md).

Unchecking **Enable course** changes no files immediately. After a successful
save the row disappears from the form, whether or not it has data. Previous
options stay archived by identity; **Add language** restores them and all
retained files. Menus and validation reject duplicate targets and the own language.

With three or more active courses the home screen has a language selector. It
retains the selected course during the current application session, including
when returning from practice. One and two active courses keep their existing
home layout. Statistics lists every active language. Editors, tags, synonyms,
audio and practice use the selected course's existing pair-specific paths.
UI language remains a separate setting.

Courses share the configured own language. Each target occurs once, can be
disabled without deleting its data, and has its own question percentages.
There are no third-language fields: the list supports every registered language
(currently six identities, so up to five active targets for one own language).
External providers retain their existing capability restrictions.

## Persistence and compatibility

The optional `Study courses` row in `settings.csv` has type `JSON`:

```json
{"version":3,"source":"cs","courses":[{"target":"es","enabled":true,"context":20,"audio":20,"grammar":true,"conjugation":true},{"target":"en","enabled":true,"context":20,"audio":20,"grammar":true,"conjugation":false},{"target":"fr","enabled":true,"context":15,"audio":35,"grammar":false,"conjugation":false}]}
```

Language identities are registry codes. The source identifies the common own
language; a course is identified by its source/target pair. List order is stable,
but question settings are looked up by language identity, never by position.
Inactive courses retain their settings. An inactive legacy course whose two
percentages total more than 100 can remain disabled; enabling it requires fixing
the total. Individual percentages must always be whole numbers from 0 to 100.
Versions 1/2 remain readable; version 1 defaults grammar to enabled. Legacy
conjugation availability follows the existing pair CSV without rewriting it.
Saving the course configuration writes version 3 with explicit grammar and
conjugation booleans. Disabled entries
are archived metadata, not rows in the next settings form.

- Without the new row, runtime adapts the existing first/second-language settings
  in memory. Loading the application does not write or migrate settings.
- Saving the settings dialog writes the versioned row through the existing
  atomic, revision-checked settings transaction. No second configuration file or
  partially committed configuration can disagree with the CSV.
- When both formats exist, the versioned list is authoritative. Legacy rows,
  disabled values, API credentials, scheduling metadata and unknown columns are
  retained. Generic programmatic preference saves do not initiate migration.
- Invalid JSON, duplicate fields, unsupported versions, duplicate targets and
  invalid active pairs are rejected. They never silently reactivate legacy slots.
- Disabled legacy slots duplicating another target or the own language are not
  made into duplicate/invalid courses; their original CSV rows remain intact.
- `RuntimePreferences` keeps legacy constructor fields for existing callers.
  Application modules consume `learning_languages`, `language_pairs`,
  `study_courses` and `testing_probabilities(language)`.

Existing populated vocabulary, histories, tags, synonyms, audio, conjugation and
theory files are not renamed, merged or rewritten. Courses reuse their original
paths. Grammar retains its target-language-specific storage contract.

## Automatic files and retirement

`app/repositories/course_files.py` prepares assets when saving settings and
ensures missing active assets during application/home initialization:

| Asset | Created for |
| --- | --- |
| `<own>_<target>_voc.csv` | Every active course |
| `<own>_<target>_tags.csv` | Every active course |
| `<own>_<target>_synonyms.csv` | Every active course |
| `audio/<own>_<target>/` | Every active course |
| `<target>_gra.csv` | Active course with grammar enabled |
| `<own>_<target>_gra_ex.csv` | Active course with grammar enabled |
| `<target>_gra_records.csv` | Active course with grammar enabled |
| `<own>_<target>_con.csv` | Active course with conjugation enabled |
| `<target>_con_persons.json` | Active course with conjugation enabled |

New CSVs contain schemas only. An empty record schema reads as streak zero;
no synthetic answer or word is inserted. Conjugation remains optional and
creates schemas and person definitions only, without generated verb content.
Person configuration is user content and is never automatically retired.

Only after a successful settings commit does retirement inspect affected
old/disabled courses. A recognized CSV with no nonblank data row can be removed.
Any nonblank row is preserved, including incomplete content and a record of zero.
Each file is checked individually: a filled vocabulary does not retain an empty
tag catalog. Unknown schemas are preserved. Audio files are never deleted; only
a completely empty pair directory is removed, non-recursively. Symlinks/junctions
and paths escaping the selected data root are not retired.

Disabling grammar retires only empty questions, theory and records. Vocabulary,
tags, synonyms and audio remain. Populated grammar resumes when enabled again;
disabled grammar is not read for home counts or statistics. Shared target-only
questions/records stay if another active pair needs them after an own-language change.

Missing assets are prepared before committing settings. Preparation/save failure
rolls back only newly created, unchanged empty assets. Saves are serialized and
revision checked; cleanup rechecks emptiness and revisions under file locks.
Concurrently populated or modified content is preserved. A cleanup failure after
a successful commit is reported separately: settings remain saved and the row
retires, while unremoved files stay intact. Startup performs no destructive cleanup.
The legacy `ensure_course` helper retains its vocabulary-only contract; application
initialization uses `ensure_course_files`.

Changing the own language selects different pair-specific courses, as before;
it does not translate or copy the old course data. A new course contains only
content explicitly entered or imported for that pair. A shared entry containing
translations into N languages, reverse-direction history migration and automatic
concept merging remain separate features.

Legacy rows provide a fallback for older application versions, but those versions
cannot display additional courses or later course-list edits. To deliberately
restore the original legacy selection in this version, remove only the optional
`Study courses` row from a backed-up settings file; no course files need removal.

## Verification

`test_course_lifecycle.py` adds 21 cases for complete provisioning, optional
grammar, empty/filled/mixed retirement, audio, archived options, schema migration,
duplicates/source rules, rollback, concurrent writes, cleanup warnings, real
statistics switching, module visibility and public entry-point guards.

Final lifecycle validation: **563 distinct tests across 86 modules**, no skips.
The complete run passed 85 modules; one integration-test wrapper still accepted
only positional statistics arguments and timed out when the new grammar keyword
was supplied. After updating the wrappers to forward keyword arguments, the
remaining module passed **13/13**. This is a complete-suite run plus a targeted
rerun, not a claim of one all-green invocation. The final legacy-empty-grammar
cleanup refinement was also checked by rerunning all **15** lifecycle data cases.
The course settings layout was inspected in Czech and grammar-caption bounds
checked in all six UI languages. Audit: six catalogs of **503 keys**, no catalog,
source-key or checked hardcoded-UI issues. All filesystem tests used synthetic
temporary data; existing user data and `sandbox.py` were not edited by this work.

`app/tests/test_study_courses.py` covers legacy adaptation, all registered
targets, canonical precedence, reordered/disabled courses, JSON/schema errors,
per-language question settings, atomic/conflicting saves, explicit activation,
unchanged course/audio bytes, empty new courses, six UI locales, home selection
and third-course statistics. Existing preference, single-language, editor,
practice, localization and statistics tests also run through the isolated test
runner (`python -B -m app.tests.run_all --timeout 240`), which blocks writes to real user data
and external network/audio operations.

The initial N-course implementation was validated with the project `.venv`: **532 distinct tests in 84
modules**, including **15 new course tests**, passed across the complete-suite
run and subsequent reruns of corrected modules; no tests were skipped. The
large seven-case tag/layout module passed with `--timeout 240` after exceeding
the default 120-second limit. The localization smoke suite passed both cases;
its final six-language message-lookup rerun passed in 53.66 seconds with 134
observed message IDs and no Tk image-finalization warnings. That fixture now
keeps known widget geometry off screen and collects retired Tk image cycles on
the owning thread before starting another statistics worker.

That initial localization audit reported six catalogs of 496 keys, no catalog issues,
no missing source keys and no hardcoded UI candidates. The three-course home
selector was also inspected in a real Windows window with synthetic data.
