import { DocumentRegistry } from '@jupyterlab/docregistry';

import { TranslationBundle } from '@jupyterlab/translation';

import { markdownIcon, kernelIcon } from '@jupyterlab/ui-components';

import { IFileTypeData } from './tokens';

export function registerFileTypes(
  availableKernelLanguages: Map<string, IFileTypeData[]>,
  docRegistry: DocumentRegistry,
  trans: TranslationBundle
) {
  // Add kernel file types to registry
  availableKernelLanguages.forEach(
    (kernelFileTypes: IFileTypeData[], kernelLanguage: string) => {
      // Do not add python as it will be already there by default
      if (kernelLanguage !== 'python') {
        kernelFileTypes.map((kernelFileType) => {
          docRegistry.addFileType({
            name: kernelLanguage,
            contentType: 'file',
            displayName: trans.__(
              kernelFileType.paletteLabel.split('New')[1].trim()
            ),
            extensions: [`.${kernelFileType.fileExt}`],
            icon: kernelFileType.kernelIcon || kernelIcon,
          });
        });
      }
    }
  );

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
