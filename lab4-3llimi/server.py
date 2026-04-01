import sys
import grpc
from concurrent import futures
import time
import logging

import game_pb2 as cf
import game_pb2_grpc as cf_grpc
from grpc import StatusCode
from grpc import RpcError

ROWS = 6
COLUMNS = 7

games = {}
game_counter = 1

class ConnectFourServicer(cf_grpc.ConnectFourServicer):
    def CreateGame(self, request, context):
        global game_counter
        game_id = game_counter
        game_counter += 1

        game = cf.Game(
            id=game_id,
            is_finished=False,
            turn=cf.MARK_RED,
            moves=[]
        )
        games[game_id] = game
        logging.info(f"Created game {game_id}")
        return game

    def GetGame(self, request, context):
        game_id = request.game_id
        if game_id not in games:
            context.abort(StatusCode.NOT_FOUND, f"Game {game_id} not found")
        logging.info(f"Retrieved game {game_id}")
        return games[game_id]

    def MakeMove(self, request, context):
        game_id = request.game_id
        move = request.move

        if game_id not in games:
            context.abort(StatusCode.NOT_FOUND, f"Game {game_id} not found")

        game = games[game_id]

        if game.is_finished:
            context.abort(StatusCode.FAILED_PRECONDITION, "Game is already finished")

        if move.mark != game.turn:
            context.abort(StatusCode.FAILED_PRECONDITION, "Not player's turn")

        if not (1 <= move.column <= COLUMNS):
            context.abort(StatusCode.INVALID_ARGUMENT, "Invalid column")

        col_count = sum(1 for m in game.moves if m.column == move.column)
        if col_count >= ROWS:
            context.abort(StatusCode.FAILED_PRECONDITION, "Column is full")

        game.moves.append(move)
        logging.info(f"Move made in game {game_id}: Player {move.mark} -> Column {move.column}")

        if self.check_winner(game.moves, move):
            game.is_finished = True
            game.winner = move.mark
            logging.info(f"Game {game_id} won by {move.mark}")
        elif len(game.moves) == ROWS * COLUMNS:
            game.is_finished = True
            logging.info(f"Game {game_id} ended in a draw")
        else:
            game.turn = cf.MARK_YELLOW if move.mark == cf.MARK_RED else cf.MARK_RED

        return game

    def check_winner(self, moves, last_move):
        board = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
        for m in moves:
            for r in reversed(range(ROWS)):
                if board[r][m.column - 1] is None:
                    board[r][m.column - 1] = m.mark
                    break

        def count_direction(r, c, dr, dc):
            count = 0
            mark = board[r][c]
            while 0 <= r < ROWS and 0 <= c < COLUMNS and board[r][c] == mark:
                count += 1
                r += dr
                c += dc
            return count

        for r in range(ROWS):
            for c in range(COLUMNS):
                if board[r][c] is None:
                    continue
                if (count_direction(r, c, 0, 1) + count_direction(r, c, 0, -1) - 1 >= 4 or
                    count_direction(r, c, 1, 0) >= 4 or
                    count_direction(r, c, 1, 1) + count_direction(r, c, -1, -1) - 1 >= 4 or
                    count_direction(r, c, 1, -1) + count_direction(r, c, -1, 1) - 1 >= 4):
                    return True
        return False


def serve():
    port = int(sys.argv[1]) if len(sys.argv) == 2 else 50051
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cf_grpc.add_ConnectFourServicer_to_server(ConnectFourServicer(), server)
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    logging.info(f"Server started on port {port}")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
