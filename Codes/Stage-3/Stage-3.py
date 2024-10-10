import os
import numpy as np
import pandas as pd

file = "adder.ckt"

if os.path.isdir('Codes'):
    os.chdir("./Codes")

if os.path.isdir('Stage-3'):
    os.chdir("./Stage-3")

#----------- Leakage Current Getter -----------

def get_current_val(ind_or_st,mosfet_type,W,params):
    if ind_or_st == "ind":
        df = pd.read_csv(f'../../Matrix/Stage-1/{mosfet_type}_W={W}.csv')

        drain = params[0]
        gate = params[1]
        source = params[2]
        current = params[3]

        currs = df[(df['v(gate)'] == gate) & (df['v(source)'] == source) & (df['v(drain)'] == drain)]
        i_val = currs[current].values[0]
    else:
        df = pd.read_csv(f'../../Matrix/Stage-2/{mosfet_type}_W={W}.csv')

        v1 = params[0]
        v2 = params[1]

        curr = df[(df['v(gate1)'] == v1) & (df['v(gate2)'] == v2)]
        i_val = curr['total'].values[0]

    return abs(i_val)

#----------- One input Gate Currents -----------

not_g = {}

not_g[0] = get_current_val("ind","pmos",64,[1.1,0,1.1,"i(vg)"]) + get_current_val("ind","nmos",32,[1.1,0,0,"i(vd)"])
not_g[1] = get_current_val("ind","nmos",32,[0,1.1,0,"i(vg)"]) + get_current_val("ind","pmos",64,[0,1.1,1.1,"i(vs)"])

#----------- Two input Gate Currents -----------

nand_g = {}

nand_g[(0,0)] = 2*get_current_val("ind","pmos",64,[1.1,0,1.1,"i(vg)"]) + get_current_val("stacked","nmos",64,[0,0])
nand_g[(0,1)] = get_current_val("ind","pmos",64,[1.1,0,1.1,"i(vg)"]) + get_current_val("ind","pmos",64,[1.1,1.1,1.1,"i(vd)"]) + get_current_val("stacked","nmos",64,[0,1.1])
nand_g[(1,0)] = get_current_val("ind","pmos",64,[1.1,1.1,1.1,"i(vd)"]) + get_current_val("ind","pmos",64,[1.1,0,1.1,"i(vg)"]) + get_current_val("stacked","nmos",64,[1.1,0])
nand_g[(1,1)] = 2*get_current_val("ind","pmos",64,[1.1,1.1,0,"i(vd)"]) + get_current_val("stacked","nmos",64,[1.1,1.1])

nor_g = {}

nor_g[(0,0)] = 2*get_current_val("ind","nmos",32,[1.1,0,0,"i(vd)"]) + get_current_val("stacked","pmos",128,[0,0])
nor_g[(0,1)] = get_current_val("ind","nmos",32,[0,0,0,"i(vd)"]) + get_current_val("ind","nmos",32,[0,1.1,0,"i(vg)"]) + get_current_val("stacked","pmos",128,[0,1.1])
nor_g[(1,0)] = get_current_val("ind","nmos",32,[0,1.1,0,"i(vg)"]) + get_current_val("ind","nmos",32,[0,0,0,"i(vd)"]) + get_current_val("stacked","pmos",128,[1.1,0])
nor_g[(1,1)] = 2*get_current_val("ind","nmos",32,[0,1.1,0,"i(vg)"]) + get_current_val("stacked","pmos",128,[1.1,1.1])

or_g = {}

or_g[(0,0)] = nor_g[(0,0)] + not_g[1]
or_g[(0,1)] = nor_g[(0,1)] + not_g[0]
or_g[(1,0)] = nor_g[(1,0)] + not_g[0]
or_g[(1,1)] = nor_g[(1,1)] + not_g[0]

and_g = {}

and_g[(0,0)] = nand_g[(0,0)] + not_g[1]
and_g[(0,1)] = nand_g[(0,1)] + not_g[1]
and_g[(1,0)] = nand_g[(1,0)] + not_g[1]
and_g[(1,1)] = nand_g[(1,1)] + not_g[0]

#----------- Three Input Gate Currents -----------

nand_3_g = {}

nand_3_g[(0, 0, 0)] = nand_g[(0, 0)] + nand_g[(0, 0)] + nand_g[(1, 1)] + nand_g[(1, 0)]
nand_3_g[(0, 0, 1)] = nand_g[(0, 0)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)]
nand_3_g[(0, 1, 0)] = nand_g[(0, 1)] + nand_g[(0, 0)] + nand_g[(1, 1)] + nand_g[(1, 0)]
nand_3_g[(0, 1, 1)] = nand_g[(0, 1)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)]
nand_3_g[(1, 0, 0)] = nand_g[(1, 0)] + nand_g[(0, 0)] + nand_g[(1, 1)] + nand_g[(1, 0)]
nand_3_g[(1, 0, 1)] = nand_g[(1, 0)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)]
nand_3_g[(1, 1, 0)] = nand_g[(1, 1)] + nand_g[(0, 0)] + nand_g[(0, 0)] + nand_g[(1, 1)]
nand_3_g[(1, 1, 1)] = nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)] + nand_g[(1, 0)]

