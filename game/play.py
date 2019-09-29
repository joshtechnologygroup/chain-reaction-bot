import pygame
from game.game import Game
from game.player import Human, Bot
from keras.models import load_model
import time


def play(player1, player2):
    game = Game()
    game.screen = pygame.display.set_mode(game.size)

    pygame.display.set_caption(game.title)

    clock = pygame.time.Clock()
    game.update_screen()
    player1_won = False

    while not game.check_game_over():
        is_valid_move = False
        while not is_valid_move:
            is_valid_move = game.make_move(*player1.make_move(game))
        game.update_screen()
        # time.sleep(2)

        if game.check_game_over():
            player1_won = True
            break

        is_valid_move = False
        while not is_valid_move:
            is_valid_move = game.make_move(*player2.make_move(game))
        game.update_screen()
        # time.sleep(2)
        clock.tick(500)

        pygame.display.flip()

    game.screen.fill((0, 0, 0))
    myfont = pygame.font.SysFont("Comic Sans MS", 30)
    myfont2 = pygame.font.SysFont("Comic Sans MS", 30)
    textsurface = myfont.render("Game Over.", False, (255, 0, 0))
    textsurface2 = myfont2.render("{} wins.".format('Player1' if player1_won else 'Player2'), False, (255, 255, 255))
    game.screen.blit(textsurface, (game.SCREEN_WIDTH // 3, game.SCREEN_HEIGHT // 2))
    game.screen.blit(textsurface2, (game.SCREEN_WIDTH // 3, game.SCREEN_HEIGHT // 2 + 30))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONUP:
                break
        else:
            continue
        break
    pygame.quit()


play(
    # Human(),
    # Bot(load_model('7775_episodes_2019-09-29 08_15_24.227286.h5')),
    Human(),
    # Bot(load_model('0.h5')),
    Human(),
    # Bot(load_model('7775_episodes_2019-09-29 08_15_24.227286.h5')),

)


