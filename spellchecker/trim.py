def trim(text):
    if len(text) == 0:
        return ""

    text = trim_front(text)
    text = trim_back(text)
    return text


def trim_front(text):
    n = 0
    while n < len(text) and text[n] in (' ', '\t', '\n', '\r'):
        n += 1

    return text[n:]


def trim_back(text):
    n = len(text) - 1
    while n >= 0 and text[n] in (' ', '\t', '\n', '\r'):
        n -= 1

    return text[0:n+1]


def trim_plural(text):
    text = text.replace(u"\u2019", "'")
    if text[-2:] == "'s":
        return text[:-2]

    if text[-1:] == "s":
        return text[:-1]

    return text


def trim_punctuation(text):
    c = text[-1]
    while len(text) > 0 and c in (".", ",", ":", ";", "?", "!"):
        text = text[:-1]
        if len(text) > 0:
            c = text[-1]

    return text
