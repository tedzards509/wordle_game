import os
import threading


# TODO: Bessere Wortlisten (n-gram)
def load_dict(file):
    with open(file, encoding="utf-8") as f:
        words = f.readlines()
    for n in range(len(words)):
        words[n] = words[n][:-1].lower()
    return words


def write_dict(filename: str, wordlist: list[str]):
    with open(filename, "w") as f:
        for word in wordlist:
            f.write(word + "\n")


def generate_dictionary(length, dictionary_location, output_location):
    full_dictionary = load_dict(dictionary_location)
    filtered = [word for word in full_dictionary if len(word) == length]
    for word in filtered:
        if filtered.count(word) > 1:
            filtered.remove(word)
    write_dict(output_location, filtered)


def generate_all_dictionaries_for_length(length, dict_names: tuple = ("common", "shorter", "full")):
    print("common")
    generate_dictionary(length,
                        os.path.join("./ger/", "german_common.txt"),
                        os.path.join(f"./ger/{length}_letter", f"common_{length}.txt"))
    print("shorter")
    generate_dictionary(length,
                        os.path.join("./ger/", "german_shorter.txt"),
                        os.path.join(f"./ger/{length}_letter", f"shorter_{length}.txt"))
    print("full")
    generate_dictionary(length,
                        os.path.join("./ger/", "german.txt"),
                        os.path.join(f"./ger/{length}_letter", f"full_{length}.txt"))


def generate_all_dictionaries(lower, upper):
    threads = []
    for i in range(lower, upper + 1):
        threads.append(threading.Thread(target=generate_all_dictionaries_for_length(),
                                        args=(i,)))
    for thread in threads:
        thread.start()
