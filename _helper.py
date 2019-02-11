import math


def pythagorean_distance(x1=0, y1=0, x2=0, y2=0, pos1=None, pos2=None):
    if pos1 is not None and pos2 is not None and len(pos1) == 2 and len(pos2) == 2:
        return math.sqrt((pos2[0]-pos1[0])*(pos2[0]-pos1[0]) + (pos2[1]-pos1[1])*(pos2[1]-pos1[1]))
    else:
        return math.sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))


def coordinate_offset(x=0, y=0, pos=None, x_offset=0, y_offset=0):
    if pos is not None and len(pos) == 2:
        return (pos[0] + x_offset, pos[1] + y_offset)
    else:
        return (x + x_offset, y + y_offset)
