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
    def make_move(self, move):
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.piece_moved

        self.move_log.append(move)
        self.whiteToMove = not self.whiteToMove

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

    def get_valid_moves(self):
        return self.get_all_possible_moves()

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
        if self.whiteToMove:
            if self.board[row-1][column] == "--": #move forward
                moves.append(Move((row, column), (row-1, column), self.board))
                if row == 6 and self.board[row-2][column] == "--":
                    moves.append(Move((row, column), (row-2, column), self.board))
            if column - 1 >= 0:
                if self.board[row-1][column-1][0] == 'b': #enemy to capture in diagonal
                    moves.append(Move((row, column), (row-1, column-1), self.board))
            if column + 1 <len(self.board): #captures to the right
                if self.board[row-1][column+1][0] == 'b':
                    moves.append(Move((row, column), (row-1, column+1), self.board))
        else:
            if self.board[row+1][column] == "--": #Move forward as black
                moves.append(Move((row, column), (row+1, column), self.board))
                if row == 1 and self.board[row+2][column] == "--":
                    moves.append(Move((row, column), (row+2, column), self.board))
            if column - 1>=0: #Capture left
                if self.board[row+1][column-1][0] == 'w':
                    moves.append(Move((row, column), (row+1, column-1), self.board))
            if column + 1<len(self.board): #Capture right
                if self.board[row+1][column+1][0] == 'w':
                    moves.append(Move((row, column), (row+1, column+1), self.board))

    def get_rook_moves(self, row, column, moves):
        directions = ((-1,0), (0, -1), (1, 0), (0, 1)) #up, left, down, right movements
        enemy_color = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0]*i
                end_column = column + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:
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
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1,2), (2, -1), (2, 1)) #All L-s
        ally_color = 'w' if self.whiteToMove else 'b'
        for m in knight_moves:
            end_row = row + m[0]
            end_column = column + m[1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                end_piece = self.board[end_row][end_column]
                if end_piece[0] != ally_color: #Opposite color -> legit move to capture it
                    moves.append(Move((row, column), (end_row, end_column), self.board))
    def get_bishop_moves(self, row, column, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_column = column + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:
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
        pass
    def get_king_moves(self, row, column, moves):
        pass

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