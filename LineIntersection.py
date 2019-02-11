# https://math.stackexchange.com/questions/275529/check-if-line-intersects-with-circles-perimeter
# Two points a = (x_a, y_a), b = (x_b, y_b) form a line
# A circle c = (x_c, y_c, r)
# d_x = x_b - x_a
# d_y = y_b - y_a
# d_r = sqrt(d_x^2 + d_y^2)
# D = (x_a * y_b) - (x_b * y_a)
# r^2 = radius of circle squared

# The discriminant delta = r^2 * d_r^2 - D^2 determines how
# the line intersects the circle
#
# delta < 0: no intersection
# delta = 0: tangent line (1 point on circumference)
# delta > 0: full intersect (2 points on circumference)

import math
import numpy


class Obstacle:

    # Model as a circle
    def __init__(self, x=0, y=0, r=0):
        self.x = x
        self.y = y
        self.r = abs(r)

    def does_line_segment_intersect(self, x1=0, y1=0, x2=0, y2=0):
        # https://stackoverflow.com/questions/1073336/circle-line-segment-collision-detection-algorithm?rq=1
        # REQUIRE NUMPY
        # python -m pip install numpy

        point_a = numpy.array([x1, y1])
        point_b = numpy.array([x2, y2])
        point_circle = numpy.array([self.x, self.y])
        direction_vector = point_b - point_a
        circle_out_vector = point_a - point_circle

        A = numpy.dot(direction_vector, direction_vector)
        B = numpy.dot(circle_out_vector, direction_vector) * 2
        C = numpy.dot(circle_out_vector, circle_out_vector) - pow(self.r, 2)

        discrim = pow(B, 2) - (4*A*C)

        if discrim < 0:
            return False

        discrim = math.sqrt(discrim)
        t1 = (-B - discrim) / (2 * A)
        t2 = (-B + discrim) / (2 * A)
        # 0 <= t1 <= 1 or 0 <= t2 <= 1
        if (t1 >= 0 and t1 <= 1) or (t2 >= 0 and t2 <= 1):
            return True

        return False

    def is_at_least_one_endpoint_within_radius(self, x1=0, y1=0, x2=0, y2=0):
        d1 = math.sqrt((self.x - x1) * (self.x - x1) +
                       (self.y - y1) * (self.y - y1))
        d2 = math.sqrt((self.x - x2) * (self.x - x2) +
                       (self.y - y2) * (self.y - y2))
        return d1 <= self.r or d2 <= self.r

    def does_obstacle_envelope_edge(self, x1=0, y1=0, x2=0, y2=0):
        """Determine if the obstacle circle completely encircles the
        edge described by two points.

        If two points of a finite line are within the radius of the circle,
        then the entire edge is also within the circle.
        """

        d1 = math.sqrt((self.x - x1) * (self.x - x1) +
                       (self.y - y1) * (self.y - y1))
        d2 = math.sqrt((self.x - x2) * (self.x - x2) +
                       (self.y - y2) * (self.y - y2))
        return d1 <= self.r and d2 <= self.r

    def is_obstacle_on_edge(self, x1=0, y1=0, x2=0, y2=0):
        """Caller function to is_obstacle_on_edge_p"""
        return self.is_obstacle_on_edge_p((x1, y1), (x2, y2))

    def is_obstacle_on_edge_p(self, p1=(0, 0), p2=(0, 0)):
        """Determine if the obstacle circle blocks the edge described by the two points"""

        if len(p1) != 2 or len(p2) != 2:
            raise ValueError(f'Provided points are not in the correct form')

        does_segment_intersect = self.does_line_segment_intersect(
            p1[0], p1[1], p2[0], p2[1])
        is_line_enveloped = self.does_obstacle_envelope_edge(
            p1[0], p1[1], p2[0], p2[1])
        at_least_once = self.is_at_least_one_endpoint_within_radius(
            p1[0], p1[1], p2[0], p2[1])

        return does_segment_intersect or is_line_enveloped or at_least_once


if __name__ == '__main__':
    pass
