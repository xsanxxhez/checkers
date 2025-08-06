import random
import string

class CheckersGame:
    def __init__(self):
        self.board = self.create_board()
        self.current_player = 'red'  # Красные ходят первыми
        self.selected_piece = None
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.players = {'red': None, 'blue': None}  # sid игроков
        self.player_count = 0
        self.must_capture = False  # Есть ли обязательные взятия
        self.possible_captures = []  # Список возможных взятий

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

    def is_valid_position(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def get_piece_valid_moves(self, row, col):
        """Получить все возможные ходы для конкретной шашки"""
        piece = self.board[row][col]
        if not piece or piece['type'] != 'piece':
            return []

        moves = []
        captures = []

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
                    moves.append({
                        'to': (new_row, new_col),
                        'captures': []
                    })

            # Взятие
            self._check_capture(piece, row, col, dr, dc, captures)

        # Если есть взятия, можно только ими ходить
        return captures if captures else moves

    def _check_capture(self, piece, row, col, dr, dc, captures):
        """Проверить возможность взятия в заданном направлении"""
        # Позиция через которую прыгаем
        jump_over_row, jump_over_col = row + dr, col + dc
        # Позиция приземления
        land_row, land_col = row + 2*dr, col + 2*dc

        if (self.is_valid_position(land_row, land_col) and
                self.is_valid_position(jump_over_row, jump_over_col)):

            middle_piece = self.board[jump_over_row][jump_over_col]
            if (middle_piece and middle_piece['type'] == 'piece' and
                    middle_piece['color'] != piece['color'] and
                    self.board[land_row][land_col] == 0):

                # Найдено базовое взятие
                capture_move = {
                    'to': (land_row, land_col),
                    'captures': [(jump_over_row, jump_over_col)]
                }

                # Проверяем возможность продолжить цепочку взятий
                chained_captures = self._find_chained_captures(
                    piece, land_row, land_col, [(jump_over_row, jump_over_col)]
                )

                if chained_captures:
                    # Добавляем все возможные цепочки взятий
                    for chain in chained_captures:
                        captures.append({
                            'to': chain['to'],
                            'captures': capture_move['captures'] + chain['captures']
                        })
                else:
                    # Простое взятие
                    captures.append(capture_move)

    def _find_chained_captures(self, piece, row, col, used_captures):
        """Найти возможные продолжения цепочки взятий"""
        captures = []

        # Определяем направления
        if piece['king']:
            directions = [(1, -1), (1, 1), (-1, -1), (-1, 1)]
        else:
            if piece['color'] == 'red':
                directions = [(1, -1), (1, 1)]
            else:
                directions = [(-1, -1), (-1, 1)]

        # Проверяем все направления
        for dr, dc in directions:
            jump_over_row, jump_over_col = row + dr, col + dc
            land_row, land_col = row + 2*dr, col + 2*dc

            if (self.is_valid_position(land_row, land_col) and
                    self.is_valid_position(jump_over_row, jump_over_col)):

                middle_piece = self.board[jump_over_row][jump_over_col]
                # Проверяем, что это вражеская шашка и она еще не была съедена
                if (middle_piece and middle_piece['type'] == 'piece' and
                        middle_piece['color'] != piece['color'] and
                        self.board[land_row][land_col] == 0 and
                        (jump_over_row, jump_over_col) not in used_captures):

                    # Найдено продолжение цепочки
                    new_used = used_captures + [(jump_over_row, jump_over_col)]
                    chain_move = {
                        'to': (land_row, land_col),
                        'captures': [(jump_over_row, jump_over_col)]
                    }

                    # Проверяем дальнейшие продолжения
                    further_chains = self._find_chained_captures(piece, land_row, land_col, new_used)

                    if further_chains:
                        # Добавляем все возможные продолжения
                        for further_chain in further_chains:
                            captures.append({
                                'to': further_chain['to'],
                                'captures': chain_move['captures'] + further_chain['captures']
                            })
                    else:
                        # Конец цепочки
                        captures.append(chain_move)

        return captures

    def get_all_possible_moves(self, player_color):
        """Получить все возможные ходы для игрока"""
        all_moves = []

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece['type'] == 'piece' and piece['color'] == player_color:
                    moves = self.get_piece_valid_moves(row, col)
                    for move in moves:
                        all_moves.append({
                            'from': (row, col),
                            'to': move['to'],
                            'captures': move['captures']
                        })

        return all_moves

    def get_valid_moves_for_piece(self, row, col):
        """Получить валидные ходы для конкретной шашки с учетом обязательных взятий"""
        piece = self.board[row][col]
        if not piece or piece['type'] != 'piece' or piece['color'] != self.current_player:
            return []

        # Получаем все возможные ходы для текущего игрока
        all_player_moves = self.get_all_possible_moves(self.current_player)

        # Проверяем, есть ли обязательные взятия
        capture_moves = [move for move in all_player_moves if move['captures']]

        if capture_moves:
            # Есть обязательные взятия - можно ходить только ими
            # Фильтруем ходы только для этой шашки
            piece_capture_moves = [move for move in capture_moves if move['from'] == (row, col)]
            return piece_capture_moves

        # Нет обязательных взятий - можно делать обычные ходы
        piece_moves = [move for move in all_player_moves if move['from'] == (row, col)]
        return piece_moves

    def make_move(self, from_row, from_col, to_row, to_col):
        """Сделать ход"""
        if self.game_over:
            return False

        piece = self.board[from_row][from_col]
        if not piece or piece['type'] != 'piece':
            return False

        # Проверяем, что это ход текущего игрока
        if piece['color'] != self.current_player:
            return False

        # Получаем валидные ходы для этой шашки
        valid_moves = self.get_valid_moves_for_piece(from_row, from_col)

        # Ищем соответствующий ход
        target_move = None
        for move in valid_moves:
            if move['to'] == (to_row, to_col):
                target_move = move
                break

        if not target_move:
            return False

        # Выполнение хода
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = 0

        # Удаление съеденных шашек
        if target_move['captures']:
            for capture_pos in target_move['captures']:
                cap_row, cap_col = capture_pos
                self.board[cap_row][cap_col] = 0

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
            'player': piece['color'],
            'captures': target_move['captures']
        })

        return True

    def add_player(self, sid):
        """Добавляет игрока в игру"""
        if self.player_count == 0:
            self.players['red'] = sid
            self.player_count += 1
            return 'red'
        elif self.player_count == 1:
            self.players['blue'] = sid
            self.player_count += 1
            return 'blue'
        return None

    def remove_player(self, sid):
        """Удаляет игрока из игры"""
        if self.players['red'] == sid:
            self.players['red'] = None
            self.player_count -= 1
        elif self.players['blue'] == sid:
            self.players['blue'] = None
            self.player_count -= 1

    def get_player_color(self, sid):
        """Возвращает цвет игрока по его sid"""
        if self.players['red'] == sid:
            return 'red'
        elif self.players['blue'] == sid:
            return 'blue'
        return None

    def get_game_state(self):
        return {
            'board': self.board,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'player_count': self.player_count,
            'move_history': self.move_history[-5:]
        }