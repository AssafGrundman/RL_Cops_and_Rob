from Class import State, Player
from utils import InitToNumbers, createVecs, writeSmv, INIT, BOARD_ROWS
from datetime import datetime

expRate = 0
max_turn = 50
NumOfIteration = 1
Results = []

if __name__ == "__main__":

    for i in range(NumOfIteration):
        max_games = 15000
        numOfPlayers = int(len(InitToNumbers(ret_type=str)) / 2)  # Number of players derive from initial vector
        max_turn = 40  # ! Not in use
        expRate = 0.3  # rate [ 0-1 ] the agent explore new action without leaning on Q-table
        pl1 = Player("p1", exp_rate=expRate)  # create first Player class (Class.py)
        pl2 = Player("p2", exp_rate=expRate)  # create second Player class (Class.py)
        st = State(INIT, pl1, pl2, max_turn)  # create new variable, st, in form of State class (Class.py)
        a_v, l_v = createVecs(numOfPlayers, BOARD_ROWS - 1)  # a_v - full list of possible state vectors
                                                             # l_v - shorter list with group of vectors that span the board dimensions
        res = st.play(max_games, INIT, a_v, l_v, numOfPlayers)
        print(res)
        print("Number of games:", sum(res))
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        Results.append(current_time)
        Results.append(res)

    print(Results)

    now = datetime.now()
    fname = 'Results_BR5_RANDOM_FALSE.txt'
    with open(fname, 'w') as fw:
        for item in Results:
            fw.write("%s\n" % item)

