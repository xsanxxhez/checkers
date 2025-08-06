let socket;
let canvas;
let ctx;
let gameBoard = [];
let currentPlayer = '';
let selectedPiece = null;
let roomCode = '';
let playerColor = null;
let playerCount = 0;

window.onload = function() {
    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext('2d');

    socket = io();

    socket.on('connect', function() {
        console.log('Подключено к серверу');
    });

    socket.on('room_created', function(data) {
        roomCode = data.room_code;
        playerColor = data.player_color;

        document.getElementById('modeScreen').style.display = 'none';
        document.getElementById('waitingScreen').style.display = 'block';
        document.getElementById('roomCodeDisplay').textContent = roomCode;
    });

    socket.on('player_joined', function(data) {
        playerCount = data.player_count;
        updatePlayerCount();

        if (data.player_count === 2) {
            document.getElementById('waitingScreen').style.display = 'none';
            document.getElementById('gameScreen').style.display = 'block';
            document.getElementById('currentRoomCode').textContent = roomCode;
            document.getElementById('yourColorDisplay').textContent =
                playerColor === 'red' ? 'красные' : 'синие';
            document.getElementById('yourColorDisplay').className = playerColor;
        }
    });

    socket.on('game_state', function(data) {
        gameBoard = data.board;
        currentPlayer = data.current_player;
        playerCount = data.player_count;

        updateGameStatus();
        updatePlayerCount();
        drawBoard();

        // Если игра началась
        if (data.player_count === 2 && document.getElementById('waitingScreen').style.display !== 'none') {
            document.getElementById('waitingScreen').style.display = 'none';
            document.getElementById('gameScreen').style.display = 'block';
            document.getElementById('currentRoomCode').textContent = roomCode;
            document.getElementById('yourColorDisplay').textContent =
                playerColor === 'red' ? 'красные' : 'синие';
            document.getElementById('yourColorDisplay').className = playerColor;
        }
    });

    socket.on('error', function(data) {
        showError(data.message);
    });

    canvas.addEventListener('click', handleCanvasClick);
};

function showModeScreen() {
    hideAllScreens();
    document.getElementById('modeScreen').style.display = 'block';
}

function showCreateRoom() {
    hideAllScreens();
    document.getElementById('createRoomScreen').style.display = 'block';
}

function showJoinRoom() {
    hideAllScreens();
    document.getElementById('joinRoomScreen').style.display = 'block';
}

function hideAllScreens() {
    const screens = ['modeScreen', 'createRoomScreen', 'joinRoomScreen', 'waitingScreen', 'gameScreen'];
    screens.forEach(screen => {
        document.getElementById(screen).style.display = 'none';
    });
}

function createRoom() {
    const roomName = document.getElementById('roomNameInput').value || 'Моя комната';
    socket.emit('create_room', {room_name: roomName});
}

function joinRoom() {
    const code = document.getElementById('roomCodeInput').value.toUpperCase();
    if (code.length !== 6) {
        showError('Код комнаты должен содержать 6 символов');
        return;
    }
    socket.emit('join_room_by_code', {room_code: code});
}

function updateGameStatus() {
    const statusElement = document.getElementById('gameStatus');
    const currentTurn = currentPlayer === 'red' ? 'красные' : 'синие';
    statusElement.textContent = `Ходит: ${currentTurn}`;
    statusElement.className = currentPlayer;
}

function updatePlayerCount() {
    const countElement = document.getElementById('playerCount');
    if (countElement) {
        countElement.textContent = `Игроков: ${playerCount}/2`;
    }
}

function drawBoard() {
    if (!ctx) return;

    const squareSize = canvas.width / 8;

    // Рисуем доску
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            // Цвет клетки
            if ((row + col) % 2 === 0) {
                ctx.fillStyle = '#f0d9b5'; // светлая
            } else {
                ctx.fillStyle = '#b58863'; // темная
            }

            ctx.fillRect(col * squareSize, row * squareSize, squareSize, squareSize);

            // Рисуем шашку
            const piece = gameBoard[row][col];
            if (piece && piece.type === 'piece') {
                const x = col * squareSize + squareSize / 2;
                const y = row * squareSize + squareSize / 2;
                const radius = squareSize / 3;

                // Цвет шашки
                ctx.fillStyle = piece.color === 'red' ? '#dc3545' : '#007bff';
                ctx.beginPath();
                ctx.arc(x, y, radius, 0, 2 * Math.PI);
                ctx.fill();

                // Если дамка
                if (piece.king) {
                    ctx.fillStyle = '#ffd700';
                    ctx.beginPath();
                    ctx.arc(x, y, radius / 2, 0, 2 * Math.PI);
                    ctx.fill();
                }

                // Выделение выбранной шашки
                if (selectedPiece && selectedPiece.row === row && selectedPiece.col === col) {
                    ctx.strokeStyle = '#28a745';
                    ctx.lineWidth = 3;
                    ctx.beginPath();
                    ctx.arc(x, y, radius + 2, 0, 2 * Math.PI);
                    ctx.stroke();
                }
            }
        }
    }
}

function handleCanvasClick(event) {
    if (!playerColor || currentPlayer !== playerColor) {
        return; // Не ваш ход
    }

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const squareSize = canvas.width / 8;
    const col = Math.floor(x / squareSize);
    const row = Math.floor(y / squareSize);

    const piece = gameBoard[row][col];

    if (selectedPiece) {
        // Пытаемся сделать ход
        socket.emit('make_move', {
            from: [selectedPiece.row, selectedPiece.col],
            to: [row, col]
        });
        selectedPiece = null;
    } else if (piece && piece.type === 'piece' && piece.color === playerColor) {
        // Выбираем свою шашку
        selectedPiece = {row: row, col: col};
        drawBoard();
    }
}

function leaveRoom() {
    socket.disconnect();
    location.reload();
}

function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    errorElement.textContent = message;
    errorElement.style.display = 'block';

    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 3000);
}

// Обработка клавиши Escape для выхода
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        if (document.getElementById('gameScreen').style.display === 'block') {
            leaveRoom();
        }
    }
});