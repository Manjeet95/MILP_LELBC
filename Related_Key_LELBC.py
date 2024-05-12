'''
Arguments:
1. Block Size - 64    
2. Number for rounds
3. Minimum Number of active S-boxes
4. Maximum Number of active S-boxes in each round
5. fix/no_fix - whether difference of some round is fixed or not
6. No. of trails to find 
7. possilbe/impossible differential characteritics
8. Solver to be used (GUROBI/CPLEX)
(if you are changing the code for anothe cipher then please change no. of ineq. in line 247 and 382)

python Related_key_LELBC.py 64 11 1 2 no_fix 1 GUROBI 
python Related_key_LELBC.py 64 5 1 2 fix 1 CPLEX
'''

import string
import sys
from math import floor


GUROBI_EXISTS = False
CPLEX_EXISTS = False

try:
  import google.colab
  IN_COLAB = True
except:
  IN_COLAB = False

if (sys.argv[7] == "GUROBI"):
    try: 
    	from gurobipy import *
    	GUROBI_EXISTS = True
    except:
    	GUROBI_EXISTS = False

if (sys.argv[7] == "CPLEX"):
	try: 
		from docplex.mp.model_reader import ModelReader
		CPLEX_EXISTS = True
	except:
		CPLEX_EXISTS = False

if (GUROBI_EXISTS == False) and (CPLEX_EXISTS == False):
	sys.exit()

conv = (1, 1, 0, 1, 1, -2, -1, -2, 3,
1, -1, -2, -1, 3, 2, 3, 2, 0,
-2, 2, -3, -1, 2, -1, 1, 2, 4,
1, -1, -1, 2, -1, -2, 2, 2, 3,
2, 2, 1, -1, -2, -1, -3, 2, 4,
1, 1, 0, 1, 1, 1, -1, 1, 0,
3, 2, 3, 2, 1, -1, -2, -1, 0,
1, 3, 0, 2, -3, 1, 1, -3, 3,
-1, 1, 3, 2, -3, 2, -1, 0, 2,
-1, 2, 2, 1, -3, -1, -1, 2, 3,
-1, 2, -1, 1, -1, 2, 0, -2, 3,
-2, -1, -3, 2, 2, 2, 1, -1, 4,
-3, 1, 1, -3, 1, 3, 0, 2, 3,
-3, -3, 1, 1, 1, 2, 0, 3, 3,
1, -2, -1, 1, -2, 2, -2, 1, 5,
-1, -1, 0, -1, 2, 3, 1, 3, 0,
-1, 1, -2, 2, -2, -2, 1, 2, 4,
1, 0, 0, 0, 0, -1, -1, -1, 2,
1, -2, 1, -2, -1, -1, 0, -1, 5,
-1, -1, 0, -1, 1, -2, 1, -2, 5,
0, -1, -1, -1, 1, 0, 0, 0, 2,
    )

convpbl = (1, -1, 0, -1, -1, 0, 0, 0, 3, 2, 0,
1, -1, 0, -1, -1, 1, -1, 1, 4, 2, 0,
1, 1, 0, 2, 1, -3, -1, 2, 0, 4, 0,
1, -1, -2, -1, 5, 2, 4, 2, -3, 0, 0,
6, 1, 2, 1, 1, -2, -3, -2, 0, 3, 0,
3, 3, 0, -1, -1, -2, -2, -1, 3, 5, 0,
2, 5, 2, 5, -2, -1, 0, -1, 0, -1, 0,
-1, 3, 0, 2, -4, 2, 1, -1, 4, 2, 0,
3, 1, 4, 3, -1, 3, -2, -4, -1, 4, 0,
3, -1, 0, 3, -1, -1, -2, -2, 3, 5, 0,
-2, 2, -2, 2, -1, 1, 0, 1, 5, 1, 0,
-5, 2, 1, -2, -1, 4, 0, 3, 5, 3, 0,
-1, -1, -2, -2, 3, -1, 0, 3, 3, 5, 0,
-5, -2, 1, 2, -1, 3, 0, 4, 5, 3, 0,
-1, -2, -2, -1, 3, 3, 0, -1, 3, 5, 0,
1, 2, -1, -3, 1, 2, 0, 1, 0, 4, 0,
1, -1, -1, 2, -2, -3, 3, 3, 5, 4, 0,
-1, -1, 0, 1, -2, -1, 2, -3, 5, 8, 0,
-1, -1, 0, -1, 1, -2, 0, -2, 6, 5, 0,
-2, -1, 1, -3, 0, -1, 1, 1, 4, 7, 0,
0, 0, 0, 0, 0, 0, 0, 0, -1, -1, 1,
    )

P64 = (32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46,
       47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61,
       62, 63, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
       15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)

LELBC = int(sys.argv[1])
s_boxes = int(LELBC/4)

if (LELBC==64):
    Perm = P64
else:
    print("Incorrect Parameters!")
    sys.exit()
    
ROUND = int(sys.argv[2])
min_sbox = int(sys.argv[3])
max_sbox_round = int(sys.argv[4])

