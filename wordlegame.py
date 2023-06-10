import pygame
import random
import os
from words.textutils import load_dict

VALID_KEYS = [num for num in range(97, 123)] + [223, 228, 246, 252]  # a-z + ß, ä, ö, ü
D_KEYBOARD_LAYOUT = ["QWERTZUIOPÜ", "ASDFGHJKLÖÄ", "ßYXCVBNM"]
FPS_LIMIT = 60

D_DARK_MODE_COLORS = {
    "green": "#538d4e",
    "yellow": "#b59f3b",
    "grey": "#3a3a3c",
    "inactive": "#818384",
    "bg": "#121213",
    "border": "#3a3a3c",
    "border-active": "#565758",
    "letter": "#ffffff"
}
D_LIGHT_MODE_COLORS = {
    "green": "#6aaa64",
    "yellow": "#c9b458",
    "grey": "#787c7e",
    "inactive": "#d3d6da",
    "bg": "#ffffff",
    "border": "#d3d6da",
    "border-active": "#878a8c",
    "letter": "#ffffff"
}

D_MAX_LENGTH = 5
D_MAX_TRIES = 6
D_TILE_SIZE = 100

D_PAD_FACTOR = 0.9
D_BORDER_WIDTH = D_TILE_SIZE * D_PAD_FACTOR // 15


def ss_safe_upper(self: str):
    return self.upper() if "ß" not in self else self.upper().replace("SS", "ß")


def key_to_letter(key):
    if key in range(97, 123):
        return pygame.key.name(key)
    else:
        return {
            252: "ü",
            246: "ö",
            228: "ä",
            223: "ß"
        }.get(key)


def init_keys(keyboard_layout: list[str]):
    letters = []
    for row in keyboard_layout:
        row_out = []
        for lett in row:
            row_out.append(Letter(lett, -1))
        letters.append(row_out)
    return letters


class Letter:
    def __init__(self, value: chr, correct: int):
        self.value = value
        self.correct = correct

    def __str__(self):
        return f"({self.value}, {self.correct})"


