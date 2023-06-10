from wordlegame import WordleGame
from words.textutils import generate_all_dictionaries

if __name__ == '__main__':
    game = WordleGame(max_length=5, max_tries=6)
    game.main_wordle_game()
    # generate_all_dictionaries(3, 7)