if (sys.argv[5] == "fix"):
    fix = True
else:
    fix = False

fix_diff = [0x0000000000000001,0x0000000000000001]
fix_pos = [0,ROUND]
#fix_diff = [0x00000000001100000000000000000000,0x0090000000c000000000000000000000]
#fix_diff = [0x00000000001100000000000000000000]
#fix_diff = [0x000000000a0000000500000000000a00]
#fix_diff = [0x00002000001000010000000000000000]
#fix_pos = [1,2]

fix_diff_bin = [bin(diff)[2:].zfill(LELBC) for diff in fix_diff];
fix_bit = [];
for diff_1 in fix_diff_bin:
    fix_bit.append([i for i in range(0,len(diff_1)) if diff_1[i]=="1" ])
    # fix_bit.append([len(diff_1)-1-i for i in range(0,len(diff_1)) if diff_1[i]=="1" ])

def Constraints_XOR(x, y, z):
    #Generate the constraints by XOR operation.
    buf = ''
    buf = buf + x + " + " + y + " - " + z + " >= 0 \n"
    buf = buf + x + " - " + y + " + " + z + " >= 0 \n"
    buf = buf + " - " + x + " + " + y + " + " + z + " >= 0 \n"
    buf = buf + x + " + " + y + " + " + z + " <= 2 \n"
    return buf

def PrintOuter(FixList,BanList):
    opOuter = open("Outer" +"_LELBC_" + str(LELBC) + "_" + str(ROUND) + ".lp",'w+')
    opOuter.write("Minimize\n")
    buf = ''
    for i in range(0,ROUND):
      for j in range(0,s_boxes):
        buf = buf + "a" + str(i) + "_" + str(j)
        buf = buf + " + "
    
