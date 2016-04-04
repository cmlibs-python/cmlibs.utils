'''
Created on Jun 23, 2015

@author: hsorby
'''
from opencmiss.utils.vectorops import sub, dot,\
    add, mult


def calculateLinePlaneIntersection(pt1, pt2, point_on_plane, plane_normal):
    line_direction = sub(pt2, pt1)
    d = dot(sub(point_on_plane, pt1), plane_normal) / dot(line_direction, plane_normal)
    intersection_point = add(mult(line_direction, d), pt1)
    if abs(dot(sub(point_on_plane, intersection_point), plane_normal)) < 1e-08:
        return intersection_point

    return None

