import pygame
import sys

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Экран
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Русские шашки')

class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = SQUARE_SIZE // 3
        pygame.draw.circle(win, self.color, (self.col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                             self.row * SQUARE_SIZE + SQUARE_SIZE // 2), radius)
        if self.king:
            pygame.draw.circle(win, GRAY, (self.col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                           self.row * SQUARE_SIZE + SQUARE_SIZE // 2), radius // 2)

class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.blue_left = 12
        self.red_kings = self.blue_kings = 0
        self.create_board()

    def draw_squares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, WHITE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, RED))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, BLUE))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.row = row
        piece.col = col

    def get_piece(self, row, col):
        return self.board[row][col]

def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def main():
    run = True
    clock = pygame.time.Clock()
    board = Board()
    selected = None
    turn = RED  # Начинает красный

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                piece = board.get_piece(row, col)

                if selected:
                    if piece == 0:
                        board.move(selected, row, col)
                        turn = BLUE if turn == RED else RED
                    selected = None
                else:
                    if piece != 0 and piece.color == turn:
                        selected = piece

        board.draw(WIN)
        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()