##        if i != ROUND-1 or j != (s_boxes-1):
##          buf = buf + " + "
                    
    opOuter.write(buf)
    buf = ''
    for i in range(0, ROUND):
      buf = buf + " A" + str(i)
      if i != ROUND-1:
        buf = buf + " + "
    opOuter.write(buf)
    
    opOuter.write('\n')
    opOuter.write("Subject to\n")

    if(fix==True):
        for b in range(0,len(fix_bit)):
            buf = ''
            fix_s_box_next = [floor((i)/4) for i in fix_bit[b]]
            for j in range(0,s_boxes):
                    #if (fix_pos!=0):
                    #    if(j in fix_s_box_prev):
                    #        buf = buf + "a" + str(fix_pos[b]-1) + "_" + str(j) + " = 1\n"
                    #    else:
                    #        buf = buf + "a" + str(fix_pos[b]-1) + "_" + str(j) + " = 0\n"
                    if (fix_pos!=ROUND):
                        if(j in fix_s_box_next):
                            buf = buf + "a" + str(fix_pos[b]) + "_" + str(j) + " = 1\n"
                        else:
                            buf = buf + "a" + str(fix_pos[b]) + "_" + str(j) + " = 0\n"
            opOuter.write(buf)
            
    if (fix==True):
        for b in range(0,len(fix_bit)):
            buf = ''
            for j in range(0,LELBC):
                if(j in fix_bit[b]):
                    buf = buf + "x" + str(fix_pos[b]) + "_" + str(j) + " = 1\n"
                else:
                    buf = buf + "x" + str(fix_pos[b]) + "_" + str(j) + " = 0\n"
            opOuter.write(buf)
            
    buf = ''
    
    for i in range(0,ROUND):
        buf = ''

        ####### Key scheduling start #####
        ##################################
        for k in range(0,4):
            buf = buf +  "k" + str(i) + "_" + str(124+k)
            if k != 3:
                buf = buf + " + "
            buf = buf + " - A" + str(i) + " >= 0\n"

            for k in range(0,4):
                buf = buf + "k" + str(i) + "_" + str(124+k) + " - A" + str(i) + " <= 0\n"
                
        for k in range(0,21):
            buf = ''
            for l in range(0,9):
                if conv[9*k+l] > 0:
                    if l <= 3:
                        buf = buf + " + " + str(conv[9*k+l]) + " k" + str(i) + "_" + str(124+l)
                    if 4 <= l and l <= 7:
                        buf = buf + " + " + str(conv[9*k+l]) + " w" + str(i) + "_" + str(l-4)
                    if l == 8:
                        buf = buf + " >= -" + str(conv[9*k+l]) + "\n"
                if conv[9*k+l] < 0:
                    if l <= 3:
                        buf = buf + " - " + str(-conv[9*k+l]) + " k" + str(i) + "_" + str(124+l)
                    if 4 <= l and l <= 7:
                        buf = buf + " - " + str(-conv[9*k+l]) + " w" + str(i) + "_" + str(l-4)
                    if l == 8:
                        buf = buf + " >= " + str(-conv[9*k+l]) + "\n"
                if conv[9*k+l] == 0:
                    if l == 8:
                        buf = buf + " >= " + str(conv[9*k+l]) + "\n"
            opOuter.write(buf)

        for j in range(128):
            buf = ''
            if j >= 60 and j <= 63:
                buf = buf + 'v' + str(i) + '_' + str(j) + ' - ' + 'w' + str(i) + '_' + str(j - 60) + " = 0\n"
            else:
                buf = buf + 'v' + str(i) + '_' + str(j) + ' - ' + 'k' + str(i) + '_' + str((j + 64) % 128) + " = 0\n"
            opOuter.write(buf)
    
        for j in range(64):
            buf = ''
            buf = buf + 'k' + str(i + 1) + '_' + str(j) + ' - ' + 'v' + str(i) + '_' + str((j + 9) % 64) + " = 0\n"
            opOuter.write(buf)

        for j in range(64):
            buf = ''
            buf = buf + 'k' + str(i + 1) + '_' + str(j + 64) + ' - ' + 'v' + str(i) + '_' + str(((j + 15) % 64) + 64) + " = 0\n"
            opOuter.write(buf)


        ################### Key scheduling end #####
        ############################################

            
        for j in range(LELBC):
            buf = ''
            if j < LELBC//2:
                opOuter.write(Constraints_XOR( "x" + str(i) + "_" + str(j), "k" + str(i + 1) + "_" + str(j), "u" + str(i) + "_" + str(j)))###########
            else:
                opOuter.write(Constraints_XOR( "u" + str(i) + "_" + str((j + 5) % 32), "x" + str(i) + "_" + str(j), "u" + str(i) + "_" + str(j)))

        buf = ''
        for j in range(0, s_boxes):
            buf = ''
            for k in range(0,4):
                buf = buf +  "u" + str(i) + "_" + str(4*j+k)
                if k != 3:
                    buf = buf + " + "
            buf = buf + " - a" + str(i) + "_" + str(j) + " >= 0\n"

            for k in range(0,4):
                buf = buf + "u" + str(i) + "_" + str(4*j+k) + " - a" + str(i) + "_" + str(j) + " <= 0\n"

            for k in range(0,21):
                for l in range(0,9):
                    if conv[9*k+l] > 0:
                        if l <= 3:
                            buf = buf + " + " + str(conv[9*k+l]) + " u" + str(i) + "_" + str(4*j+l)
                        if 4 <= l and l <= 7:
                            buf = buf + " + " + str(conv[9*k+l]) + " y" + str(i) + "_" + str(4*j+l-4)
                        if l == 8:
                            buf = buf + " >= -" + str(conv[9*k+l]) + "\n"
                    if conv[9*k+l] < 0:
                        if l <= 3:
                            buf = buf + " - " + str(-conv[9*k+l]) + " u" + str(i) + "_" + str(4*j+l)
                        if 4 <= l and l <= 7:
                            buf = buf + " - " + str(-conv[9*k+l]) + " y" + str(i) + "_" + str(4*j+l-4)
                        if l == 8:
                            buf = buf + " >= " + str(-conv[9*k+l]) + "\n"
                    if conv[9*k+l] == 0:
                        if l == 8:
                            buf = buf + " >= " + str(conv[9*k+l]) + "\n"

            opOuter.write(buf)
        
        for j in range(LELBC):
            buf = ''
            if j < LELBC//2:
                opOuter.write(Constraints_XOR( "y" + str(i) + "_" + str(j), "y" + str(i) + "_" + str((j + 5) % 32 + 32), "x" + str(i + 1) + "_" + str(j)))
            else:
                opOuter.write(Constraints_XOR( "y" + str(i) + "_" + str(j), "k" + str(i + 1) + "_" + str(j), "x" + str(i + 1) + "_" + str(j)))###########
        
    buf = ''
    if len(FixList) == 0:
        for i in range(0,LELBC):
            buf = buf + "x0_" + str(i)
            if i != (LELBC-1):
                buf = buf + " + "
            if i == (LELBC-1):
                buf = buf + " >= 1\n"
        for i in BanList:
            for j in range(0,len(i)):
                buf = buf + "a" + str(i[j][0]) + "_" + str(i[j][1])
                if j != len(i)-1:
                    buf = buf + " + "
                else:
                    buf = buf + " <= " + str(len(i)-1) + '\n'
        buf = buf + " \n "
    else:    
        fl = []
        for i in range(0,LELBC):
            fl.append(i)
            if fl in FixList:
                buf = buf + "x0_" + str(i) + " = 1\n"
            else:
                buf = buf + "x0_" + str(i) + " = 0\n"
            fl.pop()
        buf = buf + " \n "
    opOuter.write(buf)
   
    buf = ''
    for i in range(0,ROUND):
        buf = ''
        for j in range(0,s_boxes):
            buf = buf + "a" + str(i) + "_" + str(j)
            if j != (s_boxes-1):
                buf = buf + " + "
            if j == (s_boxes-1):
                buf = buf + " <= "+str(max_sbox_round)+"\n\n"
        opOuter.write(buf)
        
    buf = ''
    for i in range(0,ROUND):
        for j in range(0,s_boxes):
            buf = buf + "a" + str(i) + "_" + str(j)
            if i != ROUND-1 or j != (s_boxes-1):
                buf = buf + " + "
            else:
                buf = buf + " >= "
    
    buf = buf + str(min_sbox) + "\n\n"
    
    opOuter.write(buf)

    buf = ''###########
    for i in range(128):###########
            buf = buf + "k0_" + str(i)###########
            if i != 127:###########
                buf = buf + " + "###########
            if i == 127:###########
                buf = buf + " >= 1\n"###########
    opOuter.write(buf)###########
                
    opOuter.write("Binary\n")
    buf = ''
    for i in range(0,ROUND):
        buf = ''
        for j in range(0,s_boxes):
            buf = buf + "a" + str(i) + "_" + str(j) + "\n"
        opOuter.write(buf)

    for i in range(0,ROUND):
        buf = ''
        buf = buf + "A" + str(i) + "\n"
        opOuter.write(buf)
        
    for i in range(0,ROUND):
        buf = ''
        for j in range(128):###########
            buf = buf + 'k' + str(i) + '_' + str(j) + "\n"###########
        for j in range(4):###########
            buf = buf + 'w' + str(i) + '_' + str(j) + "\n"###########
        for j in range(128):###########
            buf = buf + 'v' + str(i) + '_' + str(j) + "\n"###########
        for j in range(0,LELBC):
            buf = buf + "x" + str(i) + "_" + str(j) + "\n"
            buf = buf + "u" + str(i) + "_" + str(j) + "\n"
            buf = buf + "y" + str(i) + "_" + str(j) + "\n"
        opOuter.write(buf)

    buf = ''###########
    for j in range(128):###########
        buf = buf + 'k' + str(ROUND) + '_' + str(j) + "\n"###########
    opOuter.write(buf)###########
    
    buf = ''
    for j in range(0,LELBC):
        buf = buf + "x" + str(ROUND) + "_" + str(j) + "\n"
    opOuter.write(buf)
    opOuter.close()

