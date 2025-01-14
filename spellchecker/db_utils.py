import getopt
import os
import shutil
import site
import sqlite3
import sys


db_config = {
    'general': {
        'columns': ["word"],
        'primary_key': "word",
        'icase': True,
    },
    'units': {
        'columns': ["word"],
        'primary_key': "word",
        'icase': False,
    },
    'places': {
        'columns': ["word"],
        'primary_key': "word",
        'icase': False,
    },
    'names': {
        'columns': ["word"],
        'primary_key': "word",
        'icase': False,
    },
    'exact_others': {
        'columns': ["word"],
        'primary_key': "word",
        'icase': False,
    },
    'non_english': {
        'columns': ["word"],
        'primary_key': "word",
        'icase': True,
    },
    'file_exts': {
        'columns': ["word"],
        'primary_key': "word",
        'icase': False,
    },
    'acronyms': {
        'columns': ["word", "description"],
        'primary_key': "word",
        'icase': False,
    },
}


def build_db():
    print("Building database from lists of valids ...")
    pkg_dirs = site.getsitepackages()
    if len(pkg_dirs) == 0:
        raise FileNotFoundError("unable to locate site-packages directory")

    try:
        data_dir = os.path.join(pkg_dirs[0], "spellchecker/data")
        conn = sqlite3.connect(os.path.join(data_dir, "valids.db"))
        cursor = conn.cursor()
        for e in db_config:
            cursor.execute("create table if not exists " + e + " (" + ", ".join("{} text nocollate nocase".format(t) for t in db_config[e]['columns']) + ", primary key (" + db_config[e]['primary_key'] + "))")
            with open(os.path.join(data_dir, e + ".lst")) as f:
                lines = f.readlines()

            for line in lines:
                words = line.split("|")
                cursor.execute("insert into " + e + " (" + ", ".join(db_config[e]['columns']) + ") values (" + ", ".join("?" for word in words) + ") on conflict do nothing", tuple(word.strip() for word in words))
                conn.commit()

            f.close()

        conn.close()
    except Exception as err:
        raise RuntimeError(err)

    print("... done.")


#def add_words(words, table, **kwargs):
def add_words():
    try:
        if len(sys.argv[1:]) == 0:
            raise getopt.GetoptError("")

        opts, args = getopt.getopt(sys.argv[1:], "t:w:")
    except getopt.GetoptError as err:
        if len(str(err)) > 0:
            print("Error: {}\n".format(err))

        print("usage: {} -t <table> -w <words> ...".format(sys.argv[0][sys.argv[0].rfind("/")+1:]))
        print("\nrequired:")
        print("    -t <table>   name of table where word(s) will be inserted")
        print("    -w <words>   words to insert")
        print("                   can be a string - e.g. -w \"word1 word2 word3\"")
        print("                   can be repeated - e.g. -w word1 -w word2")
        sys.exit(1)

    pkg_dirs = site.getsitepackages()
    if len(pkg_dirs) == 0:
        raise FileNotFoundError("unable to locate site-packages directory")

    words = []
    for opt, arg in opts:
        if opt == "-t":
            table = arg
        elif opt == "-w":
            l = arg.split()
            words.extend(l)

    if 'table' not in locals():
        raise UnboundLocalError("no table was specified")

    if table not in db_config:
        raise NameError("table '" + table + "' does not exist")

    if len(words) == 0:
        raise RuntimeError("no words were specified")

    try:
        data_dir = os.path.join(pkg_dirs[0], "spellchecker/data")
        conn = sqlite3.connect(os.path.join(data_dir, "valids.db"))
        cursor = conn.cursor()
        for x in range(0, len(words)):
            if db_config[table]['icase']:
                words[x] = words[x].lower()

            cursor.execute("insert into " + table + " values (?)", (words[x], ))

        conn.commit()
    except sqlite3.IntegrityError:
        pass
    except Exception as e:
        raise RuntimeError(e)

    conn.close()


def add_acronym():
    try:
        if len(sys.argv[1:]) == 0:
            raise getopt.GetoptError("")

        opts, args = getopt.getopt(sys.argv[1:], "a:d:")
    except getopt.GetoptError as err:
        if len(str(err)) > 0:
            print("Error: {}\n".format(err))

        print("usage: {} -a <acronym> -d <description>".format(sys.argv[0][sys.argv[0].rfind("/")+1:]))
        print("\nrequired:")
        print("    -a <acronym>     the acronym to add")
        print("    -f <full_name>   the full name of the acronym")
        sys.exit(1)

    pkg_dirs = site.getsitepackages()
    if len(pkg_dirs) == 0:
        raise FileNotFoundError("unable to locate site-packages directory")

    for opt, arg in opts:
        if opt == "-a":
            acronym = arg
        elif opt == "-f":
            full_name = arg

    if 'acronym' not in locals():
        raise UnboundLocalError("no acronym was specified")

    if 'full_name' not in locals():
        raise UnboundLocalError("full name for the acronym not specified")

    try:
        data_dir = os.path.join(pkg_dirs[0], "spellchecker/data")
        conn = sqlite3.connect(os.path.join(data_dir, "valids.db"))
        cursor = conn.cursor()
        cursor.execute("insert into acronyms values (?, ?)", (acronym.upper(), full_name))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    except Exception as e:
        raise RuntimeError(e)

    conn.close()


def dump_db():
    pass
