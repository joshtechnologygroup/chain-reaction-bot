"""This is the current driver script to run the project."""
# TODO: later convert this to the game class.

from .board import Board
from .player import Player
import pygame


class Game:

    def __init__(self, title="Chain Reaction"):
        pygame.init()
        pygame.font.init()
        self.SCREEN_WIDTH = 350
        self.SCREEN_HEIGHT = 550
        self.size = [self.SCREEN_WIDTH, self.SCREEN_HEIGHT]
        self.title = title
        self.board = Board()
        self.players_list = [Player(1), Player(-1)]
        self.currentPlayer = self.players_list[0]
        self.screen = None
        self.firstRoundOver = False
        self.clock = pygame.time.Clock()

    def clone(self):
        cloned_game = Game()
        for row in range(self.board.rows):
            for col in range(self.board.columns):
                new_box = cloned_game.board.board[row][col]
                ori_box = self.board.board[row][col]
                props = ['color', 'balls', 'coordinates', 'unstability']
                for prop in props:
                    setattr(new_box, prop, getattr(ori_box, prop))

        for player in cloned_game.players_list:
            if player.id == self.currentPlayer.id:
                cloned_game.currentPlayer = player
                break
        cloned_game.firstRoundOver = self.firstRoundOver

        return cloned_game

    def make_move(self, row, column):
        box = self.board.board[row][column]
        if box.balls == 0 or box.color == self.currentPlayer.color:
            box.balls += 1
            box.color = self.currentPlayer.color
            if box.balls > box.unstability:
                unstables = self.board.unstabilities()
                # print(unstables)
                unstables_resolved_count = 0
                while unstables:
                    unstables_resolved_count += 1
                    # for every unstability
                    for unstable in unstables:
                        # setting balls of unstable to zero
                        unstable.balls = 0

                        # finding the neighbours of the unstable element
                        neighbours = [
                            # up
                            (unstable.coordinates[0] - 1, unstable.coordinates[1]),
                            # down
                            (unstable.coordinates[0] + 1, unstable.coordinates[1]),
                            # left
                            (unstable.coordinates[0], unstable.coordinates[1] - 1),
                            # right
                            (unstable.coordinates[0], unstable.coordinates[1] + 1)
                        ]
                        for row1 in self.board.board:
                            for box1 in row1:
                                if box1.coordinates in neighbours:
                                    box1.balls += 1
                                    # print('balls', box1.balls, box1.coordinates, row, column)
                                    box1.color = unstable.color
                    self._update_player_list()
                    if self.check_game_over():
                        break

                    if unstables_resolved_count > 16:
                        print('unstables_resolved_count: ', unstables_resolved_count, self.check_game_over(), self.firstRoundOver)

                    unstables = self.board.unstabilities()

            for i, player in enumerate(self.players_list):
                if player == self.currentPlayer:
                    self.currentPlayer = self.players_list[(i + 1) % len(self.players_list)]
                    if i + 1 == len(self.players_list):
                        self.firstRoundOver = True
                    # if not i == len(self.players_list) - 1:
                    #     self.currentPlayer = self.players_list[i + 1]
                    # else:
                    #     self.currentPlayer = self.players_list[0]
                    #     self.firstRoundOver = True
                    break
            self.update_screen()
            return True
        else:
            print('tried to make illegal move')
            self.update_screen()
            return False

    def get_possible_positions(self):
        positions = []
        for row in range(self.board.rows):
            for col in range(self.board.columns):
                box = self.board.board[row][col]
                if box.balls == 0 or box.color == self.currentPlayer.color:
                    positions.append(row * self.board.columns + col)

        return positions

    def toArray(self):
        arr = []
        for row in self.board.board:
            row_arr = []
            for box in row:
                if box.balls == 0:
                    row_arr.append(0)
                elif box.color == self.currentPlayer.color:
                    row_arr.append(box.balls)
                else:
                    row_arr.append(box.balls * -1)
            arr.append(row_arr)
        return arr


    def update_screen(self):
        if self.screen:
            for row in self.board.board:
                for box in row:
                    # TODO: make white variable
                    pygame.draw.rect(self.screen, (255, 255, 255), box)
                    if box.balls:
                        for i in range(box.balls):
                            pygame.draw.circle(self.screen,
                                               box.color,
                                               (box.left + self.board.box_size // 3 + i * self.board.box_size // 4,
                                                box.top + self.board.box_size // 2),
                                               5)
            for i in range(self.board.columns + 1):
                pygame.draw.line(self.screen,
                                 self.board.board_lines_color,
                                 (self.board.epoch + i * self.board.box_size,
                                  self.board.epoch),
                                 (self.board.epoch + i * self.board.box_size,
                                  self.board.epoch + self.board.box_size * self.board.rows))
            for i in range(self.board.rows + 1):
                pygame.draw.line(self.screen,
                                 self.board.board_lines_color,
                                 (self.board.epoch,
                                  self.board.epoch + i * self.board.box_size),
                                 (self.board.epoch + self.board.box_size * self.board.columns,
                                  self.board.epoch + i * self.board.box_size))
            self.clock.tick(5)

            pygame.display.flip()


    def _update_player_list(self):
        if self.firstRoundOver:
            remove_list = []
            for player in self.players_list:
                flag = 0
                for row in self.board.board:
                    for box in row:
                        if box.color == player.color and box.balls > 0:
                            flag = 1
                            break
                    else:
                        continue
                    break
                if not flag:
                    remove_list.append(player)
            for remove in remove_list:
                self.players_list.remove(remove)

    def check_game_over(self):
        return len(self.players_list) == 1

    def init_UI(self):
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption(self.title)

    def destroy_UI(self):
        # self.screen = pygame.display.set_mode(self.size)
        # pygame.display.set_caption(self.title)
        pygame.quit()


    def run(self):

        self.screen = pygame.display.set_mode(self.size)

        pygame.display.set_caption(self.title)

        clock = pygame.time.Clock()
        self.update_screen()

        # noOfPlayers = int(input("Enter the number of players: "))

        # ------------Main Game Loop----------------- #
        while not self.check_game_over():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()

                    # search the box handle the click
                    clicked_box = [y for x in self.board.board for y in x if y.collidepoint(pos)]
                    if clicked_box:
                        clicked_box = clicked_box[0]
                        # TODO: put this into a update function later
                        self.make_move(*clicked_box.coordinates)

            # self.update_screen()
            clock.tick(500)

            pygame.display.flip()

        # self.screen.fill((0, 0, 0))
        # myfont = pygame.font.SysFont("Comic Sans MS", 30)
        # myfont2 = pygame.font.SysFont("Comic Sans MS", 15)
        # textsurface = myfont.render("Game Over", False, (255, 0, 0))
        # textsurface2 = myfont2.render("Click anywhere to continue...", False, (255, 255, 255))
        # self.screen.blit(textsurface, (self.SCREEN_WIDTH // 3, self.SCREEN_HEIGHT // 2))
        # self.screen.blit(textsurface2, (self.SCREEN_WIDTH // 3 - 15, self.SCREEN_HEIGHT // 2 + 30))
        # pygame.display.flip()
        # while True:
        #     for event in pygame.event.get():
        #         if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONUP:
        #             break
        #     else:
        #         continue
        #     break
        pygame.quit()