def PrintInner(FixList, SolveList, SolveList1):
    opInner = open("Inner" +"_LELBC_" + str(LELBC) + "_" + str(ROUND)+"_Possible" +".lp","w+")
    opInner.write("Minimize\n")
    buf = ''
    
    for i in range(0,len(SolveList)):
        buf = buf + "2 z" + str(SolveList[i][0]) + "_" + str(SolveList[i][1]) + "_0 + 3 z" + str(SolveList[i][0]) + "_" + str(SolveList[i][1]) + "_1"
        if i != len(SolveList)-1:
          buf = buf + " + "
        #else:

    for i in range(0,len(SolveList1)):
        buf = buf + " + " + "2 p" + str(SolveList1[i][0]) + "_" + "_0 + 3 p" + str(SolveList1[i][0]) + "_" + "_1"
        
    buf = buf + "\n"
    opInner.write(buf)
    opInner.write("Subject to\n")
    
    if (fix==True):
        for b in range(0,len(fix_bit)):
            buf = ''
            for j in range(0,LELBC):
                if(j in fix_bit[b]):
                    buf = buf + "x" + str(fix_pos[b]) + "_" + str(j) + " = 1\n"
                else:
                    buf = buf + "x" + str(fix_pos[b]) + "_" + str(j) + " = 0\n"
            opInner.write(buf)
    
            
    buf = ''

    for i in range(ROUND):
        buf = ''

        ####### Key scheduling start #####
        ##################################
        for j in range(0,len(SolveList1)):
            buf = ''
            if (SolveList1[j][0] == i):
                for k in range(0,4):
                    buf = buf + "4 k" + str(SolveList1[j][0]) + "_" + str(124 + k)
                    if k != 3:
                        buf = buf + " + "
                for k in range(0,4):
                    buf = buf + " - 1 w" + str(SolveList1[j][0]) + "_" + str(k)
                buf = buf + " >= 0\n"
                for k in range(0,4):
                    buf = buf + "4 w" + str(SolveList1[j][0]) + "_" + str(k)
                    if k != 3:
                        buf = buf + " + "
                for k in range(0,4):
                    buf = buf + " - 1 k" + str(SolveList1[j][0]) + "_" + str(124 + k)
                buf = buf + " >= 0\n\n"
                opInner.write(buf)
                
                for k in range(0,21):
                    buf = ''
                    for l in range(0,11):
                        if conv[11*k+l] > 0:
                            if l <= 3:
                                buf = buf + " + " + str(conv[11*k+l]) + " k" + str(SolveList1[j][0]) + "_" + str(124+l)
                            if 4 <= l and l <= 7:
                                buf = buf + " + " + str(conv[11*k+l]) + " w" + str(SolveList1[j][0]) + "_" + str(l-4)
                            if 8 <=l and l <= 9:
                                buf = buf + " + " + str(convpbl[11*k+l]) + " p" + str(SolveList1[j][0]) + "_" + str(l-8)
                            if l == 10:
                                buf = buf + " >= -" + str(conv[11*k+l]) + "\n"
                        if conv[11*k+l] < 0:
                            if l <= 3:
                                buf = buf + " - " + str(-conv[11*k+l]) + " k" + str(SolveList1[j][0]) + "_" + str(124+l)
                            if 4 <= l and l <= 7:
                                buf = buf + " - " + str(-conv[11*k+l]) + " w" + str(SolveList1[j][0]) + "_" + str(l-4)
                            if 8 <=l and l <= 9:
                                buf = buf + " + " + str(-convpbl[11*k+l]) + " p" + str(SolveList1[j][0]) + "_" + str(l-8)
                            if l == 10:
                                buf = buf + " >= " + str(-conv[11*k+l]) + "\n"
                        if conv[11*k+l] == 0:
                            if l == 10:
                                buf = buf + " >= " + str(conv[11*k+l]) + "\n"
                    opInner.write(buf)

        buf = ''
        sl = []
        sl.append(i)
        if sl not in SolveList1:
            for k in range(0,4):
                buf = buf + "k" + str(i) + "_" + str(124+k) + " = 0\n"
                buf = buf + "w" + str(i) + "_" + str(k) + " = 0\n"
            opInner.write(buf)

        for j in range(128):
            buf = ''
            if j >= 60 and j <= 63:
                buf = buf + 'v' + str(i) + '_' + str(j) + ' - ' + 'w' + str(i) + '_' + str(j - 60) + " = 0\n"
            else:
                buf = buf + 'v' + str(i) + '_' + str(j) + ' - ' + 'k' + str(i) + '_' + str((j + 64) % 128) + " = 0\n"
            opInner.write(buf)
    
        for j in range(64):
            buf = ''
            buf = buf + 'k' + str(i + 1) + '_' + str(j) + ' - ' + 'v' + str(i) + '_' + str((j + 9) % 64) + " = 0\n"
            opInner.write(buf)

        for j in range(64):
            buf = ''
            buf = buf + 'k' + str(i + 1) + '_' + str(j + 64) + ' - ' + 'v' + str(i) + '_' + str(((j + 15) % 64) + 64) + " = 0\n"
            opInner.write(buf)


        ################### Key scheduling end #####
        ############################################
  

        for j in range(LELBC):
            buf = ''
            if j < LELBC//2:
                opInner.write(Constraints_XOR( "x" + str(i) + "_" + str(j), "k" + str(i + 1) + "_" + str(j), "u" + str(i) + "_" + str(j))) #################
            else:
                opInner.write(Constraints_XOR( "u" + str(i) + "_" + str((j + 5) % 32), "x" + str(i) + "_" + str(j), "u" + str(i) + "_" + str(j)))
        
        for j in range(0,len(SolveList)):
            buf = ''
            if (SolveList[j][0] == i):
                for k in range(0,4):
                    buf = buf + "4 u" + str(SolveList[j][0]) + "_" + str(4*SolveList[j][1]+k)
                    if k != 3:
                        buf = buf + " + "
                for k in range(0,4):
                    buf = buf + " - 1 y" + str(SolveList[j][0]) + "_" + str(4*SolveList[j][1]+k)
                buf = buf + " >= 0\n"
                for k in range(0,4):
                    buf = buf + "4 y" + str(SolveList[j][0]) + "_" + str(4*SolveList[j][1]+k)
                    if k != 3:
                        buf = buf + " + "
                for k in range(0,4):
                    buf = buf + " - 1 u" + str(SolveList[j][0]) + "_" + str(4*SolveList[j][1]+k)
                buf = buf + " >= 0\n\n"
                opInner.write(buf)

                buf = ''
                for k in range(0,21):
                    for l in range(0,11):
                        if convpbl[11*k+l] > 0:
                            if l <= 3:
                                buf = buf + " + " + str(convpbl[11*k+l]) + " u" + str(SolveList[j][0]) + "_" + str(4*SolveList[j][1]+l)
                            if 4 <= l and l <= 7:
                                buf = buf + " + " + str(convpbl[11*k+l]) + " y" + str(SolveList[j][0]) + "_" + str(4*SolveList[j][1]+l-4)
                            if 8 <=l and l <= 9:
                                buf = buf + " + " + str(convpbl[11*k+l]) + " z" + str(SolveList[j][0]) + "_" + str(SolveList[j][1]) + "_" + str(l-8)
                            if l == 10:    
                                buf = buf + " >= -" + str(convpbl[11*k+l]) + "\n"
                        if convpbl[11*k+l] < 0:
                            if l <= 3:
                                buf = buf + " - " + str(-convpbl[11*k+l]) + " u" + str(SolveList[j][0]) + "_" + str(4*SolveList[j][1]+l)
                            if 4 <= l and l <= 7:
                                buf = buf + " - " + str(-convpbl[11*k+l]) + " y" + str(SolveList[j][0]) + "_" + str(4*SolveList[j][1]+l-4)
                            if 8 <= l and l <= 9:
                                buf = buf + " - " + str(-convpbl[11*k+l]) + " z" + str(SolveList[j][0]) + "_" + str(SolveList[j][1]) + "_" + str(l-8)
                            if l == 10:
                                buf = buf + " >= " + str(-convpbl[11*k+l]) + "\n"
                        if convpbl[11*k+l] == 0:
                            if l == 10:
                                buf = buf + " >= " + str(convpbl[11*k+l]) + "\n"
                buf = buf + " \n "
                opInner.write(buf)
        
        buf = ''
        sl = []
        sl.append(i)
        for j in range(0,s_boxes):
            sl.append(j)

            if sl not in SolveList:
                for k in range(0,4):
                    buf = buf + "u" + str(i) + "_" + str(4*j+k) + " = 0\n"
                    buf = buf + "y" + str(i) + "_" + str(4*j+k) + " = 0\n"
            sl.pop()
        buf = buf + " \n "
        opInner.write(buf)
        
        for j in range(LELBC):
            buf = ''
            if j < LELBC//2:
                opInner.write(Constraints_XOR( "y" + str(i) + "_" + str(j), "y" + str(i) + "_" + str((j + 5) % 32 + 32), "x" + str(i + 1) + "_" + str(j)))
            else:
                opInner.write(Constraints_XOR( "y" + str(i) + "_" + str(j), "k" + str(i + 1) + "_" + str(j), "x" + str(i + 1) + "_" + str(j)))########################
    

    if len(FixList) == 0:
        for j in SolveList:
            if j[0] == 0:
                buf = buf + "x0_" + str(4*j[1]) + " + x0_" + str(4*j[1]+1) + " + x0_" + str(4*j[1]+2) + " + x0_" + str(4*j[1]+3)
                buf = buf + " >= 1\n"
        buf = buf + " \n "
        opInner.write(buf)
    else:
        fl = []
        for j in range(0,LELBC):
            fl.append(j)
            if fl in FixList:
                buf = buf + "x0_" + str(j) + " = 1\n"
            else:
                buf = buf + "x0_" + str(j) + " = 0\n"
            fl.pop()
        buf = buf + " \n "
        opInner.write(buf)


     
    buf = ''###########
    for i in range(128):###########
            buf = buf + "k0_" + str(i)###########
            if i != 127:###########
                buf = buf + " + "###########
            if i == 127:###########
                buf = buf + " >= 1\n"###########
    opInner.write(buf)###########


    
    buf = ''    
    opInner.write("Binary\n")
    buf = ''
    for i in range(0,ROUND):
        buf = ''
        for j in range(128):###########
            buf = buf + 'k' + str(i) + '_' + str(j) + "\n"###########
        for j in range(4):###########
            buf = buf + 'w' + str(i) + '_' + str(j) + "\n"###########
        for j in range(128):###########
            buf = buf + 'v' + str(i) + '_' + str(j) + "\n"###########
        for j in range(0,LELBC):
            buf = buf + "x" + str(i) + "_" + str(j) + "\n"
            buf = buf + "u" + str(i) + "_" + str(j) + "\n"
            buf = buf + "y" + str(i) + "_" + str(j) + "\n"
        opInner.write(buf)         

    buf = ''###########
    for j in range(128):###########
        buf = buf + 'k' + str(ROUND) + '_' + str(j) + "\n"###########
    opInner.write(buf)###########

    buf = ''
    for j in range(0,LELBC):
        buf = buf + "x" + str(ROUND) + "_" + str(j) + "\n"
    opInner.write(buf)

    buf = ''
    for i in range(0,len(SolveList)):
        buf = buf + "z" + str(SolveList[i][0]) + "_" + str(SolveList[i][1]) + "_0\n"
        buf = buf + "z" + str(SolveList[i][0]) + "_" + str(SolveList[i][1]) + "_1\n"
        opInner.write(buf)
        
    buf = ''
    for i in range(0,len(SolveList1)):
        buf = buf + "p" + str(SolveList1[i][0]) + "_" + "_0\n"
        buf = buf + "p" + str(SolveList1[i][0]) + "_" + "_1\n"
        opInner.write(buf)
        buf = ''
    opInner.close()

