# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_Clusters.ipynb.

# %% auto 0
__all__ = ['CoM', 'CoMTransform', 'InertiaTensor', 'point_setup', 'geom_opt', 'System']

# %% ../nbs/03_Clusters.ipynb 2
#| echo: false
import numbers
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import basinhopping
import sympy as sp

# %% ../nbs/03_Clusters.ipynb 3
def _unitv(r):
    """returns unit vector in the direction of r"""
    return(r/np.linalg.norm(r))
def _dist(v1,v2):
    """returns the magnitude of the distance between two vectors"""
    return np.linalg.norm(v1-v2)
def _vector_sum(*vectors):
    """sums vectors"""
    array = np.array([*vectors])
    return np.sum(array, axis = 0)
def _fun_gen(f: str):
    """converts a function of r, written as a string into a python function, and a function for its derivative"""
    r = sp.Symbol('r')
    y = sp.sympify(f)
    yprime = y.diff(r)
    f = sp.lambdify(r, y, 'numpy')
    fprime = sp.lambdify(r, yprime, 'numpy')
    if not isinstance(2*f(2.2), numbers.Number):
        raise ValueError('Please enter a function purely of "r"')
    return f, fprime
def _calc_setup(function: str):
    """converts pairwise energies and forces, to total energy and net force on each point"""
    U, dU = _fun_gen(function)
    def E_calc(points):
        """The sum of the pairwise energies"""
        points = points.reshape(-1,3)
        E=0
        for i,v in enumerate(points):
            for w in points[i+1:]:
                r = _dist(v,w)
                E = E + U(r)
        return E
    def F_calc(points):
        """The net forces acting on each point"""
        points = points.reshape(-1,3)
        forces = np.zeros(points.shape)
        for i,v in enumerate(points):
            for j,w in enumerate(points[i+1:]):
                forces[i] = forces[i]+dU(_dist(v,w))*_unitv(w-v)
                forces[j+i+1] = forces[j+i+1]+dU(_dist(v,w))*_unitv(v-w)
        return forces
    return E_calc, F_calc

# %% ../nbs/03_Clusters.ipynb 4
def CoM(*vectors):
    """returns the CoM of vectors"""
    return _vector_sum(*vectors)/len(vectors)

# %% ../nbs/03_Clusters.ipynb 5
def CoMTransform(*vectors):
    """Transforms vectors so the CoM is at the origin"""
    com = CoM(*vectors)
    return np.array([*vectors])-com

# %% ../nbs/03_Clusters.ipynb 6
def InertiaTensor(*vectors):
    """returns the inertia tensor of 3D vectors"""
    Ixx = 0
    Iyy = 0
    Izz = 0
    Ixy = 0
    Iyz = 0
    Ixz = 0
    for vector in vectors:
        Ixx = Ixx + vector[1]**2 + vector[2]**2
        Iyy = Iyy + vector[0]**2 + vector[2]**2
        Izz = Izz + vector[0]**2 + vector[1]**2
        Ixy = Ixy - vector[0]*vector[1]
        Iyz = Iyz - vector[1]*vector[2]
        Ixz = Ixz - vector[0]*vector[2]
    return np.matrix([[Ixx, Ixy, Ixz], [Ixy, Iyy, Iyz], [Ixz, Iyz, Izz]])

# %% ../nbs/03_Clusters.ipynb 7
def point_setup(n:int, seed:int=0):
    """returns n points distributed on the unit sphere"""
    np.random.seed(seed)
    points = np.random.randn(3, n)
    points /= np.linalg.norm(points, axis=0)
    points = points.transpose()
    return np.array(points)

# %% ../nbs/03_Clusters.ipynb 8
def geom_opt(points, F_calc, iterations = 1000, factor = 1e-4):
    """optimises geometry of points in 3D space using gradient descent"""
    for _ in range(iterations):
        forces = F_calc(points)
        points = points + factor*forces
    return points

# %% ../nbs/03_Clusters.ipynb 9
class System:
    """A cluster system, defined by n points and a pairwise potential in term of r, given as a string"""
    def __init__(self,
                 n:int=7, # the number of atoms in the cluster
                 function:str='(4*((1/r)^12 -(1/r)^6))' # the pairwise potential between any two atoms in the cluster
                 ):
        self.n = n
        self._function = function
        self.points = point_setup(n)
        self._U, self._F = _calc_setup(function)

    @property
    def function(self):
        return self._function

    @function.setter
    def function(self, value):
        self._function = value
        self._U, self._F = _calc_setup(value)

    @property
    def E(self):
        return self._U(self.points)
    @E.setter
    def E(self, value):
        raise Exception("Energy is determined by geometry and so read only")


    def plot(self):
        x, y, z = self.points.transpose()
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x, y, z, c= 'blue', alpha=1)
        ax.axes.set_xlim3d(left=-1.2, right=1.2)
        ax.axes.set_ylim3d(-1.2, 1.2)
        ax.axes.set_zlim3d(-1.2, 1.2)
        ax.set_box_aspect([1,1,1])
        plt.show()




    def optimise(self,
                 riter:int=10000, # the number of random initial configurations to consider
                 giter:int=1000,  # the number of gradient descent iterations to consider
                 gfactor:int=1e-4,# the factor for the gradient descent
                 biter:int=100    # the number of basin hopping iterations to perform
                 ):
        for i in range(riter):
            x = point_setup(self.n,i)
            E = self._U(x)
            if E<self.E:
                self.points = x
        self.points = geom_opt(self.points, self._F, iterations=giter, factor = gfactor)
        self.points = CoMTransform(*self.points)
        minimizer_kwargs = {"method": "BFGS"}
        res = basinhopping(self._U, self.points.flatten(), minimizer_kwargs=minimizer_kwargs,
                        niter=biter)
        self.points = res.x.reshape(-1,3)
        self.points = np.array(CoMTransform(*self.points))



    def __str__(self):
        return "Energy %.6f, for %d points" % (self.E, self.n)


    def xyz(self,
            name:str = None # name of file to save to: if None prints
            ):
        """Returns the coordinates of the system in .xyz format"""
        if name is None:
            print(self.n)
            print("Energy %.6f, for %d points, calculated by ChemII tools" % (self.E, self.n))
            for v in self.points:
                print("He %.10f %.10f %.10f" % (v[0], v[1], v[2]))
        else:
            with open(name,"w+", encoding="utf-8") as f:
                f.write("%d\n" % (self.n))
                f.write("Energy %.6f, for %d points, calculated by ChemII tools\n" % (self.E, self.n))
                for v in self.points:
                    f.write("He %.10f %.10f %.10f\n" % (v[0], v[1], v[2]))
    def CoM(self):
        return CoM(*self.points)
    def InertiaTensor(self):
        return InertiaTensor(*self.points)
