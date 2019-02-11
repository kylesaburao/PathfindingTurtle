import queue

from lib import _constants
from lib import Pathfinder
from lib import Task


def main(**kwargs):
    task_queue = queue.Queue()
    robot_pathfinder = Pathfinder.Pathfinder()

    if 'start_position' in kwargs:
        start_position = kwargs['start_position']
        robot_pathfinder.add_item(item_id='START', x_pos=start_position[0], y_pos=start_position[1])
        robot_pathfinder.add_item(item_id='1', x_pos=1, y_pos=1)
        robot_pathfinder.add_item(item_id='2', x_pos=2, y_pos=2)

    continue_program = True
    default_task = None

    while continue_program:
        if not task_queue.empty():
            current_task = task_queue.get()
            current_task.execute_slice()
            default_task = None
        else:
            # Run default task

            if default_task is None:
                default_task = Task.Task()

            default_task.execute_slice()



if __name__ == '__main__':
    main(start_position=_constants.START_POSITION)
