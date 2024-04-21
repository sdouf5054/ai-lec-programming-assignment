import re
import numpy as np
from copy import copy, deepcopy
import random 
import time
from inputimeout import inputimeout, TimeoutOccurred

TIMEOUT = 5
start_time = 0

board_width, board_height = 19, 19
board = np.full((board_width, board_height), -1)

inf = 9999999999
neg_inf = -9999999999

NO_STONE = -1
BLACK = 0
WHITE = 1
OMOK = 5

turn_count = 0
player = 0

stone_on_board = [[], []]
connected = [[], []]
max_connected = [0, 0]


def clear_board(board):
    # Clear the board
    board.fill(NO_STONE)


def clear_game(board, stone_on_board, connected, max_connected):
    # Clear the game
    clear_board(board)
    stone_on_board[BLACK].clear()
    stone_on_board[WHITE].clear()
    connected[BLACK].clear()
    connected[WHITE].clear()
    max_connected[BLACK] = 0
    max_connected[WHITE] = 0
    global player
    player = BLACK
    global turn_count
    turn_count = 0


def display_board(turn, turn_num, board):
    player = "None" if (turn_num == 0) else ("Black" if turn == BLACK else "White")
    print(f"------Player: {player} - Turn Number: {turn_num}------")
    print(" " + "".join([f"{i+1:02d}" for i in range(board_width)]))
    for i, row in enumerate(board):
        row_str = f"{chr(65 + i)} "
        for stone in row:
            if stone == -1:
                row_str += "* "
            elif stone == 0:
                row_str += "○ "
            elif stone == 1:
                row_str += "● "
        print(row_str)
    print("------")


def check_valid(loc_tuple):
    loc_x, loc_y = loc_tuple
    return 1 <= loc_x <= 19 and 1 <= loc_y <= 19


def trans_location(loc_xnput):
    loc_xnput = loc_xnput.upper()
    # input값 string A19, J01 등을 받아서 x,y좌표값으로 변환. A19 -> (19, 1), S01 -> (1, 19)
    pattern = r"\s*([A-S])(\d{2})\s*"
    match = re.match(pattern, loc_xnput)

    if match:
        letter, numbers = match.groups()
        loc_x = int(numbers)
        loc_y = ord(letter) - ord('A') + 1

        loc_tuple = (loc_x, loc_y)
        if check_valid(loc_tuple):  # Utilize the check_valid function
            return loc_tuple
        else:
            print("Invalid format of input. Please write it in A-S/01-19.")
            return False
    else:
        print("Invalid format of input. Please write it in \"X00\" form.")
        return False

def retrans(loc_tuple):
    loc_x, loc_y = loc_tuple
    letter = chr(loc_y + ord('A') - 1)
    numbers = str(loc_x).zfill(2)
    return f"{letter}{numbers}"

def take_stone(turn, game_board, game_stone_on_board, new_loc):
    check_valid(new_loc)
    loc_x, loc_y = new_loc

    if game_board[loc_y - 1][loc_x - 1] != NO_STONE:
        print("The location is already occupied. Please choose another location.")
        return False

    game_board[loc_y - 1][loc_x - 1] = turn

    game_stone_on_board[turn].append((loc_x, loc_y))
    return True


