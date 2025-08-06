let socket;
let canvas;
let ctx;
let gameBoard = [];
let currentPlayer = '';
let selectedPiece = null;
let roomName = 'default';
let playerColor = null;

window.onload = function() {
    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext('2d');

    socket = io();

    socket.on('connect', function() {
        document.getElementById('status').textContent = 'Подключено! Введите название комнаты.';
    });

    socket.on('game_state', function(data) {
        gameBoard = data.board;
        currentPlayer = data.current_player;
        updateStatus();
        drawBoard();
    });

    canvas.addEventListener('click', handleCanvasClick);
};

function joinRoom() {
    roomName = document.getElementById('roomInput').value || 'default';
    socket.emit('join_game', {room: roomName});
    document.getElementById('status').textContent = 'Присоединились к комнате: ' + roomName;
}

function updateStatus() {
    let statusText = `Ходит: ${currentPlayer === 'red' ? 'красные' : 'синие'}`;
    if (playerColor) {
        statusText += ` | Вы: ${playerColor === 'red' ? 'красные' : 'синие'}`;
        document.getElementById('yourColor').textContent = playerColor === 'red' ? 'красные' : 'синие';
        document.getElementById('yourColor').className = playerColor;
    }
    document.getElementById('status').textContent = statusText;
}

function drawBoard() {
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
    } else if (piece && piece.type === 'piece' && piece.color === currentPlayer) {
        // Выбираем шашку
        selectedPiece = {row: row, col: col};
        drawBoard();
    }
}