import os
import numpy as np
import pandas as pd
import math

file1 = "nmos_2_stacked-1.ckt"
file2 = "pmos_2_stacked-1.ckt"

def read__line(tables,line):
    strs = line.split()
    if strs[0] in tables:
        tables[strs[0]].append(float(strs[2]))
    else : tables[strs[0]] = []

def euclidean_distance(t1, t2):
    return math.sqrt((t1[0] - t2[0])**2 + (t1[1] - t2[1])**2)

def add_prev_entry(file,df):
    prev_df = pd.read_csv(file)
    prev_df["max_leak"] = prev_df[[s for s in prev_df.columns if s.startswith('i')]].abs().max(axis=1)
    max_p_currs = prev_df.to_dict()

    Vg_dict = max_p_currs['v(gate)']
    Vd_dict = max_p_currs['v(drain)']

    V_dict = {}
    for i in range(len(Vg_dict)):
        V_dict[(Vg_dict[i],Vd_dict[i])] = max_p_currs['max_leak'][i]

    vgs1_arr = (df['v(gate1)']).to_numpy()
    vds1_arr = (df['v(drain1)']).to_numpy()

    new_comp = []
    for i in range(len(vgs1_arr)):
            closest_key = min(V_dict.keys(), key=lambda k: euclidean_distance(k, (vgs1_arr[i],vds1_arr[i])))
            new_comp.append(V_dict[closest_key])

    df['prev_leakage_1'] = np.array(new_comp)

    vgs2_arr = (df['v(gate2)'] - df['v(drain1)']).to_numpy()
    vds2_arr = (df['v(alimd)'] - df['v(drain1)']).to_numpy()

    new_comp = []
    for i in range(len(vgs1_arr)):
            closest_key = min(V_dict.keys(), key=lambda k: euclidean_distance(k, (vgs2_arr[i],vds2_arr[i])))
            new_comp.append(V_dict[closest_key])

    df['prev_leakage_2'] = np.array(new_comp)

def get_csv(text,name):         
    tables = {}
    with open(text,'r') as file:
        while True:
            line = file.readline()

            if not line: break
            if(line[0] != 'i' and line[0] != 'v'): continue

            read__line(tables,line)

    df = pd.DataFrame.from_dict(tables)
    df["i(vs2)"] = df["i(vd1)"]

    df["max_leak_1"] = df[[s for s in df.columns if s.startswith('i') and s[-2] == '1']].abs().max(axis=1)
    df["max_leak_2"] = df[[s for s in df.columns if s.startswith('i') and s[-2] == '2']].abs().max(axis=1)
    
    add_prev_entry(f"../Matrix/Stage-1/{name[:4]}_W=32.csv",df)
    df.to_csv(f'../Matrix/Stage-2/{name}',index=False)

def get_data(file_i):
    os.system(f"echo 'exit' | ngspice {file_i} > {'o.txt'}")

    get_csv("o.txt",f"{file_i[:4]}.csv")
    os.system(f"rm o.txt")

if os.path.isdir('Codes'):
    os.chdir("./Codes")

get_data(file1)
get_data(file2)