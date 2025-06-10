import numpy as np

data = np.array([-0.1, 0, -0.1, -0.2, -0.2, 0.1])
print(np.exp(data)/np.exp(data).sum())