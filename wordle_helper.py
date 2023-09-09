from typing import Set, List
from english_words import get_english_words_set
from collections import Counter, defaultdict
from itertools import islice, count, chain


def _sort_dict_by_value(d: dict, reverse=False):
    return dict(sorted(d.items(), key=lambda x: x[1], reverse=reverse))


def _normalize_letter_input(s: str):
    s = s.lower() if s is not None else ''
    return s.ljust(5, '?')


def filter_known_letters(known_letters: str, s: str):
    known_letters = _normalize_letter_input(known_letters)
    all_match = True
    for i, l in enumerate(known_letters):
        if l != '?' and l != s[i]:
            all_match = False

    return all_match


def letter_index_map(word: str) -> dict:
    m = defaultdict(list)
    for i, l in enumerate(word):
        m[l].append(i)
    return m


def filter_used_letters(used_letters_list: list, s: str):
    # If used_letters_list is None or empty
    if not used_letters_list:
        return True

    for used_letters_word in used_letters_list:
        used_letters_word = _normalize_letter_input(used_letters_word)
        used_letter_map = letter_index_map(used_letters_word)
        s_letter_map = letter_index_map(s)

        for used_letter in used_letter_map.keys():
            if used_letter == '?':
                continue

            if used_letter in s_letter_map:
                # Compute intersection of the used_letter in s and in the used_letter_word
                # if the intersection is empty, the used_letter doesn't appear at the
                # same position in s as it does in the used_letter_word
                used_index = set(s_letter_map[used_letter]) & set(used_letter_map[used_letter])
                if len(used_index) != 0:
                    return False
            else:
                # The used letter is not in the word,
                # so this word can't match
                return False

    # If we get this far, s has all the letters in 
    # used_letters_list in different positions.
    return True


def filter_wrong_letters(green_letters: str, gray_letters: str, s: str):
    green_letters = _normalize_letter_input(green_letters)
    gray_letters = gray_letters if gray_letters is not None else ''
    has_correct_letters = True
    for i, l in enumerate(s):
        if green_letters[i] == l:
            continue
        elif l in gray_letters:
            has_correct_letters = False
            break

    return has_correct_letters


def _build_letter_freq_dict(word_set: set):
    count_letters = len(word_set)
    freq_dict = Counter()
    for l in 'abcdefghijklmnopqrstuvwxyz':
        for w in word_set:
            if l in w:
                freq_dict[l] += 1

    for l in freq_dict:
        freq_dict[l] /= count_letters

    return _sort_dict_by_value(freq_dict, reverse=True)


def _compute_letter_frequency(w: str, letter_freq_dict: dict):
    freq_prob = 1
    for l in w:
        try:
            freq_prob *= letter_freq_dict[l]
        except KeyError:
            print(f'KeyError: {l} not in letter_freq_dict for word {w}')

    return w, freq_prob


def _pandas_word_set() -> Set:
    """Loads a set of words from BSD Unix. """
    import pandas as pd
    df = pd.read_csv('en_US.txt.gz', names=['words'])
    df = df[(df['words'].str.len() == 5) & (df['words'].str.isalpha())]
    word_set = set(df['words'].str.lower().values)
    return word_set


def _english_word_set() -> Set:
    return set(filter(lambda w: len(w) == 5, get_english_words_set(['gcide','web2'], alpha=True, lower=True)))


def _wordle_word_set() -> Set:
    import pandas as pd
    return set(pd.read_csv('wordle_words.txt', names=['words']).squeeze('columns').values)


class WordleMatchResults:
    green_letters: str = None
    yellow_letters: List[str] = None
    gray_letters: str = None

    def __init__(self, green_letters: str = None, yellow_letters: str | list = None, gray_letters: str = None):
        if green_letters is None and yellow_letters is None and gray_letters is None:
            raise ValueError(
                "At least one of green_letters, yellow_letters and gray_letters must be specified.")

        self.green_letters = green_letters or '?????'
        if isinstance(yellow_letters, str):
            self.yellow_letters = [yellow_letters, ] if len(yellow_letters) > 0 else []
        self.gray_letters = gray_letters or ''

    def __add__(self, other):
        combined_gray_letters, combined_green_letters, combined_yellow_letters = self.__internal_add(other)
        return WordleMatchResults(combined_green_letters, combined_yellow_letters, combined_gray_letters)

    def __internal_add(self, other):
        combined_green_letters = ''
        for i in range(len(self.green_letters)):
            self_green = self.green_letters[i:i + 1]
            other_green = other.green_letters[i:i + 1]
            next_green_letter = self_green if self_green != '?' else other_green
            combined_green_letters += next_green_letter
            combined_yellow_letters = self.yellow_letters + other.yellow_letters
            combined_yellow_letters = list(set(combined_yellow_letters) - {'?????'})
        combined_gray_letters = "".join(set(self.gray_letters + other.gray_letters))
        return combined_gray_letters, combined_green_letters, combined_yellow_letters

    def __iadd__(self, other):
        if other is None:
            return self
        combined_gray_letters, combined_green_letters, combined_yellow_letters = self.__internal_add(other)
        self.green_letters = combined_green_letters
        self.gray_letters = combined_gray_letters
        self.yellow_letters = combined_yellow_letters
        return self

    def green_count(self) -> int:
        return len(list(filter(lambda c: c != '?', self.green_letters)))

    def yellow_count(self) -> int:
        return len(list(filter(lambda c: c != '?', chain.from_iterable(self.yellow_letters))))

    def __repr__(self):
        return (f"Match Results: green_letters {self.green_letters}, yellow_count: {self.yellow_letters}, "
                f"gray_count: {self.gray_letters}")

class WordleHelper:
    def __init__(self, word_set: set = None) -> None:
        if word_set is None:
            self.word_set = set(sorted(_wordle_word_set()))
        letter_freq_dict = _build_letter_freq_dict(self.word_set)
        self.word_frequencies = _sort_dict_by_value(dict(map(lambda x: _compute_letter_frequency(
            x, letter_freq_dict), set(self.word_set))), reverse=True)

    def find_words(self, green_letters: str = None, yellow_letters: str | list = None, gray_letters: str = None,
                   match_results: WordleMatchResults = None,
                   by_frequency=True, max_words=100):
        if match_results is None:
            match_results = WordleMatchResults(green_letters, yellow_letters, gray_letters)

        word_set = self.word_frequencies.keys() if by_frequency else self.word_set
        words = list(islice(filter(lambda w1: filter_known_letters(match_results.green_letters, w1) and
                                   filter_used_letters(match_results.yellow_letters, w1) and
                                   filter_wrong_letters(match_results.green_letters, match_results.gray_letters, w1),
                                   word_set), max_words))

        if by_frequency:
            return list(map(lambda w: (w, round(self.word_frequencies[w] * 100, 2)), words))
        else:
            return words

    @staticmethod
    def match_letters(wordle_word: str, guess_word: str) -> WordleMatchResults:
        green_letters = '?' * 5
        yellow_letters = '?' * 5
        gray_letters = ''
        for index, guess_letter in enumerate(guess_word):
            if wordle_word[index] == guess_letter:
                green_letters = green_letters[:index] + guess_letter + green_letters[index+1:]
                continue

            try:
                _ = wordle_word.index(guess_letter)
                yellow_letters = yellow_letters[:index] + guess_letter + yellow_letters[index+1:]
            except ValueError:
                gray_letters += guess_letter

        return WordleMatchResults(green_letters, yellow_letters, gray_letters)

