#!/usr/bin/python3
from PIL import Image as Img
from graphics import *
import random
import time

nCells = 10 # Number of cells at the beginning

bckgnd = Img.open('background.png')
print(bckgnd.format)
print(bckgnd.mode)
print(bckgnd.size)

WIDTH = bckgnd.width
HEIGHT = bckgnd.height
pixels = list(bckgnd.getdata())

win = GraphWin(width = WIDTH, height = HEIGHT, autoflush=False) # create a window
win.setCoords(0, 0, WIDTH-1, HEIGHT-1)

class Spot:
  def update(self):
    self.point.setFill(color_rgb(self.color[0],self.color[1],self.color[2]))

  def visit(self):
    self.color[2] += 10
    if self.color[2] > 255:
      self.color[2] = 255
    self.update()
    # print("Visited spot at {},{}; color {}".format(self.x,self.y,self.color[2]))

  def __init__(self, x, y, color):
    self.x = x
    self.y = y
    self.point = Point(x,y)
    self.color = [color[0],color[1],color[2]]
    if self.color == [0,0,0]:
      self.wall = False
    else:
      self.wall = True
    self.update()
    self.point.draw(win)

message = Text(Point(WIDTH/2,HEIGHT/2),"Processing background...")
message.draw(win)
update()

# spots = [Spot(i%WIDTH,i//WIDTH,pixels[i]) for i in range(0,len(pixels))]
spots = [Spot(i%WIDTH,i//WIDTH,pixels[i]) for i in range(0,len(pixels))]
def spotAtXY(x,y):
  return spots[x+y*WIDTH]

message.setText("Placing cells...")
update()

nonWalls = [spot for spot in spots if not spot.wall]

class Cell:
  def place(self,x,y):
    x = x%WIDTH
    y = y%HEIGHT
    spot = spotAtXY(x,y)
    if spot.wall:
      print("Cannot place cell here: it's a wall!")
    else:
      # print("Will move point from {},{}".format(self.point.getX(),self.point.getY()))
      self.point.move(x-self.x,y-self.y)
      # print("Moved point to {},{}".format(self.point.getX(),self.point.getY()))
      self.x = x
      self.y = y
      spot.visit()
      self.point.setFill("red")

  def __init__(self, x, y):
    self.point = Point(x,y)
    self.x = x
    self.y = y
    self.place(x,y)
    self.point.draw(win)
    print("Instantiated a cell at {},{}".format(x,y))

startingPoints = random.sample(nonWalls,k=nCells)
cells = [Cell(startingPoint.x,startingPoint.y) for startingPoint in startingPoints]

message.undraw()
update() # update display now that the pixels have been drawn

# def motion(event):
#   x, y = event.x, event.y
#   # print('{}, {}'.format(x, y))
# win.bind('<Motion>', motion)

# win.getMouse()
# win.close()

lastLoopTime = time.time()
while True:
  currentTime = time.time()
  dt = currentTime - lastLoopTime
  if (dt >= 0.025):
    lastLoopTime = currentTime
    
    for cell in cells:
      dx = 0
      dy = 0
      direction = random.randint(0,3)
      if direction==0:
        dx = -1
      elif direction==1:
        dx = 1
      elif direction==2:
        dy = -1
      elif direction==3:
        dy = 1
      cell.place(cell.x+dx,cell.y+dy)
    update()

  # if win.checkMouse():
  #   win.close()
  #   break
