'''This tutorial does NOT require trigonometry, but if you know some,
you can automatically generate some fancier shapes like regular polygons and 
stars, as illustrated here, after importing some trig from the math module.
(And you can copy in the part before main and use the functions.)
'''

from graphics import *
from math import pi, sin, cos

toRad = pi/180 # convert degrees to radians

def atAngle(x, y, distance, angleDegrees):
    '''return the Point reached by going out from Point(x,y),
    the given distance, at the given angle counterclockwise from horizontal.
    '''
    return Point(x + distance*cos(angleDegrees*toRad),
                 y + distance*sin(angleDegrees*toRad) )

def regularPolygon(center, radius, sides, rotationDegrees, win):
    '''Draw and return a regular polygon in GraphWin win, given the
    center Point, the radius from center to vertices,
    the number of sides, and degrees of rotation (0 means a flat top).
    '''
    vertices = []
    angle = 90 + 180/sides + rotationDegrees # flat side up with 0 rotation
    for i in range(sides):
        vertices.append(atAngle(center.getX(), center.getY(), radius, angle))
        angle = angle + 360/sides
    poly = Polygon(vertices)
    poly.draw(win)
    return poly

def star(center, radius, points, win):
    '''Draw and return a regular points-pointed star in GraphWin win, given the
    center Point, the radius from center to points.
    '''
    vertices = []
    x = center.getX()
    y = center.getY()
    angle = 90 # start up
    angleDiff = 180/points # radial angle between points
    angPoint = (2 - (points % 2))*angleDiff/2 # 2 vert apart for even, one odd
    innerRadius = (radius*sin(.5*angPoint*toRad)/ # using trig law of sines
                         sin(.5*(angleDiff+angPoint)*toRad) )
    for i in range(points):
        vertices.append(atAngle(x, y, radius, angle))
        angle = angle + angleDiff
        vertices.append(atAngle(x, y, innerRadius, angle))
        angle = angle + angleDiff
    poly = Polygon(vertices)
    poly.draw(win)
    return poly
    
                        

def main():
    win = GraphWin('Regular Polygons', 400, 300) 
    win.yUp() # make right side up coordinates!

    regularPolygon(Point(40, 240), 30, 4, 45, win) #square rotated to diamond.
    c8 = Point(250, 170)
    p = regularPolygon(c8, 100, 8, 0, win)
    p.setWidth(5)
    p = star(c8, 80, 8, win)
    p.setOutline('red')
    c5 = Point(100, 80)
    p = regularPolygon(c5, 70, 5, 36, win) # 36: vertex up
    p.setFill('blue')
    p = regularPolygon(c5, 50, 5, 0, win)
    p.setFill('green')
    p = star(c5, 40, 5, win)
    p.setFill('yellow')

    win.promptClose(240, 40)


main()