def checkHorizontalOmok(state, loc_x, loc_y, player, connection_list, max_cnt_num):
    count = 0
    cnt = []
    tail_list = []
    wins = None

    for j in range(loc_x, loc_x + OMOK - count):
        if j > board_width - 1:
            break
        if state[loc_y - 1][j] == (BLACK if player == BLACK else WHITE):
            count += 1
            cnt.append((j + 1, loc_y))
            if count == OMOK:
                wins = True
        else:
            if state[loc_y - 1][j] == NO_STONE:
                tail_list.append((j + 1, loc_y))
            break

    for j in range(loc_x - 1, -1, -1):
        if j < 0:
            break
        if state[loc_y - 1][j] == (BLACK if player == BLACK else WHITE):
            count += 1
            cnt.append((j + 1, loc_y))
            if count == OMOK:
                wins = True
        else:
            if state[loc_y - 1][j] == NO_STONE:
                tail_list.append((j + 1, loc_y))
            break

    if len(cnt) > 1:
        tmp_list = [connection for connection in connection_list[player]
                    if not set(connection[0]).issubset(set(cnt))]
        connection_list[player] = tmp_list      
        connection_list[player].append((cnt, tail_list))

    opponent = WHITE if player == BLACK else BLACK
    for idx, (connected, tails) in enumerate(connection_list[opponent]):
        if (loc_x, loc_y) in tails:
            connection_list[opponent][idx] = (connected, [tail for tail in tails if tail != (loc_x, loc_y)])

    max_cnt_num[player] = count if max_cnt_num[player] < count else max_cnt_num[player]
    if wins:
        return True
    else:
        return False

def checkVerticalOmok(state, loc_x, loc_y, player, connection_list, max_cnt_num):
    count = 0
    cnt = []
    tail_list = []
    wins = None

    for i in range(loc_y - 1, -1, -1):
        if i < 0:
            break
        if state[i][loc_x - 1] == (BLACK if player == BLACK else WHITE):
            count += 1
            cnt.append((loc_x, i + 1))
            if count == OMOK:
                wins = True
        else:
            if state[i][loc_x - 1] == NO_STONE:
                tail_list.append((loc_x, i + 1))
            break

    for i in range(loc_y, loc_y + OMOK - count):
        if i > board_height - 1:
            break
        if state[i][loc_x - 1] == (BLACK if player == BLACK else WHITE):
            count += 1
            cnt.append((loc_x, i + 1))
            if count == OMOK:
                wins = True
        else:
            if state[i][loc_x - 1] == NO_STONE:
                tail_list.append((loc_x, i + 1))
            break

    if len(cnt) > 1:
        tmp_list = [connection for connection in connection_list[player]
                    if not set(connection[0]).issubset(set(cnt))]
        connection_list[player] = tmp_list

        connection_list[player].append((cnt, tail_list))
    
    opponent = WHITE if player == BLACK else BLACK
    for idx, (connected, tails) in enumerate(connection_list[opponent]):
        if (loc_x, loc_y) in tails:
            connection_list[opponent][idx] = (connected, [tail for tail in tails if tail != (loc_x, loc_y)])

    max_cnt_num[player] = count if max_cnt_num[player] < count else max_cnt_num[player]
    if wins:
        return True
    else:
        return False

def checkFirstDiagOmok(state, loc_x, loc_y, player, connection_list, max_cnt_num):
    count = 0
    cnt = []
    tail_list = []
    wins = None

    for d in range(0, OMOK):
        if loc_y - 1 - d < 0 or loc_x - 1 + d > board_width - 1:
            break
        if state[loc_y - 1 - d][loc_x - 1 + d] == (BLACK if player == BLACK else WHITE):
            count += 1
            cnt.append((loc_x + d, loc_y - d))
            if count == OMOK:
                wins = True
        else:
            if state[loc_y - 1 - d][loc_x - 1 + d] == NO_STONE:
                tail_list.append((loc_x + d, loc_y - d))
            break

    for d in range(1, OMOK):
        if loc_y - 1 + d > board_height - 1 or loc_x - 1 - d < 0:
            break
        if state[loc_y - 1 + d][loc_x - 1 - d] == (BLACK if player == BLACK else WHITE):
            count += 1
            cnt.append((loc_x - d, loc_y + d))
            if count == OMOK:
                wins = True
        else:
            if state[loc_y - 1 + d][loc_x - 1 - d] == NO_STONE:
                tail_list.append((loc_x - d, loc_y + d))
            break

    if len(cnt) > 1:
        tmp_list = [connection for connection in connection_list[player]
                    if not set(connection[0]).issubset(set(cnt))]
        connection_list[player] = tmp_list

        connection_list[player].append((cnt, tail_list))
    
    opponent = WHITE if player == BLACK else BLACK
    for idx, (connected, tails) in enumerate(connection_list[opponent]):
        if (loc_x, loc_y) in tails:
            connection_list[opponent][idx] = (connected, [tail for tail in tails if tail != (loc_x, loc_y)])

    max_cnt_num[player] = count if max_cnt_num[player] < count else max_cnt_num[player]
    if wins:
        return True
    else:
        return False

