import Pathfinder
import LineIntersection
import tkinter
import turtle
import time


WIDTH = 1280
HEIGHT = 720
SCALING_FACTOR = 0.5


def prepareTopLevelWindow(window=None):

    TITLE = 'Pathfinder'
    if window is not None and type(window) == tkinter.Tk:
        window.title(TITLE)
        window.minsize(width=WIDTH, height=HEIGHT)


if __name__ == '__main__':

    pathfinder = Pathfinder.Pathfinder()

    TopLevelWindow = tkinter.Tk(screenName='Pathfinder')
    print('Entering Program')

    prepareTopLevelWindow(TopLevelWindow)

    id_list = [0, 0]

    def get_incremented_object_id(id_key=0):
        id_key = int(id_key)
        id_key += 1
        return str(id_key)

    def add_object(x=0, y=0, type_of=False, id_list=[0, 0], p=None):
        """True type is item. False type is obstacle."""
        item_id = id_list[0]
        obstacle_id = id_list[1]
        current_id = None

        if type_of:
            current_id = item_id
            id_list[0] = get_incremented_object_id(item_id)
            p.add_item(current_id, x_pos=x, y_pos=y)
        else:
            current_id = obstacle_id
            id_list[1] = get_incremented_object_id(obstacle_id)
            p.add_obstacle(current_id, x_pos=x, y_pos=y, radius=10)

    # Canvas
    canvas = tkinter.Canvas(master=TopLevelWindow, width=WIDTH, height=HEIGHT)
    window = turtle.TurtleScreen(canvas)

    turtleBot = turtle.RawTurtle(window)
    turtleBot.speed(1)

    def left_click(event):
        global id_list
        global canvas
        add_object(x=event.x - 0.5 * WIDTH, y=event.y - 0.5 * HEIGHT, type_of=True,
                   p=pathfinder, id_list=id_list)
        refresh_objects()

    def right_click(event):
        global id_list
        global canvas
        add_object(x=event.x - 0.5 * WIDTH, y=event.y - 0.5 * HEIGHT, type_of=False,
                   p=pathfinder, id_list=id_list)
        refresh_objects()

    def draw_circle(x, y, r, canvas, **kwargs):
        canvas.create_oval(x-r, y-r, x+r, y+r, kwargs)

    def refresh_objects():
        canvas.delete('all')
        global turtleBot
        turtleBot = turtle.RawTurtle(window)
        turtleBot.speed(1)

        items = ((key, pathfinder.item_position(key))
                 for key in pathfinder.item_keys())
        obstacles = ((key, pathfinder.obstacle_position_radius(key))
                     for key in pathfinder.obstacle_keys())

        for item in items:
            key = item[0]
            coord = item[1]
            draw_circle(coord[0], coord[1], 10, canvas, fill='green')
            canvas.create_text(
                coord[0], (coord[1] + 15), text=f'{key}: {coord}')

        for obstacle in obstacles:
            key = obstacle[0]
            coord = obstacle[1]
            draw_circle(coord[0], coord[1], coord[2], canvas, fill='red')
            canvas.create_text(coord[0], coord[1] +
                               coord[2] + 15, text=f'{key}, {coord}')

        canvas.after(15)

    canvas.bind('<Button-1>', func=left_click)
    canvas.bind('<Button-3>', func=right_click)

    canvas.pack()

    # for coord in coordinates:
    #     draw_circle(coord[0] , -coord[1]
    #                 , 5, canvas, fill='green')
    #     canvas.create_text(coord[0] , -(coord[1]  + 15), text=f'{coord}')

    # for obstacle in obstacles:
    #     draw_circle(obstacle[0] , -obstacle[1]
    #                 , obstacle[2] , canvas, fill='red')

    is_turtle_moving = False

    def do_circuit():
        global is_turtle_moving
        global turtleBot
        if not is_turtle_moving and len(pathfinder.item_keys()) > 0:
            is_turtle_moving = True
            turtleBot.clear()
            path_coordinates = (pathfinder.item_position(key)
                                for key in pathfinder.mst_optimized_tour('0'))
            # path_coordinates = (pathfinder.item_position(key)
            # for key in pathfinder.nearest_neighbour('0')['0'])
            start_coord = pathfinder.item_position('0')
            turtleBot.goto(start_coord[0], -start_coord[1])
            for coord in path_coordinates:
                turtleBot.goto(coord[0],
                               -coord[1])
            is_turtle_moving = False

    def clear_graph():
        global id_list
        pathfinder.clear()
        refresh_objects()
        id_list = [0, 0]

    move_button = tkinter.Button(
        TopLevelWindow, text='Move', command=do_circuit)
    move_button.pack()

    clear_button = tkinter.Button(
        TopLevelWindow, text='Clear', command=clear_graph)
    clear_button.pack()

    window.mainloop()

    print('Exiting Program')
