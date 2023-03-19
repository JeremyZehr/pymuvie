#!/usr/bin/python3
import time
import math
import random
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk
from copy import deepcopy

mapImg = Image.open('background.png')

# Note: executing a frame or cycle loop might take more than the target interval duration,
# resulting in skipped loop(s). There's no real way around it for the frame loops,
# but multiple cycle loops should be run if delay is too great

TARGET_FPS = 20 # number of times the display is refreshed per second
TARGET_CPS = 40 # number of cell cycles per second
FERTILITY = 900 # number of cycles needed to recover from giving birth
LIFE = 1200 # number of remaining cycles that cells start with
NCELLS = 250 # Number of cells at the beginning
MUTATION = 100 # Prevalence of mutation per letter (1/MUTATION)
WIDTH = mapImg.width
HEIGHT = mapImg.height
print("Size: {},{}".format(WIDTH,HEIGHT))
BOTTOM_BAR = 40 # in px
PIXELS = list(mapImg.getdata())
DNA = "NSEWRLFB0" # N=North; S=South; E=East; W=West; R=Right (90deg rotation); L=Left (-90deg rotation); F=Forward; B=Back; 0=Do not move

mouse_x, mouse_y = -1, -1

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
canvas.pack(anchor=tk.N, expand=True)

info = tk.Label(root, text='0 fps, ncells: 0')
info.pack(anchor=tk.W, expand=True)

cell_info = tk.Label(root, text='Not currently hovering any cell')
cell_info.pack(anchor=tk.E, expand=True)


image_spots = Image.new(mode = "RGB", size = (WIDTH, HEIGHT), color = (0, 0, 0))
draw_spots = ImageDraw.Draw(image_spots)
image_render = image_spots.copy()
image_resized = image_render
tatras = ImageTk.PhotoImage(image_resized)
img_id = canvas.create_image(0, 0, anchor=tk.NW, image=tatras)

active_cell = None
highlighted_cell = None

updating_image = False
def update_image(copy_cells,w,h):
  if root_open:
    global updating_image
    updating_image = True
    image_cells = Image.new(mode = "RGBA", size = (WIDTH, HEIGHT), color = (0, 0, 0, 0))
    draw_cells = ImageDraw.Draw(image_cells)
    global spots_to_refresh
    for spot in spots_to_refresh:
      spot.refresh(draw_spots)
    spots_to_refresh = [s for s in spots_to_refresh if s.need_refresh>0]
    for cell in copy_cells:
      cell.refresh(draw_cells)

    hovered = None
    if (mouse_x>=0 and mouse_x<WIDTH and mouse_y>=0 and mouse_y<HEIGHT):
      hovered = closestCellXY(mouse_x,mouse_y)
    
    if hovered != None:
      hovered.highlight(draw_cells)
    global highlighted_cell
    if highlighted_cell:
      if highlighted_cell.life>0:
        highlighted_cell.highlight(draw_cells,"pink")
      else:
        highlighted_cell = None

    global active_cell
    active_cell = highlighted_cell or hovered
    
    image_render = image_spots.copy()
    image_render.paste(image_cells, (0,0), image_cells)
    # allow canvas resizing but enforce ratio
    # w, h = root.winfo_width(), root.winfo_height()
    ratio_w, ratio_h = w/WIDTH, h/(HEIGHT+BOTTOM_BAR)
    ratio = min(ratio_w,ratio_h)
    new_w, new_h = round(WIDTH*ratio), round(HEIGHT*ratio)
    global image_resized
    image_resized = image_render.resize((new_w,new_h))
    # global tatras
    # tatras = ImageTk.PhotoImage(image_resized)
    # canvas.config(width=new_w, height=new_h)
    # canvas.itemconfig(img_id,image=tatras)
    # root.update()
    updating_image = False

class Spot:
  def refresh(self,d):
    d.point([self.x,self.y], fill=(self.color[0],self.color[1],self.color[2]))
    self.need_refresh -= 1

  def visit(self, cell):
    live_cells = [c for c in self.cells if c.life>=0]
    if cell not in self.cells:
      dead_cells = [c for c in self.cells if c.life<=0]
      if (len(dead_cells)>0):
        cell.life += 100
        dead_cell = dead_cells[0]
        cells.remove(dead_cell)
        self.cells.remove(dead_cell)
      for c in live_cells:
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
    if self.need_refresh == 0:
      spots_to_refresh.append(self)
    self.need_refresh += 1

  def __init__(self, x, y, color):
    self.x = x
    self.y = y
    self.color = [color[0],color[1],color[2]]
    self.cells = []
    self.need_refresh = 0
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
    if self.life<=0:
      color = (255,0,0)
    d.point([self.x,self.y], fill=color)

  def highlight(self, d, color="purple"):
    d.ellipse((self.x-5,self.y-5,self.x+5,self.y+5), fill=None, outline=color, width=2)
    
  def place(self,x,y):
    if (self.life<=0):
      return
    old_spot = spotAtXY(self.x,self.y)
    if self in old_spot.cells:
      old_spot.cells.remove(self)
    x = x%WIDTH
    y = y%HEIGHT
    spot = spotAtXY(x,y)
    live_cells = [cell for cell in spot.cells if cell.life>=0]
    if not spot.wall and len(live_cells) < 2:
      self.x = x
      self.y = y
      spot.visit(self)
    else:
      old_spot.visit(self)

  def __init__(self, x, y, dna="NSEWRLFBFLRWESN0", female=None):
    self.x = x
    self.y = y
    self.step = 0
    self.life = LIFE
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

