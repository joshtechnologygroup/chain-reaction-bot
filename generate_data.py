input_data = []
output_data = []
leaf_nodes_found = 0


from game.game import Game


def get_coordinates(action, game):
    return int(action/game.board.columns), action % game.board.columns


def get_best_move_for(game: Game):
    global leaf_nodes_found
    global input_data
    global output_data
    possible_action = game.get_possible_positions()
    output_data_for_this_game = [0] * game.board.columns * game.board.rows
    action_game_map = {}
    for action in possible_action:
        game1 = game.clone()
        game1.make_move(*get_coordinates(action, game1))
        if game1.check_game_over():
            output_data_for_this_game[action] = 1
            input_data.append(game.toArray())
            output_data.append(output_data_for_this_game)
            leaf_nodes_found += 1
            if leaf_nodes_found % 10000 == 0:
                print('leaf nodes total', leaf_nodes_found, len(input_data), len(input_data) - leaf_nodes_found)
            return True
        action_game_map[action] = game1
    for action in possible_action:
        game1 = action_game_map[action]
        can_opponent_win = get_best_move_for(game1)
        if can_opponent_win:
            output_data_for_this_game[action] = 0
        else:
            output_data_for_this_game[action] = 1
    input_data.append(game.toArray())
    output_data.append(output_data_for_this_game)
    return any(output_data)


get_best_move_for(Game())
print('Total Games', len(output_data) )


import json
json.dump(input_data, open('input.json', 'a'))
json.dump(output_data, open('output.json', 'a'))
