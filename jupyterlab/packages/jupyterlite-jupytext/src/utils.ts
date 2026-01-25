/**
 * Utility functions for Jupytext
 */

/**
 * File extensions that should be treated as text notebooks
 */
const TEXT_NOTEBOOK_EXTENSIONS = [
  '.py',
  '.r',
  '.jl',
  '.md',
  '.Rmd',
  '.qmd',
  '.js',
  '.ts',
  '.scala',
  '.clj',
  '.sh',
  '.bash',
  '.ps1',
  '.java',
  '.c',
  '.cpp',
  '.q'
];

/**
 * Check if a file path represents a text notebook
 */
export function isTextNotebook(path: string): boolean {
  return TEXT_NOTEBOOK_EXTENSIONS.some(ext => path.endsWith(ext));
}

/**
 * Detect the Jupytext format from a file path
 */
export function detectFormat(path: string): string {
  const extension = path.substring(path.lastIndexOf('.'));

  // Map common extensions to Jupytext formats
  const formatMap: { [key: string]: string } = {
    '.py': 'py:percent',
    '.r': 'r:percent',
    '.R': 'r:percent',
    '.jl': 'jl:percent',
    '.md': 'md',
    '.Rmd': 'Rmd',
    '.qmd': 'qmd',
    '.js': 'js:percent',
    '.ts': 'ts:percent',
    '.scala': 'scala:percent',
    '.clj': 'clj:percent',
    '.sh': 'sh:percent',
    '.bash': 'bash:percent',
    '.ps1': 'ps1:percent',
    '.java': 'java:percent',
    '.c': 'c:percent',
    '.cpp': 'cpp:percent',
    '.q': 'q:percent'
  };

  return formatMap[extension] || 'auto';
}

/**
 * Get the display name for a format
 */
export function getFormatDisplayName(format: string): string {
  const displayNames: { [key: string]: string } = {
    'py:percent': 'Python (percent)',
    'py:light': 'Python (light)',
    'r:percent': 'R (percent)',
    'jl:percent': 'Julia (percent)',
    'md': 'Markdown',
    'Rmd': 'R Markdown',
    'qmd': 'Quarto',
    'myst': 'MyST Markdown'
  };

  return displayNames[format] || format;
}

/**
 * Get available formats for a language
 */
export function getAvailableFormats(language?: string): string[] {
  const commonFormats = ['md', 'Rmd', 'qmd', 'myst'];

  switch (language?.toLowerCase()) {
    case 'python':
      return ['py:percent', 'py:light', 'py:nomarker', ...commonFormats];
    case 'r':
      return ['r:percent', 'r:light', ...commonFormats];
    case 'julia':
      return ['jl:percent', 'jl:light', ...commonFormats];
    case 'javascript':
      return ['js:percent', ...commonFormats];
    case 'typescript':
      return ['ts:percent', ...commonFormats];
    default:
      return commonFormats;
  }
}
