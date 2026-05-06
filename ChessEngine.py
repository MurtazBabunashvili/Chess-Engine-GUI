import numpy as np
class GameState():
    def __init__(self):
        self.board = np.array([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--", "--","--","--","--","--","--","--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ])
        self.move_functions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}

        self.whiteToMove = True
        self.move_log = []
        self.white_king_location = (7,4)
        self.black_king_location = (0,4)

        self.inCheck = False
        self.checkmate = False
        self.stalemate = False

        self.en_passant_possible = ()
        self.en_passant_log = [()]

        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(True,True,True, True)]


    def make_move(self, move):
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.piece_moved

        self.move_log.append(move)
        self.whiteToMove = not self.whiteToMove

        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_column)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_column)

        #En passant
        if move.piece_moved[1] == 'p' and move.start_column != move.end_column and move.pieceCaptured == "--":
            self.board[move.start_row][move.end_column] = "--"

        #En passant is possible if pawn moved 2 squares
        self.en_passant_log.append(self.en_passant_possible)
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.en_passant_possible = ((move.start_row + move.end_row)//2, move.end_column)
        else:
            self.en_passant_possible = ()

        if move.piece_moved == 'wK' and abs(move.start_column - move.end_column) == 2:
            if move.end_column == 6: #King side castle
                self.board[7][5] = self.board[7][7]
                self.board[7][7] = "--"
            else: #Queen side castle
                self.board[7][3] = self.board[7][0]
                self.board[7][0] = "--"
        elif move.piece_moved == 'bK' and abs(move.start_column - move.end_column) == 2:
            if move.end_column == 6:
                self.board[0][5] = self.board[0][7]
                self.board[0][7] = "--"
            else:
                self.board[0][3] = self.board[0][0]
                self.board[0][0] = "--"

        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.white_king_side, self.current_castling_rights.black_king_side,
                                                   self.current_castling_rights.white_queen_side, self.current_castling_rights.black_queen_side))


    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castling_rights.white_king_side = False
            self.current_castling_rights.white_queen_side = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.black_king_side = False
            self.current_castling_rights.black_queen_side = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_column == 7: self.current_castling_rights.white_king_side =False
                elif move.start_column == 0: self.current_castling_rights.white_queen_side = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_column == 7: self.current_castling_rights.black_king_side = False
                if move.start_column == 0: self.current_castling_rights.black_queen_side = False
    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.pieceCaptured

            self.whiteToMove = not self.whiteToMove

            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_column)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_column)

            #Restore en passant
            self.en_passant_possible = self.en_passant_log.pop()
            if move.piece_moved[1] == 'p' and move.start_column != move.end_column and move.pieceCaptured == "--":
                enemy = 'b' if move.piece_moved[0] == 'w' else 'w'
                self.board[move.start_row][move.end_column] = enemy + 'p'

            #Undo castling
            if move.piece_moved == 'wK' and abs(move.start_column - move.end_column) == 2:
                if move.end_column == 6:
                    self.board[7][7] = self.board[7][5]
                    self.board[7][5] = "--"
                else:
                    self.board[7][0] = self.board[7][3]
                    self.board[7][3] = "--"
            elif move.piece_moved == 'bK' and abs(move.start_column- move.end_column) == 2:
                if move.end_column== 6:
                    self.board[0][7] = self.board[0][5]
                    self.board[0][5] = "--"
                else:
                    self.board[0][0] = self.board[0][3]
                    self.board[0][3] = "--"

            self.castle_rights_log.pop()
            self.current_castling_rights = self.castle_rights_log[-1]

            self.checkmate = False
            self.stalemate = False


    def get_valid_moves(self):
        #All general possible moves
        moves = []
        self.inCheck, self.pins, self.checks = self.check_pins_and_checks()

        if self.whiteToMove:
            king_row = self.white_king_location[0]
            king_column = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_column = self.black_king_location[1]

        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()
                check = self.checks[0]
                check_row, check_column = check[0], check[1]
                piece_checking = self.board[check_row][check_column]
                valid_squares = []
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_column)]
                else:
                    for i in range(1,8):
                        valid_square = (king_row + check[2] *i, king_column + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_column:
                            break
                for i in range(len(moves) -1, -1, -1):
                    if moves[i].piece_moved[1] != 'K':
                        if not (moves[i].end_row, moves[i].end_column) in valid_squares:
                            moves.remove(moves[i])
            else:#Double check
                self.get_king_moves(king_row, king_column, moves)
        else: #Not in check
            moves = self.get_all_possible_moves()
            ally_color = 'w' if self.whiteToMove else 'b'
            self.get_castle_moves(king_row, king_column, moves, ally_color)
        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        return moves

    #Determines if player is in check
    def in_check(self):
        if self.whiteToMove:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    #determines if enemy can attack square (row, column)
    def square_under_attack(self, row, column):
        self.whiteToMove = not self.whiteToMove # Switch to opponent's view
        opponent_moves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove  # Switch back
        for move in opponent_moves: #Iterate through opponent's moves
            if move.end_row == row and move.end_column == column: # Square under attack
                return True

    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                turn = self.board[row][column][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][column][1]
                    self.move_functions[piece](row, column, moves)

        return moves


    def get_pawn_moves(self, row, column, moves):
        piece_pinned = False
        pin_direction = ()

        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piece_pinned = True
                pin_direction = (self.pins[i][ 2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            if row - 1 >= 0:
                if self.board[row-1][column] == "--": #move forward
                    if not piece_pinned or pin_direction == (-1, 0):
                        moves.append(Move((row, column), (row-1, column), self.board))
                        if row == 6 and self.board[row-2][column] == "--":
                            moves.append(Move((row, column), (row-2, column), self.board))
                if column - 1 >= 0:
                    if self.board[row-1][column-1][0] == 'b' or (row-1, column-1) == self.en_passant_possible: #enemy to capture in diagonal or en passant
                        if not piece_pinned or pin_direction == (-1, -1):
                            moves.append(Move((row, column), (row-1, column-1), self.board))
                if column + 1 <len(self.board): #captures to the right
                    if self.board[row-1][column+1][0] == 'b' or (row-1, column+1) ==self.en_passant_possible:
                        if not piece_pinned or pin_direction == (-1, 1):
                            moves.append(Move((row, column), (row-1, column+1), self.board))
        else:
            if row + 1 < 8:
                if row + 1 < 8 and self.board[row+1][column] == "--": #Move forward as black
                    if not piece_pinned or pin_direction == (1, 0):
                        moves.append(Move((row, column), (row+1, column), self.board))
                        if row == 1 and self.board[row+2][column] == "--":
                            moves.append(Move((row, column), (row+2, column), self.board))
                if column - 1>=0: #Capture left
                    if not piece_pinned or pin_direction == (1, -1):
                        if self.board[row+1][column-1][0] == 'w' or (row+1, column-1) == self.en_passant_possible:
                            moves.append(Move((row, column), (row+1, column-1), self.board))
                if column + 1<len(self.board): #Capture right
                    if not piece_pinned or pin_direction == (1, 1):
                        if self.board[row+1][column+1][0] == 'w' or (row+1, column+1) == self.en_passant_possible:
                            moves.append(Move((row, column), (row+1, column+1), self.board))

    def get_rook_moves(self, row, column, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,0), (0, -1), (1, 0), (0, 1)) #up, left, down, right movements
        enemy_color = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0]*i
                end_column = column + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_column]
                        if end_piece == "--":
                            moves.append(Move((row, column), (end_row, end_column), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((row, column), (end_row, end_column), self.board))
                            break
                        else: #Cant capture own piece
                            break
                else: #off board
                    break

    def get_knight_moves(self, row, column, moves):
        piece_pinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1,2), (2, -1), (2, 1)) #All L-s
        ally_color = 'w' if self.whiteToMove else 'b'
        for m in knight_moves:
            end_row = row + m[0]
            end_column = column + m[1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_column]
                    if end_piece[0] != ally_color: #Opposite color -> legit move to capture it
                        moves.append(Move((row, column), (end_row, end_column), self.board))

    def get_bishop_moves(self, row, column, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_column = column + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_column]
                        if end_piece == "--":
                            moves.append(Move((row, column), (end_row, end_column), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((row, column), (end_row, end_column), self.board))
                            break
                        else: #Cant capture own piece
                            break
                else:
                    break
    def get_queen_moves(self, row, column, moves):
        self.get_rook_moves(row, column, moves)
        self.get_bishop_moves(row, column, moves)
    def get_king_moves(self, row, column, moves):
        row_moves = (-1, -1, -1, 0, 0 ,1, 1, 1)
        column_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            end_row = row + row_moves[i]
            end_column = column + column_moves[i]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                end_piece = self.board[end_row][end_column]
                if end_piece[0] != ally_color:
                    if ally_color == 'w':
                        self.white_king_location = (end_row, end_column)
                    else:
                        self.black_king_location = (end_row, end_column)
                    inCheck, pins, checks = self.check_pins_and_checks()
                    if not inCheck:
                        moves.append(Move((row, column), (end_row, end_column), self.board))

                    if ally_color == 'w':
                        self.white_king_location = (row, column)
                    else:
                        self.black_king_location = (row, column)
    def get_castle_moves(self, row, column, moves, ally_color):
        if self.square_under_attack(row, column):
            return #Cant castle if in check
        if (ally_color == 'w' and self.current_castling_rights.white_king_side) or \
                (ally_color == 'b' and self.current_castling_rights.black_king_side):
            self.get_king_side_castle(row, column, moves)
        if (ally_color == 'w' and self.current_castling_rights.white_queen_side) or \
                (ally_color == 'b' and self.current_castling_rights.black_queen_side):
            self.get_queen_side_castle(row, column, moves)

    def get_king_side_castle(self, row, column, moves):
        if self.board[row][column+1] == "--" and self.board[row][column+2] == "--":
            if not self.square_under_attack(row, column+1) and not self.square_under_attack(row, column+2):
                moves.append(Move((row, column), (row, column+2), self.board))

    def get_queen_side_castle(self, row, column, moves):
        if self.board[row][column-1] == "--" and self.board[row][column-2] == "--" and self.board[row][column-3] == "--":
            if not self.square_under_attack(row, column-1) and not self.square_under_attack(row, column-2) and not self.square_under_attack(row, column-3):
                moves.append(Move((row, column), (row, column-2), self.board))


    def check_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False
        if self.whiteToMove:
            enemy_color = 'b'
            ally_color = 'w'
            start_row = self.white_king_location[0]
            start_column = self.white_king_location[1]
        else:
            enemy_color = 'w'
            ally_color = 'b'
            start_row = self.black_king_location[0]
            start_column = self.black_king_location[1]

        #Check pins and checks to king
        directions = ((-1, 0), (0, -1), (1,0), (0,1), (-1,-1), (-1,1), (1, -1), (1,1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1,8):
                end_row = start_row + d[0] * i
                end_column = start_column + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:
                    end_piece = self.board[end_row][end_column]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == ():
                            possible_pin = (end_row, end_column, d[0], d[1])
                        else: #We have another piece, defending king, so no check possible
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        #5 cases: 1. rook attack othogonally, 2. diagonally by biship 3. 1 square away by pawn
                        # 4. any direction from queen 5. any direction 1 square away king (2 kings can't intercept)
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and (
                                        (enemy_color == 'w' and 6 <= j <= 7) or
                                        (enemy_color == 'b' and 4 <= j <= 5)
                                )) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_column, d[0], d[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else: #No check
                            break
                else:
                    break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))  # All L-s
        for m in knight_moves:
            end_row = start_row + m[0]
            end_column = start_column + m[1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                end_piece = self.board[end_row][end_column]
                if end_piece[0] == enemy_color and end_piece[1] == 'N': #Enemy knight attacking king
                    in_check = True
                    checks.append((end_row, end_column, m[0], m[1]))
        return in_check, pins, checks


class Move():
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7":1, "8": 0}
    rows_to_ranks = {value: key for key, value in ranks_to_rows.items()}

    files_to_columns = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    columns_to_files = {value: key for key, value in files_to_columns.items()}


    def __init__(self, start_square, end_square, board):
        self.start_row = start_square[0]
        self.start_column = start_square[1]
        self.end_row = end_square[0]
        self.end_column = end_square[1]

        self.piece_moved = board[self.start_row][self.start_column]
        self.pieceCaptured = board[self.end_row][self.end_column]
        self.moveID = self.start_row * 1000 + self.start_column * 100 + self.end_row * 10 + self.end_column
        print(self.moveID)

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)

    def get_rank_file(self, row, column):
        return self.columns_to_files[column] + self.rows_to_ranks[row]

class CastleRights():
    def __init__(self, white_king_side, black_king_side, white_queen_side, black_queen_side):
        self.white_king_side = white_king_side
        self.black_king_side = black_king_side
        self.white_queen_side = white_queen_side
        self.black_queen_side = black_queen_side