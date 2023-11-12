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
 * Supported file types.
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
 * Supported Jupytext formats with metadata.
 */
export const ALL_JUPYTEXT_FORMATS = [
  {
    format: 'ipynb',
    label: 'Pair Notebook with ipynb document',
  },
  {
    format: 'auto:light',
    label: 'Pair Notebook with Light Script',
  },
  {
    format: 'auto:percent',
    label: 'Pair Notebook with Percent Script',
  },
  {
    format: 'auto:hydrogen',
    label: 'Pair Notebook with Hydrogen Script',
  },
  {
    format: 'auto:nomarker',
    label: 'Pair Notebook with Nomarker Script',
  },
  {
    format: 'md',
    label: 'Pair Notebook with Markdown',
  },
  {
    format: 'md:myst',
    label: 'Pair Notebook with MyST Markdown',
  },
  {
    format: 'Rmd',
    label: 'Pair Notebook with R Markdown',
  },
  {
    format: 'qmd',
    label: 'Pair Notebook with Quarto (qmd)',
  },
  {
    format: 'custom',
    label: 'Custom pairing',
  },
  {
    format: 'none',
    label: 'Unpair Notebook',
  },
];

/**
 * Supported Jupytext format extensions bar custom and none
 */
export const ALL_JUPYTEXT_FORMAT_EXTENSIONS = ALL_JUPYTEXT_FORMATS.map(
  (formatObj) => {
    return formatObj.format;
  }
).filter((format) => {
  return !['custom', 'none'].includes(format);
});

/**
 * List of formats that would be added to launcher icons
 */
export const TEXT_NOTEBOOKS_LAUNCHER_ICONS =
  ALL_JUPYTEXT_FORMAT_EXTENSIONS.filter((format) => {
    return ![
      'ipynb',
      'auto:hydrogen',
      'auto:nomarker',
      'qmd',
      'custom',
      'none',
    ].includes(format);
  });

/**
 * An interface for Jupytext format
 */
export interface IJupytextFormat {
  format: string;
  label: string;
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
