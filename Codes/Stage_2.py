import os
import numpy as np
import pandas as pd
import math

file1 = "nmos_2_stacked-2.ckt"
file2 = "pmos_2_stacked-2.ckt"

def read__line(tables,line):
    strs = line.split()
    if strs[0] in tables:
        tables[strs[0]].append(float(strs[2]))
    else : tables[strs[0]] = []

def euclidean_distance(t1, t2):
    return math.sqrt((t1[0] - t2[0])**2 + (t1[1] - t2[1])**2)

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

    df["total"] = pd.NA
    if name[:4] == "nmos":
        df.loc[(df['v(gate1)'] <= 0.5) & (df['v(gate2)'] <= 0.5), 'total'] = df['i(vd1)'].abs() + df['i(vd2)'].abs()
        df.loc[(df['v(gate1)'] <= 0.5) & (df['v(gate2)'] > 0.5), 'total'] = df['i(vd1)'].abs() + df['i(vg2)'].abs()
        df.loc[(df['v(gate1)'] > 0.5) & (df['v(gate2)'] <= 0.5), 'total'] = df['i(vg1)'].abs() + df['i(vd2)'].abs()
        df.loc[(df['v(gate1)'] > 0.5) & (df['v(gate2)'] > 0.5), 'total'] = df['i(vg1)'].abs() + df['i(vg2)'].abs()
    else:
        df.loc[(df['v(gate1)'] > 0.5) & (df['v(gate2)'] > 0.5), 'total'] = df['i(vs1)'].abs() + df['i(vs2)'].abs()
        df.loc[(df['v(gate1)'] <= 0.5) & (df['v(gate2)'] > 0.5), 'total'] = df['i(vs1)'].abs() + df['i(vg2)'].abs()
        df.loc[(df['v(gate1)'] > 0.5) & (df['v(gate2)'] <= 0.5), 'total'] = df['i(vg1)'].abs() + df['i(vs2)'].abs()
        df.loc[(df['v(gate1)'] <= 0.5) & (df['v(gate2)'] <= 0.5), 'total'] = df['i(vg1)'].abs() + df['i(vg2)'].abs()
    
    df.to_csv(f'../Matrix/Stage-2/{name}',index=False)

def get_data(file_i):
    os.system(f"echo 'exit' | ngspice {file_i} > {'o.txt'}")

    get_csv("o.txt",f"{file_i[:4]}.csv")
    os.system(f"rm o.txt")

if os.path.isdir('Codes'):
    os.chdir("./Codes")

get_data(file1)
get_data(file2)