class KeyboardButton:
    def __init__(self, rect: tuple[int, int, int, int], colors, key: Letter):
        self.rect = pygame.Rect(rect)  # Left, Top, Width, Height
        self.button_color = colors[{-1: "inactive", 0: "grey", 1: "yellow", 2: "green"}.get(key.correct)]
        self.text_color = colors["letter"]
        self.key = key

    def draw(self, screen):
        pygame.draw.rect(screen, self.button_color, self.rect, border_radius=self.rect[2] // 5)
        font = pygame.font.Font(None, self.rect[3])
        text = font.render(self.key.value, True, self.text_color)
        text_width, text_height = font.size(self.key.value)
        text_x = self.rect[0] + (self.rect[2] - text_width) // 2
        text_y = self.rect[1] + (self.rect[3] - text_height) // 2
        screen.blit(text, (text_x, text_y))

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class GameVars:
    def __init__(self,
                 words: list[list[Letter]],
                 cur_try: int,
                 cur_word: list,
                 cur_word_index: int,
                 secret_word: str,
                 won: bool,
                 lost: bool,
                 keys: list[list[Letter]],
                 possible_words: list[str],
                 default_keys: list[list[Letter]],
                 max_length: int
                 ):
        self.words = words
        self.cur_try = cur_try
        self.cur_word = cur_word
        self.cur_word_index = cur_word_index
        self.secret_word = secret_word
        self.won = won
        self.lost = lost
        self.keys = keys
        self.possible_words = possible_words
        self.init_keys = default_keys
        self.max_length = max_length

    def reset_game_vars(self):
        self.words, self.cur_try, self.cur_word, self.cur_word_index, self.secret_word, self.won, self.lost, self.keys \
            = (
                [],
                1,
                [' ' for _ in range(self.max_length)],
                0,
                ss_safe_upper(random.choice(self.possible_words)),
                False,
                False,
                self.init_keys.copy()
            )


def get_game_vars(max_length, possible_words, keyboard_layout):
    return (
            [],
            1,
            [' ' for _ in range(max_length)],
            0,
            ss_safe_upper(random.choice(possible_words)),
            False,
            False,
            init_keys(keyboard_layout)
        )


class StyleVars:
    def __init__(
            self,
            colors: tuple[dict[str, str], dict[str, str]] = (D_DARK_MODE_COLORS, D_LIGHT_MODE_COLORS),
            dark_mode: bool = True,
            tile_size: int = D_TILE_SIZE,
            padding_factor: float = D_PAD_FACTOR,
            border_width: int = D_BORDER_WIDTH,
    ):
        self.colors = colors
        self.dark_mode = dark_mode
        self.tile_size = tile_size
        self.pad_factor = padding_factor
        self.border_width = int(border_width)

    def get_colors(self):
        return self.colors[0] if self.dark_mode else self.colors[1]

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        return self.get_colors()

    def size_from_tiles(self, tiles_width: float = 1, tiles_height: float = 1):
        return round(tiles_width * self.tile_size), round(tiles_height * self.tile_size)


class WordleGame:
    def __init__(self,
                 max_length: int = D_MAX_LENGTH,
                 max_tries: int = D_MAX_TRIES,
                 keyboard_layout: list[str] = None,
                 style_vars: StyleVars = StyleVars()
                 ):
        self.running = True

        self.max_length = max_length
        self.max_tries = max_tries

        self.allowed_words = load_dict(os.path.join(f"./words/ger/{max_length}_letter", f"shorter_{max_length}.txt"))
        self.possible_words = load_dict(os.path.join(f"./words/ger/{max_length}_letter", f"common_{max_length}.txt"))

        if keyboard_layout is None:
            self.keyboard_layout = D_KEYBOARD_LAYOUT.copy()

        self.game_vars = GameVars(
            *get_game_vars(self.max_length, self.possible_words, self.keyboard_layout),
            possible_words=self.possible_words,
            default_keys=init_keys(self.keyboard_layout),
            max_length=self.max_length
        )

        self.style_vars = style_vars
        self.colors = self.style_vars.get_colors()

    # TODO - low level draw methods to functions
    def draw_letter(self, font, colors, position: tuple[int, int], screen, letter: chr):
        text = font.render(letter, True, colors["letter"])
        text_width, text_height = font.size(letter)
        text_x = position[0] + (self.style_vars.tile_size - text_width) // 2
        text_y = position[1] + (self.style_vars.tile_size - text_height) // 2
        screen.blit(text, (text_x, text_y))

    def draw_tile_completed(self, letter: Letter, position: tuple[int, int], screen: pygame.surface, colors, font):
        square_size = round(self.style_vars.tile_size * self.style_vars.pad_factor)
        offset = (self.style_vars.tile_size - square_size) / 2
        rect = (position[0] + offset, position[1] + offset, square_size, square_size)
        color = {
            -1: "inactive",
            0: "grey",
            1: "yellow",
            2: "green"
        }.get(letter.correct)
        pygame.draw.rect(surface=screen, color=colors[color], rect=rect)

        self.draw_letter(font, colors, position, screen, letter.value)

    def draw_tile_active_row(self, letter, position, screen, colors, font):
        square_size = round(self.style_vars.tile_size * self.style_vars.pad_factor)
        offset = (self.style_vars.tile_size - square_size) // 2
        rect = (position[0] + offset, position[1] + offset, square_size, square_size)
        color = colors["border"] if letter == ' ' else colors["border-active"]
        pygame.draw.rect(surface=screen, color=color, rect=rect, width=self.style_vars.border_width)

        self.draw_letter(font, colors, position, screen, letter)

    def draw_tile_inactive(self, position, screen, colors):
        square_size = round(self.style_vars.tile_size * self.style_vars.pad_factor)
        offset = (self.style_vars.tile_size - square_size) / 2
        rect = (position[0] + offset, position[1] + offset, square_size, square_size)
        color = colors["border"]
        pygame.draw.rect(surface=screen, color=color, rect=rect, width=self.style_vars.border_width)

    def draw_key(self, lett, screen, colors, rect: tuple[int, int, int, int]):
        button = KeyboardButton(rect, colors, lett)
        button.draw(screen)

    def draw_keyboard(self, game_vars: GameVars, screen, colors, pos: tuple[int, int] = (0, 0), ):
        keyboard_key_width = \
            round((self.style_vars.tile_size * self.max_length //
                   max([len(row) for row in game_vars.keys])) * self.style_vars.pad_factor)
        keyboard_key_height = round(keyboard_key_width * 2 * self.style_vars.pad_factor * self.style_vars.pad_factor)
        horizontal_offset = round(keyboard_key_width * (1 - self.style_vars.pad_factor) // 2)
        vertical_offset = round(keyboard_key_height * (1 - self.style_vars.pad_factor*self.style_vars.pad_factor) // 2)
        for i in range(len(game_vars.keys)):
            row = game_vars.keys[i]
            for j in range(len(row)):
                lett = row[j]
                rect = (round(pos[0] + j * (keyboard_key_width + horizontal_offset)),
                        round(pos[1] + i * (keyboard_key_height + vertical_offset)),
                        keyboard_key_width, keyboard_key_height)
                self.draw_key(lett, screen, colors, rect)

    def draw_word_grid(self, game_vars: GameVars, screen, colors, font, pos: tuple[int, int] = (0, 0)):
        # Draw checked tiles (Using Letter objects from words)
        for trie in range(game_vars.cur_try - 1):  # try und let.... Oh mann
            for lett in range(self.max_length):
                position = (pos[0] + lett * self.style_vars.tile_size, pos[1] + trie * self.style_vars.tile_size)
                self.draw_tile_completed(game_vars.words[trie][lett], position, screen, colors, font)

        # Draw currently edited line (Using cur_word)
        if game_vars.cur_try <= self.max_tries:
            for lett in range(self.max_length):
                position = (pos[0] + lett * self.style_vars.tile_size,
                            pos[1] + (game_vars.cur_try - 1) * self.style_vars.tile_size)
                self.draw_tile_active_row(game_vars.cur_word[lett], position, screen, colors, font)

        # Draw inactive lines
        for trie in range(game_vars.cur_try, self.max_tries):
            for lett in range(self.max_length):
                position = (pos[0] + lett * self.style_vars.tile_size, pos[1] + trie * self.style_vars.tile_size)
                self.draw_tile_inactive(position, screen, colors)

    def check_word(self, cur_word):
        for lett in cur_word:
            if lett == ' ':
                print("Wort noch nicht vollendet")
                return False
        word = ''.join([lett for lett in cur_word])
        if word.lower() not in self.allowed_words:
            print("Wort nicht erlaubt")
            return False
        return True

    def word_to_letter_list(self, cur_word, keys, secret_word):
        letter_list = []
        counted_letters = []
        for i in range(self.max_length):
            lett = cur_word[i]
            lett_obj = Letter(lett, 0)
            if lett == secret_word[i]:
                lett_obj.correct = 2
            elif lett in secret_word:
                if secret_word.count(lett) >= cur_word.count(lett):
                    lett_obj.correct = 1
                else:
                    not_green_letters = secret_word.count(lett) - len(
                        [index for index in range(len(cur_word)) if cur_word[index] == secret_word[index]]
                    )
                    if counted_letters.count(lett) < not_green_letters:
                        lett_obj.correct = 1
                        counted_letters.append(lett)
            letter_list.append(lett_obj)

            for row in keys:
                for key in row:
                    if key.value == lett and key.correct < lett_obj.correct:
                        key.correct = lett_obj.correct
        return letter_list

    def initialize_pygame(self, screen_size):
        screen_width = screen_size[0]
        screen_height = screen_size[1]
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Wordle Game")
        return screen

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_key_event(event.key)

    def handle_key_event(self, key):
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_SPACE:
            self.colors = self.style_vars.toggle_dark_mode()
        if not self.game_vars.won or self.game_vars.lost:
            if key in VALID_KEYS:
                self.handle_valid_key(key)
            elif key == pygame.K_BACKSPACE:
                self.handle_backspace_key()
            elif key == pygame.K_RETURN and self.check_word(
                    self.game_vars.cur_word) and self.game_vars.cur_try <= self.max_tries:
                self.handle_return_key()

    def handle_valid_key(self, key):
        if not self.game_vars.cur_word_index >= self.max_length:
            self.game_vars.cur_word[self.game_vars.cur_word_index] = ss_safe_upper(key_to_letter(key))
            self.game_vars.cur_word_index += 1

    def handle_backspace_key(self):
        if not self.game_vars.cur_word_index <= 0:
            self.game_vars.cur_word_index -= 1
            self.game_vars.cur_word[self.game_vars.cur_word_index] = ' '

    def handle_return_key(self):
        new_line = self.word_to_letter_list(self.game_vars.cur_word, self.game_vars.keys, self.game_vars.secret_word)
        if [lett.correct == 2 for lett in new_line].count(True) == self.max_length:
            self.game_vars.won = True
        elif self.game_vars.cur_try == self.max_tries:
            self.game_vars.lost = True
        self.game_vars.words.append(new_line)
        self.game_vars.cur_try += 1
        self.game_vars.cur_word = [' ' for _ in range(self.max_length)]
        self.game_vars.cur_word_index = 0

    def draw_game(self, screen, colors, font):
        screen.fill(colors["bg"])
        self.draw_word_grid(self.game_vars, screen, colors, font, (0, self.style_vars.tile_size))
        self.draw_keyboard(self.game_vars, screen, colors, (0, self.style_vars.tile_size * (self.max_tries + 1)))

    def main_wordle_game(self, screen_size: tuple[int, int] = None, colors: dict[str, str] = None,
                         font: pygame.font.Font = None,
                         ):
        pygame.init()
        clock = pygame.time.Clock()

        if screen_size is None:
            screen_size = self.style_vars.size_from_tiles(self.max_length, self.max_tries + 3.5)
        if colors is None:
            colors = self.style_vars.get_colors()
        if font is None:
            font = pygame.font.Font(None, self.style_vars.tile_size)

        screen = self.initialize_pygame(screen_size)

        while self.running:
            self.handle_events()
            self.draw_game(screen, colors, font)
            pygame.display.flip()
            clock.tick(FPS_LIMIT)
        pygame.quit()
