import numpy as np
import pickle
import os
import utils
from utils import rearrange_vector, next_positions, index_to_number
from utils import writeSmv, runSmv

BOARD_COLS = utils.BOARD_COLS
BOARD_ROWS = utils.BOARD_ROWS
Q_LEARNING = True
Play_Random = False


class State:
    def __init__(self, init_vec=None, p1=None, p2=None, max_turns=50, exp_rate=0):
        self.position = [init_vec[0], init_vec[1]]
        self.p1 = p1
        self.p2 = p2
        self.isEnd = False
        self.boardHash = None
        # init p1 plays first
        self.player_turn = 1  # 1 = Cop, -1 = Rob
        self.counter = 0
        self.max_turns = max_turns
        self.smv = False
        self.exp_rate = exp_rate

    def winner(self):
        if sum(self.position[1], []) in self.position[0]:
            return 1
        if self.counter > self.max_turns:
            return -1
        return None

    def availablePositions(self):
        positions = next_positions(self.player_turn, self.position)
        return positions

    # get unique hash of current board state
    def getHash(self):
        self.boardHash = self.position
        return self.boardHash

    def updateState(self, action):
        if self.player_turn == 1:
            self.position = [action, self.position[1]]
        else:
            self.position = [self.position[0], [action]]
        # switch to another player
        self.player_turn = -1 if self.player_turn == 1 else 1
        self.counter = self.counter + 1

    # only when game ends
    def giveReward(self):
        result = self.winner()
        # backpropagate reward
        if result == 1:
            print("The cop caught the rob\n")
            self.p1.feedReward(100)
            self.p2.feedReward(-100)
        elif result == -1:
            print("The rob managed to escape the cop\n")
            self.p1.feedReward(-100)
            self.p2.feedReward(100)
        else:
            self.p1.feedReward(0)
            self.p2.feedReward(0)

    # board reset
    def reset(self, a_vecs=None, num_of_players=None):
        self.boardHash = None
        self.isEnd = False
        self.player_turn = 1

        writeSmv(num_of_players, BOARD_COLS - 1, self.p1, a_vecs)
        ans, wl_r = runSmv()
        if ans == 'win':
            self.isEnd = True
            self.smv = True
            return
        if Play_Random or np.random.uniform(0, 1) <= self.exp_rate:
            idx = np.random.choice(len(a_vecs))
            action = a_vecs[idx]
        else:
            action = ans
            # pl1.states_value[wl_r] = min(-1, pl1.states_value[wl_r])

        c_action = int(action / 100)
        r_action = int(action % 100)
        l_action = []
        for i in range(int(len(str(c_action)) / 2)):
            n = int(str(c_action)[2 * i: 2 * i + 2])
            l_action.append([int(n / 10), int(n % 10)])
        l_action = [l_action, [[int(r_action / 10), int(r_action % 10)]]]
        self.position = l_action
        self.counter = 0

    def play(self, rounds=100, init_pos=None, a_vecs=None, l_vecs=None, num_of_players=None):
        if init_pos is not None:
            self.position = init_pos
        win_arr = [0, 0]
        for i in range(rounds + 1):
            if i == 0:
                continue
            if i % 1000 == 0 and i > 0:
                print("Rounds {}".format(i))
            if self.smv:
                print("End after {} rounds".format(i))
                break
            self.showBoard(True)
            while not self.isEnd:
                # Player 1
                positions = self.availablePositions()
                if Q_LEARNING:
                    p1_action = self.p1.chooseAction(positions, self.player_turn, self.position)
                else:
                    p1_action = self.p1.chooseAction2(positions, self.player_turn, self.position)
                self.updateState(sum(p1_action, []))
                board_hash = self.getHash()
                self.p1.addState(board_hash)
                self.showBoard()
                win = self.winner()
                if win is not None:
                    self.giveReward()
                    self.p1.reset()
                    self.p2.reset()
                    self.reset(a_vecs, num_of_players)
                    if win == 1:
                        win_arr[0] = win_arr[0] + 1
                    else:
                        win_arr[1] = win_arr[1] + 1
                    break

                else:
                    # Player 2
                    positions = self.availablePositions()
                    if Q_LEARNING:
                        p2_action = self.p2.chooseAction(positions, self.player_turn, self.position)
                    else:
                        p2_action = self.p2.chooseAction2(positions, self.player_turn, self.position)
                    self.updateState(p2_action)
                    board_hash = self.getHash()
                    self.p2.addState(board_hash)
                    self.showBoard()
                    win = self.winner()
                    if win is not None:
                        # self.showBoard()
                        # ended with p2 either win or draw
                        self.giveReward()
                        self.winner()
                        self.p1.reset()
                        self.p2.reset()
                        self.reset(a_vecs, num_of_players)
                        if win == 1:
                            win_arr[0] = win_arr[0] + 1
                        else:
                            win_arr[1] = win_arr[1] + 1
                        break

        return win_arr

    # play with human
    def play2(self):
        while not self.isEnd:
            # Player 1
            positions = self.availablePositions()
            if positions != [0]:
                self.showBoard()
                p1_action = self.p1.chooseAction(positions)
                # take action and update board state
                self.updateState(p1_action)
            # check board status if it is end
            win = self.winner()
            if win is not None:
                if win == 1:
                    print(self.p1.name, "wins!")
                    return 1
                elif win == -1:
                    print(self.p2.name, "wins!")
                    return -1
                else:
                    print("tie!")
                self.reset()
                break

            else:
                # Player 2
                positions = self.availablePositions()
                if positions != [0]:
                    self.showBoard()
                    p2_action = self.p2.chooseAction(positions, self.player_turn, self.position)
                    self.updateState(p2_action)
                    win = self.winner()
                if win is not None:
                    if win == 1:
                        print(self.p1.name, "wins!")
                        return 1
                    elif win == -1:
                        print(self.p2.name, "wins!")
                        return -1
                    else:
                        print("tie!")
                    self.reset()
                    break

    def showBoard(self, initial=False):
        # p1: C  p2: R
        if initial:
            print("Initial state:")
        else:
            print("Cop turn:") if self.player_turn == -1 else print("Rob turn:")
        a = self.position[0]
        b = self.position[1]
        # print('-----')
        out = []
        for i in range(BOARD_ROWS):
            out += [[]]
            for j in range(BOARD_COLS):
                out[i] += ["-"]
        for ap in a:
            out[ap[0]][ap[1]] = 'C'
        if sum(b, []) not in a:
            # if len(sum(b, [])) == 1:
            #     b = sum(b, [])
            out[b[0][0]][b[0][1]] = 'R'
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if i != 0 and j != 0:
                    print(out[i][j], end=" ")
            print("")
        print('\n')


