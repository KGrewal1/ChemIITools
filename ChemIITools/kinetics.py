# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_Kinetics.ipynb.

# %% auto 0
__all__ = ['steady_state_calc', 'oreg_calc', 'oreg_calc_RK4']

# %% ../nbs/02_Kinetics.ipynb 2
#| echo: false
import numpy as np

# %% ../nbs/02_Kinetics.ipynb 4
def steady_state_calc(kf1:float, # rate constant for D->I
                      kr1:float, # rate constant for I->D
                      kf2:float, # rate constant for I->N
                      kr2:float  # rate constant for N->I
                      ):
    """
    Calculate the steady state equilibrium of reaction a<->b<->c, given the rate of the forwards and backwards processes at each step
    """
    mat = np.array([[-kf1,kr1,0],[0,kf2,-kr2],[1,1,1]])
    vec = np.array([0,0,1])
    mat_inv = np.linalg.inv(mat)
    out = np.matmul(mat_inv, vec)
    return out

# %% ../nbs/02_Kinetics.ipynb 10
def _deriv(t, concs, k1, k2, k3, k4, k5):
    """
    Returns the time derivatives of concs = A, B, X, Y, Z, P, Q
    """
    A, B, X, Y, Z, P, Q = concs
    r1 = A*Y*k1
    r2 = X*Y*k2
    r3 = B*X*k3
    r4 = X*X*k4
    r5 = Z*k5
    return -r1, -r3, r1 -r2 +r3 -2*r4, -r1-r2+r5, r3-r5, r1 +r2, r4

# %% ../nbs/02_Kinetics.ipynb 15
def oreg_calc(concs:list, tmax:float = 90, dt:float =1e-6, k1:float =1.34, k2:float =1.6e9, k3:float =8e3, k4:float =4e7, k5:float =1):
    """
    Calculates the time dependent concentrations of species in the oregonator system using the Euler method
    """
    t = np.arange(0, tmax+dt, dt)
    conc_t = np.zeros((len(t),len(concs)))
    conc_t[0] = concs
    for i, c in enumerate(conc_t[:-1]):
        #if i == len(t)-1: break
        rk_1 = _deriv(1, c, k1,k2,k3,k4,k5)
        rk_1 = np.array(rk_1)
        conc_t[i+1]= c + rk_1*dt
    conc_t = conc_t.transpose()
    return t, conc_t

# %% ../nbs/02_Kinetics.ipynb 16
def oreg_calc_RK4(concs:list, tmax:float = 90, dt:float =1e-6, k1:float =1.34, k2:float =1.6e9, k3:float =8e3, k4:float =4e7, k5:float =1):
    """
    Calculates the time dependent concentrations of species in the oregonator system using the RK4 method
    """
    t = np.arange(0, tmax+dt, dt)
    conc_t = np.zeros((len(t),len(concs)))
    conc_t[0] = concs
    for i, c in enumerate(conc_t[:-1]):
        rk_1 = np.array(_deriv(1, c, k1,k2,k3,k4,k5))
        rk_2 = np.array(_deriv(1, c+dt*rk_1/2, k1,k2,k3,k4,k5))
        rk_3 = np.array(_deriv(1, c+dt*rk_2/2, k1,k2,k3,k4,k5))
        rk_4 = np.array(_deriv(1, c+dt*rk_3, k1,k2,k3,k4,k5))
        conc_t[i+1]=c+dt*(rk_1+2*rk_2+2*rk_3+rk_4)/6
    conc_t = conc_t.transpose()
    return t, conc_t
