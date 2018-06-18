import os
from nbformat import writes as ipynb_writes
from nbrmd import readf, writef
from nbrmd import writes as rmd_writes
import argparse


def convert(nb_files, in_place=True):
    """
    Export R markdown notebooks, or Jupyter notebooks, to the opposite format
    :param nb_files: one or more notebooks
    :param in_place: should result of conversion be stored in file with opposite extension?
    :return:
    """
    for nb_file in nb_files:
        file, ext = os.path.splitext(nb_file)
        if ext not in ['.ipynb', '.Rmd']:
            raise TypeError(
                "File '{}' is neither a Jupyter (.ipynb) nor a R markdown (.Rmd) notebook".format(nb_file))

        nb = readf(nb_file)

        if in_place:
            if ext == '.ipynb':
                nb_dest = file + '.Rmd'
                print("Jupyter notebook {} being converted to R markdown {}".format(nb_file, nb_dest))
            else:
                nb_dest = file + '.ipynb'
                print("R markdown {} being converted to Jupyter notebook {}".format(nb_file, nb_dest))
            writef(nb, nb_dest)
        else:
            if ext == '.ipynb':
                print(rmd_writes(nb))
            else:
                print(ipynb_writes(nb))


def cli(args=None):
    parser = argparse.ArgumentParser(description='''Jupyter notebook from/to R markdown''')
    parser.add_argument('notebooks',
                        help='One or more .ipynb or .Rmd notebook(s) to be converted to the alternate form',
                        nargs='+')
    parser.add_argument('-i', '--in-place', action='store_true',
                        help='Store the result of conversion to file with opposite extension')
    return parser.parse_args(args)


def main():
    args = cli()
    convert(args.notebooks, args.in_place)