nor_3_g = {}

nor_3_g[(0, 0, 0)] = nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)] + nor_g[(1, 0)]
nor_3_g[(0, 0, 1)] = nor_g[(0, 0)] + nor_g[(1, 1)] + nor_g[(1, 1)] + nor_g[(0, 0)]
nor_3_g[(0, 1, 0)] = nor_g[(0, 1)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)]
nor_3_g[(0, 1, 1)] = nor_g[(0, 1)] + nor_g[(1, 1)] + nor_g[(0, 0)] + nor_g[(0, 1)]
nor_3_g[(1, 0, 0)] = nor_g[(0, 1)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)]
nor_3_g[(1, 0, 1)] = nor_g[(0, 1)] + nor_g[(1, 1)] + nor_g[(0, 0)] + nor_g[(0, 1)]
nor_3_g[(1, 1, 0)] = nor_g[(1, 1)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)]
nor_3_g[(1, 1, 1)] = nor_g[(1, 1)] + nor_g[(1, 1)] + nor_g[(0, 0)] + nor_g[(1, 0)]

#----------- Four Input Gate Currents -----------

nand_4_g = {}

nand_4_g[(0, 0, 0, 0)] = nand_g[(0, 0)] + nand_g[(0, 0)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)]
nand_4_g[(0, 0, 0, 1)] = nand_g[(0, 0)] + nand_g[(0, 1)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)]
nand_4_g[(0, 0, 1, 0)] = nand_g[(0, 0)] + nand_g[(1, 0)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)]
nand_4_g[(0, 0, 1, 1)] = nand_g[(0, 0)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)] + nand_g[(1, 0)]
nand_4_g[(0, 1, 0, 0)] = nand_g[(0, 1)] + nand_g[(0, 0)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)]
nand_4_g[(0, 1, 0, 1)] = nand_g[(0, 1)] + nand_g[(0, 1)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)]
nand_4_g[(0, 1, 1, 0)] = nand_g[(0, 1)] + nand_g[(1, 0)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)]
nand_4_g[(0, 1, 1, 1)] = nand_g[(0, 1)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)] + nand_g[(1, 0)]
nand_4_g[(1, 0, 0, 0)] = nand_g[(1, 0)] + nand_g[(0, 0)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)]
nand_4_g[(1, 0, 0, 1)] = nand_g[(1, 0)] + nand_g[(0, 1)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)]
nand_4_g[(1, 0, 1, 0)] = nand_g[(1, 0)] + nand_g[(1, 0)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)]
nand_4_g[(1, 0, 1, 1)] = nand_g[(1, 0)] + nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)] + nand_g[(1, 0)]
nand_4_g[(1, 1, 0, 0)] = nand_g[(1, 1)] + nand_g[(0, 0)] + nand_g[(0, 0)] + nand_g[(1, 1)] + nand_g[(1, 0)]
nand_4_g[(1, 1, 0, 1)] = nand_g[(1, 1)] + nand_g[(0, 1)] + nand_g[(0, 0)] + nand_g[(1, 1)] + nand_g[(1, 0)]
nand_4_g[(1, 1, 1, 0)] = nand_g[(1, 1)] + nand_g[(1, 0)] + nand_g[(0, 0)] + nand_g[(1, 1)] + nand_g[(1, 0)]
nand_4_g[(1, 1, 1, 1)] = nand_g[(1, 1)] + nand_g[(1, 1)] + nand_g[(0, 0)] + nand_g[(0, 0)] + nand_g[(1, 1)]

nor_4_g = {}

nor_4_g[(0, 0, 0, 0)] = nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)] + nor_g[(1, 1)] + nor_g[(0, 0)]
nor_4_g[(0, 0, 0, 1)] = nor_g[(0, 0)] + nor_g[(0, 1)] + nor_g[(1, 1)] + nor_g[(0, 0)] + nor_g[(0, 1)]
nor_4_g[(0, 0, 1, 0)] = nor_g[(0, 0)] + nor_g[(1, 0)] + nor_g[(1, 1)] + nor_g[(0, 0)] + nor_g[(0, 1)]
nor_4_g[(0, 0, 1, 1)] = nor_g[(0, 0)] + nor_g[(1, 1)] + nor_g[(1, 1)] + nor_g[(0, 0)] + nor_g[(1, 0)]
nor_4_g[(0, 1, 0, 0)] = nor_g[(0, 1)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)] + nor_g[(0, 1)]
nor_4_g[(0, 1, 0, 1)] = nor_g[(0, 1)] + nor_g[(0, 1)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)]
nor_4_g[(0, 1, 1, 0)] = nor_g[(0, 1)] + nor_g[(1, 0)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)]
nor_4_g[(0, 1, 1, 1)] = nor_g[(0, 1)] + nor_g[(1, 1)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)]
nor_4_g[(1, 0, 0, 0)] = nor_g[(1, 0)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)] + nor_g[(1, 0)]
nor_4_g[(1, 0, 0, 1)] = nor_g[(1, 0)] + nor_g[(0, 1)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)]
nor_4_g[(1, 0, 1, 0)] = nor_g[(1, 0)] + nor_g[(1, 0)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)]
nor_4_g[(1, 0, 1, 1)] = nor_g[(1, 0)] + nor_g[(1, 1)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)]
nor_4_g[(1, 1, 0, 0)] = nor_g[(1, 1)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)] + nor_g[(1, 0)]
nor_4_g[(1, 1, 0, 1)] = nor_g[(1, 1)] + nor_g[(0, 1)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)]
nor_4_g[(1, 1, 1, 0)] = nor_g[(1, 1)] + nor_g[(1, 0)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)]
nor_4_g[(1, 1, 1, 1)] = nor_g[(1, 1)] + nor_g[(1, 1)] + nor_g[(0, 0)] + nor_g[(0, 0)] + nor_g[(1, 1)]

