from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from game_logic import CheckersGame
import os
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Храним игры по комнатам
games = {}
player_rooms = {}  # sid -> room_code
room_codes = {}    # room_code -> room_name

def generate_room_code():
    """Генерирует уникальный 6-значный код комнаты"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in games:
            return code

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)

@socketio.on('create_room')
def handle_create_room(data):
    # Генерируем уникальный код комнаты
    room_code = generate_room_code()
    room_name = data.get('room_name', f'Комната {room_code}')

    # Создаем новую игру
    games[room_code] = CheckersGame()
    room_codes[room_code] = room_name

    # Присоединяемся к комнате
    join_room(room_code)
    player_rooms[request.sid] = room_code

    # Добавляем игрока в игру
    game = games[room_code]
    player_color = game.add_player(request.sid)

    # Отправляем информацию о комнате создателю
    emit('room_created', {
        'room_code': room_code,
        'room_name': room_name,
        'player_color': player_color
    })

    # Отправляем состояние игры
    emit('game_state', game.get_game_state())

@socketio.on('join_room_by_code')
def handle_join_room_by_code(data):
    room_code = data.get('room_code', '').upper()

    if room_code not in games:
        emit('error', {'message': 'Комната не найдена'})
        return

    game = games[room_code]
    if game.player_count >= 2:
        emit('error', {'message': 'Комната уже заполнена'})
        return

    # Присоединяемся к комнате
    join_room(room_code)
    player_rooms[request.sid] = room_code

    # Добавляем игрока в игру
    player_color = game.add_player(request.sid)

    # Уведомляем всех в комнате об обновлении
    emit('player_joined', {
        'player_color': player_color,
        'player_count': game.player_count
    }, room=room_code)

    # Отправляем состояние игры всем в комнате
    emit('game_state', game.get_game_state(), room=room_code)

@socketio.on('make_move')
def handle_move(data):
    room_code = player_rooms.get(request.sid)
    if not room_code or room_code not in games:
        return

    game = games[room_code]
    from_pos = data['from']
    to_pos = data['to']

    # Проверяем, что игрок может ходить
    player_color = game.get_player_color(request.sid)
    if player_color != game.current_player:
        emit('error', {'message': 'Не ваш ход!'})
        return

    success = game.make_move(from_pos[0], from_pos[1], to_pos[0], to_pos[1])
    if success:
        emit('game_state', game.get_game_state(), room=room_code)
    else:
        emit('error', {'message': 'Неверный ход'})

@socketio.on('disconnect')
def handle_disconnect():
    room_code = player_rooms.pop(request.sid, None)
    if room_code and room_code in games:
        game = games[room_code]
        game.remove_player(request.sid)

        # Уведомляем остальных игроков
        emit('player_left', {
            'player_count': game.player_count
        }, room=room_code)

        # Если комната пуста, удаляем её
        if game.player_count == 0:
            del games[room_code]
            if room_code in room_codes:
                del room_codes[room_code]

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))