import getopt
import inspect
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
    'unit_abbrevs': {
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


def build_db(args):
    if args[0] == "-h":
        sys.exit(1)

    print("Building database from lists of valids ...")
    pkg_dirs = site.getsitepackages()
    if len(pkg_dirs) == 0:
        raise FileNotFoundError("unable to locate site-packages directory")

    dict_dir = os.path.join(pkg_dirs[0], "spellchecker/dictionary")
    db_name = os.path.join(dict_dir, "valids.db")
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        for e in db_config:
            cursor.execute("create table if not exists " + e + " (" + ", ".join("{} text nocollate nocase".format(t) for t in db_config[e]['columns']) + ", primary key (" + db_config[e]['primary_key'] + "))")
            with open(os.path.join(dict_dir, e + ".lst")) as f:
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
def add_words(args):
    util_name = args[-1]
    del args[-1]
    try:
        if len(args) == 0:
            raise getopt.GetoptError("missing input")

        if args[0] == "-h":
            raise getopt.GetoptError("")

        opts, args = getopt.getopt(args, "t:w:")
    except getopt.GetoptError as err:
        func_name = inspect.currentframe().f_code.co_name
        if len(str(err)) > 0:
            print("Error: {}\n".format(err))

        print("usage: {} {} -t <table> -w <words> ...".format(util_name, func_name))
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
        dict_dir = os.path.join(pkg_dirs[0], "spellchecker/dictionary")
        conn = sqlite3.connect(os.path.join(dict_dir, "valids.db"))
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


def add_acronym(args):
    util_name = args[-1]
    del args[-1]
    try:
        if len(args) == 0:
            raise getopt.GetoptError("missing input")

        if args[0] == "-h":
            raise getopt.GetoptError("")

        opts, args = getopt.getopt(args, "a:d:")
    except getopt.GetoptError as err:
        func_name = inspect.currentframe().f_code.co_name
        if len(str(err)) > 0:
            print("Error: {}\n".format(err))

        print("usage: {} {} -a <acronym> -d <description>".format(util_name, func_name))
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
        dict_dir = os.path.join(pkg_dirs[0], "spellchecker/dictionary")
        conn = sqlite3.connect(os.path.join(dict_dir, "valids.db"))
        cursor = conn.cursor()
        cursor.execute("insert into acronyms values (?, ?)", (acronym.upper(), full_name))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    except Exception as e:
        raise RuntimeError(e)

    conn.close()


def dump_db(args):
    if args[0] == "-h":
        sys.exit(1)

    pass


def spellchecker_manage():
    util_name = inspect.currentframe().f_code.co_name
    args = sys.argv[1:] + [util_name]
    if len(args) < 2:
        print("usage: {} <command> [args...]".format(util_name))
        print("\ncommand:")
        print("    add_words     add words to the spellchecker database")
        print("    add_acronym   add an acronym to the spellchecker database")
        print("    build_db      build the spellchecker database")
        print("    dump_db       dump the spellchecker database")
        print("\nuse `{} <command> -h` to get help for the specific\n     command".format(util_name))
        sys.exit(1)

    if args[0] == "build_db":
        build_db(args[1:])
    elif args[0] == "add_words":
        add_words(args[1:])
    elif args[0] == "add_acronym":
        add_acronym(args[1:])
    elif args[0] == "dump_db":
        dump_db(args[1:])
    else:
        raise ValueError("invalid command")


if __name__ == "__main__":
    spellchecker_manage()
