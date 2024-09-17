import os
import numpy as np
import pandas as pd

file1 = "nmos_2_stacked.ckt"
file2 = "pmos_2_stacked.ckt"

def read__line(tables,line):
    strs = line.split()
    if strs[0] in tables:
        tables[strs[0]].append(float(strs[2]))
    else : tables[strs[0]] = []

def add_prev_entry(file,df):
    prev_df = pd.read_csv(file)
    max_p_currs = prev_df.to_dict()
    v_dict = {[max_p_currs['v(gate)'],max_p_currs['v(drain)']] : max_p_currs['']}

    # for row in df.iterrows():
    #     vgs1 = row['v(gate1)'] - row['v(alimd)']
    #     vds1 = row['v(drain1)'] - row['v(alimd)']

    #     vgs2 = row['v(gate2)']
    #     vds2 = row['v(alimd)']


    #     row['prev_leakage_1'] = 

def get_csv(text,name):
    tables = {}
    with open(text,'r') as file:
        while True:
            line = file.readline()

            if not line: break
            if(line[0] != 'i' and line[0] != 'v'): continue

            read__line(tables,line)

    df = pd.DataFrame.from_dict(tables)

    df["max_leak_1"] = df[[s for s in df.columns if s.startswith('i') and s[-2] == '1']].abs().max(axis=1)
    df["max_leak_2"] = df[[s for s in df.columns if s.startswith('i') and s[-2] == '2']].abs().max(axis=1)
    
    add_prev_entry(f"{name[:4]}_W=32.csv",df)
    df.to_csv(name,index=False)

def get_data(file_i):
    os.system(f"echo 'exit' | ngspice {file_i} > {'o.txt'}")

    get_csv("o.txt",f"{file_i[:4]}_s2.csv")
    os.system(f"rm o.txt")

get_data(file1)
get_data(file2)