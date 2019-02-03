import {
  JupyterLab, JupyterLabPlugin
} from '@jupyterlab/application';

import {
  ICommandPalette
} from '@jupyterlab/apputils';

import '../style/index.css';

const JUPYTEXT_FORMATS = [
  {
    'formats': 'ipynb,auto:light',
    'label': 'Pair Notebook with light Script'
  },
  {
    'formats': 'ipynb,auto:percent',
    'label': 'Pair Notebook with percent Script'
  },
  {
    'formats': 'ipynb,auto:hydrogen',
    'label': 'Pair Notebook with hydrogen Script'
  },
  {
    'formats': 'ipynb,md',
    'label': 'Pair Notebook with Markdown'
  },
  {
    'formats': 'ipynb,Rmd',
    'label': 'Pair Notebook with R Markdown'
  },
  {
    'formats': 'unpair',
    'label': 'Unpair Notebook'
  }
]

/**
 * Initialization data for the jupyterlab-jupytext extension.
 */
const extension: JupyterLabPlugin<void> = {
  id: 'jupyterlab-jupytext',
  autoStart: true,
  requires: [ICommandPalette],
  activate: (app: JupyterLab, palette: ICommandPalette) => {
    console.log('JupyterLab extension jupyterlab-jupytext is activated');

    // Jupytext formats
    JUPYTEXT_FORMATS.forEach((args, rank) => {
      const command: string = 'jupytext:' + args['formats']
      app.commands.addCommand(command, {
        label: args['label'],
        execute: args => {
          // TODO: Replace the below with a code that sets/removes
          // notebook.metadata.jupytext.formats=args['formats']
          // when the focus is on a notebook.
          console.log('Jupytext: executing command=' + command + ' with args=' + String(args))
        }
      });

      console.log('Jupytext: adding command=' + command + ' with rank=' + rank)
      palette.addItem({ command, rank, category: 'Jupytext' });
    })

    // Jupytext README
    palette.addItem({
      args: {
        'text': 'Jupytext Reference',
        'url': 'https://jupytext.readthedocs.io/en/latest/'
      }, command: 'help:open', category: 'Jupytext', rank: JUPYTEXT_FORMATS.length
    });
  }
};

export default extension;
