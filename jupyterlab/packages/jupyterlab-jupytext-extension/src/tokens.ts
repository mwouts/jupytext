import { ServerConnection } from '@jupyterlab/services';

import { LabIcon } from '@jupyterlab/ui-components';

import jupytextSvgstr from '../style/icons/logo.svg';

/**
 * Jupytext extension ID
 */
export const JUPYTEXT_EXTENSION_ID = 'jupyterlab-jupytext:plugin';

/**
 * Jupytext widget factory
 */
export const FACTORY = 'Jupytext Notebook';

/**
 * Supported file formats.
 */
export const LANGUAGE_INDEPENDENT_NOTEBOOK_EXTENSIONS = [
  'ipynb',
  'md',
  'Rmd',
  'qmd',
];

/**
 * Supported file types names.
 */
export const FILE_TYPES = [
  'markdown',
  'myst',
  'r-markdown',
  'quarto',
  'julia',
  'python',
  'r',
];

/**
 * The short namespace for commands, etc.
 */
export const NS = 'jupytext';

/**
 * Command IDs of Jupytext
 */
export namespace CommandIDs {
  export const metadata = `${NS}:metadata`;
  export const reference = `${NS}:reference`;
  export const faq = `${NS}:faq`;
  export const newUntitled = `${NS}:new-untitled-text-notebook`;
}

/**
 * Jupytext logo icon
 */
export const JupytextIcon = new LabIcon({
  name: `${NS}:icon:logo`,
  svgstr: jupytextSvgstr,
});

/**
 * Current Jupyter server settings
 */
export const SERVER_SETTINGS = ServerConnection.makeSettings();

/**
 * Supported Jupytext pairings along with metadata.
 */
export const JUPYTEXT_PAIR_COMMANDS_FILETYPE_DATA = new Map<
  string,
  IFileTypeData[]
>([
  [
    'ipynb',
    [
      {
        fileExt: 'ipynb',
        paletteLabel: 'Pair with ipynb',
        caption: 'Pair Notebook with ipynb document',
        iconName: 'ui-components:notebook',
        separator: true,
      },
    ],
  ],
  [
    'auto:light',
    [
      {
        fileExt: 'auto:light',
        paletteLabel: 'Pair with light script',
        caption: 'Pair Notebook with Light Format',
        iconName: 'ui-components:text-editor',
      },
    ],
  ],
  [
    'auto:percent',
    [
      {
        fileExt: 'auto:percent',
        paletteLabel: 'Pair with percent script',
        caption: 'Pair Notebook with Percent Format',
        iconName: 'ui-components:text-editor',
      },
    ],
  ],
  [
    'auto:hydrogen',
    [
      {
        fileExt: 'auto:hydrogen',
        paletteLabel: 'Pair with hydrogen script',
        caption: 'Pair Notebook with Hydrogen Format',
        iconName: 'ui-components:text-editor',
      },
    ],
  ],
  [
    'auto:nomarker',
    [
      {
        fileExt: 'auto:nomarker',
        paletteLabel: 'Pair with nomarker script',
        caption: 'Pair Notebook with Nomarker Format',
        iconName: 'ui-components:text-editor',
        separator: true,
      },
    ],
  ],
  [
    'md',
    [
      {
        fileExt: 'md',
        paletteLabel: 'Pair with md',
        caption: 'Pair Notebook with Markdown',
        iconName: 'ui-components:markdown',
      },
    ],
  ],
  [
    'md:myst',
    [
      {
        fileExt: 'md:myst',
        paletteLabel: 'Pair with myst md',
        caption: 'Pair Notebook with MyST Markdown',
        iconName: 'ui-components:markdown',
        separator: true,
      },
    ],
  ],
  [
    'Rmd',
    [
      {
        fileExt: 'Rmd',
        paletteLabel: 'Pair with Rmd',
        caption: 'Pair Notebook with R Markdown',
        iconName: 'ui-components:markdown',
      },
    ],
  ],
  [
    'qmd',
    [
      {
        fileExt: 'qmd',
        paletteLabel: 'Pair with qmd',
        caption: 'Pair Notebook with Quarto (qmd)',
        iconName: 'ui-components:markdown',
        separator: true,
      },
    ],
  ],
  [
    'custom',
    [
      {
        fileExt: 'custom',
        paletteLabel: 'Custom pair',
        caption: 'Custom Pairing',
        iconName: 'ui-components:text-editor',
      },
    ],
  ],
  [
    'none',
    [
      {
        fileExt: 'none',
        paletteLabel: 'Unpair',
        caption: 'Unpair Current Notebook',
      },
    ],
  ],
]);

/**
 * Supported kernels file types metadata
 */
