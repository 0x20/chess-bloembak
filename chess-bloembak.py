#!/usr/bin/env python3

import chess
import chess.engine
import math
import time
import os
import logging
import argparse
lumos = None

# color of a piece owned by the black player
black_piece = "550000"
# color of a piece owned by the white player
white_piece = "ffffff"
# board color white
white = "222222"
# board color for black
#black= "b58863"
black= "000000"
# resets the terminal color
ENDC = '\033[0m'

# 4x4 'sprites' of chess pieces
knight_arr = "0000011001000000"
rook_arr = "0000010001000000"
pawn_arr = "0000001000000000"
bishop_arr = "0000001001000000"
king_arr = "0000011011110000"
queen_arr = "0000011001100000"
empty_arr = "0000000000000000"

# engine = chess.engine.SimpleEngine.popen_uci(r"/home/pi/miker/Stockfish-sf_15/src/stockfish")
engine = chess.engine.SimpleEngine.popen_uci(r"/opt/homebrew/bin/stockfish")
engine.configure({"Threads": 4})


class Canvas():
    the_canvas = ""
    CANVAS_LENGTH = 32*32*6

    def __init__(self):
        self.the_canvas = black*1024
        assert len(self.the_canvas) == self.CANVAS_LENGTH

    def pos_to_index(self, pos):
        pos_in_row = pos%8
        rows = math.floor(pos/8)
        start = rows*768 + pos_in_row * 6*4
        return start

    def set_piece(self, sub_frame, position):
        #print(f"Setting piece with subframe {sub_frame} on pos {position}")
        #self.print(frame=sub_frame, line=4)
        start = self.pos_to_index(position)
        #print(f"start is {start}")
        for i in range(0, len(sub_frame), 24):
            self.the_canvas = self.the_canvas[:start] + sub_frame[i:i+24] + self.the_canvas[start+24:]
            #print(self.the_canvas[:start-1], " ", sub_frame[i:i+24], " ", self.the_canvas[start+24:])
            #print(len(self.the_canvas))
            assert len(self.the_canvas) == self.CANVAS_LENGTH, f"len is {len(self.the_canvas)}"
            start = start + 6*32

    def print(self, frame=None, line=32):
        count = 1
        if frame == None:
            frame = self.the_canvas
        os.system('clear')
        #print(chr(27) + "[2J")
        for i in range(0, len(frame), 6):
            r = frame[i:i+2]
            g = frame[i+2:i+4]
            b = frame[i+4:i+6]
            print_pixel(r,g,b)
            if count == line:
                print("")
                count = 0
            count = count + 1

    def lumos(self):
        lumos.push(self.the_canvas, 1)



board = chess.Board()
canvas = Canvas()

def create_piece(arr, back_color, piece_color):
    result = ""
    assert len(arr) == 16
    for entry in arr:
        if entry == '0':
            result = result + back_color
        else:
            result = result + piece_color
    assert len(result) == 16*6
    return result

def print_pixel(r,g,b):
    rh = int("0x"+r, 16)
    gh = int("0x"+g, 16)
    bh = int("0x"+b, 16)
    print("\x1B[48;2;" + f"{rh};{gh};{bh}m", ENDC, end="")
    print("\x1B[48;2;" + f"{rh};{gh};{bh}m", ENDC, end="")


knight = create_piece(knight_arr, black, white_piece)
rook = create_piece(rook_arr, black, white_piece)
pawn = create_piece(pawn_arr, black, white_piece)
bishop = create_piece(bishop_arr, black, white_piece)
king = create_piece(king_arr, black, white_piece)
queen = create_piece(queen_arr, black, white_piece)
empty_black = create_piece(empty_arr, black, white_piece)
empty_white = create_piece(empty_arr, white, white_piece)


white_block = white * 4
black_block = black * 4
start_line = (white_block + black_block) * 4
other_line = (black_block + white_block) * 4
start_line_full = start_line * 4
other_line_full = other_line * 4

frame = (start_line_full + other_line_full) * 4

def print_frame(frame, line=32):
    #print(f"len frame is {len(frame)}")
    count = 1
    for i in range(0, len(frame), 6):
        r = frame[i:i+2]
        g = frame[i+2:i+4]
        b = frame[i+4:i+6]
        print_pixel(r,g,b)
        if count == line:
            print("")
            count = 0
        count = count + 1

def get_board_frame(fen, black_board_color=black, white_board_color=white):
    frame = ""
    board_colors=[white_board_color, black_board_color]
    board_counter = 0
    board_fen = fen.split(' ')[0]
    position = 0
    #print(board_fen)
    for cased_char in board_fen:
        piece_color = white_piece if cased_char.isupper() else black_piece
        board_color = board_colors[board_counter%2]
        #print(f"board color: {board_color}, piece color: {piece_color}")
        char = cased_char.lower()
        result = ""
        if char == 'r':
            result = create_piece(rook_arr, board_color, piece_color)
            canvas.set_piece(result, position)
            board_counter = board_counter + 1
            position = position + 1
        elif char == 'n':
            result = create_piece(knight_arr, board_color, piece_color)
            canvas.set_piece(result, position)
            board_counter = board_counter + 1
            position = position + 1
        elif char == 'b':
            result = create_piece(bishop_arr, board_color, piece_color)
            canvas.set_piece(result, position)
            board_counter = board_counter + 1
            position = position + 1
        elif char == 'q':
            result = create_piece(queen_arr, board_color, piece_color)
            canvas.set_piece(result, position)
            board_counter = board_counter + 1
            position = position + 1
        elif char == 'k':
            result = create_piece(king_arr, board_color, piece_color)
            canvas.set_piece(result, position)
            board_counter = board_counter + 1
            position = position + 1
        elif char == 'p':
            result = create_piece(pawn_arr, board_color, piece_color)
            canvas.set_piece(result, position)
            board_counter = board_counter + 1
            position = position + 1
        elif char == '/':
            result = ""
            board_counter = board_counter + 1
        else:
            #print("unrecognized char", char)
            number = int(char)
            for i in range(0,number):
                board_color = board_colors[board_counter%2]
                board_counter = board_counter + 1
                result = create_piece(empty_arr, board_color, board_color)
                canvas.set_piece(result, position)
                position = position + 1


def game_loop(console_output=False, delay=2):
    if not console_output:
        import lumos
    output = canvas.print if console_output else canvas.lumos
    output()
    while 1:
        #moves = list(board.legal_moves)
        #move = moves[random.randint(0, len(moves)-1)]
        result = engine.play(board, chess.engine.Limit(time=0.1))
        board.push(result.move)
        get_board_frame(board.fen())
        output()
        # blink the board 5 times if the game is finished
        if board.outcome() is not None:
            print("board outcome is ", board.outcome())
            for i in range(0,5):
                get_board_frame(board.fen(), black_board_color=white, white_board_color=black)
                output()
                time.sleep(delay/4)
                get_board_frame(board.fen())
                output()
                time.sleep(delay/4)
            time.sleep(delay*10)
            board.reset()
        time.sleep(delay)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.basicConfig(format="%(asctime)s %(name)s: %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="chess on bloembak")
    parser.add_argument(
        "--ascii",
        help="outputs the frames on the terminal",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-x", "--verbose", help="Set logging to debug mode", action="store_true"
    )
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    game_loop(console_output=args.ascii, delay=10)
