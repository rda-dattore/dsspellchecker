import os
import site
import sqlite3


from .utils import clean_word, unknown
from .trim import trim, trim_plural, trim_punctuation


class SpellChecker:
    def __init__(self):
        self._general_valids = []
        self._acronym_valids = []
        self._exact_match_valids = []
        self._units_valids = []
        self._file_ext_valids = []
        self._valids = {
            'general': [
                {'column': "word", 'set': self._general_valids},
            ],
            'non_english': [
                {'column': "word", 'set': self._general_valids},
            ],
            'acronyms': [
                {'column': "word", 'set': self._acronym_valids},
                {'column': "description", 'set': self._exact_match_valids},
            ],
            'places': [
                {'column': "word", 'set': self._exact_match_valids},
            ],
            'names': [
                {'column': "word", 'set': self._exact_match_valids},
            ],
            'exact_others': [
                {'column': "word", 'set': self._exact_match_valids},
            ],
            'units': [
                {'column': "word", 'set': self._units_valids},
            ],
            'file_exts': [
                {'column': "word", 'set': self._file_ext_valids},
            ],
        }
        self._misspelled_words = []
        self._error = ""
        try:
            conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "data/valids.db"))
            cursor = conn.cursor()
            for key in self._valids:
                for e in self._valids[key]:
                    e['set'].extend(self.fill_valids(cursor, key, e['column']))

            self._initialized = True
        except Exception as err:
            self._initialized = False
            self._error = err


    def __del__(self):
        del self._general_valids
        del self._acronym_valids
        del self._exact_match_valids
        del self._units_valids
        del self._file_ext_valids


    @property
    def initialized(self):
        return self._initialized


    @property
    def error(self):
        return self._error


    @property
    def misspelled_words(self):
        return self._misspelled_words


    def fill_valids(self, cursor, table, column):
        try:
            cursor.execute("select " + column + " from " + table)
            res = cursor.fetchall()
            return [e[0] for e in res]
        except Exception as err:
            raise Exception("error filling valids table '{}': '{}'".format(table, err))


    def check(self, text):
        check_text = text
        check_text = check_text.replace("\n", " ").replace("\u2010", "-")
        check_text = trim(check_text)

        # check the text case-insensitive against the general words
        self._misspelled_words = unknown(check_text, self._general_valids, icase=True, file_ext_valids=self._file_ext_valids)
        if len(self._misspelled_words) > 0:
            check_text = self.new_text(check_text)

            # check the text directly against the acronyms, trimming plurals
            self._misspelled_words = unknown(check_text, self._acronym_valids, trimPlural=True)

        if len(self._misspelled_words) > 0:
            check_text = self.new_text(check_text)

            # check the text directly against the exact match valids
            self._misspelled_words = unknown(check_text, self._exact_match_valids)

        if len(self._misspelled_words) > 0:
            check_text = self.new_text(check_text)
            if text.find("-") >= 0:
                # check compound (hyphen) words in the text case-insensitive against the general words
                self._misspelled_words = unknown(check_text, self._general_valids, separator="-", icase=True)

        if len(self._misspelled_words) > 0:
            check_text = self.new_text(check_text)
            if text.find("\u2013") >= 0:
                # check compound (unicode En-dash) words in the text case-insensitive against the general words
                self._misspelled_words = unknown(check_text, self._general_valids, separator="\u2013", icase=True)

        if len(self._misspelled_words) > 0:
            check_text = self.new_text(check_text)
            if text.find("/") >= 0:
                # check compound (slash) words in the text case-insensitive against the general words
                self._misspelled_words = unknown(check_text, self._general_valids, separator="/", icase=True)

        if len(self._misspelled_words) > 0:
            check_text = self.new_text(check_text)
            if text.find("/") >= 0:
                # check compound (slash) words in the text directly against the acronyms
                self._misspelled_words = unknown(check_text, self._acronym_valids, separator="/")

        if len(self._misspelled_words) > 0:
            check_text = text
            check_text = check_text.replace("\n", " ")
            check_text = trim(check_text)
            check_text = self.new_text(check_text, includePrevious=True)
            # check text directly against the units valids
            self._misspelled_words = unknown(check_text, self._units_valids, units=True)

        if len(self._misspelled_words) > 0:
            check_text = self.new_text(check_text)
            if text.find("_") >= 0:
                # check snake_case words in the text case-insensitive against the general words
                self._misspelled_words = unknown(check_text, self._general_valids, separator="_", icase=True)

        # ignore 'unknown' acronyms
        if len(self._misspelled_words) > 0:
            for x in range(0, len(self._misspelled_words)):
                word = trim_plural(self._misspelled_words[x].replace(".", ""))
                if word.isalnum() and word == word.upper():
                    self._misspelled_words[x] = ""

            self._misspelled_words = [e for e in self._misspelled_words if len(e) > 0]


    def new_text(self, text, **kwargs):
        if 'includePrevious' in kwargs and kwargs['includePrevious']:
            words = text.split()
            text = ""
            if words[0] == self._misspelled_words[0]:
                text = "XX " + self._misspelled_words[0]
                midx = 1
            else:
                midx = 0

            for n in range(1, len(words)):
                if midx == len(self._misspelled_words):
                    break

                if self._misspelled_words[midx] in (words[n], clean_word(words[n]), trim_punctuation(words[n]), trim(words[n])):
                    text += " " + words[n-1] + " " + self._misspelled_words[midx]
                    midx += 1

            return text

        return " ".join(self._misspelled_words)
