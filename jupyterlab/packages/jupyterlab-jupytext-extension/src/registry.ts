import { DocumentRegistry } from '@jupyterlab/docregistry';

import { TranslationBundle } from '@jupyterlab/translation';

import { markdownIcon, LabIcon, fileIcon } from '@jupyterlab/ui-components';

import { IFileTypeData } from './tokens';

export function registerFileTypes(
  availableKernelLanguages: Map<string, IFileTypeData[]>,
  jupytextFormatsWithFileTypeData: IFileTypeData[],
  docRegistry: DocumentRegistry,
  trans: TranslationBundle,
) {
  const mystExtensions = ['myst', 'mystnb', 'mnb'];
  const rmdExtensions = ['Rmd'];
  const quartoExtensions = ['qmd'];

  const extensionsWithFactory = [
    ...mystExtensions,
    ...rmdExtensions,
    ...quartoExtensions,
  ];

  // Add a catch-all file type to overrride icon which by default is derive from model type.
  // Because jupytext changes the type of all files it can handle to Notebook, we need to
  // override it. We exclude file types which have dedicated icons (handled later).
  const excludedExtensions = [
    'ipynb',
    ...jupytextFormatsWithFileTypeData.map((f) => f.fileExt),
    ...extensionsWithFactory,
  ].join('|');
  docRegistry.addFileType({
    name: 'jupytext-notebook-file',
    contentType: 'notebook',
    pattern: `^(?!.*\\.(${excludedExtensions})$).*$`,
    icon: fileIcon,
  });

  // Handle file types with dedicated icons
  for (const format of jupytextFormatsWithFileTypeData) {
    if (!extensionsWithFactory.includes(format.fileExt)) {
      docRegistry.addFileType({
        name: `${format.fileExt}-jupytext-notebook`,
        contentType: 'notebook',
        // `pattern` field gives it precedence over other file type information when resolving the icon
        pattern: `\\.${format.fileExt}$`,
        extensions: [`.${format.fileExt}`],
        icon: format.iconName
          ? LabIcon.resolve({ icon: format.iconName })
          : format.kernelIcon,
      });
    }
  }

  // Add kernel file types to registry
  availableKernelLanguages.forEach(
    (kernelFileTypes: IFileTypeData[], kernelLanguage: string) => {
      kernelFileTypes.map((kernelFileType) => {
        docRegistry.addFileType({
          name: kernelLanguage,
          contentType: 'notebook',
          pattern: `\\.${kernelFileType.fileExt}$`,
          displayName: trans.__(
            kernelFileType.paletteLabel.split('New')[1].trim(),
          ),
          extensions: [`.${kernelFileType.fileExt}`],
          icon: kernelFileType.iconName
            ? LabIcon.resolve({ icon: kernelFileType.iconName })
            : kernelFileType.kernelIcon,
        });
      });
    },
  );

  const markdownNotebookIcon = markdownIcon.bindprops({
    boxSizing: 'border-box',
    border: '2px solid var(--jp-notebook-icon-color)',
    borderRadius: '2px',
  });

  // Add markdown file types to registry - these will be open with Notebook by default
  docRegistry.addFileType(
    {
      name: 'myst',
      contentType: 'notebook',
      displayName: trans.__('MyST Markdown Notebook'),
      extensions: mystExtensions.map((ext) => '.' + ext),
      icon: markdownNotebookIcon,
    },
    ['Notebook'],
  );

  docRegistry.addFileType(
    {
      name: 'r-markdown',
      contentType: 'notebook',
      displayName: trans.__('R Markdown Notebook'),
      // Extension file are transformed to lower case...
      extensions: rmdExtensions.map((ext) => '.' + ext),
      icon: markdownNotebookIcon,
    },
    ['Notebook'],
  );

  docRegistry.addFileType(
    {
      name: 'quarto',
      contentType: 'notebook',
      displayName: trans.__('Quarto Notebook'),
      extensions: quartoExtensions.map((ext) => '.' + ext),
      pattern: '\\.qmd$',
      icon: markdownNotebookIcon,
    },
    ['Notebook'],
  );
}