#----------- Calculating Circuit Currents -----------

def read__line(line,file):
    strs = line.split()
    if len(strs) == 0: return "NULL"

    gates = ['Inverter','NAND','NOR','AND','OR']
    gate = strs[0]

    if(gate[0] == 'i'):
        cuur = float(strs[2])
        if cuur < 0:
            return [abs(cuur)]

    if gate not in gates: return "NULL"

    number = 1
        
    if gate != "Inverter":
        number = int(strs[1])

    inputs = []

    for i in range(number):
        line_i = file.readline()
        strs = line_i.split()

        inp = float(strs[2])

        if abs(inp - 0) <= abs(inp - 1.1):
            inp = 0
        else:
            inp = 1
        
        inputs.append(inp)

    return [gate,inputs]

def get_currents(file_name):
    total_current = 0
    ng_curr = 0

    with open(file_name,'r') as file:
        while True:
            line = file.readline()

            if not line: break

            out = read__line(line,file)

            if(len(out) == 1):
                ng_curr+=out[0]
                continue

            if out == "NULL": continue

            print("\n")

            gate = out[0]
            inputs = out[1]

            print(gate + " " + str(len(inputs)) + " Leakage Current:")

            if gate == 'Inverter':
                total_current = total_current + not_g[inputs[0]]
                print(not_g[inputs[0]])
            elif gate == 'NAND':
                if len(inputs) == 2:
                    total_current = total_current + nand_g[tuple(inputs)]
                    nand_g[tuple(inputs)]
                elif len(inputs) == 3:
                    total_current = total_current + nand_3_g[tuple(inputs)]
                    print(nand_3_g[tuple(inputs)])
                else:
                    total_current = total_current + nand_4_g[tuple(inputs)]
                    print(nand_4_g[tuple(inputs)])
            elif gate == 'NOR':
                if len(inputs) == 2:
                    total_current = total_current + nor_g[tuple(inputs)]
                    print(nor_g[tuple(inputs)])
                elif len(inputs) == 3:
                    total_current = total_current + nor_3_g[tuple(inputs)]
                    print(nand_3_g[tuple(inputs)])
                else:
                    total_current = total_current + nor_4_g[tuple(inputs)]
                    print(nand_4_g[tuple(inputs)])
            elif gate == 'OR':
                if len(inputs) == 2:
                    total_current = total_current + or_g[tuple(inputs)]
                    print(or_g[tuple(inputs)])
                elif len(inputs) == 3:
                    if inputs == [0]*3:
                        out = nor_3_g[tuple(inputs)] + not_g[1]
                    else:
                        out = nor_3_g[tuple(inputs)] + not_g[0]

                    total_current = total_current + out
                    print(out)
                else:
                    if inputs == [0]*4:
                        out = nor_4_g[tuple(inputs)] + not_g[1]
                    else:
                        out = nor_4_g[tuple(inputs)] + not_g[0]
                    
                    total_current = total_current + out
                    print(out)
            else:
                if len(inputs) == 2:
                    total_current = total_current + and_g[tuple(inputs)]
                    print(nand_g[tuple(inputs)])
                elif len(inputs) == 3:
                    if inputs == [1]*3:
                        out = nand_3_g[tuple(inputs)] + not_g[0]
                    else:
                        out = nand_3_g[tuple(inputs)] + not_g[1]

                    total_current = total_current + out
                    print(out)
                else:
                    if inputs == [1]*4:
                        out = nand_4_g[tuple(inputs)] + not_g[0]
                    else:
                        out = nand_4_g[tuple(inputs)] + not_g[1]
                    
                    total_current = total_current + out
                    print(out)

    return total_current,ng_curr

os.system(f"echo 'exit' | ngspice {file} > o.txt")

total_leakage,ngspice_current = get_currents('o.txt')

print(' ')
print("Estimated Leakage Current total : " + str(total_leakage) + "\n")

print('Simulation Leakage Current total : ' + str(ngspice_current))

accuracy = (1 - abs(ngspice_current - total_leakage)/ngspice_current)*100

print('\nTotal Accuracy : ' + str(accuracy) + '%')

os.system("rm o.txt")