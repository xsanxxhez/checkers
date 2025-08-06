class CheckersGame:
    def __init__(self):
        self.board = self.create_board()
        self.current_player = 'red'
        self.selected_piece = None
        self.game_over = False
        self.winner = None
        self.move_history = []

    def create_board(self):
        board = [[0 for _ in range(8)] for _ in range(8)]

        # Расстановка красных шашек (вверху)
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = {'type': 'piece', 'color': 'red', 'king': False}

        # Расстановка синих шашек (внизу)
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = {'type': 'piece', 'color': 'blue', 'king': False}

        return board

    def get_valid_moves(self, row, col):
        piece = self.board[row][col]
        if not piece or piece['type'] != 'piece':
            return []

        moves = []
        capture_moves = []

        # Определяем направления движения
        if piece['king']:
            # Дамка может ходить во всех направлениях
            directions = [(1, -1), (1, 1), (-1, -1), (-1, 1)]
        else:
            # Обычная шашка ходит только вперед
            if piece['color'] == 'red':
                directions = [(1, -1), (1, 1)]  # вниз
            else:
                directions = [(-1, -1), (-1, 1)]  # вверх

        # Проверяем обычные ходы и взятия
        for dr, dc in directions:
            # Обычный ход
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                if self.board[new_row][new_col] == 0:
                    moves.append((new_row, new_col))

            # Взятие
            jump_row, jump_col = row + 2*dr, col + 2*dc
            if (self.is_valid_position(jump_row, jump_col) and
                    self.is_valid_position(new_row, new_col)):
                middle_piece = self.board[new_row][new_col]
                if (middle_piece and middle_piece['type'] == 'piece' and
                        middle_piece['color'] != piece['color'] and
                        self.board[jump_row][jump_col] == 0):
                    capture_moves.append((jump_row, jump_col))

        # Если есть взятия, можно только ими ходить
        return capture_moves if capture_moves else moves

    def is_valid_position(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def make_move(self, from_row, from_col, to_row, to_col):
        if self.game_over:
            return False

        piece = self.board[from_row][from_col]
        if not piece or piece['type'] != 'piece':
            return False

        if piece['color'] != self.current_player:
            return False

        valid_moves = self.get_valid_moves(from_row, from_col)
        if (to_row, to_col) not in valid_moves:
            return False

        # Выполнение хода
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = 0

        # Проверка взятия
        if abs(to_row - from_row) == 2:
            # Удаляем съеденную шашку
            mid_row = (from_row + to_row) // 2
            mid_col = (from_col + to_col) // 2
            self.board[mid_row][mid_col] = 0

        # Проверка на превращение в дамку
        if piece['color'] == 'red' and to_row == 7:
            piece['king'] = True
        elif piece['color'] == 'blue' and to_row == 0:
            piece['king'] = True

        # Смена хода
        self.current_player = 'blue' if self.current_player == 'red' else 'red'

        # Сохраняем ход в истории
        self.move_history.append({
            'from': (from_row, from_col),
            'to': (to_row, to_col),
            'player': piece['color']
        })

        return True

    def get_game_state(self):
        return {
            'board': self.board,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'move_history': self.move_history[-5:]  # последние 5 ходов
        }