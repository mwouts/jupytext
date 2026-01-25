/**
 * Pyodide-based Jupytext converter for JupyterLite
 * This module provides client-side notebook conversion using Jupytext running in Pyodide
 */

import { PromiseDelegate } from '@lumino/coreutils';

/**
 * Interface for the Pyodide Jupytext converter
 */
export interface IJupytextConverter {
  /**
   * Whether the converter is ready to use
   */
  isReady: boolean;

  /**
   * Promise that resolves when the converter is ready
   */
  ready: Promise<void>;

  /**
   * Convert notebook content to a text format
   */
  notebookToText(
    notebook: any,
    format: string
  ): Promise<string>;

  /**
   * Convert text content to notebook format
   */
  textToNotebook(
    text: string,
    format: string
  ): Promise<any>;
}

/**
 * Jupytext converter using Pyodide
 */
export class PyodideJupytextConverter implements IJupytextConverter {
  private _isReady = false;
  private _readyDelegate = new PromiseDelegate<void>();
  private _pyodide: any = null;

  constructor() {
    this._initialize();
  }

  get isReady(): boolean {
    return this._isReady;
  }

  get ready(): Promise<void> {
    return this._readyDelegate.promise;
  }

  /**
   * Initialize Pyodide and install Jupytext
   */
  private async _initialize(): Promise<void> {
    try {
      // Check if we're running in JupyterLite (Pyodide available)
      if (typeof (window as any).loadPyodide === 'undefined') {
        console.warn('Pyodide not available - Jupytext conversion disabled');
        this._readyDelegate.reject(
          new Error('Pyodide not available in this environment')
        );
        return;
      }

      console.log('Loading Pyodide for Jupytext...');
      this._pyodide = await (window as any).loadPyodide({
        indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/'
      });

      // Install required packages
      console.log('Installing Jupytext in Pyodide...');
      await this._pyodide.loadPackage('micropip');
      const micropip = this._pyodide.pyimport('micropip');

      // Install jupytext and dependencies
      await micropip.install([
        'nbformat',
        'markdown-it-py',
        'mdit-py-plugins',
        'pyyaml',
        'packaging'
      ]);

      // Load jupytext from the local installation
      // In a real deployment, this would be bundled or loaded from a CDN
      await micropip.install('jupytext');

      // Test the installation
      await this._pyodide.runPythonAsync(`
        import jupytext
        print(f"Jupytext {jupytext.__version__} loaded successfully")
      `);

      this._isReady = true;
      this._readyDelegate.resolve();
      console.log('Jupytext is ready in Pyodide');
    } catch (error) {
      console.error('Failed to initialize Jupytext:', error);
      this._readyDelegate.reject(error);
    }
  }

  /**
   * Convert notebook to text format
   */
  async notebookToText(notebook: any, format: string): Promise<string> {
    await this.ready;

    try {
      // Prepare the notebook data
      const notebookJson = JSON.stringify(notebook);

      // Run the conversion in Pyodide
      const result = await this._pyodide.runPythonAsync(`
import json
import jupytext

# Parse the notebook
notebook = json.loads(${JSON.stringify(notebookJson)})

# Convert to text format
text = jupytext.writes(notebook, fmt='${format}')
text
      `);

      return result;
    } catch (error) {
      console.error('Error converting notebook to text:', error);
      throw error;
    }
  }

  /**
   * Convert text to notebook format
   */
  async textToNotebook(text: string, format: string): Promise<any> {
    await this.ready;

    try {
      // Run the conversion in Pyodide
      const result = await this._pyodide.runPythonAsync(`
import json
import jupytext

# Convert text to notebook
notebook = jupytext.reads(${JSON.stringify(text)}, fmt='${format}')

# Return as JSON string
json.dumps(notebook)
      `);

      return JSON.parse(result);
    } catch (error) {
      console.error('Error converting text to notebook:', error);
      throw error;
    }
  }
}

/**
 * Singleton instance of the converter
 */
let _converterInstance: IJupytextConverter | null = null;

/**
 * Get the Jupytext converter instance
 */
export function getJupytextConverter(): IJupytextConverter {
  if (!_converterInstance) {
    _converterInstance = new PyodideJupytextConverter();
  }
  return _converterInstance;
}
