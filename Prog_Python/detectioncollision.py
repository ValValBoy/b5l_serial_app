import serial
import serial.tools.list_ports
import time
import binascii
from itertools import islice



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



liste32x120D = [0]*32*120
liste32x12D = [0]*32*12
Valeur_min = [0]*32



hexadecimal_string_pcd = "FE 84 00 02 00 01" #Set pcd
byte_array_pcd = bytearray.fromhex(hexadecimal_string_pcd)


hexadecimal_string_ON = "FE 80 00 00 " #START distance measurement
byte_array_ON = bytearray.fromhex(hexadecimal_string_ON)

hexadecimal_string_Result = "FE 82 00 01 00 " #Get Result 
byte_array_Result = bytearray.fromhex(hexadecimal_string_Result)

hexadecimal_string_close = "FE 86 00 01 01" #Set close range
byte_array_close = bytearray.fromhex(hexadecimal_string_close)

hexadecimal_string_normal = "FE 86 00 01 00" #Set close range
byte_array_normal = bytearray.fromhex(hexadecimal_string_normal)

hexadecimal_string_OFF = "FE 81 00 00"  # STOP distance measurement
byte_array_OFF = bytearray.fromhex(hexadecimal_string_OFF)


serialPort = serial.Serial('COM4', baudrate=115200) 

#############

answer = input("Do you want close range mode ? (yes/no)")

if answer == "yes":

    serialPort.write(byte_array_close)
    data = serialPort.read(6)
    print("Mode Close Range", data)
    time.sleep(0.001)

elif answer == "no":

    serialPort.write(byte_array_normal)
    data = serialPort.read(6)
    print("Mode Normal", data)
    time.sleep(0.001)
else:
    
    serialPort.write(byte_array_normal)
    data = serialPort.read(6)
    print("Mode Normal", data)
    time.sleep(0.001)
###############

serialPort.write(byte_array_pcd)

serialPort.write(byte_array_ON)

time.sleep(0.001)

data = serialPort.read(12)

tps = int(input('Number of frame desired (<5fps when data visualisation) : '))

starttot = time.monotonic()

####################################

t=0
while t < tps:
   
    serialPort.write(byte_array_Result)
    
    data1 = serialPort.read(176)
###########################
    datapcd = serialPort.read(460800)
    time.sleep(0.001)
    
    print("read")

    data_list = binascii.hexlify(datapcd, ',')
    Tableau = list(split_n_chunks(data_list.decode("utf-8"), 2))

    DepthData = [0]*38400
    y=57602
    posData=0
    while y<172799:
        Input = Tableau[y]
        length_to_split = [len(Input)//2]*2
        lst = iter(Input)
        Output = [list(islice(lst, elem))
           for elem in length_to_split]
        String_1 = " ".join(Output[0])
        String_2 = " ".join(Output[1])

        String_f = String_2 + String_1
        
        Value = int(String_f, 16)

        DepthData[posData] = Value
        
        y = y + 3
        posData = posData + 1 


    DepthData = divide(DepthData, 120)    

    Premiereboucle = time.monotonic()    

    k=0
    j=0

    while j<119:

        liste32x120 = divide(DepthData[j], 32)

        i=0
        while i < 32:
        
            liste32x120D[k]=sum(liste32x120[i])/len(liste32x120[i])
            i = i + 1
            k=k+1
        j=j+1

    k=0
    j=0
    
    ## Ok

    while j<3840:

        i=0
        while i<32:
            liste32x12D[k] = (liste32x120D[0+i+j]+liste32x120D[32+i+j]+liste32x120D[64+i+j]+liste32x120D[96+i+j]+liste32x120D[128+i+j]+liste32x120D[160+i+j]+liste32x120D[192+i+j]+liste32x120D[224+i+j]+liste32x120D[256+i+j]+liste32x120D[288+i+j])/10
            i=i+1
            k=k+1
        j = j + 320

    
## 2D MIN VALUE ##

    i=0

    while i < 32:
    
        Valeur_min[i] = min([liste32x12D[0+i], liste32x12D[32+i], liste32x12D[64+i], liste32x12D[96+i], liste32x12D[128+i], liste32x12D[160+i], liste32x12D[192+i], liste32x12D[224+i], liste32x12D[256+i], liste32x12D[288+i], liste32x12D[320+i]])
        i=i+1

    mini = str(min(Valeur_min))
    res = float(mini)
    res = int(res)
    if res < 300:
        print("                                 DANGER COLLISION : ", res, " mm")
    else:
        print(res, " mm")

############################

    time.sleep(0.001) 
    t = t + 1

######################################

stop = time.monotonic()
serialPort.write(byte_array_OFF)

time.sleep(0.5)


data = serialPort.read_all() 
data = binascii.hexlify(data)
print("Fin d'enregistrement : " , data, "\n")

serialPort.__exit__('COM4')  # COM4 empty to avoid issues

print ("temps total d exe : ", stop-starttot, " secondes")

print("fps : ", round(tps/(stop-starttot), 1))