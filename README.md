<h1 align="center">Pymuvie</h1>

<p align="center">This is a port to python of a game named "Simuvie" designed by valoulef with Adventure Game Studio. Cells move on a grid following basic instructions in their DNA, reproduce and die. Hopefully patterns emerge.</p>

## Libraries and Dependencies

- Python3
- OpenCV and Numpy
- PyQt6
- PyQtGraph
- PIL (Pillow)

## Configuration

Change the values of the all-cap variables at the top of the program to customize the experience.

## Execution

Simply run `main.py`

## Rules of the game

Each cell has a "DNA": a sequence of letters which each represent a move from one spot (one pixel) to an adjacent one. The meaning of each letter is documented in the code below the definition of `DNA`. At each cycle, the cell looks up the next letter in its DNA and moves accordingly. If the destination spot is a wall or is already occupied by two cells, it remains where it is. Each move consumes 1 HP, but cells can "eat" the spot they land on to gain back 1 HP; when their life is under `LIFE/2`, they will try to eat 2 HPs instead. Whenever a spot is eaten, its blue component is increased by 1; when it reaches 255, it appears bright blue and there is no food left: cells that land on it can no longer eat. When two cells meet and are fertile, they automatically reproduce, giving half their life to the new born cell. When a cell dies, it turns red and can be eaten by another cell for 1 HP.
