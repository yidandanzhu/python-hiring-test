"""Main script for generating output.csv."""

import pandas as pd
import numpy as np

## Logistics
split_map = {'vs RHP':lambda df:df[df['PitcherSide'] == 'R'],
             'vs LHP':lambda df:df[df['PitcherSide'] == 'L'],
             'vs RHH':lambda df:df[df['HitterSide'] == 'R'],
             'vs LHH':lambda df:df[df['HitterSide'] == 'L']}

def calculate_avg(df):
    return df['H'] / df['AB']
    
def calculate_obp(df):
    return (df['H'] + df['BB'] + df['HBP']) / (df['AB'] + df['BB'] + df['HBP'] + df['SF'])

def calculate_slg(df):
    return df['TB'] / df['AB']

def calculate_ops(df):
    return calculate_obp(df) + calculate_slg(df)

stats_map = {'AVG':calculate_avg,
             'OBP':calculate_obp,
             'SLG':calculate_slg,
             'OPS':calculate_ops}


## Run the query over the dataframe
def process_df(df, q):
    qs = q.strip().split(',')     # qs = [<Stat>, <Subject>, <Split>]
    
    # Split
    tmp_df = split_map[qs[2]](df)
    
    # Group by Subject
    tmp_df = tmp_df.groupby(qs[1]).agg({'PA': np.sum, 'H': np.sum, 'AB': np.sum, 'BB': np.sum, 'HBP': np.sum, 'TB': np.sum, 'SF': np.sum})
    tmp_df = tmp_df[tmp_df['PA']>=25]
    
    # Necessary cols
    tmp_df.index.names = ['SubjectId']  
    tmp_df['Stat'] = qs[0]
    tmp_df['Split'] = qs[2]
    tmp_df['Subject'] = qs[1]
    tmp_df['Value'] = pd.Series(stats_map[qs[0]](tmp_df)).round(3)
  
    return tmp_df[['Stat', 'Split', 'Subject', 'Value']]

def main():
    # add basic program logic here
    pitches = pd.read_csv('data/raw/pitchdata.csv')
    queries = open('data/reference/combinations.txt').readlines()[1:]
    
    retlist = []
    for q in queries:
        new_df = process_df(pitches, q)
        retlist.append(new_df)
    
    ret = pd.concat(retlist)
    ret['SubjectId'] = ret.index.values
    ret = ret.sort_values(by=['SubjectId', 'Stat', 'Split', 'Subject'])
    
    ret[['Stat', 'Split', 'Subject', 'Value']].to_csv('data/processed/output.csv')

if __name__ == '__main__':
    main()
