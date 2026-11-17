"""Prepare valid synthetic defaults, retaining only public preference schema names."""
import argparse
import json
from pathlib import Path
import sys


def prepare(root):
    sys.path.insert(0,str(root))
    from app.paths import ROOT_DIR
    if ROOT_DIR.resolve()!=root:raise RuntimeError('Fixture imports must resolve to the isolated copy.')
    from app.tests.test_preferences_data import sample_preferences
    from app.preferences.data import with_defaults,options_for,RuntimePreferences
    from app.preferences.courses import COURSE_FIELD,StudyCourse,encode_courses
    frame=with_defaults(sample_preferences())
    schema=json.loads((root/'preference-schema.json').read_text(encoding='utf-8'))
    known=set(frame.Name)
    for row in schema:
        if row['Name'] in known:continue
        name,kind=row['Name'],row['Type'];choices=options_for(kind)
        value=choices[0] if choices else '10' if kind=='Int' and 'batch' in name.casefold() else '0' if kind in ('Int','Bool') else '{}' if kind=='JSON' else ''
        if name==COURSE_FIELD:
            kind='JSON';value=encode_courses('Czech',(StudyCourse('es',conjugation_enabled=True),StudyCourse('en',conjugation_enabled=False)))
        frame.loc[len(frame)]=[name,kind,value];known.add(name)
    frame.loc[frame.Name.isin(('Next backup','Backup mail','11Labs token')),'Value']=''
    frame.loc[frame.Name.eq('Backup period (days)'),'Value']='0'
    RuntimePreferences.from_frame(frame)
    frame.to_csv(root/'files/settings.csv',sep=';',index=False)
    print('Synthetic preferences prepared; no stored preference values were copied.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    prepare(parser.parse_args().root.resolve())