def strtoint(s):
    reg = 0
    s1 = ''
    s2 = ''
    res = 0
    result = []
    for i in range(0,len(s)):
        if s[i] == '_':
            reg = 1
        if s[i] >= '0' and s[i]<= '9':
            if reg == 0:
                s1 = s1 + s[i]
            if reg == 1:
                s2 = s2 + s[i]

    result.append(int(s1))
    result.append(int(s2))    
    return result

def strtoint1(s):
    s1 = ''
    result = []
    for i in range(0,len(s)):
        if s[i] >= '0' and s[i]<= '9':
                s1 = s1 + s[i]

    result.append(int(s1))  
    return result

def strtoint2(s):
    reg = 0
    s1 = ''
    s2 = ''
    res = 0
    result = []
    for i in range(0,len(s)):
        if s[i] == '_':
            reg = 1
        if s[i] >= '0' and s[i]<= '9':
            if reg == 0:
                s1 = s1 + s[i]
            if reg == 1:
                s2 = s2 + s[i]
        
    #result.append(string.atoi(s1))
    result.append(string.atoi(s2))
    return result

def print_binary_data(data,key_data,prob,key_prob):
##    for i in range(0,len(data),4):
##        print(data[i:i+4],end='  ');
##    print(":: Hex => ",end='');
    print("Input difference: ", end = ' ')
    for i in range(0,len(data),16):
        print(hex(int(data[i:i+16],2))[2:].zfill(4),end=' ')
    print(" :: Probability => 2^{-"+str(prob)+"}", end = ' ')
