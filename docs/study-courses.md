# Study courses (N learning languages)

## Using the feature

Open **Settings → Languages → Study courses → Add language**. Select the new
language, enable its course and set the percentages of context and audio
questions. The remaining percentage uses ordinary translation questions.
Save settings to activate the course. At least one course must stay enabled.

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
{"version":1,"source":"cs","courses":[{"target":"es","enabled":true,"context":20,"audio":20},{"target":"en","enabled":true,"context":20,"audio":20},{"target":"fr","enabled":true,"context":15,"audio":35}]}
```

Language identities are registry codes. The source identifies the common own
language; a course is identified by its source/target pair. List order is stable,
but question settings are looked up by language identity, never by position.
Inactive courses retain their settings. An inactive legacy course whose two
percentages total more than 100 can remain disabled; enabling it requires fixing
the total. Individual percentages must always be whole numbers from 0 to 100.

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

Vocabulary, histories, tags, synonyms, audio, conjugation and theory files are
not renamed, merged or rewritten by this conversion. Existing courses reuse
their original paths. Activating a genuinely new pair creates only an empty
vocabulary schema through `ensure_course`; it copies no learning history.
Grammar retains its existing target-language-specific storage contract.

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

`app/tests/test_study_courses.py` covers legacy adaptation, all registered
targets, canonical precedence, reordered/disabled courses, JSON/schema errors,
per-language question settings, atomic/conflicting saves, explicit activation,
unchanged course/audio bytes, empty new courses, six UI locales, home selection
and third-course statistics. Existing preference, single-language, editor,
practice, localization and statistics tests also run through the isolated test
runner (`python -B -m app.tests.run_all --timeout 240`), which blocks writes to real user data
and external network/audio operations.

Validation on Windows with the project `.venv`: **532 distinct tests in 84
modules**, including **15 new course tests**, passed across the complete-suite
run and subsequent reruns of corrected modules; no tests were skipped. The
large seven-case tag/layout module passed with `--timeout 240` after exceeding
the default 120-second limit. The localization smoke suite passed both cases;
its final six-language message-lookup rerun passed in 53.66 seconds with 134
observed message IDs and no Tk image-finalization warnings. That fixture now
keeps known widget geometry off screen and collects retired Tk image cycles on
the owning thread before starting another statistics worker.

The localization audit reports six catalogs of 496 keys, no catalog issues,
no missing source keys and no hardcoded UI candidates. The three-course home
selector was also inspected in a real Windows window with synthetic data.
