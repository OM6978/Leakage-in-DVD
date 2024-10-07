import os
import numpy as np
import pandas as pd

loops = 6
file1 = "nmos"
file2 = "pmos"

def get_df(filee,name):
    os.system(f"echo 'exit' | ngspice {filee} > {name}")

    mat = []
    titles = []

    line = []
    prev = []
    prev_p = []
    with open(name,'r') as file:
        while True:
            prev_p = prev
            prev = line
            line = file.readline()
            if not line:
                break

            if(line[0] <= '9' and line[0] >= '0'):
                line = line[:-1].split()
                if(line[0] == '0'):
                    mat.append([])
                    titles.append(prev_p.split())

                for i in range(len(line)):
                    line[i] = float(line[i])
                    
                mat[-1].append(line)
    
    mat[0] = np.array(mat[0])
    mat[0] = mat[0][:,1:]
    df = pd.DataFrame(mat[0])
    df.columns = titles[0][1:]

    for i in range(1,len(mat)):
        mat[i] = np.array(mat[i])
        mat[i] = mat[i][:,2:]
        df2 = pd.DataFrame(mat[i])
        df2.columns = titles[i][2:]
        df = pd.concat([df,df2],axis=1)

    os.system(f"rm {name}")
    return df

def make_csv(filee_on,filee_off,name):
    df_1 = get_df(filee_on,name)
    df_2 = get_df(filee_off,name)

    df = pd.concat([df_1, df_2], ignore_index=True)
    df.to_csv(f'../../Matrix/Stage-1/{name[:-4]}.csv',index = False)

def sweep_W(filee):
    for i in range(loops):
        os.system(f"touch {filee}_on_temp_{i+1}.ckt")
        os.system(f"touch {filee}_off_temp_{i+1}.ckt")
    
    W = "unknown"

    with open(f"{filee}_on.ckt",'r') as file:
        while True:
            line = file.readline()
            if not line: break

            for i in range(loops):
                with open(f"{filee}_on_temp_{i+1}.ckt",'a') as lol:
                    if(len(line) > 12 and line[:12] == ".PARAM Wmin="):
                        if W == "unknown":
                            W = int(line[12:-2])
                        lol.write(line[:12] + str(int(line[12:-2])*(i+1)) + line[-2:])
                    else: lol.write(line)

    W = "unknown"

    with open(f"{filee}_off.ckt",'r') as file:
        while True:
            line = file.readline()
            if not line: break

            for i in range(loops):
                with open(f"{filee}_off_temp_{i+1}.ckt",'a') as lol:
                    if(len(line) > 12 and line[:12] == ".PARAM Wmin="):
                        if W == "unknown":
                            W = int(line[12:-2])
                        lol.write(line[:12] + str(int(line[12:-2])*(i+1)) + line[-2:])
                    else: lol.write(line)

    for i in range(loops):
        make_csv(f"{filee}_on_temp_{i+1}.ckt",f"{filee}_off_temp_{i+1}.ckt",f"{filee}_W={W*(i+1)}.txt")
        os.system(f"rm {filee}_on_temp_{i+1}.ckt")
        os.system(f"rm {filee}_off_temp_{i+1}.ckt")

if os.path.isdir('Codes'):
    os.chdir("./Codes")

if os.path.isdir('Stage-1'):
    os.chdir('./Stage-1')

sweep_W(file1)
sweep_W(file2)