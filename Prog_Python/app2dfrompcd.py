
import serial
import serial.tools.list_ports
import time
import binascii
import numpy as np
import open3d as o3d
from itertools import islice
import csv
from matplotlib import pyplot as plt
import pandas as pd

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



liste32x240D = [0]*32*240

Valeur_min = [0]*32
liste32x24D = [0]*32*24


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


serialPort = serial.Serial('/dev/ttyUSB0', baudrate=115200) 

#############

answer = input("Do you want close range mode ? (yes/no)")
print("\n")

if answer == "yes":

    serialPort.write(byte_array_close)
    data = serialPort.read(6)
    print("Mode Close Range", data, '\n')
    time.sleep(0.01)

elif answer == "no":

    serialPort.write(byte_array_normal)
    data = serialPort.read(6)
    print("Mode Normal", data, '\n')
    time.sleep(0.01)
else:
    
    serialPort.write(byte_array_normal)
    data = serialPort.read(6)
    print("Mode Normal", data, '\n')
    time.sleep(0.01)
###############

serialPort.write(byte_array_pcd)
print('\n En mode pcd')

serialPort.write(byte_array_ON)
print('\n Démarrage caméra')

time.sleep(0.001)

data = serialPort.read(12)

print("\n Good start : ", data, "\n")

tps = int(input('Number of frame desired (<5fps when data visualisation) : '))

vis = o3d.visualization.Visualizer()
vis.create_window(width=1500, height=800)

Totalexe = 0
####################################

t=0
count = 1
while t < tps:
    
    start = time.monotonic()

    serialPort.write(byte_array_Result)
    print('Get Result : ', count)
    data = serialPort.read(6)
############################
############################
############################
    ListePDCinfo = serialPort.read(170) 

    datapcd = serialPort.read(460800)
    time.sleep(0.001)


    data_list = binascii.hexlify(datapcd, ',')
    data_list = data_list.decode("utf-8")
    Tableau = list(split_n_chunks(data_list, 2))

    DepthData = [0]*76799

    y=2
    posData=0
    while y<230399:
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

    DepthData = divide(DepthData, 240)    
    
    
    k=0
    j=0

    while j<239:

        liste32x240 = divide(DepthData[j], 32)

        i=0
        while i < 32:
        
            liste32x240D[k]=sum(liste32x240[i])/len(liste32x240[i])
            i = i + 1
            k=k+1
        j=j+1

    k=0
    j=0
    

    while j<7680:

        i=0
        while i<32:
            liste32x24D[k] = (liste32x240D[0+i+j]+liste32x240D[32+i+j]+liste32x240D[64+i+j]+liste32x240D[96+i+j]+liste32x240D[128+i+j]+liste32x240D[160+i+j]+liste32x240D[192+i+j]+liste32x240D[224+i+j]+liste32x240D[256+i+j]+liste32x240D[288+i+j])/10
            i=i+1
            k=k+1
        j = j + 320

## 2D MIN VALUE ##

    i=0

    while i < 32:
    
        listepartielle = [liste32x24D[192+i], liste32x24D[224+i], liste32x24D[256+i], liste32x24D[288+i], liste32x24D[320+i], liste32x24D[352+i], liste32x24D[384+i], liste32x24D[416+i], liste32x24D[448+i], liste32x24D[480+i], liste32x24D[512+i], liste32x24D[544+i]]
      
        Valeur_min[i] = min(listepartielle)
        i=i+1

    Depth32 = divide(Valeur_min, 32)


    plt.axis([0,32,0,5000])
    plt.ylabel("distance de collision en mm")
    plt.ion()
    plt.show()  
    plt.plot(Depth32, 'r+')
    plt.draw()
    plt.pause(0.001)
    plt.clf()

    with open("/home/boyer/Documents/Projet/donnéesPCD.pcd","wb") as fichier:
        fichier.write(ListePDCinfo)
        fichier.write(datapcd)

    print("PointcloudData à jour !")  


    pcd = o3d.io.read_point_cloud("/home/boyer/Documents/Projet/donnéesPCD.pcd")

######
    points = np.asarray(pcd.points)
    center = np.array([0,0,0])
    radius = 20000
    distances = np.linalg.norm(points-center,axis=1)
    pcd.points = o3d.utility.Vector3dVector(points[distances <= radius])
######
    
    vis.add_geometry(pcd)
    
    ctr = vis.get_view_control()
    ctr.set_up([0, 1, 0])
    ctr.set_front([0, 0, -2])
    ctr.set_lookat([2, 2, 2])
    ctr.set_zoom(0.1)
    
    
    vis.poll_events()
    vis.update_renderer()
    vis.remove_geometry(pcd)

    
############################
############################
    stop = time.monotonic()
    elapsed = stop - start
    
    Totalexe = Totalexe + elapsed 
    
    elapsed = elapsed  * 1000

    print(f'Temps d\'exécution : {elapsed:.4} ms \n')

    time.sleep(0.001) 
    t = t + 1
    count = count + 1

######################################


serialPort.write(byte_array_OFF)

time.sleep(0.5)


data = serialPort.read_all() 
data = binascii.hexlify(data)
print("Fin d'enregistrement : " , data, "\n")

serialPort.__exit__('/dev/ttyUSB0')  # COM4 empty to avoid issues

print ("temps total d exe en s : ", Totalexe)