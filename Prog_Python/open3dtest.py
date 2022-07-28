import  open3d as o3d
import numpy as np

pcd = o3d.io.read_point_cloud("/home/boyer/Documents/Projet/Donnee01.pcd")

print(pcd)

points = np.asarray(pcd.points)

center = np.array([0,0,0])
radius = 20000

distances = np.linalg.norm(points -center,axis=1)
pcd.points = o3d.utility.Vector3dVector(points[distances <= radius])


o3d.io.write_point_cloud("out.pcd",pcd)

o3d.visualization.draw_geometries([pcd])
