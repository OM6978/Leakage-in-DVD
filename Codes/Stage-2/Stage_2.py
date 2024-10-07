import os
import numpy as np
import pandas as pd
import math

file1 = "nmos_2_stacked-3.ckt"
file2 = "pmos_2_stacked-3.ckt"

loops = 6

def read__line(tables,line):
    strs = line.split()
    if strs[0] in tables:
        tables[strs[0]].append(float(strs[2]))
    else : tables[strs[0]] = [float(strs[2])]

def euclidean_distance(t1, t2):
    return math.sqrt((t1[0] - t2[0])**2 + (t1[1] - t2[1])**2 + (t1[2] - t2[2])**2)

def add_prev_entry(file,df):
    prev_df = pd.read_csv(file)

    max_p_currs = prev_df.to_dict()

    Vg_dict = max_p_currs['v(gate)']
    Vd_dict = max_p_currs['v(drain)']
    Vs_dict = max_p_currs['v(source)']
    
    V_dict = {}
    for i in range(len(Vg_dict)):
        V_dict[(Vg_dict[i],Vd_dict[i],Vs_dict[i])] = (max_p_currs['i(vg)'][i],max_p_currs['i(vd)'][i])
        
    vgs1_arr = (df['v(gate1)']).to_numpy()
    vds1_arr = (df['v(drain1)']).to_numpy()

    new_comp = []
    for i in range(len(vgs1_arr)):
        if "nmos" in file:
            closest_key = min(V_dict.keys(), key=lambda k: euclidean_distance(k, (vgs1_arr[i],vds1_arr[i],0)))
        else: 
            closest_key = min(V_dict.keys(), key=lambda k: euclidean_distance(k, (vgs1_arr[i],vds1_arr[i],1.1)))

        if vgs1_arr[i] == 1.1:
            if "pmos" in file:
                new_comp.append(V_dict[closest_key][1])
            else: new_comp.append(V_dict[closest_key][0])
        else:
            if "pmos" in file:
                new_comp.append(V_dict[closest_key][0])
            else: new_comp.append(V_dict[closest_key][1])

    df['prev_leakage_1'] = np.array(new_comp)

    vgs2_arr = (df['v(gate2)']).to_numpy()
    vds2_arr = (df['v(drain2)']).to_numpy()
    vss_2_arr = (df['v(drain1)']).to_numpy()

    new_comp = []
    for i in range(len(vgs1_arr)):
            closest_key = min(V_dict.keys(), key=lambda k: euclidean_distance(k, (vgs2_arr[i],vds2_arr[i],vss_2_arr[i])))
            if vgs2_arr[i] == 1.1:
                if "pmos" in file:
                    new_comp.append(V_dict[closest_key][1])
                else: new_comp.append(V_dict[closest_key][0])
            else:
                if "pmos" in file:
                    new_comp.append(V_dict[closest_key][0])
                else: new_comp.append(V_dict[closest_key][1])

    df['prev_leakage_2'] = np.array(new_comp)
    df['total_prev'] = df['prev_leakage_1'].abs() + df['prev_leakage_2'].abs()

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
        df.loc[(df['v(gate1)'] == 0) & (df['v(gate2)'] == 0), 'total'] = df['i(vd1)'].abs() + df['i(vd2)'].abs()
        df.loc[(df['v(gate1)'] == 0) & (df['v(gate2)'] == 1.1), 'total'] = df['i(vd1)'].abs() + df['i(vg2)'].abs()
        df.loc[(df['v(gate1)'] == 1.1) & (df['v(gate2)'] == 0), 'total'] = df['i(vg1)'].abs() + df['i(vd2)'].abs()
        df.loc[(df['v(gate1)'] == 1.1) & (df['v(gate2)'] == 1.1), 'total'] = df['i(vg1)'].abs() + df['i(vg2)'].abs()
    else:
        df.loc[(df['v(gate1)'] == 1.1) & (df['v(gate2)'] == 1.1), 'total'] = df['i(vd1)'].abs() + df['i(vd2)'].abs()
        df.loc[(df['v(gate1)'] == 0) & (df['v(gate2)'] == 1.1), 'total'] = df['i(vg1)'].abs() + df['i(vd2)'].abs()
        df.loc[(df['v(gate1)'] == 1.1) & (df['v(gate2)'] == 0), 'total'] = df['i(vd1)'].abs() + df['i(vg2)'].abs()
        df.loc[(df['v(gate1)'] == 0) & (df['v(gate2)'] == 0), 'total'] = df['i(vg1)'].abs() + df['i(vg2)'].abs()
    
    add_prev_entry(f"../../Matrix/Stage-1/{name}",df)
    df.to_csv(f'../../Matrix/Stage-2/{name}',index=False)

def get_data(file_i,name):
    os.system(f"echo 'exit' | ngspice {file_i} > {name}")

    get_csv(name,f"{name[:-4]}.csv")
    os.system(f"rm {name}")

def sweep_W(filee):
    for i in range(loops):
        os.system(f"touch {filee[:4]}_temp_{i+1}.ckt")
    
    W = "unknown"

    with open(filee,'r') as file:
        while True:
            line = file.readline()
            if not line: break

            for i in range(loops):
                with open(f"{filee[:4]}_temp_{i+1}.ckt",'a') as lol:
                    if(len(line) > 12 and line[:12] == ".PARAM Wmin="):
                        if W == "unknown":
                            W = int(line[12:-2])
                        lol.write(line[:12] + str(int(line[12:-2])*(i+1)) + line[-2:])
                    else: lol.write(line)

    for i in range(loops):
        get_data(f"{filee[:4]}_temp_{i+1}.ckt",f'{filee[:4]}_W={W*(i+1)}.txt')
        os.system(f"rm {filee[:4]}_temp_{i+1}.ckt")

if os.path.isdir('Codes'):
    os.chdir("./Codes")

if os.path.isdir('Stage-2'):
    os.chdir("./Stage-2")

sweep_W(file1)
sweep_W(file2)