export const AUTO_LANGUAGE_FILETYPE_DATA = new Map<string, IFileTypeData[]>([
  [
    'python',
    [
      {
        fileExt: 'py',
        paletteLabel: 'New Python Text Notebook',
        caption: 'Create a new Python Text Notebook',
        iconName: 'ui-components:python',
        launcherLabel: 'Python',
        kernelName: 'python3',
      },
    ],
  ],
  [
    'julia',
    [
      {
        fileExt: 'jl',
        paletteLabel: 'New Julia Text Notebook',
        caption: 'Create a new Julia Text Notebook',
        iconName: 'ui-components:julia',
        launcherLabel: 'Julia',
        kernelName: 'julia',
      },
    ],
  ],
  [
    'R',
    [
      {
        fileExt: 'R',
        paletteLabel: 'New R Text Notebook',
        caption: 'Create a new R Text Notebook',
        iconName: 'ui-components:r-kernel',
        launcherLabel: 'R',
        kernelName: 'ir',
      },
    ],
  ],
]);

/**
 * Supported Jupytext create new text notebooks file types
 */
export const JUPYTEXT_CREATE_TEXT_NOTEBOOK_FILETYPE_DATA = new Map<
  string,
  IFileTypeData[]
>([
  [
    'auto:light',
    [
      {
        fileExt: 'auto:light',
        paletteLabel: 'Light Format',
        caption: 'Light Format',
        launcherLabel: 'Light Format',
      },
    ],
  ],
  [
    'auto:percent',
    [
      {
        fileExt: 'auto:percent',
        paletteLabel: 'Percent Format',
        caption: 'Percent Format',
        launcherLabel: 'Percent Format',
      },
    ],
  ],
  [
    'auto:hydrogen',
    [
      {
        fileExt: 'auto:hydrogen',
        paletteLabel: 'Hydrogen Format',
        caption: 'Hydrogen Format',
        launcherLabel: 'Hydrogen Format',
      },
    ],
  ],
  [
    'auto:nomarker',
    [
      {
        fileExt: 'auto:nomarker',
        paletteLabel: 'Nomarker Format',
        caption: 'Nomarker Format',
        launcherLabel: 'Nomarker Format',
      },
    ],
  ],
  [
    'md',
    [
      {
        fileExt: 'md',
        paletteLabel: 'New Markdown Text Notebook',
        caption: 'Create a new Markdown Text Notebook',
        iconName: 'ui-components:markdown',
        launcherLabel: 'Markdown',
      },
    ],
  ],
  [
    'md:myst',
    [
      {
        fileExt: 'md:myst',
        paletteLabel: 'New MyST Markdown Text Notebook',
        caption: 'Create a new MyST Markdown Text Notebook',
        iconName: 'ui-components:markdown',
        launcherLabel: 'MyST Markdown',
      },
    ],
  ],
  [
    'Rmd',
    [
      {
        fileExt: 'Rmd',
        paletteLabel: 'New R Markdown Text Notebook',
        caption: 'Create a new R Markdown Text Notebook',
        iconName: 'ui-components:markdown',
        launcherLabel: 'R Markdown',
      },
    ],
  ],
  [
    'qmd',
    [
      {
        fileExt: 'qmd',
        paletteLabel: 'New Quarto Markdown Text Notebook',
        caption: 'Create a new Quarto Markdown Text Notebook',
        iconName: 'ui-components:markdown',
        launcherLabel: 'Quarto Markdown',
      },
    ],
  ],
]);

/**
 * Supported Jupytext format extensions bar custom and none
 */
export const JUPYTEXT_FORMATS = Array.from(
  JUPYTEXT_PAIR_COMMANDS_FILETYPE_DATA.keys()
)
  .map((format) => {
    return format;
  })
  .filter((format) => {
    return !['custom', 'none'].includes(format);
  });

/**
 * List of formats that would be added to launcher icons
 */
export const TEXT_NOTEBOOKS_LAUNCHER_ICONS = JUPYTEXT_FORMATS.filter(
  (format) => {
    return ![
      'ipynb',
      'auto:hydrogen',
      'auto:nomarker',
      'qmd',
      'custom',
      'none',
    ].includes(format);
  }
);

/**
 * An interface for file type metadata
 */
export interface IFileTypeData {
  fileExt: string;
  paletteLabel: string;
  caption: string;
  iconName?: string;
  kernelIcon?: LabIcon;
  launcherLabel?: string;
  kernelName?: string;
  separator?: boolean;
}

/**
 * An interface for Jupytext representation
 */
export interface IJupytextRepresentation {
  formatName: string;
  extension: string;
}

/**
 * An interface for Jupytext metadata
 */
export interface IJupytextSection {
  formats?: string;
  notebook_metadata_filter?: string;
  cell_metadata_filer?: string;
  text_representation?: IJupytextRepresentation;
}