##    print(" :: ",end='0x')
    print(" :: Key difference: ", end = ' ')
    for i in range(0,len(key_data),16):
        print(hex(int(key_data[i:i+16],2))[2:].zfill(4),end=' ')
    print(" :: Probability => 2^{-"+str(key_prob)+"}")
    print("");

def print_binary_data_1(data):
##    for i in range(0,len(data),4):
##        print(data[i:i+4],end='  ');
##    print(":: Hex => ",end='');
    print("S-boxes input difference: ", end = ' ')
    for i in range(0,len(data),16):
        print(hex(int(data[i:i+16],2))[2:].zfill(4),end=' ')
    print("\n")   
##    print(" :: ",end='0x')
##    for i in range(0,len(data),16):
##        print(hex(int(data[i:i+16],2))[2:].zfill(4),end='')
##    print("");

def print_binary_data_2(data):
    print("S-boxes output difference: ", end = ' ')
    for i in range(0,len(data),16):
        print(hex(int(data[i:i+16],2))[2:].zfill(4),end=' ')
    print("\n")
    
def shift(n,d,N):
    return ((n << d) % (1 << N) | (n >> (N-d) ))


filename = "Result" +"_LELBC_" + str(LELBC) + "_" + str(ROUND) + "_Possible" + ".txt"
opResult = open(filename,'w+')

