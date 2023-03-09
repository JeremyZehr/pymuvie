#!/usr/bin/python3
import time
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk

bckgnd = Image.open('background.png')

TARGET_FPS = 30
FERTILITY = 1800 # number of cycles needed to recover from giving birth
NCELLS = 300 # Number of cells at the beginning
MUTATION = 100 # Prevalence of mutation per letter (1/MUTATION)
WIDTH = bckgnd.width
HEIGHT = bckgnd.height
BOTTOM_BAR = 40 # in px
PIXELS = list(bckgnd.getdata())
DNA = "NSEWRLFB0" # N=North; S=South; E=East; W=West; R=Right (90deg rotation); L=Left (-90deg rotation); F=Forward; B=Back; 0=Do not move

root = tk.Tk()
root.title('Pymuvie')

root_open = True
def on_closing():
  global root_open
  root_open = False
  root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)

# get the screen dimension
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# find the center point
center_x = int(screen_width/2 - WIDTH / 2)
center_y = int(screen_height/2 - (HEIGHT+BOTTOM_BAR) / 2)

# set the position of the window to the center of the screen
root.geometry(f'{WIDTH}x{HEIGHT+BOTTOM_BAR}+{center_x}+{center_y}')
root.minsize(WIDTH, HEIGHT+BOTTOM_BAR)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='black')
canvas.pack(anchor=tk.NW, expand=True)

image = Image.new(mode = "RGB", size = (WIDTH, HEIGHT), color = (0, 0, 0))
tatras = [ImageTk.PhotoImage(image)]
img_id = canvas.create_image(0, 0, anchor=tk.NW, image=tatras[0])

def update_image(lbd):
  if root_open:
    d = ImageDraw.Draw(image)
    lbd(d)
    image_resized = image
    w,h = root.winfo_width(), root.winfo_height()
    if w > WIDTH or h > HEIGHT+BOTTOM_BAR:
      image_resized = image.resize((w,h-BOTTOM_BAR))
      canvas.config(width=w, height=h-BOTTOM_BAR)
    tatras[0] = ImageTk.PhotoImage(image_resized)
    canvas.itemconfig(img_id,image=tatras[0])
    root.update()

