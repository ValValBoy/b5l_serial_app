import serial
import serial.tools.list_ports
import time
import binascii
from itertools import islice

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

hexadecimal_string_ON = "FE 80 00 00 " #START distance measurement
byte_array_ON = bytearray.fromhex(hexadecimal_string_ON)

hexadecimal_string_Result = "FE 82 00 01 00 " #Get Result 
byte_array_Result = bytearray.fromhex(hexadecimal_string_Result)

hexadecimal_string_OFF = "FE 81 00 00"  # STOP distance measurement
byte_array_OFF = bytearray.fromhex(hexadecimal_string_OFF)

serialPort = serial.Serial('COM4', baudrate=115200)   #Connecting to the camera 

serialPort.write(byte_array_ON)
print('\n Démarrage caméra')

time.sleep(0.001)

serialPort.write(byte_array_Result)

time.sleep(0.001)

data = serialPort.read(153612) 

time.sleep(0.001)

data_list = binascii.hexlify(data, ',')
data_list = data_list.decode("utf-8")
Tableau = list(split_n_chunks(data_list, 2))

i = 0
while i<6:
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

Valeur_min = [0]*32
i=0

while i < 32:

    listepartielle = [liste32x24D[192+i], liste32x24D[224+i], liste32x24D[256+i], liste32x24D[288+i], liste32x24D[320+i], liste32x24D[352+i], liste32x24D[384+i], liste32x24D[416+i], liste32x24D[448+i], liste32x24D[480+i], liste32x24D[512+i], liste32x24D[544+i]]
      
    Valeur_min[i] = min(listepartielle)
    i=i+1

Liste_Min = divide(Valeur_min, 32)

print(Liste_Min)

end = time.monotonic()

elapsed= end - start

print(f'Temps d\'exécution : {elapsed:.4} ms \n')

serialPort.write(byte_array_OFF)

time.sleep(0.5)


data = serialPort.read_all() 
data = binascii.hexlify(data)
print("Fin d'enregistrement : " , data, "\n")

serialPort.__exit__('COM4')  # COM4 empty to avoid issues
