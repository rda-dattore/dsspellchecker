# spellchecker

This spellchecker validates the words in a text string, and returns a list of words that fail to validate.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install spellchecker.

Follow these steps:
1. Download the wheel (.whl) file from the dist directory
1. From within your python environment, run `pip install <name_of_wheel_file>`
1. Build the spellchecker database with the command `build_spellchecker_db`


## Usage

```python
from spellchecker import SpellChecker


spell_checker = SpellChecker()
```
