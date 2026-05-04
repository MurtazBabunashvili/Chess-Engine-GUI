import numpy
import pygame as p
import ChessEngine
WIDTH = HEIGHT = 800
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ',
              'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        image = p.image.load("pieces/" + piece + ".png")
        IMAGES[piece] = p.transform.scale(image, (SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False

    promotion_mode = False
    promotion_square = None

    load_images()
    running = True
    square_selected = ()
    player_clicks = []

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if promotion_mode:
                    promotion_mode, promotion_square, move_made = handle_promotion_click(e, gs, promotion_square)
                    continue
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if square_selected == (row, col):
                    square_selected = () #deselect
                    player_clicks = []
                else:
                    square_selected = (row, col)
                    player_clicks.append(square_selected)
                if len(player_clicks) == 2: #Make a move
                    move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                    print(move.getChessNotation())
                    if move in valid_moves:

                        if (move.piece_moved == 'wp' and move.end_row ==0) or \
                                (move.piece_moved == 'bp' and move.end_row == 7):
                            promotion_mode = True
                            promotion_square = move
                        else:
                            gs.make_move(move)
                            move_made = True
                        square_selected = ()
                        player_clicks = []
                    else:
                        player_clicks = [square_selected]
            elif e.type == p.KEYDOWN:
                if promotion_mode:
                    continue
                if e.key == p.K_z: #undo when z is pressed
                    gs.undo_move()
        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False
        drawGameState(screen, gs)

        if promotion_mode:
            draw_promotion_menu(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    colors = numpy.array([p.Color("white"), p.Color("lime")])
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) %2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_promotion_menu(screen, gs):
    pieces = ['Q', 'R', 'B', 'N']
    color = 'w' if gs.whiteToMove else 'b'

    draw_blur(screen)

    menu_width = 4 * SQ_SIZE
    start_x = (WIDTH - menu_width) // 2
    y = SQ_SIZE // 2 #Top area

    for i, piece in enumerate(pieces):
        rect = p.Rect(start_x + i*SQ_SIZE, y, SQ_SIZE, SQ_SIZE)
        screen.blit(IMAGES[color + piece], rect)

def draw_blur(screen):
    small = p.transform.smoothscale(screen, (WIDTH//6, HEIGHT//6))
    blurred = p.transform.smoothscale(small, (WIDTH, HEIGHT))
    screen.blit(blurred, (0,0))

def handle_promotion_click(event, gs, promotion_square):
    if event.type == p.MOUSEBUTTONDOWN:
        x, y = p.mouse.get_pos()
        col = x // SQ_SIZE

        pieces = ['Q', 'R', 'B', 'N']
        if 0 <= col < 4:
            chosen_piece = pieces[col]

            move = promotion_square

            gs.board[move.start_row][move.start_column] = "--"
            gs.board[move.end_row][move.end_column] = move.piece_moved[0] + chosen_piece

            gs.move_log.append(move)
            gs.whiteToMove = not gs.whiteToMove

            return False, None, True
        else:
            return True, promotion_square, False
    return True, promotion_square, False

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = str(board[r][c])
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main()