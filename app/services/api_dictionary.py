"""Dictionary provider parsing, separate from HTTP transport and the GUI."""
import logging
import re
from os.path import exists
from urllib.parse import quote
from requests import RequestException
from app.repositories.api_settings import audio_path, load_settings
from app.services.api_http import get_entries, download_audio

logger = logging.getLogger(__name__)

def dictionary_entry(i,df,learning_by,*,settings_path=None):
    phonetic = df.loc[i,'Phonetic']
    a_flag = df.loc[i,'Audio']
    word = df.loc[i,'English'].lower()
    example = df.loc[i,'Example']
    desc = df.loc[i,'Description']
    id = df.loc[i,'ID']
    for prefix in ['the','a','an']:
        if word.startswith(prefix + ' '):
            word = word[(len(prefix)+1):]
            break
    path_mp3 = audio_path(learning_by,'English',id,settings_path)
    exist_mp3 = exists(path_mp3)
    response = get_entries(f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(word, safe='')}")
    example_f = phonetic_f = a_url_f = desc_f = ''
    us_a = uk_a = rest_a = us_p = uk_p = rest_p = 0
    if response:
        for resp in response:
            if example_f == '' and example == '-':
                for mean in resp.get('meanings',[]):
                    definitions = mean.get('definitions', [])
                    for d in definitions:
                        if 'example' in d:
                            example_f = d['example']
                            if word not in example_f: example_f = ''
                            else: break
                        if example_f != '': break
            if desc_f == '' and desc == '-':
                for mean in resp.get('meanings',[]):
                    definitions = mean.get('definitions', [])
                    for d in definitions:
                        if 'definition' in d:
                            desc_f = d['definition']
                            if word in desc_f: desc_f = ''
                            else: break
                        if desc_f != '': break
            if phonetic_f == '' and phonetic == '[]':
                for j in resp.get('phonetics', []):
                    p_url_temp = (j.get('text') or 'N/A')
                    if '-us' in p_url_temp and us_p == 0:
                        us_p, phonetic_f = 1, p_url_temp
                        break
                    elif '-uk' in p_url_temp and uk_p == 0: uk_p, phonetic_f = 1, p_url_temp
                    elif rest_p == 0 and p_url_temp != 'N/A': rest_p, phonetic_f = 1, p_url_temp
            if (not exist_mp3) and ('Automatic' in a_flag) and (a_flag != 'Automatic - 11Labs') and us_a == 0:
                for j in resp.get('phonetics', []):
                    a_url_temp = (j.get('audio') or 'N/A')
                    if '-us' in a_url_temp and us_a == 0:
                        us_a, a_url_f = 1, a_url_temp
                        break
                    elif '-uk' in a_url_temp and uk_a == 0: uk_a, a_url_f = 1, a_url_temp
                    elif rest_a == 0 and a_url_temp != 'N/A': rest_a, a_url_f = 1, a_url_temp
        if phonetic_f != '': df.at[i, 'Phonetic'] = '[' + phonetic_f.replace('/','').replace('[','').replace(']','') + ']'
        if a_url_f != '':
            try:
                download_audio(a_url_f, path_mp3)
                df.at[i,'Audio'] = 'Automatic - dictapi'
            except (OSError, ValueError, RequestException):
                logger.warning("Dictionary audio download failed")
        if example_f != '': df.at[i,'Example'] = example_f
        if desc_f != '': df.at[i,'Description'] = desc_f
    return df

