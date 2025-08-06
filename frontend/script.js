let socket;
let canvas;
let ctx;
let gameBoard = [];
let currentPlayer = 'red';
let selectedPiece = null;
let roomCode = '';
let playerColor = null;
let playerCount = 0;

window.onload = function() {
    // Адаптируем размер canvas под мобильные устройства
    const canvasElement = document.getElementById('gameCanvas');
    const maxSize = Math.min(window.innerWidth - 40, 500);
    canvasElement.width = maxSize;
    canvasElement.height = maxSize;

    canvas = canvasElement;
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
        console.log('Game state received:', data);
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
        console.log('Error:', data.message);
        showError(data.message);
    });

    canvas.addEventListener('click', handleCanvasClick);
    canvas.addEventListener('touchstart', handleCanvasClick, { passive: false });
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
    statusElement.textContent = `Ходят: ${currentTurn}`;
    statusElement.className = currentPlayer;
}

function updatePlayerCount() {
    const countElement = document.getElementById('playerCount');
    if (countElement) {
        countElement.textContent = `Игроки: ${playerCount}/2`;
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
    event.preventDefault();

    if (!playerColor) {
        return;
    }

    // Получаем координаты с учетом touch событий
    let x, y;
    if (event.type === 'touchstart') {
        const touch = event.touches[0];
        const rect = canvas.getBoundingClientRect();
        x = touch.clientX - rect.left;
        y = touch.clientY - rect.top;
    } else {
        const rect = canvas.getBoundingClientRect();
        x = event.clientX - rect.left;
        y = event.clientY - rect.top;
    }

    const squareSize = canvas.width / 8;
    const col = Math.floor(x / squareSize);
    const row = Math.floor(y / squareSize);

    // Проверяем, что кликнули на доску
    if (row < 0 || row >= 8 || col < 0 || col >= 8) {
        return;
    }

    const piece = gameBoard[row][col];

    // Проверяем, что это наш ход
    if (currentPlayer !== playerColor) {
        showError('Сейчас ход другого игрока!');
        return;
    }

    if (selectedPiece) {
        // Пытаемся сделать ход
        console.log('Making move from', selectedPiece, 'to', [row, col]);
        socket.emit('make_move', {
            from: [selectedPiece.row, selectedPiece.col],
            to: [row, col]
        });
        selectedPiece = null;
    } else if (piece && piece.type === 'piece' && piece.color === playerColor) {
        // Выбираем свою шашку
        console.log('Selecting piece at', [row, col]);
        selectedPiece = {row: row, col: col};
        drawBoard();
    } else if (piece && piece.type === 'piece' && piece.color !== playerColor) {
        showError('Это шашка противника!');
    }
}

function leaveRoom() {
    if (socket) {
        socket.disconnect();
    }
    location.reload();
}

function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    errorElement.textContent = message;
    errorElement.style.display = 'block';

    // Вибрация на мобильных
    if (navigator.vibrate) {
        navigator.vibrate([200]);
    }

    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 3000);
}

// Обработка ввода кода комнаты
document.getElementById('roomCodeInput').addEventListener('input', function(e) {
    let value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
    if (value.length > 6) {
        value = value.substring(0, 6);
    }
    e.target.value = value;
});

// Предотвращение масштабирования
document.addEventListener('touchmove', function(event) {
    if (event.scale !== 1) {
        event.preventDefault();
    }
}, { passive: false });

// Адаптация при изменении размера окна
window.addEventListener('resize', function() {
    if (document.getElementById('gameScreen').style.display === 'block') {
        const canvasElement = document.getElementById('gameCanvas');
        const maxSize = Math.min(window.innerWidth - 40, 500);
        canvasElement.width = maxSize;
        canvasElement.height = maxSize;
        drawBoard();
    }
});