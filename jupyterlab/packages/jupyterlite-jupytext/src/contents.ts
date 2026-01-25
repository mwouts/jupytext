/**
 * Contents manager wrapper for JupyterLite that handles Jupytext conversions
 */

import { Contents, Drive } from '@jupyterlab/services';
import { getJupytextConverter } from './converter';
import { detectFormat, isTextNotebook } from './utils';

/**
 * Wrapper around JupyterLite's contents manager that adds Jupytext support
 */
export class JupytextContentsManager implements Contents.IDrive {
  constructor(private _baseDrive: Contents.IDrive) {}

  get name(): string {
    return this._baseDrive.name;
  }

  get serverSettings(): any {
    return this._baseDrive.serverSettings;
  }

  get fileChanged(): any {
    return this._baseDrive.fileChanged;
  }

  get isDisposed(): boolean {
    return this._baseDrive.isDisposed;
  }

  dispose(): void {
    this._baseDrive.dispose();
  }

  /**
   * Get a file or directory model
   */
  async get(
    path: string,
    options?: Contents.IFetchOptions
  ): Promise<Contents.IModel> {
    const model = await this._baseDrive.get(path, options);

    // If it's a text notebook file, convert it to notebook format
    if (
      options?.type === 'notebook' &&
      model.type === 'file' &&
      isTextNotebook(path)
    ) {
      try {
        const format = detectFormat(path);
        const converter = getJupytextConverter();

        if (converter.isReady && model.content) {
          const notebook = await converter.textToNotebook(
            model.content,
            format
          );

          return {
            ...model,
            type: 'notebook',
            format: 'json',
            content: notebook,
            mimetype: 'application/x-ipynb+json'
          };
        }
      } catch (error) {
        console.error('Failed to convert text to notebook:', error);
        // Fall through to return the original model
      }
    }

    return model;
  }

  /**
   * Get a file download URL
   */
  getDownloadUrl(path: string): Promise<string> {
    return this._baseDrive.getDownloadUrl(path);
  }

  /**
   * Create a new untitled file or directory
   */
  newUntitled(options?: Contents.ICreateOptions): Promise<Contents.IModel> {
    return this._baseDrive.newUntitled(options);
  }

  /**
   * Delete a file
   */
  delete(path: string): Promise<void> {
    return this._baseDrive.delete(path);
  }

  /**
   * Rename a file or directory
   */
  rename(oldPath: string, newPath: string): Promise<Contents.IModel> {
    return this._baseDrive.rename(oldPath, newPath);
  }

  /**
   * Save a file
   */
  async save(
    path: string,
    options?: Partial<Contents.IModel>
  ): Promise<Contents.IModel> {
    // If we're saving a notebook to a text format, convert it first
    if (
      options?.type === 'notebook' &&
      options?.content &&
      isTextNotebook(path)
    ) {
      try {
        const format = detectFormat(path);
        const converter = getJupytextConverter();

        if (converter.isReady) {
          const text = await converter.notebookToText(
            options.content,
            format
          );

          // Save as text file instead
          return await this._baseDrive.save(path, {
            ...options,
            type: 'file',
            format: 'text',
            content: text,
            mimetype: 'text/plain'
          });
        }
      } catch (error) {
        console.error('Failed to convert notebook to text:', error);
        // Fall through to save as-is
      }
    }

    return this._baseDrive.save(path, options);
  }

  /**
   * Copy a file into a given directory
   */
  copy(path: string, toDir: string): Promise<Contents.IModel> {
    return this._baseDrive.copy(path, toDir);
  }

  /**
   * Create a checkpoint for a file
   */
  createCheckpoint(path: string): Promise<Contents.ICheckpointModel> {
    return this._baseDrive.createCheckpoint(path);
  }

  /**
   * List available checkpoints for a file
   */
  listCheckpoints(path: string): Promise<Contents.ICheckpointModel[]> {
    return this._baseDrive.listCheckpoints(path);
  }

  /**
   * Restore a file to a known checkpoint state
   */
  restoreCheckpoint(path: string, checkpointID: string): Promise<void> {
    return this._baseDrive.restoreCheckpoint(path, checkpointID);
  }

  /**
   * Delete a checkpoint for a file
   */
  deleteCheckpoint(path: string, checkpointID: string): Promise<void> {
    return this._baseDrive.deleteCheckpoint(path, checkpointID);
  }
}

/**
 * Create a Jupytext-aware contents manager
 */
export function createJupytextContentsManager(
  baseDrive: Contents.IDrive
): Contents.IDrive {
  return new JupytextContentsManager(baseDrive);
}