def checkSecondDiagOmok(state, loc_x, loc_y, player, connection_list, max_cnt_num):
    count = 0
    cnt = []
    tail_list = []
    wins = None

    for d in range(0, OMOK):
        if loc_y - 1 - d < 0 or loc_x - 1 - d < 0:
            break
        if state[loc_y - 1 - d][loc_x - 1 - d] == (BLACK if player == BLACK else WHITE):
            count += 1
            cnt.append((loc_x - d, loc_y - d))
            if count == OMOK:
                wins = True
        else:
            if state[loc_y - 1 - d][loc_x - 1 - d] == NO_STONE:
                tail_list.append((loc_x - d, loc_y - d))
            break

    for d in range(1, OMOK):
        if loc_y - 1 + d > board_height - 1 or loc_x - 1 + d > board_height - 1:
            break
        if state[loc_y - 1 + d][loc_x - 1 + d] == (BLACK if player == BLACK else WHITE):
            count += 1
            cnt.append((loc_x + d, loc_y + d))
            if count == OMOK:
                wins = True
        else:
            if state[loc_y - 1 + d][loc_x - 1 + d] == NO_STONE:
                tail_list.append((loc_x + d, loc_y + d))
            break

    if len(cnt) > 1:
        tmp_list = [connection for connection in connection_list[player]
                    if not set(connection[0]).issubset(set(cnt))]
        connection_list[player] = tmp_list

        connection_list[player].append((cnt, tail_list))
    
    opponent = WHITE if player == BLACK else BLACK
    for idx, (connected, tails) in enumerate(connection_list[opponent]):
        if (loc_x, loc_y) in tails:
            connection_list[opponent][idx] = (connected, [tail for tail in tails if tail != (loc_x, loc_y)])

    max_cnt_num[player] = count if max_cnt_num[player] < count else max_cnt_num[player]
    if wins:
        return True
    else:
        return False

def checkOmok(state, new_loc, player, connection_list, max_cnt_num):
    loc_x, loc_y = new_loc
    isOmok = False
    if checkHorizontalOmok(state, loc_x, loc_y, player, connection_list, max_cnt_num):
        isOmok = True
    if checkVerticalOmok(state, loc_x, loc_y, player, connection_list, max_cnt_num):
        isOmok = True
    if checkFirstDiagOmok(state, loc_x, loc_y, player, connection_list, max_cnt_num):
        isOmok = True
    if checkSecondDiagOmok(state, loc_x, loc_y, player, connection_list, max_cnt_num):
        isOmok = True
    return isOmok

def pre_rule(player, connected_list, max_connected):
    opponent = WHITE if player == BLACK else BLACK
    connected = deepcopy(connected_list[player])
    opponent_connected = deepcopy(connected_list[opponent])
    if max_connected[opponent] < 3:
        return False
    else:      
        for connected_pair, opened in connected:
            if len(connected_pair) >= 4 and len(opened) >= 1:
                tail_x, tail_y = random.choice(opened)
                return tail_x, tail_y
        for connected_pair, opened in opponent_connected:
            if len(connected_pair) >= 4 and len(opened) == 1:
                tail_x, tail_y = random.choice(opened)
                return tail_x, tail_y
        # for connected_pair, opened in connected:
        #     if len(connected_pair) == 3 and len(opened) == 2:
        #         tail_x, tail_y = random.choice(opened)
        #         return tail_x, tail_y
        for connected_pair, opened in opponent_connected:
            if len(connected_pair) == 3 and len(opened) == 2:
                tail_x, tail_y = random.choice(opened)
                return tail_x, tail_y
        # for connected_pair, opened in opponent_connected:
        #     if len(connected_pair) >= 4 and len(opened) == 2:
        #         tail_x, tail_y = random.choice(opened)
        #         return tail_x, tail_y
        
    return False

