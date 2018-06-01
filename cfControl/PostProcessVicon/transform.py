import math
import numpy as np

sp = np.array([1,1])

quad = np.array([0,0])

psi = np.deg2rad(45)

newspx = sp[0]*np.cos(psi) - sp[1]*np.sin(psi)
newspy = sp[0]*np.sin(psi) + sp[1]*np.cos(psi)

print(newspx)
print(newspy)