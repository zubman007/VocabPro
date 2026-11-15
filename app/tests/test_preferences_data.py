"""Preferences validation and failure safety with synthetic settings only."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd
from app.preferences.data import PreferenceError, validate_preferences
from app.repositories.preferences import load_preferences, save_preferences


def sample_preferences():
    rows=[('App language','Options[English,Czech]','English'),
        ('Learned by','Options[Czech,English,Spanish]','Czech'),
        ('First learning language','Options[English,Spanish]','Spanish'),
        ('Second learning language','Options[English,Spanish]','English'),
        ('Learn batch','Int','10'),('Backup mail','Str',''),
        ('Backup period (days)','Int','0'),('Next backup','Str','2026-11-21 15:16:41.812144'),
        ('11Labs token','Str','synthetic-test-value'),
        ('App sounds enabled','Bool','1'),('App sound volume','Int','100'),
        ('Autoplay pronunciation','Bool','1'),('Remember grammar categories','Bool','1'),
        ('Automatically show synonyms in repeat','Bool','1')]
    for order in (1,2):
        rows.extend([(f'Percentage of type 2 testing - {order}.lang (description and use in a sentence)','Int','20'),
                     (f'Percentage of type 3 testing - {order}.lang (audio and options)','Int','20')])
    return pd.DataFrame(rows,columns=['Name','Type','Value'])


class PreferencesTests(unittest.TestCase):
    def test_literal_na_values_and_leading_zeroes_survive_loading(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv'
            for value in ('NA', 'null', '001234'):
                frame=sample_preferences()
                frame.loc[frame.Name=='11Labs token','Value']=value
                frame.to_csv(path,sep=';',index=False)
                self.assertEqual(load_preferences(path).set_index('Name').at['11Labs token','Value'],value)

    def test_validated_date_and_email_are_saved_without_outer_whitespace(self):
        updated=validate_preferences(sample_preferences(),{
            'Next backup':' 2026-11-21 15:16:41 ', 'Backup mail':' user@example.com '})
        values=updated.set_index('Name')['Value']
        self.assertEqual(values['Next backup'],'2026-11-21 15:16:41')
        self.assertEqual(values['Backup mail'],'user@example.com')
        from datetime import datetime
        datetime.strptime(values['Next backup'][:19],'%Y-%m-%d %H:%M:%S')

    def test_changed_file_is_not_overwritten_by_a_stale_dialog(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv'
            original=sample_preferences()
            original.to_csv(path,sep=';',index=False)
            stale=load_preferences(path)
            changed=original.copy()
            changed.loc[changed.Name=='11Labs token','Value']='new-test-token'
            changed.to_csv(path,sep=';',index=False)
            before=path.read_bytes()
            with self.assertRaisesRegex(ValueError,'Settings changed on disk'):
                save_preferences(stale,{'Learn batch':'12'},path)
            self.assertEqual(path.read_bytes(),before)

    def test_empty_preference_name_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv'
            frame=sample_preferences()
            frame.loc[0,'Name']=' '
            frame.to_csv(path,sep=';',index=False)
            with self.assertRaises(ValueError):
                load_preferences(path)

    def test_api_cache_reads_the_saved_literal_value_after_atomic_replacement(self):
        from app.repositories import api_settings as api_config
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv'
            frame=sample_preferences()
            frame.to_csv(path,sep=';',index=False)
            with patch.object(api_config,'SETTINGS_PATH',path), \
                 patch.object(api_config,'_signature',None), patch.object(api_config,'_values',{}):
                self.assertEqual(api_config.load_settings()['11Labs token'],'synthetic-test-value')
                save_preferences(load_preferences(path),{'11Labs token':'NA'},path)
                self.assertEqual(api_config.load_settings()['11Labs token'],'NA')

    def test_each_language_percentages_are_checked(self):
        frame=sample_preferences()
        for order in (1,2):
            fields=[name for name in frame['Name'] if f'{order}.lang' in name]
            with self.subTest(language=order), self.assertRaises(PreferenceError):
                validate_preferences(frame,{fields[0]:'70',fields[1]:'40'})

    def test_bounds_and_language_validation(self):
        frame=sample_preferences()
        percent=next(name for name in frame['Name'] if name.startswith('Percentage'))
        for values in ({'Learn batch':'0'},{'Learn batch':'-1'},{'Learn batch':''},
                {'Learn batch':'abc'},{percent:'101'},{'App language':'Unknown'},
                {'Second learning language':'Spanish'}):
            with self.subTest(fields=list(values)), self.assertRaises(PreferenceError):
                validate_preferences(frame,values)

    def test_dates_reject_incompatible_formats(self):
        frame=sample_preferences()
        for value in ('2026-11-21','tomorrow','2026-11-21T15:16:41','2026-11-21 15:16:41+02:00'):
            with self.subTest(value=value), self.assertRaises(PreferenceError):
                validate_preferences(frame,{'Next backup':value})
        validate_preferences(frame,{'Next backup':''})
        validate_preferences(frame,{})

    def test_unknown_rows_and_extra_columns_survive(self):
        frame=sample_preferences()
        frame.loc[len(frame)]=['Future preference','UnknownType','preserve me']
        frame['Notes']='extra metadata'
        original=frame.copy(deep=True)
        updated=validate_preferences(frame,{'Learn batch':'12'})
        self.assertEqual(updated.iloc[-1]['Value'],'preserve me')
        self.assertEqual(updated['Notes'].tolist(),frame['Notes'].tolist())
        pd.testing.assert_frame_equal(frame,original)

    def test_invalid_save_does_not_touch_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv'
            sample_preferences().to_csv(path,sep=';',index=False)
            before=path.read_bytes()
            with self.assertRaises(PreferenceError):
                save_preferences(load_preferences(path),{'Learn batch':'invalid'},path)
            self.assertEqual(path.read_bytes(),before)

    def test_io_failure_does_not_mutate_form(self):
        frame=sample_preferences()
        original=frame.copy(deep=True)
        with patch('app.repositories.preferences.commit_document',side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                save_preferences(frame,{'Learn batch':'12'},'unused.csv')
        pd.testing.assert_frame_equal(frame,original)

    def test_valid_save_preserves_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv'
            frame=sample_preferences()
            save_preferences(frame,{'Learn batch':'12'},path)
            saved=load_preferences(path)
            self.assertEqual(list(saved.columns),list(frame.columns))
            self.assertEqual(saved.set_index('Name').loc['Learn batch','Value'],'12')