def check_connection(player, connection_list):
    cur_player = player
    score = 0

    if cur_player == BLACK:
        for connected_pair, opened in connection_list[BLACK]:
            if len(opened) == 0 and len(connected_pair) < 5:
                continue
            elif len(connected_pair) == 2:
                if len(opened) == 2:
                    score += 20
                else: score +=5
            elif len(connected_pair) == 3:
                if len(opened) == 2:
                    score += 100
                else: score +=10
            elif len(connected_pair) == 4:
                if len(opened) == 2:
                    score += 7777
                else: score +=50
            elif len(connected_pair) == 5:
                score += 999999999
            else:
              continue

    else:
        for connected_pair, opened in connection_list[WHITE]:
            if len(opened) == 0 and len(connected_pair) < 5:
                continue
            elif len(connected_pair) == 2:
                if len(opened) == 2:
                    score -= 20
                else: score -=5
            elif len(connected_pair) == 3:
                if len(opened) == 2:
                    score -= 100
                else: score -=10
            elif len(connected_pair) == 4:
                if len(opened) == 2:
                    score -= 7777
                else: score -=50
            elif len(connected_pair) == 5:
                score -= 999999999
            else:
              continue

    return score


def eval(board, player, connected, max_connected, loc_x, loc_y):

    heuristic = 0
    checking_cnt_list = deepcopy(connected)
    
    heuristic = check_connection(BLACK, checking_cnt_list) + check_connection(WHITE, checking_cnt_list)

    return heuristic


def minimax(state, connected, max_connected, alpha, beta, maximizing_p, depth, new_x, new_y):
    global start_time
    # Find the available positions in the state where a move can be made
    rowsLeft, columnsLeft = np.where(state == -1)
    player = BLACK if maximizing_p else WHITE
    
    # Base case: if depth reaches 0, return the utility of the current state
    if depth == 0:
        if (new_x or new_y) is None:
            print('youshouldsetdepthmorethanthis')
            random_index = random.randrange(len(rowsLeft))
            new_x, new_y = rowsLeft[random_index] , columnsLeft[random_index] 
        return eval(state, player, connected, max_connected, new_x, new_y), new_x, new_y
    # Time set.
    if time.time() - start_time >= TIMEOUT:
        return eval(state, player, connected, max_connected, new_x, new_y), new_x, new_y

    # Create a copy of the state to be returned
    return_x, return_y = new_x, new_y

    # If there are no more available positions or the game is over, return the utility of the current state
    if rowsLeft.shape[0] == 0:
        return eval(state, player, connected, max_connected, return_x, return_y), return_x, return_y

    if maximizing_p:
        utility = neg_inf
        for i in range(0, rowsLeft.shape[0]):
            nextState = deepcopy(state)
            nextConnected = deepcopy(connected)
            nextMaxNum = copy(max_connected)
            for k in range(0, rowsLeft.shape[0]): # Choose random location in the board not occupied
                j = random.randrange(0, rowsLeft.shape[0])
                if nextState[columnsLeft[j]-1, rowsLeft[j]-1] == NO_STONE:  # Check if the location is already occupied
                    break
            nextState[columnsLeft[j]-1][rowsLeft[j]-1] = BLACK
            next_x, next_y = rowsLeft[j], columnsLeft[j]
            next_loc = (next_x, next_y)
            checkOmok(nextState, next_loc, BLACK, nextConnected, nextMaxNum)
            Nutility, Nx, Ny = minimax(nextState, nextConnected, max_connected, alpha, beta, False, depth - 1, next_x, next_y)

            if Nutility > utility:
                utility = Nutility
                return_x, return_y = next_x, next_y

            if utility > alpha:
                alpha = utility

            if alpha >= beta:
                break

        return utility, return_x, return_y

    else:
        utility = inf
        for i in range(0, rowsLeft.shape[0]):
            nextState = deepcopy(state)
            nextConnected = deepcopy(connected)
            nextMaxNum = copy(max_connected)
            for k in range(0, rowsLeft.shape[0]):
                j = random.randrange(0, rowsLeft.shape[0])
                if nextState[columnsLeft[j]-1, rowsLeft[j]-1] == NO_STONE:
                    break
            nextState[columnsLeft[j]-1][rowsLeft[j]-1] = WHITE
            next_x, next_y = rowsLeft[j], columnsLeft[j]
            next_loc = (next_x, next_y)
            checkOmok(nextState, next_loc, WHITE, nextConnected, nextMaxNum)
            Nutility, Nx, Ny = minimax(nextState, nextConnected, max_connected, alpha, beta, True, depth - 1, next_x, next_y)

            if Nutility < utility:
                utility = Nutility
                return_x, return_y = next_x, next_y

            if utility < beta:
                beta = utility

            if alpha >= beta:
                break

        return utility, return_x, return_y