def possible_differential():
    count = 1
    fsl = []
    fsl1 = []
    fslstring = []
    fslstring1 = []
    ftlstring = []
    BanList = []
    bl = []
    bl1 = []
    FixList = []    
    while (count<=int(sys.argv[6])):
        PrintOuter(FixList,BanList)
        ###########################GUROBI#################################
        if(GUROBI_EXISTS == True):
            o = read("Outer" +"_LELBC_" + str(LELBC) + "_" + str(ROUND) +".lp")
            o.optimize()
            obj = o.getObjective()
        ##########################CPLEX####################################
        if(CPLEX_EXISTS == True):
            mr = ModelReader()
            o = mr.read("Outer" +"_LELBC_" + str(LELBC) + "_" + str(ROUND) +".lp")
            o_sol  = o.solve(log_output=True)
            
        ###########################GUROBI#################################
        if(GUROBI_EXISTS == True):
            o_obj = obj.getValue()
        ##################CPELX###############
        if(CPLEX_EXISTS == True):
            o_obj = o_sol.get_objective_value()
        if o_obj < (min_sbox + 64) :
            b1=[]
            fsl = []
            fslstring = []
            ###########################GUROBI#############################
            if(GUROBI_EXISTS == True):
                for v in o.getVars():
                    if v.x == 1 and v.VarName[0] == 'a':
                        fslstring.append(v.VarName)

            if(GUROBI_EXISTS == True):
                for v in o.getVars():
                    if v.x == 1 and v.VarName[0] == 'A':
                        fslstring1.append(v.VarName)
            ###########CPLEX###########################
            if(CPLEX_EXISTS == True):
                for v in o_sol.iter_variables():
                    if ('a' in str(v)):
                        fslstring.append(str(v))
            for f in fslstring:
                fsl.append(strtoint(f))
            for f in fslstring1:
                fsl1.append(strtoint1(f))
            #if count == 1:
            for f in fslstring:
                bl.append(strtoint(f))
            BanList.append(bl)
            for f in fslstring1:
                bl1.append(strtoint1(f))
            BanList.append(bl1)
            print("*\n*\n*\n*\n")
            print(BanList)
            print("*\n*\n*\n*\n")
            
            print(fsl, fsl1)
            PrintInner(FixList,fsl, fsl1)
            
            FixList = []
            ###########################GUROBI#################################
            if(GUROBI_EXISTS == True):
                i = read("Inner" +"_LELBC_" + str(LELBC) + "_" + str(ROUND) + "_Possible" +".lp")
                i.optimize()
                i_obj = i.getObjective().getValue()
            ###################CPLEX#############################
            if(CPLEX_EXISTS == True):
                i = mr.read("Inner" +"_LELBC_" + str(LELBC) + "_" + str(ROUND) + "_Possible" +".lp")
                i_sol  = i.solve(log_output=True)
                i_obj = i_sol.get_objective_value()
            print("Number of Active S-boxes: " + str(o_obj))  
            print("FOUND Optimal Probability: " + str(i_obj))
            #if i_obj > IVLBC:
            #    break
            buf = ''
            buf = buf + str(fsl) + " " + str(i_obj) + "\n"
            
            ftlstring = []
            ###########################GUROBI#################################
            if(GUROBI_EXISTS == True):
                for v in i.getVars():
                    if v.x == 1:
                        buf = buf + v.VarName + " "
                    if v.x == 1 and v.VarName[0] == 'x' and v.VarName[1] == str(ROUND-2):
                        ftlstring.append(v.VarName)
            ############CPLEX##################################################
            if(CPLEX_EXISTS == True):
                for v in i_sol.iter_variables():
                    buf = buf + str(v) + " "
                    #if(fix==True):
                    if (('x' in str(v)) and (str(v).split("_")[0][1:] == str(ROUND)) ):
                            ftlstring.append(str(v))
            if(fix==True):
                for f in ftlstring:
                    FixList.append(strtoint2(f))
            
            buf = buf + "\n"
            opResult.write(buf)
            opResult.flush()
            round_bit_arr  = []
            round_bit_arr_u = []
            round_bit_arr_y = []
            prob_arr = []
            key_round_bit_arr = []
            key_prob_arr = []
            ###########################GUROBI#################################
            if(GUROBI_EXISTS == True):
                for v in i.getVars():
                    if v.x == 1:
                        var = v.VarName
                        if (var[0] == 'x'):
                            round_bit_arr += [strtoint(var)]
                        elif (var[0] == 'u'):
                            round_bit_arr_u += [strtoint(var)]
                        elif (var[0] == 'y'):
                            round_bit_arr_y += [strtoint(var)]
                        elif (var[0] == 'z'):
                            new_var = var.split("_");
                            prob_arr += [strtoint("_".join([new_var[0],new_var[2]]))]
                        elif (var[0] == 'k'):
                            key_round_bit_arr += [strtoint(var)]
                        elif (var[0] == 'p'):
                            key_prob_arr += [strtoint(var)]

            ############CPLEX################
            if(CPLEX_EXISTS == True):
                for v in i_sol.iter_variables():
                        var = str(v)
                        if (var[0] == 'x'):
                            round_bit_arr += [strtoint(var)]
                        elif (var[0] == 'u'):
                            round_bit_arr_u += [strtoint(var)]
                        elif (var[0] == 'y'):
                            round_bit_arr_y += [strtoint(var)]
                        elif (var[0] == 'z'):
                            new_var = var.split("_");
                            prob_arr += [strtoint("_".join([new_var[0],new_var[2]]))]
                        elif (var[0] == 'k'):
                            key_round_bit_arr += [strtoint(var)]
                        elif (var[0] == 'p'):
                            key_prob_arr += [strtoint(var)]
    
            #no_of_rounds = max([_[0] for _ in round_bit_arr])
