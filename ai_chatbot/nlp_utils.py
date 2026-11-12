import re

STOPWORDS = {
    "a", "an", "the", "is", "are", "am", "was", "were", "be", "been",
    "to", "of", "and", "or", "in", "on", "at", "for", "with", "it", "this",
    "that", "does", "did", "could", "would", "will", "please",
    "just", "so", "there", "some", "any",
}

CONTRACTIONS = [
    (r"n't\b", " not"),
    (r"'m\b", " am"),
    (r"'re\b", " are"),
    (r"'ll\b", " will"),
    (r"'ve\b", " have"),
    (r"'d\b", " would"),
    (r"'s\b", ""),
]


def edit_distance(a, b):
    rows, cols = len(a) + 1, len(b) + 1
    table = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        table[i][0] = i
    for j in range(cols):
        table[0][j] = j

    for i in range(1, rows):
        for j in range(1, cols):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            table[i][j] = min(
                table[i - 1][j] + 1,        
                table[i][j - 1] + 1,       
                table[i - 1][j - 1] + cost,  
            )
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                table[i][j] = min(table[i][j], table[i - 2][j - 2] + 1)
    return table[-1][-1]


def stem(word):
    if len(word) <= 3 or not word.isalpha():
        return word

    if word.endswith("ies") and len(word) > 4:
        word = word[:-3] + "y"
    elif word.endswith("s") and not word.endswith(("ss", "us", "is")):
        word = word[:-1]

    for suffix in ("ing", "ed", "ly"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[:-len(suffix)]
            break

    # make "make" and "making" meet in the middle
    if word.endswith("e") and len(word) > 3:
        word = word[:-1]
    return word


class Preprocessor:

    def __init__(self, vocabulary=None):
        self.vocabulary = set(vocabulary or [])

    def tokenize(self, text):
        text = text.lower().replace("’", "'")
        text = text.replace("won't", "will not").replace("can't", "can not")
        for pattern, replacement in CONTRACTIONS:
            text = re.sub(pattern, replacement, text)
        return re.findall(r"[a-z0-9]+", text)

    def correct(self, tokens):
        known = self.vocabulary | STOPWORDS
        fixed = []
        for token in tokens:
            if token in known or not token.isalpha() or len(token) < 4:
                fixed.append(token)
                continue

            allowed = 1 if len(token) <= 5 else 2
            best, best_distance = token, allowed + 1
            for word in sorted(self.vocabulary):
                if abs(len(word) - len(token)) > allowed:
                    continue
                distance = edit_distance(token, word)
                if distance < best_distance:
                    best, best_distance = word, distance
            fixed.append(best)
        return fixed

    def remove_stopwords(self, tokens):
        return [token for token in tokens if token not in STOPWORDS]

    def process(self, text, correct=True):
        tokens = self.tokenize(text)
        if correct:
            tokens = self.correct(tokens)
        tokens = self.remove_stopwords(tokens)
        return [stem(token) for token in tokens]