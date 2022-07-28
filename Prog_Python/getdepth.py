from tkinter.messagebox import YES
from turtle import color
import serial
import serial.tools.list_ports
import time
import binascii
from itertools import islice
import csv
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.cm as cm 
import numpy as np

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

serialPort = serial.Serial('/dev/ttyUSB0', baudrate=115200)   #Connecting to the camera 

serialPort.write(byte_array_Polar)
print('\n En mode Polar')

serialPort.write(byte_array_ON)
print('\n Démarrage caméra')

time.sleep(0.001)

serialPort.write(byte_array_Result)
print('       Get Result : ')
 
time.sleep(0.001)

data = serialPort.read(153618) 

time.sleep(0.001)

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

with open('/home/boyer/Documents/Projet/donnéescapturées.csv', 'w') as f:

  write = csv.writer(f)

  j=0
  while j < 240:  
    write.writerow(Liste_Finale[j])
    j = j + 1



df = pd.read_csv("/home/boyer/Documents/Projet/donnéescapturées.csv", skiprows=80, skipfooter=80, sep=',', na_values=['30000'], engine='python')

pd.set_option('display.max_columns', None)

pd.set_option('display.max_rows', 5)

df = df.T

plt.plot(df,"r+") 
plt.axis([0, 320, 0, 5000])
plt.ylabel('longueur en millimètres')
plt.xlabel('vue en large')
plt.show()

serialPort.write(byte_array_OFF)

time.sleep(1)

data = serialPort.read_all() 
data = binascii.hexlify(data)
print("Fin d'enregistrement : " , data, "\n")

serialPort.__exit__('/dev/ttyUSB0')  # COM4 empty to avoid issues