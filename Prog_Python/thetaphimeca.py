import serial
import serial.tools.list_ports
import time
import binascii
from itertools import islice
import csv
import pandas as pd 
import matplotlib.pyplot as plt

import math

######

start = time.time()

def split_n_chunks(s, words_per_chunk):
    s_list = s.split(',')
    pos = 0
    while pos < len(s_list):
        yield s_list[pos:pos+words_per_chunk]
        pos += words_per_chunk

def divide(lst, n):
    p = len(lst) // n
    if len(lst)-p > 0:
        return [lst[:p]] + divide(lst[p:], n-1)
    else:
        return [lst]

hexadecimal_string_Polar = "FE 84 00 02 00 00" #Set polar
byte_array_Polar = bytearray.fromhex(hexadecimal_string_Polar)


hexadecimal_string_ON = "FE 80 00 00 " #START distance measurement
byte_array_ON = bytearray.fromhex(hexadecimal_string_ON)

hexadecimal_string_Result = "FE 82 00 01 00 " #Get Result 
byte_array_Result = bytearray.fromhex(hexadecimal_string_Result)

hexadecimal_string_OFF = "FE 81 00 00"  # STOP distance measurement
byte_array_OFF = bytearray.fromhex(hexadecimal_string_OFF)


hexadecimal_string_TP = "FE 94 00 00"  # Get TP
byte_array_TP = bytearray.fromhex(hexadecimal_string_TP)

serialPort = serial.Serial('COM4', baudrate=115200)   #Connecting to the camera 

serialPort.write(byte_array_Polar)
print('\nEn mode Polar')

time.sleep(0.01)
serialPort.write(byte_array_ON)
print('Démarrage caméra')

#############
serialPort.write(byte_array_Result)
print('Get Result : ')

time.sleep(0.001)

data = serialPort.read(153618) 

time.sleep(0.001)

data_list = binascii.hexlify(data, ',')
data_list = data_list.decode("utf-8")
Tableau = list(split_n_chunks(data_list, 2))

i = 0
while i<9:
  del Tableau[0]
  i = i + 1

print("nombre de pixel trouvés : ", len(Tableau), "\n")

Tableau.reverse()   


Listededistance = [0]*76800

y=0
while y<76799:
  Input = Tableau[y]
  length_to_split = [len(Input)//2]*2
  lst = iter(Input)
  Output = [list(islice(lst, elem))
           for elem in length_to_split]
  String_1 = " ".join(Output[0])
  String_2 = " ".join(Output[1])

  String_f = String_2 + String_1
  Distance = int(String_f, 16)

  Listededistance[y] = Distance
  y = y + 1 

Liste_Finale = divide(Listededistance, 240)

######

serialPort.write(byte_array_OFF)
serialPort.write(byte_array_TP)
print('Get Angles')

time.sleep(0.001)

dataTheta = serialPort.read(153612) 

data_list = binascii.hexlify(dataTheta, ',')
data_list = data_list.decode("utf-8")
Tableau = list(split_n_chunks(data_list, 2))

i = 0
while i<6:
  del Tableau[0]
  i = i + 1

Tableau.reverse()

ListeTheta = [0]*76800

y=0
while y<76799:
  Input = Tableau[y]
  length_to_split = [len(Input)//2]*2
  lst = iter(Input)
  Output = [list(islice(lst, elem))
           for elem in length_to_split]
  String_1 = " ".join(Output[0])
  String_2 = " ".join(Output[1])

  String_f = String_2 + String_1
  Theta = 90*int(String_f, 16)/4096
  thetar = math.radians(Theta)


  ListeTheta[y] = thetar
  y = y + 1 

Liste_FinaleT = divide(ListeTheta, 240)

######

dataPhi = serialPort.read(153600) 


data_list = binascii.hexlify(dataTheta, ',')
data_list = data_list.decode("utf-8")
Tableau = list(split_n_chunks(data_list, 2))
Tableau.reverse()


ListePhi = [0]*76800

y=0
while y<76799:
  Input = Tableau[y]
  length_to_split = [len(Input)//2]*2
  lst = iter(Input)
  Output = [list(islice(lst, elem))
           for elem in length_to_split]
  String_1 = " ".join(Output[0])
  String_2 = " ".join(Output[1])

  String_f = String_2 + String_1
  Phi = 360*int(String_f, 16)/16384
  phir = math.radians(Phi)

  ListePhi[y] = Phi
  y = y + 1 


Liste_FinaleP = divide(ListePhi, 240)

########

Listez=[0]*76800

y=0
while y<76799:
    Listez[y] = Listededistance[y] * math.cos(ListeTheta[y])
    y = y + 1

Liste_FinaleZ = divide(Listez, 240)

#######

Listey=[0]*76800

y=0
while y<76799:
    Listey[y] = Listededistance[y] * math.sin(ListeTheta[y])*math.sin(ListePhi[y])/math.cos(ListePhi[y])
    y = y + 1

Liste_FinaleY = divide(Listey, 240)

#######

Listex=[0]*76800


y=0
while y<76799:
    Listex[y] = Listededistance[y] * math.sin(ListeTheta[y])
    y = y + 1

Liste_FinaleX = divide(Listex, 240)



with open('C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/donnéescapturées.csv', 'w') as f:

    write = csv.writer(f)

    j=0
    while j < 240:  
      write.writerow(Liste_Finale[j])
      j = j + 1

with open('C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/Théta.csv', 'w') as f:

    write = csv.writer(f)

    j=0
    while j < 240:  
      write.writerow(Liste_FinaleT[j])
      j = j + 1


with open('C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/Phi.csv', 'w') as f:

    write = csv.writer(f)

    j=0
    while j < 240:  
      write.writerow(Liste_FinaleP[j])
      j = j + 1

#########################

with open('C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/Z.csv', 'w') as f:
      
    write = csv.writer(f)

    j=0
    while j < 240:  
      write.writerow(Liste_FinaleZ[j])
      j = j + 1

with open('C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/Y.csv', 'w') as f:
      
    write = csv.writer(f)

    j=0
    while j < 240:  
      write.writerow(Liste_FinaleY[j])
      j = j + 1

with open('C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/X.csv', 'w') as f:
      

    write = csv.writer(f)
    j=0
    while j < 240:  
      write.writerow(Liste_FinaleX[j])
      j = j + 1

fig = plt.figure()

ax = plt.axes(projection='3d')

# Data for a three-dimensional line
z = pd.read_csv("C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/Z.csv", sep=',', engine='python')

y = pd.read_csv("C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/Y.csv", sep=',',engine='python')

x = pd.read_csv("C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/X.csv", sep=',',engine='python')

ax.scatter(x, y, z)

plt.show()

end = time.monotonic()
elapsed= end - start
elapsed = elapsed + 3
print(f'Temps d\'exécution : {elapsed:.4} ms \n')

serialPort.write(byte_array_OFF)

time.sleep(1)

data = serialPort.read_all() 
data = binascii.hexlify(data)
print("Fin d'enregistrement : " , data, "\n")

serialPort.__exit__('COM4')  # COM4 empty to avoid issues