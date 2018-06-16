import os
from nbrmd import readf, writef
import argparse

parser = argparse.ArgumentParser(description='''Jupyter notebook to R markdown converter''')
parser.add_argument('notebooks',
                    help='Name of one or multiple .ipynb or .Rmd notebook(s) to be converted to the alternate form',
                    nargs='+')


def convert(nb_files):
    """
    Export R markdown notebooks, or Jupyter notebooks, to the opposite format
    :param nb_files: list of notebooks
    :return:
    """
    for nb_file in nb_files:
        file, ext = os.path.splitext(nb_file)
        if ext == '.ipynb':
            nb_dest = file + '.Rmd'
            print("Jupyter notebook {} being converted to R markdown {}".format(nb_file, nb_dest))
        elif ext == '.Rmd':
            nb_dest = file + '.ipynb'
            print("R markdown {} being converted to Jupyter notebook {}".format(nb_file, nb_dest))
        else:
            raise TypeError(
                "File '{}' is neither a Jupyter (.ipynb) nor a R markdown (.Rmd) notebook".format(nb_file))
        nb = readf(nb_file)
        writef(nb, nb_dest)


def main():
    args = parser.parse_args()
    convert(args.notebooks)
