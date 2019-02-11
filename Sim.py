import tkinter as tk
import turtle
import math
import Pathfinder
import time

# CONTROLS
#
# - Left click on canvas: Add new item
# - Left click on item: Start optimized tour from that item
# - Right click on item: Start prim mst tour from that item
# - Middle click on item: Move turtle directly to that item
#


class CanvasInput:

    def __init__(self, c=None, input_code='', action_func=None):
        self.canvas = c
        self.action = action_func
        self._bind_action(input_code)

    def _bind_action(self, input_code: str = '', **kwargs):
        self.canvas.bind(input_code, self.action)


class Application:

    _APPLICATION_NAME = "Pathfinder"
    _MIN_WIDTH = 1280
    _MIN_HEIGHT = 720

    _ITEM_DRAW_RADIUS = 8
    _DEFAULT_OBSTACLE_RADIUS = 12

    BTN_CODES = {'L_BTN': '<Button-1>', 'R_BTN': '<Button-3>', 'M_BTN': '<Button-2>',
                 'HOVER': '<Enter>', 'UNHOVER': '<Leave>'}

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(self._APPLICATION_NAME)
        self.root.minsize(width=self._MIN_WIDTH, height=self._MIN_HEIGHT)
        self.root.maxsize(width=self._MIN_WIDTH, height=self._MIN_HEIGHT)
        self.pathfinder = Pathfinder.Pathfinder()

        self._init_default_states()

        self._init_canvas()
        self._init_turtle()
        self._init_canvas_buttons()

    def _init_default_states(self):
        self.lock_hover_lines = False
        self.hover_render_time = None
        self.hover_engaged = False
        self.hover_lines = []

        self.itemID = '0'
        self.obstacleID = '0'
        self.addItemMode = True
        self.pathfinder.clear()
        self.keyPressed = False

    def _init_canvas(self):
        self.canvas = tk.Canvas(
            master=self.root, width=self._MIN_WIDTH, height=self._MIN_HEIGHT)
        self.canvas.pack()
        self.visit_order_text = []

    def _init_turtle(self):
        self.turtleWindow = turtle.TurtleScreen(self.canvas)
        self.turtleBot = turtle.RawTurtle(self.turtleWindow)
        self.turtleBot.shape('turtle')
        self.turtleBot.shapesize(1.5, 1.5)
        self.isTurtleMoving = False

    def _item_key_at_raw_coord(self, coord=(0, 0)):
        new_coordinate = self._convert_canvas_coordinate_to_draw_coordinate(
            coord[0], coord[1])
        current_item = self.canvas.find_closest(
            x=new_coordinate[0], y=new_coordinate[1])
        item_tags = self.canvas.itemcget(current_item, 'tags')
        item_id = item_tags.split(' ')[0][4:]
        if self.pathfinder.has_item(item_id):
            return item_id
        else:
            return None

    def _turtle_traversal(self, item_id='a', traversal_type='optimized'):
        if not self.isTurtleMoving:
            item_position = self.pathfinder.item_position(item_id)
            self.isTurtleMoving = True
            self.turtleBot.clear()
            self.canvas.delete(*self.visit_order_text)
            self.visit_order_text = []

            outline_radial_factor = 1.75
            outline = self.canvas.create_oval(item_position[0] - outline_radial_factor * self._ITEM_DRAW_RADIUS, item_position[1] - outline_radial_factor * self._ITEM_DRAW_RADIUS,
                                              item_position[0] + outline_radial_factor * self._ITEM_DRAW_RADIUS, item_position[1] + outline_radial_factor * self._ITEM_DRAW_RADIUS)

            vertical_text_offset = 20

            path = []

            if traversal_type == 'optimized':
                path = self.pathfinder.mst_optimized_tour(item_id)
            elif traversal_type == 'tour':
                path = self.pathfinder.mst_euler_tour(item_id)[item_id]
            else:
                return

            original_turtle_size = self.turtleBot.turtlesize()
            size = list(original_turtle_size)

            for visit_order, key in enumerate(path, 1):
                key_position = self.pathfinder.item_position(key)
                if visit_order > 1:
                    self._move_turtle(key_position)
                else:
                    # Move the turtle to the start without drawing a line
                    self.turtleBot.penup()
                    self._move_turtle(item_position)
                    self.turtleBot.pendown()

                self.visit_order_text.append(self.canvas.create_text(
                    key_position[0], key_position[1] + vertical_text_offset, text=str(visit_order)))
                if size[0] < 2.5:
                    size[0] *= 1.025
                    size[1] *= 1.025
                self.turtleBot.turtlesize(*size)

            while size[0] > original_turtle_size[0]:
                size[0] *= 0.95
                size[1] *= 0.95
                self.turtleBot.turtlesize(*size)

            self.turtleBot.turtlesize(*original_turtle_size)
            self.canvas.delete(outline)
            self.isTurtleMoving = False

    def _item_id_at_canvas_coordinate(self, event):
        new_coordinate = self._convert_canvas_coordinate_to_draw_coordinate(
            event.x, event.y)
        current_item = self.canvas.find_closest(
            x=new_coordinate[0], y=new_coordinate[1])
        item_tags = self.canvas.itemcget(current_item, 'tags')
        item_id = item_tags.split(' ')[0][4:]
        if self.pathfinder.has_item(item_id):
            return item_id

    def _item_entered(self, event):
        if len(self.hover_lines) > 0 or len(self.pathfinder.itemGraph.vertexDict) <= 1:
            return

        if not self.hover_engaged and not self.lock_hover_lines:

            render_refresh_time = (1/30) * 1000

            current_time = time.time() * 1000

            if self.hover_render_time is None:
                self.hover_render_time = current_time
            elif current_time - self.hover_render_time < render_refresh_time:
                return

            self.hover_render_time = current_time

            self.hover_engaged = True
            self.lock_hover_lines = True
            item_id = self._item_id_at_canvas_coordinate(event)
            if self.pathfinder.has_item(item_id):

                path_endpoints = self.pathfinder.mst_euler_tour(item_id)[item_id]

                endpoint_coordinates = [(
                    self.pathfinder.item_position(c)[0], self.pathfinder.item_position(c)[1]) for c in path_endpoints]

                edge_set = set()

                for i in range(len(endpoint_coordinates) - 1):
                    curr_ = endpoint_coordinates[i]
                    next_ = endpoint_coordinates[i + 1]

                    if (curr_, next_) not in edge_set and (next_, curr_) not in edge_set:
                        edge_set.add((curr_, next_))

                tag = 'HOVERLINE'

                for edge in edge_set:
                    x1 = edge[0][0]
                    y1 = edge[0][1]
                    x2 = edge[1][0]
                    y2 = edge[1][1]
                    line = self.canvas.create_line(x1, y1, x2, y2, fill = 'grey', tags = (tag, ))
                    self.hover_lines.append(line)

            self.lock_hover_lines = False
          

    def _item_left(self, event):

        if len(self.hover_lines) == 0:
            return

        current_time = time.time() * 1000
        at_least_time = (1/15) * 1000

        if self.hover_render_time is None:
            return
        elif current_time - self.hover_render_time < at_least_time:
            return

        if self.hover_engaged and not self.lock_hover_lines:

            self.lock_hover_lines = True

            for line in self.hover_lines:
                self.canvas.delete(line)

            self.hover_lines = []

            self.lock_hover_lines = False
            self.hover_engaged = False


    def _item_left_clicked(self, event):
        item_id = self._item_id_at_canvas_coordinate(event)
        if not self.pathfinder.has_item(item_id):
            return

        self._turtle_traversal(item_id, 'optimized')

    def _item_right_clicked(self, event):
        new_coordinate = self._convert_canvas_coordinate_to_draw_coordinate(
            event.x, event.y)
        current_item = self.canvas.find_closest(
            x=new_coordinate[0], y=new_coordinate[1])
        item_tags = self.canvas.itemcget(current_item, 'tags')
        item_id = item_tags.split(' ')[0][4:]
        if not self.pathfinder.has_item(item_id):
            return

        self._turtle_traversal(item_id, 'tour')

    def _item_middle_clicked(self, event):
        if not self.isTurtleMoving:
            self.turtleBot.penup()
            self.turtleBot.clear()
            self.canvas.delete(*self.visit_order_text)
            self.visit_order_text = []
            self.isTurtleMoving = True
            self._move_turtle(
                self._convert_canvas_coordinate_to_draw_coordinate(event.x, event.y))
            self.isTurtleMoving = False
            self.turtleBot.pendown()

    def _init_canvas_buttons(self):

        def item_control(event):
            new_coordinate = self._convert_canvas_coordinate_to_draw_coordinate(
                event.x, event.y)

            if self.addItemMode:
                candidate_clicked_item_key = self._get_clicked_item_key(
                    click_pos=(event.x, event.y))

                if candidate_clicked_item_key is None:
                    item_id = self.itemID
                    oval_tag = 'ITEM' + item_id

                    self.itemID = str(int(item_id) + 1)
                    self.canvas.create_oval(new_coordinate[0] - self._ITEM_DRAW_RADIUS, new_coordinate[1] - self._ITEM_DRAW_RADIUS,
                                            new_coordinate[0] + self._ITEM_DRAW_RADIUS, new_coordinate[1] + self._ITEM_DRAW_RADIUS, fill='green', tags=(oval_tag,))
                    self.canvas.tag_bind(
                        oval_tag, self.BTN_CODES['L_BTN'], self._item_left_clicked)
                    self.canvas.tag_bind(
                        oval_tag, self.BTN_CODES['R_BTN'], self._item_right_clicked)
                    self.canvas.tag_bind(
                        oval_tag, self.BTN_CODES['M_BTN'], self._item_middle_clicked)
                    self.canvas.tag_bind(
                        oval_tag, self.BTN_CODES['HOVER'], self._item_entered)
                    self.canvas.tag_bind(
                        oval_tag, self.BTN_CODES['UNHOVER'], self._item_left)                        

                    self.pathfinder.add_item(
                        item_id=item_id, x_pos=new_coordinate[0], y_pos=new_coordinate[1])

            else:
                candidate_clicked_obstacle_key = self._get_clicked_obstacle_key(
                    click_pos=(event.x, event.y))

                if candidate_clicked_obstacle_key is None:
                    obstacle_id = self.obstacleID
                    oval_tag = 'OBSTACLE' + obstacle_id

                    self.obstacleID = str(int(obstacle_id) + 1)
                    self.canvas.create_oval(new_coordinate[0] - self._DEFAULT_OBSTACLE_RADIUS, new_coordinate[1] - self._DEFAULT_OBSTACLE_RADIUS,
                                            new_coordinate[0] + self._DEFAULT_OBSTACLE_RADIUS, new_coordinate[1] + self._DEFAULT_OBSTACLE_RADIUS, fill='red', tags=(oval_tag,))
                    self.pathfinder.add_obstacle(
                        obstacle_id, new_coordinate[0], new_coordinate[1], self._DEFAULT_OBSTACLE_RADIUS)

        def key_press(event):
            if not self.keyPressed:
                self.keyPressed = True

                if event.char == 't':
                    self.addItemMode = not self.addItemMode

                if event.char == 'c':
                    if not self.isTurtleMoving:
                        self.canvas.delete('all')
                        self._init_turtle()
                        self._init_canvas_buttons()
                        self.pathfinder.clear()
                        self._init_default_states()

        def key_release(event):
            self.keyPressed = False

        self.addItem = CanvasInput(
            c=self.canvas, input_code=self.BTN_CODES['L_BTN'], action_func=item_control)
        self.addItem = CanvasInput(
            c=self.root, input_code='<KeyPress>', action_func=key_press)
        self.addItem = CanvasInput(
            c=self.root, input_code='<KeyRelease>', action_func=key_release)

    def _move_turtle(self, raw_coordinate=(0, 0)):
        converted_pos = (raw_coordinate[0], -raw_coordinate[1])
        self.turtleBot.setheading(self.turtleBot.towards(converted_pos))
        self.turtleBot.goto(converted_pos)

    def _convert_canvas_coordinate_to_draw_coordinate(self, x=0, y=0):
        # (0, 0) for turtle is the centre
        # (0, 0) for the canvas is the top left
        return (x - 0.5*self._MIN_WIDTH, (y - 0.5*self._MIN_HEIGHT))

    def _pythag_dist(self, pos1=(0, 0), pos2=(0, 0)):
        return math.sqrt(pow(pos2[0] - pos1[0], 2) + pow(pos2[1] - pos1[1], 2))

    def _get_closest_key_to_coord(self, pos=(0, 0)):
        items = [(key, self.pathfinder.item_position(key))
                 for key in self.pathfinder.item_keys()]

        if len(items) == 0:
            return None
        else:
            return min(items, key=lambda x: self._pythag_dist(pos, x[1]))[0]

    def _get_clicked_item_key(self, click_pos=(0, 0)):
        pos_converted = self._convert_canvas_coordinate_to_draw_coordinate(
            click_pos[0], click_pos[1])
        closest_key = self._get_closest_key_to_coord(pos_converted)
        if closest_key is not None and self._pythag_dist(pos_converted, self.pathfinder.item_position(closest_key)) <= 3 * self._ITEM_DRAW_RADIUS:
            return closest_key
        else:
            return None

    def _get_clicked_obstacle_key(self, click_pos=(0, 0)):
        pos_converted = self._convert_canvas_coordinate_to_draw_coordinate(
            click_pos[0], click_pos[1])
        obstacles = [(key, self.pathfinder.obstacle_position_radius(key))
                     for key in self.pathfinder.obstacle_keys()]

        if len(obstacles) == 0:
            return None

        closest_obstacle = min(obstacles, key=lambda x: self._pythag_dist(
            pos_converted, (x[1][0], x[1][1])))

        radius = closest_obstacle[1][2]
        closest_obstacle_pos = (closest_obstacle[1][0], closest_obstacle[1][1])

        if self._pythag_dist(pos_converted, closest_obstacle_pos) <= 1.5 * radius:
            return closest_obstacle[0]
        else:
            return None

    def start(self):
        self.root.mainloop()


if __name__ == '__main__':
    main = Application()
    main.start()
