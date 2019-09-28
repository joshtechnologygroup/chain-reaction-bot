import tensorflow as tf
import keras
from keras import layers
from keras.models import Model, load_model
from keras import models
from keras.optimizers import Adam
import numpy as np
import math
from collections import deque
import os
import re
import time
from datetime import datetime
import h5py
import copy
from game.game import Game

""" 
Functions for game board
"""
ROWS = 5
COLUMNS = 3
ENABLE_UI = False
# hyperparameters
train_episodes = 25
mcts_search = 100
n_pit_network = 1
playgames_before_training = 2
cpuct = 4
training_epochs = 2
learning_rate = 0.001
save_model_path = 'training_dir'
episodes_already_trained = 0
save_nn_after_episodes = 30

# initializing search tree
Q = {}  # state-action values
Nsa = {}  # number of times certain state-action pair has been visited
Ns = {}  # number of times state has been visited
W = {}  # number of total points collected after taking state action pair
P = {}  # initial predicted probabilities of taking certain actions in state



def get_empty_board():
    return Game()


def possiblePos(game):
    return game.get_possible_positions()


def move(game, action):
    game.make_move(int(action/game.board.columns), action % game.board.columns)
    win = game.check_game_over()
    return game, win

""" 
---------------------------------------------------------

Stuff to actually train the model

---------------------------------------------------------
"""

def board_to_array(game):
    return np.array(game.toArray())


def mcts(game):
    possibleA = possiblePos(game)

    sArray = board_to_array(game)
    sTuple = tuple(map(tuple, sArray))

    if sTuple not in P.keys():

        policy, v = nn.predict(sArray.reshape(1, ROWS, COLUMNS))
        v = v[0][0]
        valids = np.zeros(ROWS * COLUMNS)
        np.put(valids, possibleA, 1)
        policy = policy.reshape(ROWS * COLUMNS) * valids
        policy = policy / np.sum(policy)
        P[sTuple] = policy

        Ns[sTuple] = 1

        for a in possibleA:
            Q[(sTuple, a)] = 0
            Nsa[(sTuple, a)] = 0
            W[(sTuple, a)] = 0
        return -v

    best_uct = -100
    for a in possibleA:

        uct_a = Q[(sTuple, a)] + cpuct * P[sTuple][a] * (math.sqrt(Ns[sTuple]) / (1 + Nsa[(sTuple, a)]))

        if uct_a > best_uct:
            best_uct = uct_a
            best_action = a
    next_state, win = move(game, best_action)

    if win:
        v = 1
    else:
        v = mcts(next_state)

    W[(sTuple, best_action)] += v
    Ns[sTuple] += 1
    Nsa[(sTuple, best_action)] += 1
    Q[(sTuple, best_action)] = W[(sTuple, best_action)] / Nsa[(sTuple, best_action)]
    return -v


def get_action_probs(game):
    for _ in range(mcts_search):
        s = game.clone()
        mcts(s)

    actions_dict = {}

    sArray = board_to_array(game)
    sTuple = tuple(map(tuple, sArray))

    for a in possiblePos(game):
        actions_dict[a] = Nsa[(sTuple, a)] / Ns[sTuple]

    action_probs = np.zeros(ROWS * COLUMNS)

    for a in actions_dict:
        np.put(action_probs, a, actions_dict[a], mode='raise')

    return action_probs


def playgame():
    """
    Plays a complete single round of game until any result.
    """
    done = False
    game_mem = []

    real_board = get_empty_board()
    if ENABLE_UI:
        real_board.init_UI()

    while not done:
        policy = get_action_probs(real_board)
        policy = policy / np.sum(policy)
        game_mem.append([board_to_array(real_board), real_board.currentPlayer.id, policy, None])
        action = np.random.choice(len(policy), p=policy)


        next_state, wonBoard = move(real_board, action)
        if wonBoard:
            print('game won by: ', next_state.currentPlayer.id)
            if ENABLE_UI:
                next_state.destroy_UI()
            for tup in game_mem:
                if tup[1] == next_state.currentPlayer.id:
                    tup[3] = 1
                else:
                    tup[3] = -1
            return game_mem


def neural_network():
    input_layer = layers.Input(shape=(ROWS, COLUMNS), name="BoardInput")
    reshape = layers.core.Reshape((ROWS, COLUMNS, 1))(input_layer)
    conv_1 = layers.Conv2D(128, (5, 3), padding='valid', activation='relu', name='conv1')(reshape)
    conv_3 = conv_1

    conv_3_flat = layers.Flatten()(conv_3)

    dense_1 = layers.Dense(512, activation='relu', name='dense1')(conv_3_flat)
    dense_2 = layers.Dense(256, activation='relu', name='dense2')(dense_1)

    pi = layers.Dense(ROWS*COLUMNS, activation="softmax", name='pi')(dense_2)
    v = layers.Dense(1, activation="tanh", name='value')(dense_2)

    model = Model(inputs=input_layer, outputs=[pi, v])
    model.compile(loss=['categorical_crossentropy', 'mean_squared_error'], optimizer=Adam(learning_rate))

    model.summary()
    return model


