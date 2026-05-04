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
    game_over = False

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
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
                    move_made = True
                if e.key == p.K_r: #Resets board when r is pressed
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
        if move_made:
            if len(gs.move_log) > 0:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
        drawGameState(screen, gs, valid_moves, square_selected)

        if gs.checkmate:
            game_over = True
            if gs.whiteToMove:
                draw_text(screen, 'Black wins by checkmate')
            else:
                draw_text(screen, 'White wins by checkmate')
        elif gs.stalemate:
            game_over = True
            draw_text(screen, 'Stalemate')

        if promotion_mode:
            draw_promotion_menu(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, valid_moves, square_selected):
    drawBoard(screen)
    highlight_squares(screen, gs, valid_moves, square_selected)
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
        menu_width = 4 * SQ_SIZE
        start_x = (WIDTH - menu_width) // 2
        menu_col = (x - start_x) // SQ_SIZE

        if 0 <= menu_col < 4:
            chosen_piece = pieces[menu_col]

            move = promotion_square

            gs.board[move.start_row][move.start_column] = "--"
            gs.board[move.end_row][move.end_column] = move.piece_moved[0] + chosen_piece

            gs.move_log.append(move)
            gs.whiteToMove = not gs.whiteToMove

            return False, None, True
        else:
            return True, promotion_square, False
    return True, promotion_square, False

def highlight_squares(screen, game_screen, valid_moves, square_selected):
    if square_selected != ():
        row, column = square_selected
        if game_screen.board[row][column][0] == ('w' if game_screen.whiteToMove else 'b'): #square selected is piece that can be moved
            surface = p.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100)
            surface.fill(p.Color('grey'))
            screen.blit(surface, (column * SQ_SIZE, row * SQ_SIZE)) #Highligts selected square

            surface.fill(p.Color('Yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_column == column:
                    screen.blit(surface, (move.end_column * SQ_SIZE, move.end_row*SQ_SIZE))



def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = str(board[r][c])
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animate_move(move, screen, board, clock):
    colors = [p.Color("white"), p.Color("lime")]
    dR = move.end_row - move.start_row
    dC = move.end_column - move.start_column
    frames_per_square = 10
    frame_count = (abs(dR) + abs(dC)) *  frames_per_square

    for frame in range(frame_count + 1):
        row, column = (move.start_row + dR * frame / frame_count, move.start_column + dC * frame / frame_count)
        drawBoard(screen)
        drawPieces(screen, board)

        color = colors[(move.end_row + move.end_column) % 2]
        end_square = p.Rect(move.end_column * SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)

        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], end_square)

        screen.blit(IMAGES[move.piece_moved], p.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)
def draw_text(screen, text):
    font = p.font.SysFont("Helvitca", 64, True, False)
    text_object = font.render(text, 0, p.Color('Black'))

    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_object.get_width() / 2,
                                                     HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)

if __name__ == "__main__":
    main()