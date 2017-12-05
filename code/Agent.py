from Environment import Point
import math


class Agent:
    k = 120000
    kappa = 24000

    def __init__(self, size, mass, pos, goal, desiredSpeed=4):
        # the constants
        self.A = 2000
        self.B = 0.08
        self.tau = 0.5
        # instance variables
        self.size = size  # radius
        self.mass = mass
        self.pos = pos  # current position: Point object
        self.velocity = Point(0, 0)  # current velocity: Point object
        self.desiredSpeed = desiredSpeed  # preferred speed: float
        self.goal = goal  # exit: Goal object
        # TODO: add maximum of velocity?

    @property
    def desiredDirection(self):
        """ Calculates the unit vector pointing towards the goal. """
        p1 = self.goal.parameters['p1']
        p2 = self.goal.parameters['p2']

        # Test if vertical or horizontal
        if p1.x == p2.x:
            if self.pos.y < p1.y:
                return self.vectorTo(p1).norm()

            elif self.pos.y > p2.y:
                return self.vectorTo(p2).norm()

            else:
                direction = 1 if self.pos.x < p1.x else -1
                return Point(direction, 0)
        else:
            if self.pos.x < p1.x:
                return self.vectorTo(p1).norm()

            elif self.pos.x > p2.x:
                return self.vectorTo(p2).norm()

            else:
                direction = 1 if self.pos.y < p1.y else -1
                return Point(0, direction)

    def vectorTo(self, point):
        return point - self.pos

    def move(self, force):
        """ update step - move to goal during unit time """
        time = 1  # TODO: needed to define in simulator
        self.pos = self.pos + self.velocity * time
        self.velocity = self.velocity + force / self.mass * time

    def wallForce(self, wall):
        if wall.wallType == 'line':
            p1 = wall.parameters["p1"]
            p2 = wall.parameters["p2"]
            r = self.vectorTo(p1)
            wallLine = (p2 - p1).norm()
            normalUnitVector = Point(-wallLine.y, wallLine.x)  # rotate 90 degrees counterclockwise
            temp = dotProduct(r, normalUnitVector)
            if temp > 0:  # perpendicular
                normalUnitVector.x *= -1
                normalUnitVector.y *= -1
            elif temp == 0:
                normalUnitVector = -r.norm()

            if dotProduct(self.velocity, wallLine) >= 0:
                tangentUnitVector = wallLine
            else:
                tangentUnitVector = -wallLine
            distance = -dotProduct(r, normalUnitVector)

        else:  # wallType : circle
            normalUnitVector = (self.pos - wall.parameters["center"]).norm()
            tangentLine = Point(-normalUnitVector.y, normalUnitVector.x)  # rotate 90 degrees counterclockwise
            if dotProduct(self.velocity, tangentLine) >= 0:
                tangentUnitVector = tangentLine
            else:
                tangentUnitVector = -tangentLine
            distance = (self.pos - wall.parameters["center"]).mag - wall.parameters["radius"]

        overlap = self.size - distance

        # psychological force
        psyForce = self.psychologicalForce(overlap)

        if overlap > 0:  # if
            # young and tangential force
            youngForce = self.youngForce(overlap)
            tangentForce = self.tangentialForce(overlap, self.velocity, tangentUnitVector)
        else:
            youngForce = 0
            tangentForce = 0

        return (psyForce + youngForce) * normalUnitVector - tangentForce * tangentUnitVector

    def pairForce(self, other):
        displacement = self.pos - other.pos
        overlap = self.size + other.size - displacement.mag
        normalUnitVector = (self.pos - other.pos).norm()
        tangentUnitVector = Point(-normalUnitVector.y, normalUnitVector.x)

        # psychological force
        psyForce = self.psychologicalForce(overlap)
        # young and tangential force
        if overlap > 0: # if distance is shorter than radius
            youngForce = self.youngForce(overlap)
            tangentForce = self.tangentialForce(overlap, other.velocity - self.velocity, tangentUnitVector)
        else:
            youngForce = 0
            tangentForce = 0

        return (psyForce + youngForce) * normalUnitVector + tangentForce * tangentUnitVector

    def selfDriveForce(self):
        desiredVelocity = self.desiredDirection * self.desiredSpeed
        return self.mass * (desiredVelocity - self.velocity) / self.tau

    # scalar function for the magnitude of force
    def psychologicalForce(self, overlap):
        return self.A * math.exp(overlap / self.B)

    @classmethod
    def youngForce(cls, overlap):  # overlap > 0
        return cls.k * overlap

    @classmethod
    def tangentialForce(cls, overlap, tangVeloDiff, tangDirection):  # overlap > 0
        return cls.kappa * overlap * dotProduct(tangVeloDiff, tangDirection) * tangDirection


def dotProduct(vec1, vec2):
    return vec1.x * vec2.x + vec1.y * vec2.y