def train_nn(nn, game_mem):
    print("Training Network")
    print("lenght of game_mem", len(game_mem))

    state = []
    policy = []
    value = []

    for mem in game_mem:
        state.append(mem[0])
        policy.append(mem[2])
        value.append(mem[3])

    state = np.array(state)
    policy = np.array(policy)
    value = np.array(value)

    nn.fit(state, [policy, value], batch_size=32, epochs=training_epochs, verbose=1)


def pit(nn, new_nn):
    # function pits the old and new networks. If new network wins, then return True
    print("Pitting networks")
    nn_wins = 0
    new_nn_wins = 0

    for _ in range(n_pit_network):

        game = get_empty_board()

        while True:

            policy, v = nn.predict(board_to_array(game).reshape(1, ROWS, COLUMNS))
            valids = np.zeros(ROWS * COLUMNS)

            possibleA = possiblePos(game)

            if len(possibleA) == 0:
                break

            np.put(valids, possibleA, 1)
            policy = policy.reshape(ROWS * COLUMNS) * valids
            policy = policy / np.sum(policy)
            action = np.argmax(policy)

            next_state, win = move(game, action)
            game = next_state

            if win:
                nn_wins += 1
                break

            # new nn makes move

            policy, v = new_nn.predict(board_to_array(game).reshape(1, ROWS, COLUMNS))
            valids = np.zeros(ROWS * COLUMNS)

            possibleA = possiblePos(game)
            if len(possibleA) == 0:
                break

            np.put(valids, possibleA, 1)
            policy = policy.reshape(ROWS * COLUMNS) * valids
            policy = policy / np.sum(policy)
            action = np.argmax(policy)

            next_state, win = move(game, action)
            game = next_state

            if win:
                new_nn_wins += 1
                break

    win_percent = float(new_nn_wins) / float(new_nn_wins + nn_wins)
    if win_percent > 0.52:
        print("The new network won by ", win_percent)
        return True
    else:
        print("The new network lost. Win percent: ", win_percent)
        return False

def save_nn(nnet, train_episodes):
    now = datetime.utcnow()
    filename = '{}_episodes_{}.h5'.format(train_episodes, now)
    nnet.save(os.path.join(save_model_path, filename))
    print('network saved')


def initNN():
    global nn
    global episodes_already_trained
    episodes_already_trained = 0
    max_episodes_file_name = ''
    try:
        files = os.listdir(save_model_path)
    except Exception:
        nn = neural_network()
        episodes_already_trained = 0
    else:
        for file_name in files:
            numbers = re.findall(r'(\d+)', file_name)
            if numbers:
                episodes_trained = int(numbers[0])
                if episodes_trained > episodes_already_trained:
                    episodes_already_trained = episodes_trained
                    max_episodes_file_name = file_name
        if max_episodes_file_name:
            nn = load_model(os.path.join(save_model_path, max_episodes_file_name))
            print('loaded: ', max_episodes_file_name)
        else:
            nn = neural_network()
            episodes_already_trained = 0
    return nn


def augment_game_memory(mem):
    new_memory = []
    for ele in mem:
        new_memory.append(ele)
        new_memory.append([np.flip(np.copy(ele[0], 2), 0), ele[1], ele[2], ele[3]])
        new_memory.append([np.flip(np.copy(ele[0], 2), 1), ele[1], ele[2], ele[3]])
        new_memory.append([np.flip(np.copy(ele[0], 2), (0, 1)), ele[1], ele[2], ele[3]])

    return new_memory


# nn = neural_network()
nn = initNN()


def train():
    global nn
    global Q
    global Nsa
    global Ns
    global W
    global P
    global episodes_already_trained

    game_mem = []

    for episode in range(1, train_episodes + 1):
        episode_start_time = datetime.now()
        print('running episode: ', episode)
        nn.save('temp.h5')
        old_nn = models.load_model('temp.h5')

        for _ in range(playgames_before_training):
            # game_mem += augment_game_memory(playgame())
            game_mem += playgame()

        train_nn(nn, game_mem)
        game_mem = []
        if pit(old_nn, nn):
            del old_nn
            Q = {}
            Nsa = {}
            Ns = {}
            W = {}
            P = {}
        else:
            nn = old_nn
            del old_nn
        print('Total time for episode {} is: '.format(episode), (datetime.now() - episode_start_time).seconds)
        if (episode % save_nn_after_episodes) == 0:
            save_nn(nn, episode + episodes_already_trained)

    save_nn(nn, train_episodes + episodes_already_trained)


train()
