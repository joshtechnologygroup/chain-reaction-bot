"""The Board Class stores and performs all board functions."""

from pygame import Rect


class Board:

    def __init__(self, box_size=50, epoch=20, rows=5, columns=3, board_lines_color=(255, 0, 0)):
        self.epoch = epoch
        self.box_size = box_size
        self.rows = rows
        self.columns = columns
        self.board_lines_color = board_lines_color

        self.board = []
        for i in range(rows):
            row = []
            for j in range(columns):
                unstability = 3
                if i == 0 or i == rows - 1 or j == 0 or j == columns - 1:
                    unstability = 2
                if i % (rows - 1) == 0 and j % (columns - 1) == 0:
                    unstability = 1

                row.append(Box(j * box_size + epoch,
                               i * box_size + epoch,
                               box_size,
                               box_size,
                               (i, j),
                               unstability))
            self.board.append(row)


    def printBoard(self):
        for row in self.board:
            print(row[0].value, row[1].value, row[2].value)

    def unstabilities(self):
        explosions = []
        for row in self.board:
            for elem in row:
                if elem.balls > elem.unstability:
                    explosions.append(elem)
        return explosions


class Box(Rect):
    # TODO: think whether unstability boolean or number_of_balls is better for updating the game
    def __init__(self, left, top, width, height, coordinates, unstability, balls=0, color=None):
        super().__init__(left, top, width, height)
        self.balls = balls
        self.coordinates = coordinates
        self.unstability = unstability
        self.color = color

    @property
    def value(self):
        return self.balls

    def __str__(self):
        return '{}-{}'.format(self.balls, self.color)