clear_game(board, stone_on_board, connected, max_connected)
display_board(player, turn_count, board)

while (1):
    gamemode = input('Choose gamemode | 1: 2p play | 2: 1p vs. AI | 3: AI vs. AI | \n==>')
    if gamemode in ['1', '2', '3']:
        gamemode = int(gamemode)
        break  # Break out of the loop if the input is valid
    else:
        print("Invalid input. Please enter 1, 2, or 3.")


if gamemode == 1:
    while (1):
        playing_color = 'Black' if player == 0 else 'White'
        try:
            cur_in = inputimeout(
                prompt=f"now turn: {turn_count + 1} - now play {playing_color} TIMEOUT:{TIMEOUT}"
                    f"=> insert the location form of \"X00\"\n(quit: /q, regame: /r)\n->", timeout=TIMEOUT)
        except TimeoutOccurred:
            print("Time's up! No input received.")
            # 다음 플레이어의 턴으로 넘김
            player = WHITE if player == BLACK else BLACK
            continue
        if (cur_in == '/q'):
            clear_game(board, stone_on_board, connected, max_connected)
            print("see ya.")
            break
        elif (cur_in == '/r'):
            clear_game(board, stone_on_board, connected, max_connected)
            display_board(player, turn_count, board)
        else:
            new_location = trans_location(cur_in)
            if not new_location:
                continue
            if take_stone(player, board, stone_on_board, new_location):
                turn_count += 1
                display_board(player, turn_count, board)
                if checkOmok(board, new_location, player, connected, max_connected):
                    for pairs in connected[player]:
                        if len(pairs) == 5:  # Check for winning connections (length 5)
                            print("Winning connected coordinates:")
                            for coord in pairs:
                                print(coord, end=' ')
                            print('')
                    winner = "None" if (turn_count == 0) else ("Black" if player == BLACK else "White")
                    print(f"{winner} is Winner!  - Turn Number: {turn_count}") 
                    break
                # print(f'connected: {connected}')
                # print(f'max_connected: {max_connected}')

                player = WHITE if player == BLACK else BLACK