def merriam_entry(i,df,lang,learning_by,*,settings_path=None):
    if lang not in ("English", "Spanish"):
        from app.shared.messages import UserMessageError
        raise UserMessageError('Dictionary provider does not support {language}', language=lang)
    settings = load_settings(settings_path)
    key_name = "Merriam-Webster's spanish API key" if lang == "Spanish" else "Merriam-Webster's english API key"
    api_key = settings.get(key_name, "")
    if not api_key:
        from app.shared.messages import UserMessageError
        raise UserMessageError('Missing dictionary API key for {language}', language=lang)
    a_flag = df.loc[i,'Audio']
    word = df.loc[i,lang].lower()
    if lang == 'Spanish': prefixes = ['el','los','las']
    elif lang == 'English': prefixes = ['the','a','an']
    elif lang == 'French': prefixes = ['la','le','un','les','une','des']
    for prefix in prefixes:
        if word.startswith(prefix + ' '):
            word = word[(len(prefix)+1):]
            break
    example = df.loc[i,'Example']
    desc = df.loc[i,'Description']
    id = df.loc[i,'ID']
    path_mp3 = audio_path(learning_by,lang,id,settings_path)
    exist_mp3 = exists(path_mp3)
    if lang == 'Spanish':
        uri = f"https://dictionaryapi.com/api/v3/references/spanish/json/{quote(word, safe='')}"
        phonetic = 'not generate'
    if lang == 'English':
        uri = f"https://dictionaryapi.com/api/v3/references/sd3/json/{quote(word, safe='')}"
        phonetic = df.loc[i,'Phonetic']
    response = get_entries(uri, params={"key": api_key})
    example_f = phonetic_f = a_url_f = desc_f = ''
    if response:
        for resp in response:
            if phonetic_f == '' and phonetic == '[]':
                hwi = resp.get('hwi', {})
                prs = hwi.get('prs', [])
                for j in prs:
                    phonetic_f = (j.get('mw') or '')
                    if phonetic_f: break
            if desc_f == '' and desc == '-' and 'def' in resp:
                for desc_def in resp['def']:
                    if 'sseq' in desc_def:
                        for desc_sseq in desc_def['sseq']:
                            for desc_sseq_item in desc_sseq:
                                if isinstance(desc_sseq_item, list) and len(desc_sseq_item) > 1:
                                    try:
                                        desc_dt = desc_sseq_item[1].get('dt', [])
                                        for desc_dt_item in desc_dt:
                                            if isinstance(desc_dt_item, list) and len(desc_dt_item) > 1:
                                                try:
                                                    desc_f = re.sub(r'\{[^}]*\}', '', desc_dt_item[1])
                                                    if word in desc_f or desc_f in [',',';',', ',' ,',' ']: desc_f = ''
                                                    else: break
                                                except (KeyError, IndexError, TypeError, ValueError): pass
                                        if desc_f != '': break
                                    except (KeyError, IndexError, TypeError, ValueError): pass
                            if desc_f != '': break
            if example_f == '' and example == '-':
                for exm_def in resp.get('def', []):
                    if 'sseq' in exm_def:
                        for exm_sseq in exm_def['sseq']:
                            for exm_sseq_item in exm_sseq:
                                if isinstance(exm_sseq_item, list) and len(exm_sseq_item) > 1 and isinstance(exm_sseq_item[1], dict) and 'dt' in exm_sseq_item[1]:
                                    for exm_dt in exm_sseq_item[1]['dt']:
                                        if isinstance(exm_dt, list) and len(exm_dt) > 1 and exm_dt[0] == 'vis':
                                            for exm_dt_item in exm_dt[1]:
                                                try:
                                                    example_f = re.sub(r'\{[^}]*\}', '', exm_dt_item['t'])
                                                    if word not in example_f or example_f in [',',';',', ',' ,',' ']: example_f = ''
                                                    else: break
                                                except (KeyError, IndexError, TypeError, ValueError): pass
                                    if example_f != '': break
                            if example_f != '': break
            if (not exist_mp3) and ('Automatic' in a_flag) and (a_flag != 'Automatic - 11Labs') and a_url_f == '':
                if 'hwi' in resp:
                    if 'prs' in resp['hwi']:
                        for pronuc in resp['hwi']['prs']:
                            if 'sound' in pronuc and 'audio' in pronuc['sound']:
                                try:
                                    a_name = pronuc['sound']['audio']
                                    a_url_f = f"https://media.merriam-webster.com/audio/prons/es/me/mp3/{a_name[0]}/{a_name}.mp3"
                                    if a_url_f != '': break
                                except (KeyError, IndexError, TypeError, ValueError): pass
        if phonetic_f != '': df.at[i, 'Phonetic'] = '[' + phonetic_f.replace('/','').replace('[','').replace(']','') + ']'
        if a_url_f != '':
            try:
                download_audio(a_url_f, path_mp3)
                df.at[i,'Audio'] = 'Automatic - Merriam_Webster'
            except (OSError, ValueError, RequestException):
                logger.warning("Dictionary audio download failed")
        if example_f != '': df.at[i,'Example'] = example_f
        if desc_f != '': df.at[i,'Description'] = desc_f
    return df