class Spot:
  def refresh(self, d):
    d.point([self.x,self.y], fill=(self.color[0],self.color[1],self.color[2]))

  def visit(self, cell, d):
    if cell not in self.cells:
      for c in self.cells:
        if (c.female != cell.female) and c.fertile_in==0 and cell.fertile_in==0:
          dna = c.dna[0:len(c.dna)//2] + cell.dna[len(cell.dna)//2:len(cell.dna)]
          cells.append( Cell(self.x,self.y,dna=dna) )
          if c.female:
            c.fertile_in = FERTILITY
          if cell.female:
            cell.fertile_in = FERTILITY
      self.cells.append(cell)
    self.color[2] += 10
    if self.color[2] > 255:
      self.color[2] = 255
    self.refresh(d)

  def __init__(self, x, y, color):
    self.x = x
    self.y = y
    self.color = [color[0],color[1],color[2]]
    self.cells = []
    if self.color == [0,0,0]:
      self.wall = False
    else:
      self.wall = True

spots = [Spot(i%WIDTH,i//WIDTH,PIXELS[i]) for i in range(0,len(PIXELS))]
def spotAtXY(x,y):
  return spots[x+y*WIDTH]
walls = [spot for spot in spots if spot.wall]
nonWalls = [spot for spot in spots if not spot.wall]

class Cell:
  def refresh(self,d):
    color = (255,255,0)
    if self.female:
      color = (0,255,0)
    d.point([self.x,self.y], fill=color)

  def place(self,x,y,d):
    old_spot = spotAtXY(self.x,self.y)
    if self in old_spot.cells:
      old_spot.cells.remove(self)
      old_spot.refresh(d)
      for cell in old_spot.cells:
        cell.refresh(d)
    x = x%WIDTH
    y = y%HEIGHT
    spot = spotAtXY(x,y)
    if spot.wall:
      return # Cannot place cell here: it's a wall!
    elif len(spot.cells) > 1:
      return # Spot already occupied by 2 cells
    else:
      self.x = x
      self.y = y
      spot.visit(self,d)
      self.refresh(d)

  def __init__(self, x, y, dna="NSEWRLFBFLRWESN0", female=None):
    self.x = x
    self.y = y
    self.step = 0
    self.life = 10
    self.dna = list(range(0,len(dna)))
    for i in range(0,len(dna)):
      if random.randint(1,MUTATION)==MUTATION:
        self.dna[i] = random.choice(DNA)
      else:
        self.dna[i] = dna[i]
    self.dna = ''.join(x for x in self.dna)
    self.direction = "0"
    self.fertile_in = FERTILITY
    if female==None:
      self.female = bool(random.getrandbits(1))
    else:
      self.female = female

startingPoints = random.sample(nonWalls,k=NCELLS)
cells = [Cell(startingPoint.x,startingPoint.y) for startingPoint in startingPoints]
for i in range(0,NCELLS):
  cells[i].dna = cells[i].dna[0:i%len(cells[i].dna)]+cells[i].dna[i%len(cells[i].dna):len(cells[i].dna)]

def init(d):
  for wall in walls:
    wall.refresh(d)
  for cell in cells:
    cell.refresh(d)

update_image(lambda d:init(d))

def cycle(d):
  for cell in cells:
    cell.step = (cell.step+1) % len(cell.dna)
    cell.fertile_in = max(0,cell.fertile_in-1)
    previous_direction = cell.direction
    cell.direction = cell.dna[cell.step]
    dx = 0
    dy = 0
    if cell.direction in "RLFB" and previous_direction=="0":
      cell.direction="0"
    elif cell.direction=="R": # Right, 90deg angle
      if previous_direction=="W":
        cell.direction="N"
      elif previous_direction=="E":
        cell.direction="S"
      elif previous_direction=="N":
        cell.direction="E"
      elif previous_direction=="S":
        cell.direction="W"
    elif cell.direction=="L": # Left, 270deg angle
      if previous_direction=="W":
        cell.direction="S"
      elif previous_direction=="E":
        cell.direction="N"
      elif previous_direction=="N":
        cell.direction="W"
      elif previous_direction=="S":
        cell.direction="E"
    elif cell.direction=="B": # Backward
      if previous_direction=="W":
        cell.direction="E"
      elif previous_direction=="E":
        cell.direction="W"
      elif previous_direction=="N":
        cell.direction="S"
      elif previous_direction=="S":
        cell.direction="N"
    elif cell.direction=="F": # Forward
      cell.direction = previous_direction
    
    if cell.direction=="W":
      dx = -1
    elif cell.direction=="E":
      dx = 1
    elif cell.direction=="N":
      dy = -1
    elif cell.direction=="S":
      dy = 1

    x, y = cell.x, cell.y
    cell.place(cell.x+dx,cell.y+dy, d)
    # Update cell.direction with the *actual* movement (maybe there was a wall on the way)
    if cell.x < x:
      cell.direction = "W"
    elif cell.x > x:
      cell.direction = "E"
    elif cell.y < y:
      cell.direction = "N"
    elif cell.y > y:
      cell.direction = "S"
    else:
      cell.direction = "0"
# end cycle

info = tk.Label(root, text='0 fps, ncells: 0')
info.pack(anchor=tk.CENTER, expand=True)

fps = {'timestamp': 0, 'n': 0}

lastLoopTime = time.time()
while True:
  if not root_open:
    break

  currentTime = time.time()
  if currentTime-fps['timestamp'] >= 1:
    info.config(text='{} fps, ncells: {}'.format(fps['n'],len(cells)))
    fps['n'] = 0
    fps['timestamp'] = currentTime

  dt = currentTime - lastLoopTime
  if (dt >= 1/TARGET_FPS):
    fps['n'] += 1
    lastLoopTime = currentTime
    update_image(lambda d:cycle(d))
