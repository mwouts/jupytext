/**
 * JupyterLite Jupytext Extension
 *
 * This extension enables Jupytext functionality in JupyterLite by:
 * 1. Running Jupytext conversion code in Pyodide (Python in WebAssembly)
 * 2. Wrapping the contents manager to intercept file operations
 * 3. Converting between notebook and text formats on-the-fly
 */

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { IDocumentManager } from '@jupyterlab/docmanager';

import { ITranslator, nullTranslator } from '@jupyterlab/translation';

import { INotification } from '@jupyterlab/apputils';

import { getJupytextConverter } from './converter';
import { createJupytextContentsManager } from './contents';

/**
 * Initialization data for the jupyterlite-jupytext extension
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlite-jupytext:plugin',
  autoStart: true,
  requires: [IDocumentManager],
  optional: [ITranslator],
  activate: async (
    app: JupyterFrontEnd,
    docManager: IDocumentManager,
    translator: ITranslator | null
  ) => {
    const trans = (translator ?? nullTranslator).load('jupyterlite-jupytext');

    console.log('JupyterLite Jupytext extension is activating...');

    // Initialize the converter (loads Pyodide and Jupytext)
    const converter = getJupytextConverter();

    // Show a notification that we're loading
    let loadingNotification: ReturnType<typeof INotification.info> | undefined;

    if (INotification) {
      loadingNotification = INotification.info(
        trans.__('Loading Jupytext for JupyterLite...'),
        { autoClose: false }
      );
    }

    try {
      // Wait for the converter to be ready
      await converter.ready;

      console.log('Jupytext converter is ready');

      // Wrap the contents manager with Jupytext support
      const services = app.serviceManager;
      const contents = services.contents;

      // Get the default drive
      const defaultDrive = contents.getDefaultDrive();

      if (defaultDrive) {
        // Wrap it with Jupytext functionality
        const jupytextDrive = createJupytextContentsManager(defaultDrive);

        // Replace the default drive
        // Note: This is a workaround since we can't directly replace the drive
        // In a production implementation, you'd want to register this as a proper drive
        Object.defineProperty(contents, 'defaultDrive', {
          get: () => jupytextDrive,
          configurable: true
        });

        console.log('Jupytext contents manager installed');
      }

      // Dismiss loading notification
      if (loadingNotification) {
        loadingNotification.dismiss();
      }

      // Show success notification
      if (INotification) {
        INotification.success(
          trans.__('Jupytext is ready! You can now open .py, .md, .R, and other text files as notebooks.'),
          { autoClose: 5000 }
        );
      }

      console.log('JupyterLite Jupytext extension activated successfully');
    } catch (error) {
      console.error('Failed to activate Jupytext extension:', error);

      // Dismiss loading notification
      if (loadingNotification) {
        loadingNotification.dismiss();
      }

      // Show error notification
      if (INotification) {
        INotification.error(
          trans.__('Failed to load Jupytext: {error}', { error: String(error) }),
          { autoClose: 10000 }
        );
      }
    }
  }
};

export default extension;
