from Class import State, Player
from utils import InitToNumbers, createVecs, writeSmv, INIT, BOARD_ROWS


if __name__ == "__main__":
    max_games = 15000
    numOfPlayers = int(len(InitToNumbers(ret_type=str)) / 2)
    res = st.play(max_games, INIT, a_v, numOfPlayers)
    a_v, l_v = createVecs(numOfPlayers, BOARD_ROWS - 1)
    max_turn = 40
    expRate = 0.3
    pl1 = Player("p1", exp_rate=expRate)
    pl2 = Player("p2", exp_rate=expRate)
    st = State(INIT, pl1, pl2, max_turn)
    res = st.play(max_games, INIT, a_v, l_v, numOfPlayers)
    print(res)
    writeSmv(numOfPlayers, BOARD_ROWS - 1, pl1, a_v)
    print("Number of games:", sum(res))
