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

serialPort = serial.Serial('/dev/ttyUSB0', baudrate=115200)   #Connecting to the camera 

serialPort.write(byte_array_ON)
print('\n Démarrage caméra')

time.sleep(0.001)

serialPort.write(byte_array_Result)
print('       Get Result : ')
 
time.sleep(0.001)

data = serialPort.read(153612) 

time.sleep(0.001)

## TEST Data ##

#data_write = binascii.hexlify(data, ' ')
#data_write= data_write.decode("utf-8")
#out=sys.stdout
#out.write(data_write)


data_list = binascii.hexlify(data, ',')
data_list = data_list.decode("utf-8")
Tableau = list(split_n_chunks(data_list, 2))

print("\n Good start :", Tableau[0], Tableau[1], Tableau[2], Tableau[3], Tableau[4], Tableau[5], "\n")

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

## Exe time ##

end = time.monotonic()
elapsed= end - start
elapsed = elapsed*1000
print(f'Temps d\'exécution : {elapsed:.4} ms \n')

serialPort.write(byte_array_OFF)

time.sleep(0.5)

data = serialPort.read_all() 
data = binascii.hexlify(data)
print("Fin d'enregistrement : " , data, "\n")

## COM4 empty to avoid issues ##

serialPort.__exit__('/dev/ttyUSB0') 