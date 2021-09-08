import matplotlib.pyplot as plt
import numpy as np
import Active_layer_Classes as AlC
import Text_Importer as txtImp
from tkinter import filedialog
import Small_Functions as sf
import os
from matplotlib import gridspec
from scipy import integrate

q = 1.602176634*10**(-19) # C
k = 1.38064852 * 10**(-23) # m2 kg s-2 K-1
sigma = 5.670374419 * 10**(-8) # W⋅m−2⋅K−4
T = 300 # K

Eg = 1# eV

u = (Eg*q)/(k*T)

J0_constant = (q*15*sigma*T**3)/(k*np.pi**4)

integral_term_expression = lambda x: (x**2)/(np.exp(x)-1)
integral_term = integrate.quad(integral_term_expression, u, np.inf)

print(integral_term)
# print(q)
# print(k)
# print(sigma)
# print(u)


J0 = J0_constant * integral_term[0]

print(J0)





