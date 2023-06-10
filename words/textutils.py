import os


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


def generate_all_dictionaries():
    for i in range(3, 8):
        print("=" * 20 + "\n")
        print(f"Generating {i}-letter dictionaries...")
        print("common")
        generate_dictionary(i,
                            os.path.join("./ger/", "german_common.txt"),
                            os.path.join(f"./ger/{i}_letter", f"common_{i}.txt"))
        print("shorter")
        generate_dictionary(i,
                            os.path.join("./ger/", "german_shorter.txt"),
                            os.path.join(f"./ger/{i}_letter", f"shorter_{i}.txt"))
        print("full")
        generate_dictionary(i,
                            os.path.join("./ger/", "german.txt"),
                            os.path.join(f"./ger/{i}_letter", f"full_{i}.txt"))
        print(f"Done generating {i}-letter dictionaries!")
        print("=" * 20)
