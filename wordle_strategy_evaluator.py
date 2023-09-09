from random import randrange

from wordle_helper import WordleHelper, WordleMatchResults

wh = WordleHelper()
word_list = list(wh.word_set)


def count_guesses() -> int:
    word_index = randrange(len(word_list))
    word = word_list[word_index]

    words_to_try = ['lumpy', 'chair', 'stone']

    match_results = WordleMatchResults(yellow_letters='')
    guess_count = 0

    while guess_count < 6 and match_results.green_count() != 5:
        guess_count += 1
        word_to_try = words_to_try.pop()
        match_results += WordleHelper.match_letters(word, word_to_try)
        # print(f"Guess {guess_count}: {word_to_try}, results: {match_results}")
        green_count = match_results.green_count()
        if green_count == 5:
            break

        yellow_count = match_results.yellow_count()
        if (green_count > 2 or green_count + yellow_count > 3
                or len(words_to_try) == 0):
            suggestions = wh.find_words(match_results=match_results, max_words=1)
            words_to_try.append(suggestions[0][0])

    if match_results.green_count() == 5:
        return guess_count
    else:
        print(f"Match Results: {match_results}, word: {word}")
        return 7


if __name__ == '__main__':
    iterations = 200
    guess_distribution = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0}
    for i in range(iterations):
        guesses = count_guesses()
        guess_distribution[str(guesses)] += 1

    print({k: v / float(iterations) * 100.0 for k,v in guess_distribution.items()})
