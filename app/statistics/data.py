"""Cached statistics calculations; chart construction remains eager in the UI."""
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
from app.shared.learning_data import Count_trailing_s
from app.statistics.cache import cache
from app.statistics.difficult_words import difficult_words
from app.statistics.grammar_categories import grammar_categories
from app.statistics.grammar_progress import grammar_question_progress
from app.statistics.vocabulary_tags import tag_statistics
from app.repositories.csv_store import read_csv


def prepare_statistics(files, learned_by, language, horizon, gaps, default_wait, pos_types, pos_ideal, *, grammar_enabled=True,conjugation_enabled=True):
    """Prepare all language datasets without touching Tk or Matplotlib objects."""
    vocabulary = vocabulary_statistics(files/f'{learned_by}_{language}_voc.csv', language,
        learned_by, horizon, gaps, default_wait, pos_types, pos_ideal)
    con_file, gra_file = files/f'{learned_by}_{language}_con.csv', files/f'{language}_gra.csv'
    return (vocabulary,
            training_statistics(con_file,'conjugation', language) if conjugation_enabled and con_file.exists() else None,
            training_statistics(gra_file,'grammar') if grammar_enabled and gra_file.exists() else None)


def simulate_reps_per_day(frame, horizon, gaps, default_wait, today=None):
    today = today or date.today()
    rows = frame.loc[frame['Repetition'].ne(''), ['Repetition', 'Next repetition']].copy()
    rows['Next repetition'] = pd.to_datetime(rows['Next repetition'], errors='coerce').dt.date
    rows.loc[rows['Next repetition'] < today, 'Next repetition'] = today
    dates = []
    for history, next_date in rows.itertuples(index=False, name=None):
        if pd.isna(next_date):
            continue
        count = index = 0
        while index < len(history) and count < 4:
            count += history[index] == 'S'
            index += 1
        remaining = history[index:]
        streak = len(remaining) - len(remaining.rstrip('S')) + 1
        while next_date < today + timedelta(days=horizon):
            dates.append(next_date)
            gap = gaps.get(streak, default_wait)
            if gap <= 0:
                raise ValueError('Repetition intervals must be positive.')
            next_date += timedelta(days=gap)
            streak += 1
    return pd.DataFrame({'Next repetition': dates})


def _trailing(history):
    values = history.map(Count_trailing_s)
    counts = values.value_counts().sort_index()
    return counts.reindex(range(int(values.max())+1), fill_value=0) if len(values) else counts


def _summary(frame, history):
    successes = int(history.str.count('S').sum())
    failures = int(history.str.count('F').sum())
    return len(frame), successes, failures


def vocabulary_statistics(path, language, learned_by, horizon, gaps, default_wait, pos_types, pos_ideal, today=None):
    today = today or date.today()
    options = (language, learned_by, horizon, tuple(sorted(gaps.items())), default_wait,
               tuple(pos_types), tuple(pos_ideal.items()), today)

    def calculate(source):
        frame = read_csv(source).drop(columns=['Enabled'],errors='ignore')
        frame['Next repetition'] = pd.to_datetime(frame['Next repetition'])
        frame['Created'] = pd.to_datetime(frame['Created'])
        mastered = frame.loc[frame['Repetition'].str.count('S').gt(4)].copy()
        histories = mastered['Repetition'].str.replace(r'^S{1,5}', '', regex=True)
        mastered['Success'] = histories.str.count('S')
        mastered['Failure'] = histories.str.count('F')
        mastered['Total'] = mastered['Success'] + mastered['Failure']
        mastered['Next repetition'] = mastered['Next repetition'].dt.strftime('%Y-%m-%d %H:%M:%S')
        table = mastered.drop(columns=['ID', learned_by, 'Audio', 'Created',
            'Repetition', 'Description', 'Example'] + (['Phonetic'] if language == 'English' else []))
        simulated = simulate_reps_per_day(frame, horizon, gaps, default_wait, today)
        simulated['Next repetition'] = pd.to_datetime(simulated['Next repetition'])
        forecast = simulated.groupby(simulated['Next repetition'].dt.date).size()
        valid_created = frame['Created'].dt.date != pd.Timestamp('1900-01-01').date()
        growth = frame.loc[valid_created].groupby(frame.loc[valid_created, 'Created'].dt.date).size()
        growth = growth.sort_index().cumsum() + (~valid_created).sum()
        pos = frame.groupby('Part of Speech').size().reindex(pos_types, fill_value=0)
        ideal = pd.Series(pos_ideal)
        percentages = pd.concat([pos / pos.sum() * 100 if pos.sum() else pos.astype(float), ideal], axis=1)
        counts = pd.concat([pos, (ideal / 100 * pos.sum()).round().astype(int)], axis=1)
        percentages.columns = counts.columns = ['Real', 'Ideal']
        return dict(table=table, summary=(len(frame), int(mastered.Success.sum()), int(mastered.Failure.sum())),
            forecast=forecast, growth=growth, pos=[percentages, counts], trailing=_trailing(frame.Repetition),
            difficult=difficult_words(frame, language, learned_by), tags=tag_statistics(frame,mastered))

    return cache.get(path, 'vocabulary', options, calculate)


def training_statistics(path, kind, language=None):
    path=Path(path)
    config=None
    category_revision=None
    if kind=='conjugation' and language is not None:
        from app.repositories.conjugation_persons import load_configuration
        config,_=load_configuration(path.parent,language,path)
        from app.conjugation.categories import catalog_path
        from app.shared.storage import file_revision
        category_path=catalog_path(path)
        category_revision=file_revision(category_path) if category_path.exists() else None
    def calculate_snapshot(source):
        frame = read_csv(source)
        result = dict(summary=_summary(frame, frame['R']),
            categories=grammar_categories(frame) if kind == 'grammar' else [],
            trailing=_trailing(frame['R']) if kind == 'conjugation' else None)
        if kind == 'conjugation' and language is not None:
            from app.conjugation.categories import load_catalog, category_names
            catalog,_=load_catalog(source,frame)
            grouped=pd.DataFrame({'Category':category_names(frame,catalog),'R':frame['R']})
            result['categories']=grammar_categories(grouped)
            from app.conjugation.data import eligible_verbs
            result['category_available']=frozenset(category_names(eligible_verbs(frame,config.practice),catalog))
            from app.statistics.conjugation import conjugation_progress
            result['progress'] = conjugation_progress(frame,language,config)
            from app.statistics.conjugation import person_statistics
            result['persons']=person_statistics(frame,config)
        if kind == 'grammar':
            result['question_progress'] = grammar_question_progress(frame)
        return result
    def calculate(source):
        if kind=='conjugation' and language is not None:
            from app.conjugation.categories import catalog_path
            from app.shared.storage import destination_lock
            with destination_lock(catalog_path(source)):return calculate_snapshot(source)
        return calculate_snapshot(source)
    result=cache.get(path,kind,(language,config,category_revision),calculate)
    if kind in ('grammar','conjugation'):
        from app.repositories.practice_records import load_records
        records=load_records(path)
        result['best_streak']=records.best_streak
        result['best_correct']=records.best_correct
    return result
