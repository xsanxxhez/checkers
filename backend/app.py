from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from game_logic import CheckersGame
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Храним игры по комнатам
games = {}
player_rooms = {}

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)

@socketio.on('join_game')
def handle_join_game(data):
    room = data.get('room', 'default')
    join_room(room)

    # Создаем игру для комнаты, если её нет
    if room not in games:
        games[room] = CheckersGame()

    player_rooms[request.sid] = room
    emit('game_state', games[room].get_game_state(), room=room)

@socketio.on('make_move')
def handle_move(data):
    room = player_rooms.get(request.sid, 'default')
    if room not in games:
        return

    game = games[room]
    from_pos = data['from']
    to_pos = data['to']

    success = game.make_move(from_pos[0], from_pos[1], to_pos[0], to_pos[1])
    if success:
        emit('game_state', game.get_game_state(), room=room)

@socketio.on('disconnect')
def handle_disconnect():
    room = player_rooms.pop(request.sid, None)
    if room and room in games:
        # Можно добавить логику завершения игры при отключении игрока
        pass

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))