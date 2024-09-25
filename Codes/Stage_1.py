import os
import numpy as np
import pandas as pd

loops = 6
file1 = "nmos_multi_value_change.ckt"
file2 = "pmos_multi_value_change.ckt"

def make_csv(filee,name):
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

        # mat[i][:,1:] = np.float64(mat[i][:,1:])

        # df = pd.DataFrame(np.float64(mat[i]))
        df2 = pd.DataFrame(mat[i])

        # df2.columns = titles[i][1:]
        # df = pd.merge(df, df2)
        df2.columns = titles[i][2:]
        df = pd.concat([df,df2],axis=1)
        
    df.to_csv(f'../Matrix/Stage-1/{name[:-4]}.csv',index = False)
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
        make_csv(f"{filee[:4]}_temp_{i+1}.ckt",f"{filee[:4]}_W={W*(i+1)}.txt")
        os.system(f"rm {filee[:4]}_temp_{i+1}.ckt")

if os.path.isdir('Codes'):
    os.chdir("./Codes")

sweep_W(file1)
sweep_W(file2)