spots_to_refresh = [w for w in walls]
for cell in cells:
  cell.place(cell.x,cell.y)
update_image(cells,root.winfo_width(),root.winfo_height())

def closestCellXY(x,y,radius=10):
  spot = spotAtXY(x,y)
  live_cells = [c for c in spot.cells if c.life>0]
  if (len(live_cells)>0):
    return live_cells[0]
  last_x, last_y = x, y
  for d in range(1,radius):
    for r in range(0,360,20):
      xi, yi = x+round(d*math.cos(math.radians(r))), y+round(d*math.sin(math.radians(r)))
      if (xi<0 or xi>=WIDTH or yi<0 or yi>=HEIGHT or (xi==last_x and yi==last_y)):
        continue
      last_x, last_y = xi, yi
      spot = spotAtXY(xi,yi)
      live_cells = [c for c in spot.cells if c.life>0]
      if (len(live_cells)>0):
        return live_cells[0]
  return None

def clear_mouse(event=None):
  global mouse_x, mouse_y
  mouse_x, mouse_y = -1, -1
def motion(event):
  global mouse_x, mouse_y
  mouse_x, mouse_y = round(event.x*WIDTH/canvas.winfo_width()), round(event.y*HEIGHT/canvas.winfo_height())
canvas.bind('<Motion>', motion)
canvas.bind('<Leave>', clear_mouse)
def click(event):
  cell = closestCellXY(mouse_x,mouse_y)
  global highlighted_cell
  if (cell==None):
    highlighted_cell = None
    return
  if (cell==highlighted_cell):
    highlighted_cell = None
  else:
    highlighted_cell = cell
canvas.bind('<Button-1>', click)

def cycle():
  for cell in cells:
    if (cell.life<=0):
      continue
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

    cell.life = max(0,cell.life-1)
    x, y = cell.x, cell.y
    cell.place(cell.x+dx,cell.y+dy)
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

fps = {'timestamp': 0, 'n': 0, 'c': 0, 'f': 0}

lastCycleTime = time.time()
lastFrameTime = lastCycleTime
while True:
  if not root_open:
    break

  fps['n'] += 1
  currentTime = time.time()
  
  if currentTime-fps['timestamp'] >= 1:
    info.config(text='{} fps, {} cps, {} lps, ncells: {} (alive {})'.format(fps['f'],fps['c'],fps['n'],len(cells),len([c for c in cells if c.life>0])))
    fps['n'] = 0
    fps['f'] = 0
    fps['c'] = 0
    fps['timestamp'] = currentTime
  
  cps_time_difference = currentTime-lastCycleTime
  fps_time_difference = currentTime-lastFrameTime
  
  # Frame cycle (asynchronous - threaded)
  if ((fps_time_difference) >= 1/TARGET_FPS and updating_image == False and root_open):
    # get size now before window gets closed
    root_w, root_h = root.winfo_width(),root.winfo_height()

    tatras = ImageTk.PhotoImage(image_resized)
    new_w, new_h = image_resized.size
    canvas.config(width=new_w, height=new_h)
    canvas.itemconfig(img_id,image=tatras)
    if active_cell:
      cell_info.config(text='Cell: {} hp, female? {}, fertile in {}, DNA is {}'.format(
        active_cell.life,active_cell.female,active_cell.fertile_in,active_cell.dna)
      )
    else:
      cell_info.config(text='No cell to display')
    root.update()

    fps['f'] += 1
    lastFrameTime = currentTime
    # use deep copies of cells because the attributes of the original ones might be updated while the thread gets executed
    copy_cells = [deepcopy(c) for c in cells]
    ui_thread = threading.Thread(target=update_image, args=(copy_cells,root_w,root_h))
    ui_thread.start()
    
  # Cell cycle (synchronous - main thread)
  if (cps_time_difference >= 1/TARGET_CPS):
    cycle()
    fps['c'] += 1
    lastCycleTime = currentTime
    