elif gamemode == 2:    
    while (1):
        playable = input('Choose your color - 1:Black 2:White\n==>')
        if playable in ['1', '2']:
            playable = BLACK if playable == '1' else WHITE
            break
        else:
            print("Invalid input. Please enter 1, 2")

    while (1):
        playing_color = 'Black' if player == 0 else 'White'
        if player == playable:
            try:
                cur_in = inputimeout(
                    prompt=f"now YOUR turn. | turn #{turn_count + 1} - play as {playing_color} | TIMEOUT:{TIMEOUT} "
                        f"=> insert the location form of \"X00\"\n(quit: /q, regame: /r)\n->", timeout=TIMEOUT)
            except TimeoutOccurred:
                print("Time's up! No input received.")
                # 다음 플레이어의 턴으로 넘김
                player = WHITE if player == BLACK else BLACK
                continue
            if (cur_in == '/q'):
                clear_game(board, stone_on_board, connected, max_connected)
                print("see ya.")
                break
            elif (cur_in == '/r'):
                clear_game(board, stone_on_board, connected, max_connected)
                display_board(player, turn_count, board)
                player = BLACK
                continue
            else:
                new_loc = trans_location(cur_in)
                if not new_loc:
                    continue
        else: 
            start_time = time.time()
            print(f"now AI turn... | turn #{turn_count + 1} - play as {playing_color} | TIMEOUT:{TIMEOUT}")
            state = np.copy(board)
            cnt_list = deepcopy(connected)
            oppP = False if playable == BLACK else True
            max_num = max_connected
            if pre_rule(player, cnt_list, max_connected):
                next_x, next_y = pre_rule(player, cnt_list, max_num)
            else: 
                value, next_x, next_y = minimax(state, cnt_list, max_num, neg_inf, inf, oppP, 3, None, None)      
            debug_loc = (next_x, next_y)
            retrans(debug_loc)
            print("AI's move:", retrans(debug_loc))           
            new_loc = (next_x, next_y)

        if take_stone(player, board, stone_on_board, new_loc):
            turn_count += 1
            display_board(player, turn_count, board)
            if checkOmok(board, new_loc, player, connected, max_connected):
                for pairs in connected[player]:
                    if len(pairs) == 5:  
                        print("Winning connected coordinates:")
                        for coord in pairs:
                            print(coord, end=' ')
                        print('')
                winner = "None" if (turn_count == 0) else ("Black" if player == BLACK else "White")
                print(f"{winner} is Winner!  - Turn Number: {turn_count}")
                break
            player = WHITE if player == BLACK else BLACK
    
elif gamemode == 3: 
    while(1):
        start_time = time.time()
        if turn_count % 2 == 0:  # AI 1's turn
            player = BLACK
            print(f"Now AI_1 turn... | turn #{turn_count + 1} - play as Black | TIMEOUT:{TIMEOUT}")
            state = np.copy(board)
            cnt_list = deepcopy(connected)
            max_num = max_connected
            if pre_rule(player, cnt_list, max_connected):
                next_x, next_y = pre_rule(player, cnt_list, max_num)
            else: 
                value, next_x, next_y = minimax(state, cnt_list, max_num, neg_inf, inf, True, 3, None, None)      
            debug_loc = (next_x, next_y)
            retrans(debug_loc)
            print("AI_1's move:", retrans(debug_loc))
        else:  # AI 2's turn
            player = WHITE
            print(f"Now AI_2 turn... | turn #{turn_count + 1} - play as White | TIMEOUT:{TIMEOUT}")
            state = np.copy(board)
            cnt_list = deepcopy(connected)
            max_num = max_connected
            if pre_rule(player, cnt_list, max_num):
                next_x, next_y = pre_rule(player, cnt_list, max_num)
            else: 
                value, next_x, next_y = minimax(state, cnt_list, max_num, neg_inf, inf, False, 3, None, None)
            debug_loc = (next_x, next_y)
            retrans(debug_loc)
            print("AI_2's move:", retrans(debug_loc))

        new_loc = (next_x, next_y)
        if take_stone(player, board, stone_on_board, new_loc):
            turn_count += 1
            display_board(player, turn_count, board)
            if checkOmok(board, new_loc, player, connected, max_connected):
                for pairs in connected[player]:
                    if len(pairs) == 5:  # Check for winning connections (length 5)
                        print("Winning connected coordinates:")
                        for coord in pairs:
                            print(coord, end=' ')
                        print('')
                winner = "None" if (turn_count == 0) else ("Black" if player == BLACK else "White")
                print(f"{winner} is Winner!  - Turn Number: {turn_count}")
                break
        
else:
    print("woopsy.")
