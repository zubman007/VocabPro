"""Grammar question loading and atomic answer-history transactions."""
import csv
import os
import pandas as pd
from app.shared.learning_data import Count_trailing_s
from app.shared.storage import file_revision,save_csv,FileChangedError


def Load_questions_from_csv(csv_path):
    questions = []
    identifiers = set()
    if not os.path.exists(csv_path): raise FileNotFoundError(f"CSV file not found: {csv_path}")
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        required_columns = ["prompt","anchor","option_1","option_2","option_3","option_4"]
        if reader.fieldnames is None: raise ValueError("CSV file is empty or has no header.")
        missing = [col for col in required_columns if col not in reader.fieldnames]
        if missing: raise ValueError(f"Missing required CSV columns: {', '.join(missing)}")
        for row in reader:
            if None in row:
                raise ValueError(f'CSV row {reader.line_num}: too many fields.')
            row={key:value or '' for key,value in row.items() if key is not None}
            if not any(row.values()):continue
            if any(not row.get(column,'').strip() for column in required_columns):
                raise ValueError('Fill in the category, question, sentence and all four answers.')
            identifier = row.get('question_id', '').strip()
            if not identifier or identifier in identifiers:
                raise ValueError(f'Question IDs must be filled and unique. CSV row {reader.line_num}.')
            identifiers.add(identifier)
            options = [row["option_1"].strip(),row["option_2"].strip(),row["option_3"].strip(),row["option_4"].strip(),]
            repetition = row.get('R', '').strip()
            question = {
                "id": row.get("question_id", "").strip(),
                "category": (row.get('category') or row.get('Category') or '').strip(),
                "prompt": row["prompt"].strip(),
                "anchor": row["anchor"].strip(),
                "options": options,
                "correct_answer": options[0],
                "explanation": row.get("explanation", "").strip(),
                "repetition": repetition,
                "last_review": row.get('LR', '').strip(),
                "count_trailing_s": Count_trailing_s(repetition),}
            questions.append(question)
    if not questions: raise ValueError("CSV file contains no questions.")
    return questions


def save_answers(csv_path, answers):
    if not answers:return
    revision=file_revision(csv_path)
    df=pd.read_csv(csv_path,sep=';',dtype=str,keep_default_na=False).fillna('')
    for column in ('R','LR'):
        if column not in df:df[column]=''
    if 'question_id' not in df or df.question_id.eq('').any() or df.question_id.duplicated().any():
        raise ValueError('Question IDs must be filled and unique.')
    positions = {identifier: index for index, identifier in enumerate(df.question_id)}
    records = df.to_dict('records')
    additions, timestamps = {}, {}
    for identifier, result, expected, when in answers:
        identifier = str(identifier)
        if identifier not in positions:
            raise FileChangedError('The grammar file changed. Reopen the editor before saving.')
        row = records[positions[identifier]]
        if expected is not None and (any(str(row.get(column,'')).strip()!=str(expected.get(key,'')).strip()
                for column,key in (('prompt','prompt'),('anchor','anchor'))) or
                [str(row[f'option_{i}']).strip() for i in range(1,5)]!=expected['options']):
            raise FileChangedError('The grammar file changed. Reopen the editor before saving.')
        additions.setdefault(identifier, []).append(result)
        timestamps[identifier] = when
    histories = df['R'].tolist()
    last_answers = df['LR'].tolist()
    for identifier, results in additions.items():
        position = positions[identifier]
        histories[position] += ''.join(results)
        last_answers[position] = timestamps[identifier]
    df['R'], df['LR'] = histories, last_answers
    save_csv(df,csv_path,sep=';',index=False,expected_revision=revision)
