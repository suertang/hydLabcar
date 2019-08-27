import numpy as np
from scipy.spatial import cKDTree

# inputs
LTU = np.genfromtxt('test.txt', delimiter=',')

coords = ((12.5, 25.5, 137),
          (13.5, 26.5, 141),
          (14.5, 25.5, 144))

# querying and interpolating
xyz = LTU[:, :3]
val = LTU[:, 3]

del LTU # attempt to clean up memory

tree = cKDTree(xyz)
dist, ind = tree.query(coords, k=2)

d1, d2 = dist.T
v1, v2 = val[ind].T
v = (d1)/(d1 + d2)*(v2 - v1) + v1

print(v)