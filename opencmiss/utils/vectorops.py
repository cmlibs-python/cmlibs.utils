"""
A collection of functions that operate on python lists as if
they were vectors.  A basic implementation to forgo the need
to use numpy.
"""
from math import sqrt


def magnitude(v):
    return sqrt(sum(v[i] * v[i] for i in range(len(v))))


def add(u, v):
    return [ u[i] + v[i] for i in range(len(u)) ]


def sub(u, v):
    return [ u[i] - v[i] for i in range(len(u)) ]


def dot(u, v):
    return sum(u[i] * v[i] for i in range(len(u)))


def eldiv(u, v):
    return [u[i] / v[i] for i in range(len(u))]


def elmult(u, v):
    return [u[i] * v[i] for i in range(len(u))]


def normalize(v):
    vmag = magnitude(v)
    return [v[i] / vmag for i in range(len(v)) ]


def cross(u, v):
    c = [u[1] * v[2] - u[2] * v[1],
         u[2] * v[0] - u[0] * v[2],
         u[0] * v[1] - u[1] * v[0]]

    return c


def mult(u, c):
    return [u[i] * c for i in range(len(u))]


def div(u, c):
    return [u[i] / c for i in range(len(u))]


def rotmx(quaternion):
    '''
    This method takes a quaternion representing a rotation
    and turns it into a rotation matrix. 
    '''
    mag_q = magnitude(quaternion)
    norm_q = div(quaternion, mag_q)
    qw, qx, qy, qz = norm_q
    mx = [[qw * qw + qx * qx - qy * qy - qz * qz, 2 * qx * qy - 2 * qw * qz, 2 * qx * qz + 2 * qw * qy],
          [2 * qx * qy + 2 * qw * qz, qw * qw - qx * qx + qy * qy - qz * qz, 2 * qy * qz - 2 * qw * qx],
          [2 * qx * qz - 2 * qw * qy, 2 * qy * qz + 2 * qw * qx, qw * qw - qx * qx - qy * qy + qz * qz]]

    return mx


def mxmult(mx, u):
    return []


def matmult(a, b):
    return [dot(row_a, b) for row_a in a]

