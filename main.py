from wordlegame import WordleGame
import threading


def start_game(tr_game: WordleGame):
    tr_game.main_wordle_game()


if __name__ == '__main__':
    game = WordleGame(max_length=5, max_tries=6)
    thread = threading.Thread(target=start_game, args=(game,))
    thread.start()