class Player:
    def __init__(self, name, exp_rate=0.3):
        self.name = name
        self.states = []  # record all positions taken
        self.lr = 0.2
        self.exp_rate = exp_rate
        self.decay_gamma = 0.9
        self.states_value = {}  # state -> value

    @staticmethod
    def getHash(board):
        boardHash = str(board.reshape(BOARD_COLS * BOARD_ROWS))
        return boardHash

    def chooseAction(self, positions, pl_turn, current_position):
        if positions is None:
            return sum(current_position[np.maximum(0, -pl_turn)], [])
        idx = np.random.choice(len(positions))
        action = positions[idx]
        if np.random.uniform(0, 1) <= self.exp_rate:
            # take random action
            idx = np.random.choice(len(positions))
            action = positions[idx]
        else:
            value_max = -999
            for p in positions:
                if pl_turn == 1:
                    cop_po = index_to_number(sum(p, []))
                    rob_po = index_to_number(current_position[1])
                else:
                    cop_po = index_to_number(current_position[0])
                    rob_po = index_to_number([p])
                next_boardHash = rearrange_vector(cop_po * 100 + rob_po)
                value = 0 if self.states_value.get(next_boardHash) is None else self.states_value.get(next_boardHash)
                # print("value", value)
                if value >= value_max:
                    value_max = value
                    action = p
        # print("{} takes action {}".format(self.name, action))
        return action

    @staticmethod
    def chooseAction2(positions, pl_turn, current_position):
        if positions is None:
            return sum(current_position[np.maximum(0, -pl_turn)], [])
        idx = np.random.choice(len(positions))
        action = positions[idx]
        if pl_turn == 1:
            opt_value = 100
        else:
            opt_value = 0

        # find the 2 closest
        for p in positions:
            if pl_turn == 1:
                cop_po = sum(p, [])
                rob_po = current_position[1]
            else:
                cop_po = current_position[0]
                rob_po = [p]
            cop_po_x = cop_po[0][0]
            cop_po_y = cop_po[0][1]
            rob_po_x = rob_po[0][0]
            rob_po_y = rob_po[0][1]
            dist = (cop_po_x - rob_po_x) ** 2 + (cop_po_y - rob_po_y) ** 2
            if pl_turn == 1:
                if dist < opt_value:
                    opt_value = dist
                    action = p
            else:
                if dist > opt_value:
                    opt_value = dist
                    action = p
        return action

    # append a hash state
    def addState(self, state):
        state_ul = sum(state, [])
        res_state = 0
        for i in range(len(state_ul)):
            res_state = res_state + index_to_number([state_ul[i]]) * (100 ** (len(state_ul) - i - 1))
        self.states.append(rearrange_vector(res_state))

    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        for sta in reversed(self.states):
            if self.states_value.get(sta) is None:
                self.states_value[sta] = 0
            self.states_value[sta] += self.lr * (self.decay_gamma * reward - self.states_value[sta])
            reward = self.states_value[sta]

    def reset(self):
        self.states = []

    def savePolicy(self, si):
        fw = open('policy_' + si + '_' + str(self.name), 'wb')
        pickle.dump(self.states_value, fw)
        fw.close()

    def loadPolicy(self, file):
        fr = open(file, 'rb')
        self.states_value = pickle.load(fr)
        fr.close()

    def savePolicyCsv(self, numberOfGames):
        filename = f"tests/test_{numberOfGames}.csv"
        if os.path.exists(filename):
            os.remove(filename)
        with open(filename, 'w') as f:
            for key in self.states_value.keys():
                f.write("%s,%s\n" % (key, self.states_value[key]))


class HumanPlayer:
    def __init__(self, name):
        self.name = name

    @staticmethod
    def chooseAction(positions):
        while True:
            print(positions)
            # idx = int(input("Input your action from available positions:"))
            idx = np.random.choice(len(positions))
            action = positions[idx]
            return action

    # append a hash state
    def addState(self, state):
        pass

    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        pass

    def reset(self):
        pass

