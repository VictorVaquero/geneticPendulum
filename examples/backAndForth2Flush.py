'''Test animation of a group of objects making a face.

This version replaces moveAllOnLine by moveAllOnLineFlush,
to only update thescreen once for each animation step,
after multiple individual graphics instructions are given.'''

from graphics import *
import time

def moveAll(shapeList, dx, dy):
    ''' Move all shapes in shapeList by (dx, dy).'''   
    for shape in shapeList: 
        shape.move(dx, dy)
            
                                  #NEW Flush version with win parameter
def moveAllOnLineFlush(shapeList, dx, dy, repetitions, delay, win): 
    '''Animate the shapes in shapeList along a line in win.
    Move by (dx, dy) each time.
    Repeat the specified number of repetitions.
    Have the specified delay (in seconds) after each repeat.
    '''
    win.autoflush = False          # NEW: set before animation
    for i in range(repetitions):
        moveAll(shapeList, dx, dy)
        win.flush()         # NEW needed to make all the changes appear
        time.sleep(delay)
    win.autoflush = True           # NEW: set after animation
        

def main():
    win = GraphWin('Back and Forth', 300, 300)
    win.yUp() # make right side up coordinates!

    rect = Rectangle(Point(200, 90), Point(220, 100))
    rect.setFill("blue")
    rect.draw(win)

    head = Circle(Point(40,100), 25)
    head.setFill("yellow")
    head.draw(win)

    eye1 = Circle(Point(30, 105), 5)
    eye1.setFill('blue')
    eye1.draw(win)

    eye2 = Line(Point(45, 105), Point(55, 105))
    eye2.setWidth(3)
    eye2.draw(win)

    mouth = Oval(Point(30, 90), Point(50, 85))
    mouth.setFill("red")
    mouth.draw(win)

    faceList = [head, eye1, eye2, mouth]
    
    cir2 = Circle(Point(150,125), 25)
    cir2.setFill("red")
    cir2.draw(win)

    moveAllOnLineFlush(faceList, 5, 0, 46, .05, win)  # NEW Flush version
    moveAllOnLineFlush(faceList, -5, 0, 46, .05, win) #     added win

    win.promptClose(win.getWidth()/2, 20)

main()
