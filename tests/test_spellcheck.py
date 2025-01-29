import unittest


from spellchecker import SpellChecker


sc = SpellChecker()


class TestSpellCheck(unittest.TestCase):
    def test_initialize(self):
        self.assertTrue(sc.initialized)


    def test_general(self):
        sc.check("Hello, world!")
        self.assertEqual(sc.misspelled_words, [])
        sc.check("Hello, wrold!")
        self.assertEqual(sc.misspelled_words, ["wrold"])
        sc.check("This is a test, (and I hope it passes)!")
        self.assertEqual(sc.misspelled_words, [])


    def test_place(self):
        sc.check("I live in Tennessee.")
        self.assertEqual(sc.misspelled_words, [])
        sc.check("I live in tennessee.")
        self.assertEqual(sc.misspelled_words, ['tennessee'])


if __name__ == "__main__":
    unittest.main(verbosity=2)
