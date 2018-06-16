import os
import nbrmd
import nbformat
import argparse

parser = argparse.ArgumentParser(description='''Jupyter notebook to R markdown converter''')
parser.add_argument('notebooks',
                    help='Name of one or multiple .ipynb or .Rmd notebook(s) to be converted to the alternate form',
                    nargs='+')

def main():
    """
    Export R markdown notebooks, or Jupyter notebooks, to the opposite format
    :return:
    """
    args = parser.parse_args()
    for nb_file in args.notebooks:
        file, ext = os.path.splitext(nb_file)
        if ext=='.ipynb':
            nb_dest = file + '.Rmd'
            print("Jupyter notebook {} being converted to R markdown {}".format(nb_file, nb_dest))
            with open(nb_file) as fp:
                nb = nbformat.read(fp, as_version=4)
            with open(nb_dest, 'w') as fp:
                nbrmd.write(nb, fp)
        elif ext=='.Rmd':
            nb_dest = file + '.ipynb'
            print("R markdown {} being converted to Jupyter notebook {}".format(nb_file, nb_dest))
            with open(nb_file) as fp:
                nb = nbrmd.read(fp)
            with open(nb_dest, 'w') as fp:
                nbformat.write(nb, fp)
        else:
            raise nbrmd.nbrmd.RmdReaderError(
                "File '{}' is neither a Jupyter (.ipynb) nor a R markdown (.Rmd) notebook".format(nb_file))
