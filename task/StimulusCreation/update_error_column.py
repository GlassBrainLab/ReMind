"""
update_error_column.py

Calculate is_error column for reading experiment stimuli.
Created 2/16/23 by DJ.
"""

import numpy as np, pandas as pd

topics = ['history_of_film','pluto','prisoners_dilemma','serena_williams','the_voynich_manuscript']
errors = ['gibberish','lexical']

for topic in topics:
  df_control = pd.read_csv(f'{topic}_control/{topic}_control_coordinates.csv',index_col=0)

  for error in errors:
    print(f'=== {topic}, {error} ===')
    df_error = pd.read_csv(f'{topic}_{error}/{topic}_{error}_coordinates.csv',index_col=0)
    df_error['is_error'] = (df_error['words']!=df_control['words']).astype(int)
    print(pd.concat([df_error.loc[df_error.is_error==1,'words'], df_control.loc[df_error.is_error==1,'words']],axis=1))
    out_file = f'{topic}_{error}/{topic}_{error}_coordinates.csv'
    print(f'== Saving as {out_file}.')
    df_error.to_csv(out_file)
print('=== Done!')
