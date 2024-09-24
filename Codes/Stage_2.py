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
    prev_df["max_leak"] = prev_df[[s for s in prev_df.columns if s.startswith('i')]].abs().max(axis=1)
    max_p_currs = prev_df.to_dict()

    Vg_dict = max_p_currs['v(gate)']
    Vd_dict = max_p_currs['v(drain)']

    V_dict = {}
    for i in range(len(Vg_dict)):
        V_dict[(Vg_dict[i],Vd_dict[i])] = max_p_currs['max_leak'][i]

    vgs1_arr = (df['v(gate1)'] - df['v(alimd)']).to_numpy()
    vds1_arr = (df['v(drain1)'] - df['v(alimd)']).to_numpy()

    vgs1_new = (df['v(gate1)']).to_numpy()
    vds1_new = (df['v(drain1)']).to_numpy()

    key_tuples = np.array(list(zip(vgs1_arr, vds1_arr)))
    is_in_v_dict = np.isin(key_tuples, list(V_dict.keys()))
    result = np.all(is_in_v_dict, axis=1)

    new_comp = []
    for i in range(len(result)):
        if result[i]:
            new_comp.append(V_dict[(vgs1_arr[i],vds1_arr[i])])
        else : new_comp.append(V_dict[(vgs1_new[i],vds1_new[i])])

    df['prev_leakage_1'] = np.array(new_comp)

    V_dict = {}
    for i in range(len(Vg_dict)):
        V_dict[(Vg_dict[i],Vd_dict[i])] = max_p_currs['max_leak'][i]

    vgs2_arr = df['v(gate2)'].to_numpy()
    vds2_arr = df['v(alimd)'].to_numpy()

    key_tuples = np.array(list(zip(vgs2_arr, vds2_arr)))
    is_in_v_dict = np.isin(key_tuples, list(V_dict.keys()))
    result = np.all(is_in_v_dict, axis=1)

    new_comp = []
    for i in range(len(result)):
        if result[i]:
            new_comp.append(V_dict[(vgs2_arr[i],vds2_arr[i])])
        else : new_comp.append(-1)

    df['prev_leakage_2'] = np.where(result, new_comp , -1)

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
    
    add_prev_entry(f"../Matrix/Stage-1/{name[:4]}_W=32.csv",df)
    df.to_csv(f'../Matrix/Stage-2/{name}',index=False)

def get_data(file_i):
    os.system(f"echo 'exit' | ngspice {file_i} > {'o.txt'}")

    get_csv("o.txt",f"{file_i[:4]}.csv")
    os.system(f"rm o.txt")

get_data(file1)
get_data(file2)