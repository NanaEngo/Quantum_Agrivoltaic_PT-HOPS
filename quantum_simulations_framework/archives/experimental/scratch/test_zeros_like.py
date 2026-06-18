import numpy as np
import scipy.sparse as sp

L = sp.csc_matrix(np.eye(7))
L_zeros = np.zeros_like(L)
print(f"Shape: {L_zeros.shape}")
print(f"NDim: {L_zeros.ndim}")
print(f"Data: {L_zeros}")
