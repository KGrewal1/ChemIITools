# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_EnergySurfaces.ipynb.

# %% auto 0
__all__ = ['parse_out', 'surface_plot', 'heatmap', 'vib_calc']

# %% ../nbs/01_EnergySurfaces.ipynb 2
#| echo: false
import os
import re
import linecache
from rdkit import Chem
from rdkit.Chem.Draw import IPythonConsole
from rdkit.Chem import Draw
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import curve_fit

# %% ../nbs/01_EnergySurfaces.ipynb 5
def parse_out(file):
    """
    parses an out file of a symmetric triatomic for the bond length, angle and SCF energy 
    """
    shape_lookup = "Symbolic Z-matrix"
    energy_lookup = "SCF Done"
    e_search = r'(?<=SCF Done:  E\(RHF\) =).+?(?=A\.U\.)'
    r_search = r'(?<=1).+?(?= 2 )'
    a_search = r'(?<= 2 ).*'
    shape_line = None
    with open(file) as myFile:
        for num, line in enumerate(myFile):
                if shape_lookup in line:
                        shape_line = num+4
                if num == shape_line:
                        r= float(re.findall(r_search,line)[0])
                        angle= float(re.findall(a_search,line)[0])
                if energy_lookup in line:
                         energy= float(re.findall(e_search,line)[0])




    return ((r, angle), energy)

    

# %% ../nbs/01_EnergySurfaces.ipynb 8
def _func(r,theta, dict):
    # dictionary lookup
    return dict[(r,theta)]
def _dict_to_mesh(dict):
    """
    convert a dictioonary of ((r,theta) z) values to a mesh
    """
    r,theta = zip(*dict.keys())
    r = np.unique(r)
    theta = np.unique(theta)
    r,theta= np.meshgrid(r,theta)
    z = np.array([_func(r,theta, dict) for (r,theta) in zip(r.ravel(), theta.ravel())]).reshape(r.shape)




    return r,theta, z

# %% ../nbs/01_EnergySurfaces.ipynb 9
def surface_plot(dict, fname = None):
    """Plots a surface from the output of the regex"""
    r,theta, z = _dict_to_mesh(dict)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(r,theta, z, cmap=cm.viridis_r, linewidth=0)
    plt.xlabel('Bond Length/ $\AA$')
    plt.ylabel('Bond Angle/ $^\circ$')
    ax.set_zlabel('Energy/ $E_{h}$')
    fig.tight_layout()
    if fname is not None:
        plt.savefig(fname)
    plt.show()

# %% ../nbs/01_EnergySurfaces.ipynb 11
def heatmap(dict, fname = None):
    """Plots a heatmap from the output of the regex"""
    r,theta, z = _dict_to_mesh(dict)
    z_min, z_max = z.min(), z.max()
    fig, ax = plt.subplots()

    c = ax.pcolormesh(r,theta, z, cmap=cm.viridis_r, vmin=z_min, vmax=z_max)
    # set the limits of the plot to the limits of the data
    ax.axis([r.min(), r.max(), theta.min(), theta.max()])
    fig.colorbar(c, ax=ax)
    plt.xlabel('Bond Length/ $\AA$')
    plt.ylabel('Bond Angle/ $^\circ$')
    if fname is not None:
        plt.savefig(fname)
    plt.show()

# %% ../nbs/01_EnergySurfaces.ipynb 13
def vib_calc(dict, mass = 1.6735575E-27):
    """
    Calculate optimum bond length and angle and symmetric stretch and bending frequencies
    Default mass is that of the hydrogen atom
    """
    h_to_J = 4.3597482E-18 # hartree to joule conversion factor
    deg_to_r = np.pi/180 # degrees to radians
    A_to_m = 1E-10 # angstrom to m
    r_opt, theta_opt = min(dict, key=dict.get)
    r,theta = zip(*dict.keys())
    r = np.unique(r)
    theta = np.unique(theta)
    zr = [] # with constant theta
    ztheta = [] # with constant r

    for R in r:
        zr.append(dict[(R, theta_opt)]*h_to_J)

    zr = np.array(zr)
    r_adj = (r - r_opt)*A_to_m
    rslice = (r_adj>=.25*r_adj.min()) & (r_adj<=.25*r_adj.max())
    rfit = np.linspace(r_adj.min(), r_adj.max(), 1000)
    rquad = np.linspace(.4*r_adj.min(), .4*r_adj.max(), 1000)

    poly = np.polyfit(r_adj , zr, 8)
    quad = np.polyfit(r_adj [rslice], zr[rslice], 2)
    zfit = np.polyval(poly, rfit)
    zquad = np.polyval(quad, rquad)

    plt.plot(r_adj, zr,"ro")
    plt.plot(rfit, zfit)
    plt.plot(rquad, zquad)
    plt.xlabel('Bond Length from Optimum/ m')
    plt.ylabel('Energy/ J')
    plt.show()

    kr = 2*quad[0]
    mu_1 = 2*mass
    nu_r = np.sqrt(kr/mu_1)/(2*np.pi)

    for Theta in theta:
        ztheta.append(dict[(r_opt, Theta)]*h_to_J)

    ztheta = np.array(ztheta)
    theta_adj = (theta-theta_opt)*deg_to_r
    thetaslice = (theta_adj>=.25*theta_adj.min()) & (theta_adj<=.25*theta_adj.max())

    thetafit = np.linspace(theta_adj.min(), theta_adj.max(), 1000)
    thetaquad = np.linspace(.4*theta_adj.min(), .4*theta_adj.max(), 1000)
    poly = np.polyfit(theta_adj , ztheta, 8)
    quad = np.polyfit(theta_adj[thetaslice], ztheta[thetaslice], 2)
    zfit = np.polyval(poly, thetafit)
    zquad = np.polyval(quad, thetaquad)

  
    plt.plot(theta_adj, ztheta,"ro", markersize=2)
    plt.plot(thetafit, zfit)
    plt.plot(thetaquad, zquad)
    plt.xlabel('Bond Angle from Optimum/ rad')
    plt.ylabel('Energy/ J')
    plt.show()

    ktheta = 2*quad[0]
    mu_2 = 0.5*mass
    nu_theta = np.sqrt(ktheta/(mu_2*r_opt**2))/(2*np.pi)
    return r_opt, theta_opt, nu_r, nu_theta
