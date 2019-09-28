"""The Player class stores all the functions and data related to the Player."""

from pygame import Rect
import pygame
import numpy as np


class Player:
    COLORS = [
        (255, 0, 0),      # Tomato
        # (0, 0, 255),        # Blue
        (60, 179, 113),     # Green
        (238, 130, 238),    # Pink
        (255, 165, 0),      # Orange
        (106, 90, 205)      # Violet
    ]

    def __init__(self, id, color=None):
        self.id = id
        if not color:
            self.color = self.COLORS[id]
        else:
            self.color = color


class Marker(Rect):
    def __init__(self, color):
        self.color = color


class Human:

    def make_move(self, game):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()

                    # search the box handle the click
                    clicked_box = [y for x in game.board.board for y in x if y.collidepoint(pos)]
                    if clicked_box:
                        clicked_box = clicked_box[0]
                        return clicked_box.coordinates


class Bot:
    def __init__(self, nn):
        self.nn = nn

    def make_move(self, game):
        policy, value = self.nn.predict(
            np.array(game.toArray()).reshape(1, game.board.rows, game.board.columns)
        )
        print('policy')
        print(policy)
        print('value', value)
        possible_actions = game.get_possible_positions()
        valids = np.zeros(game.board.rows * game.board.columns)
        np.put(valids, possible_actions, 1)
        policy = policy.reshape(game.board.rows * game.board.columns) * valids
        policy = policy / np.sum(policy)
        action = np.argmax(policy)
        return int(action/game.board.columns), action % game.board.columns
