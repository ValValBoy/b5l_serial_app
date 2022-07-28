import serial
import serial.tools.list_ports
import time
import binascii
from itertools import islice
import csv
import pandas as pd 
import matplotlib.pyplot as plt

##

start = time.monotonic()

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

##

hexadecimal_string_Polar = "FE 84 00 02 00 00" #Set polar
byte_array_Polar = bytearray.fromhex(hexadecimal_string_Polar)

hexadecimal_string_ON = "FE 80 00 00 " #START distance measurement
byte_array_ON = bytearray.fromhex(hexadecimal_string_ON)

hexadecimal_string_Result = "FE 82 00 01 00 " #Get Result 
byte_array_Result = bytearray.fromhex(hexadecimal_string_Result)

hexadecimal_string_OFF = "FE 81 00 00"  # STOP distance measurement
byte_array_OFF = bytearray.fromhex(hexadecimal_string_OFF)

serialPort = serial.Serial('COM4', baudrate=115200)   #Connecting to the camera 

serialPort.write(byte_array_Polar)
print('\n En mode Polar')

serialPort.write(byte_array_ON)
print('\n Démarrage caméra')

time.sleep(0.001)


## Possible to have a real time capture ##

serialPort.write(byte_array_Result)
print('       Get Result : ')
 
time.sleep(0.001)

data = serialPort.read(153618) 

time.sleep(0.001)

#TEST DATA#
#data_write = binascii.hexlify(data, ' ')
#data_write= data_write.decode("utf-8")
#out=sys.stdout
#out.write(data_write)

data_list = binascii.hexlify(data, ',')
data_list = data_list.decode("utf-8")
Tableau = list(split_n_chunks(data_list, 2))

print("\n Good start :", Tableau[0], Tableau[1], Tableau[2], Tableau[3], Tableau[4], Tableau[5], Tableau[6], Tableau[7], Tableau[8], "\n")

i = 0
while i<9:
  del Tableau[0]
  i = i + 1

print("nombre de pixel trouvés : ", len(Tableau), "\n")

Tableau.reverse()   

## 2D 76800 pixels ##

Listededistance = [0]*76799

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

## 2D 768 pixels##

liste32x240D = [0]*32*240

k=0
j=0

while j<239:

    liste32x240 = divide(Liste_Finale[j], 32)

    i=0
    while i < 32:
        
        liste32x240D[k]=sum(liste32x240[i])/len(liste32x240[i])
        i = i + 1
        k=k+1
    j=j+1

k=0
j=0
liste32x24D = [0]*32*24

while j<7680:

    i=0
    while i<32:
        liste32x24D[k] = (liste32x240D[0+i+j]+liste32x240D[32+i+j]+liste32x240D[64+i+j]+liste32x240D[96+i+j]+liste32x240D[128+i+j]+liste32x240D[160+i+j]+liste32x240D[192+i+j]+liste32x240D[224+i+j]+liste32x240D[256+i+j]+liste32x240D[288+i+j])/10
        i=i+1
        k=k+1
    j = j + 320

Liste_1010 = divide(liste32x24D, 24)

## 2D MIN VALUE ##

Valeur_min = [0]*32
i=0

while i < 32:
    
    listepartielle = [liste32x24D[192+i], liste32x24D[224+i], liste32x24D[256+i], liste32x24D[288+i], liste32x24D[320+i], liste32x24D[352+i], liste32x24D[384+i], liste32x24D[416+i], liste32x24D[448+i], liste32x24D[480+i], liste32x24D[512+i], liste32x24D[544+i]]
      
    Valeur_min[i] = min(listepartielle)
    i=i+1

Liste_Min = divide(Valeur_min, 32)

## END ##

end = time.monotonic()
elapsed= end - start
print(f'Temps d\'exécution : {elapsed:.4} ms \n')

serialPort.write(byte_array_OFF)

time.sleep(1)

data = serialPort.read_all() 
data = binascii.hexlify(data)
print("Fin d'enregistrement : " , data, "\n")

## COM4 empty to avoid issues ##

serialPort.__exit__('COM4')  

with open('C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/donnéescapturées.csv', 'w') as f:
      
    write = csv.writer(f)

    j=0
    while j < 240:  
        write.writerow(Liste_Finale[j])
        j = j + 1

df = pd.read_csv("C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/donnéescapturées.csv", skiprows=180, skipfooter=180, sep=',', na_values=['30000'], engine='python')

pd.set_option('display.max_columns', None)

pd.set_option('display.max_rows', 5)

df = df.T

plt.plot(df,"r+") 
plt.axis([0, 320, 0, 5000])
plt.ylabel('longueur en millimètres')
plt.xlabel('vue en large')
plt.show()

with open('C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/donnéescapturées1010.csv', 'w') as f:
    write = csv.writer(f)
    j=0
    while j < 24:  
        write.writerow(Liste_1010[j])
        j = j + 1

df = pd.read_csv("C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/donnéescapturées1010.csv",skiprows=16, skipfooter=16, sep=',', na_values=['30000'], engine='python')

pd.set_option('display.max_columns', None)

pd.set_option('display.max_rows', 5)

df = df.T

plt.plot(df,"bo") 
plt.axis([0, 32, 0, 5000])
plt.ylabel('longueur en millimètres')
plt.xlabel('vue en large')
plt.show()

with open('C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/donnéescapturéesMin.csv', 'w') as f:
      
    write = csv.writer(f)

    j=0
    while j < 32:  
        write.writerow(Liste_Min[j])
        j = j + 1

df = pd.read_csv("C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/donnéescapturéesMin.csv", sep=',', na_values=['30000'], engine='python')

pd.set_option('display.max_columns', None)

pd.set_option('display.max_rows', 5)

plt.plot(df,"bo") 
plt.axis([0, 32, 0, 5000])
plt.ylabel('longueur en millimètres')
plt.xlabel('Pixel n°')
plt.show()


fig = plt.figure()

ax = plt.axes(projection='3d')

# Data for a three-dimensional line
z = pd.read_csv("C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/donnéescapturées.csv", sep=',', skiprows=80, skipfooter=80, na_values=['30000'], engine='python')

x = pd.read_csv("C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/Testy.csv", sep=',',skiprows=80, skipfooter=80,engine='python')

y = pd.read_csv("C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/Testx.csv", sep=' ',skiprows=80, skipfooter=80,engine='python')


ax.scatter(x, y, z, c='red')

ax.set_xlim(0,240) ; ax.set_ylim(0,320) ; ax.set_zlim(0,4000)

plt.show()

##

fig = plt.figure()

ax = plt.axes(projection='3d')

# Data for a three-dimensional line
z = pd.read_csv("C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/donnéescapturées1010.csv", sep=',', engine='python')

x = pd.read_csv("C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/Testy1010.csv", sep=' ',engine='python')

y = pd.read_csv("C:/Users/boyval/Documents/Projet B5L/LePython/Python/All_csv/Testx1010.csv", sep=',',engine='python')

ax.scatter(x, y, z, c='red')

ax.set_zlim(0,5000)

plt.show()