##            print("Active bits in input differences in all rounds", round_bit_arr,"no_of_rounds=",no_of_rounds, "\n")
##            print("Prob_arr = ", prob_arr, "\n")
            #print("Differential Probability for " + str(no_of_rounds) + " rounds of LELBC_"+str(LELBC)+" is 2^{-" + str(i_obj) + "}")
            print("Differential Probability for " + str(ROUND) + " rounds of LELBC_"+str(LELBC)+" is 2^{-" + str(i_obj) + "}")
            for r in range(0,ROUND+1):
                print("The input difference of the round "+ str(r+1)+" and corresponding key difference are: ");
                diff_bits = list("0"*LELBC);
                diff_bits_u = list("0"*LELBC);
                diff_bits_y = list("0"*LELBC);
                key_diff_bits = list("0"*128)
                active_bits = [a[1] for a in round_bit_arr if a[0]==r]
                active_bits_u = [a[1] for a in round_bit_arr_u if a[0]==r]
                active_bits_y = [a[1] for a in round_bit_arr_y if a[0]==r]
                key_active_bits = [a[1] for a in key_round_bit_arr if a[0]==r]
                # for bit in active_bits:
                #     diff_bits[len(diff_bits)-1-bit] = "1";
                # for bit in active_bits_y:
                #     diff_bits_y[len(diff_bits_y)-1-bit] = "1";
                # for bit in active_bits_u:
                #     diff_bits_u[len(diff_bits_u)-1-bit] = "1";
                for bit in active_bits:
                    diff_bits[bit] = "1";
                for bit in active_bits_u:
                    diff_bits_u[bit] = "1";
                for bit in active_bits_y:
                    diff_bits_y[bit] = "1";
                for bit in key_active_bits:
                    key_diff_bits[bit] = "1";
                probability = 0;
                key_probability = 0;
                if (r>0):
                    round_prob  = [a[1] for a in prob_arr if a[0]==r-1]
                    key_round_prob  = [a[1] for a in key_prob_arr if a[0]==r-1]
                    for prob in round_prob:
                        if (prob==1):
                            probability += 3;
                        elif (prob==0):
                            probability += 2;
                    for prob in key_round_prob:
                        if (prob==1):
                            key_probability += 3;
                        elif (prob==0):
                            key_probability += 2;
                print_binary_data("".join(diff_bits),"".join(key_diff_bits),probability,key_probability);
                print("\n")
                if r!=ROUND:
                    print_binary_data_1("".join(diff_bits_u));
                    print_binary_data_2("".join(diff_bits_y));
                    print("\n")
            count = count + 1     
        else:
            continue

possible_differential()
    
opResult.close()
