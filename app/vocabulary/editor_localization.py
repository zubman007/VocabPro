"""Translate enum display values without changing the stored vocabulary schema."""
ENUMS={'Audio':('Automatic','Automatic - 11Labs','Automatic - dictapi','Automatic - Merriam_Webster','Own','No audio'),
       'Part of Speech':('Noun','Verb','Other','Adjective','Adverb'),
       'Description':('No found',),'Example':('No found',)}


def display_frame(frame,translate):
    result=frame.copy()
    for column,values in ENUMS.items():
        if column in result:result[column]=result[column].replace({value:translate(value) for value in values})
    return result


def canonical_rows(rows,headers,translate):
    import pandas as pd
    result=pd.DataFrame(rows,columns=headers)
    for column,values in ENUMS.items():
        if column in result:result[column]=result[column].replace({translate(value):value for value in values})
    return result.values.tolist()
