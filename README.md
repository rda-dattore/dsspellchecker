# dsspellchecker

This spellchecker validates the words in a text string and returns a list of words that fail to validate.

The project was developed mainly for the purpose of validating the text fields of the dataset metadata for the NSF NCAR Research Data Archive. This means that the dictionary is mainly geoscience- and dataset-focused, and you might not find words like 'beautiful', for example, that you otherwise expect to find. There is a way to add words to the dictionary, but be aware that if you want to use it for more general use, it will likely require numerous additions.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install spellchecker.

Follow these steps:
1. Download the wheel (.whl) file from the dist directory
1. From within your python environment:
   - run `pip install <name_of_wheel_file>`
   - build the spellchecker database from the command line with the utility `build_spellchecker_db`

## Usage

```python
from spellchecker import SpellChecker

spell_checker = SpellChecker()
print(spell_checker.initialized)
# True if the spellchecker is ready, False if error

print(spell_checker.error)
# '' for no error (initialized == True), otherwise some message

# check some text
spell_checker.check("This dataset contains data from a reanalysis model. Parameters include "
    "temperature at 2 meters and winds at 10 meters.")
print(spell_checker.misspelled_words)
# prints [] because all words validate

# check some text with two misspellings
spell_checker.check("This datset contains data from a reanalysis model. Parmeters include "
    "temperature at 2 meters and winds at 10 meters.")
print(spell_checker.misspelled_words)
# prints ['datset', 'Parmeters'] for the two misspelled words
```

## Data
