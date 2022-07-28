import numpy as np
import open3d as o3d
import serial
import serial.tools.list_ports
import time
import binascii



################################################################################################################

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

hexadecimal_string_pdc = "FE 84 00 02 00 01" #Set pcd
byte_array_pdc = bytearray.fromhex(hexadecimal_string_pdc)

hexadecimal_string_ON = "FE 80 00 00 " #START distance measurement
byte_array_ON = bytearray.fromhex(hexadecimal_string_ON)

hexadecimal_string_Result = "FE 82 00 01 00 " #Get Result 
byte_array_Result = bytearray.fromhex(hexadecimal_string_Result)

hexadecimal_string_OFF = "FE 81 00 00"  # STOP distance measurement
byte_array_OFF = bytearray.fromhex(hexadecimal_string_OFF)


serialPort = serial.Serial('/dev/ttyUSB0', baudrate=115200)   #Connecting to the camera 

################################################################################################################

serialPort.write(byte_array_pdc)
print('\n En mode pcd')

serialPort.write(byte_array_ON)
print('\n Démarrage caméra')

time.sleep(0.001)


serialPort.write(byte_array_Result)
print('       Get Result : ')

dataStart = serialPort.read(18)

data_list = binascii.hexlify(dataStart, ',')
data_list = data_list.decode("utf-8")
Tableau = list(split_n_chunks(data_list, 2))

print("\n Good start :", Tableau[0], Tableau[1], Tableau[2], Tableau[3], Tableau[4], Tableau[5], Tableau[6], Tableau[7], Tableau[8], "\n")


ListePDCinfo = serialPort.read(170) 

print("Info PDC : ", ListePDCinfo)

data = serialPort.read(460800)
datastr = str(data)



with open("/home/boyer/Documents/Projet/donnéesPCD.pcd","wb") as fichier:
    fichier.write(ListePDCinfo)
    fichier.write(data)

with open("/home/boyer/Documents/Projet/donnéesPCD.txt","wb") as fichier:
    fichier.write(ListePDCinfo)
    fichier.write(data)


#################


serialPort.write(byte_array_OFF)
serialPort.write(byte_array_Polar)

print('\nRetourne en mode Polar')

time.sleep(1)

data = serialPort.read_all() 
data = binascii.hexlify(data)
print("Fin d'enregistrement : " , data, "\n")

serialPort.__exit__('/dev/ttyUSB0')  # COM4 empty to avoid issues


pcd = o3d.io.read_point_cloud("/home/boyer/Documents/Projet/donnéesPCD.pcd")
print(pcd)

######
points = np.asarray(pcd.points)
center = np.array([0,0,0])
radius = 20000
distances = np.linalg.norm(points-center,axis=1)
pcd.points = o3d.utility.Vector3dVector(points[distances <= radius])
######

plane_model, inliers = pcd.segment_plane(distance_threshold=0.01,
                                         ransac_n=3,
                                         num_iterations=1000)



inlier_cloud = pcd.select_by_index(inliers)

outlier_cloud = pcd.select_by_index(inliers, invert=True)

o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud],
                                  zoom=0.2,
                                  front=[0, 0.4, -2],
                                  lookat=[2, 2, 2],
                                  up=[0, 1, 0])