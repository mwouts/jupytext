import { DocumentRegistry } from '@jupyterlab/docregistry';

import { TranslationBundle } from '@jupyterlab/translation';

import { markdownIcon } from '@jupyterlab/ui-components';

export function registerFileTypes(
  docRegistry: DocumentRegistry,
  trans: TranslationBundle
) {
  // Add markdown file types to registry
  docRegistry.addFileType(
    {
      name: 'myst',
      contentType: 'notebook',
      displayName: trans.__('MyST Markdown Notebook'),
      extensions: ['.myst', '.mystnb', '.mnb'],
      icon: markdownIcon,
    },
    ['Notebook']
  );

  docRegistry.addFileType(
    {
      name: 'r-markdown',
      contentType: 'notebook',
      displayName: trans.__('R Markdown Notebook'),
      // Extension file are transformed to lower case...
      extensions: ['.Rmd'],
      icon: markdownIcon,
    },
    ['Notebook']
  );

  docRegistry.addFileType(
    {
      name: 'quarto',
      contentType: 'notebook',
      displayName: trans.__('Quarto Notebook'),
      extensions: ['.qmd'],
      icon: markdownIcon,
    },
    ['Notebook']
  );
}
