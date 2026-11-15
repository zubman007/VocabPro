"""Application defaults and learning parameters (not user preferences)."""
import pandas as pd

app_name = "VocabPro"
days_gap_map = {0: 0, 1: 1, 2: 2, 3: 4, 4: 7, 5: 15, 6: 25, 7: 50, 8: 100, 9: 150}
default_wait = 200
stat_horizon = 200

PoS_types = ['Noun', 'Verb', 'Other', 'Adjective', 'Adverb']
PoS_ideal = pd.Series([32, 25, 20, 15, 8],index=PoS_types,name='Percentage')


