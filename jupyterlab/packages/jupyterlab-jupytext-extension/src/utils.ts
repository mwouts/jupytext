import { ServiceManager } from '@jupyterlab/services';

import { IDocumentWidget } from '@jupyterlab/docregistry';

import { CommandRegistry } from '@lumino/commands';

import {
  AUTO_LANGUAGE_FILETYPE_DATA,
  JUPYTEXT_CREATE_TEXT_NOTEBOOK_FILETYPE_DATA,
  FACTORY,
  CommandIDs,
  IFileTypeData,
} from './tokens';

// NOTE: Instead of defining AUTO_LANGUAGE_FILETYPE_DATA upfront, try to
// get extension and other file metadata from default languages model
// This might be bit tricky as cases are not same in names in kernelspecs
// and languages. The idea we pick up _any_ kernel directly from supported
// default languages.
// const defaultLangugaes = EditorLanguageRegistry.getDefaultLanguages();

/**
 * Get all available kernel file types so that we replace auto format
 * with these file extensions
 */
async function getAvailableKernelFileTypes(
  serviceManager: ServiceManager.IManager
): Promise<Map<string, IFileTypeData[]>> {
  const specsManager = serviceManager.kernelspecs;
  await specsManager.ready;
  const fileTypes = new Map<string, IFileTypeData[]>();
  const specs = specsManager.specs?.kernelspecs ?? {};
  Object.keys(specs).forEach((spec) => {
    const specModel = specs[spec];
    if (specModel) {
      const exts = AUTO_LANGUAGE_FILETYPE_DATA.get(specModel.language);
      if (exts !== undefined) {
        fileTypes.set(specModel.language, exts);
      }
    }
  });
  return fileTypes;
}

/**
 * Get all available 'Create New Text Notebook' commands based on configured
 * formats and available kernels
 */
export async function getAvailableCreateTextNotebookCommands(
  launcherItems: string[],
  serviceManager: ServiceManager.IManager
): Promise<Map<string, IFileTypeData[]>> {
  // Get a map of available kernels in current widget
  const availableKernels = await getAvailableKernelFileTypes(serviceManager);

  // Initialise a map of 'Create New Text Notebook' command filetypes
  const createTextNotebookCommands = new Map<string, IFileTypeData[]>();

  // Iterate through all JUPYTEXT_CREATE_TEXT_NOTEBOOK_FILETYPE_DATA file types.
  JUPYTEXT_CREATE_TEXT_NOTEBOOK_FILETYPE_DATA.forEach(
    (fileTypes: IFileTypeData[], format: string) => {
      fileTypes.map((fileType: IFileTypeData) => {
        // If format is auto, we need to add all currently available kernels
        // For instance if there are Python and R kernels available, format
        // auto:light will be replaced by py:light and R:light
        if (format.startsWith('auto')) {
          const formatType = format.split(':')[1];
          availableKernels.forEach(
            (kernelFileTypes: IFileTypeData[], kernelKey: string) => {
              const updatedKernelKey = `${kernelKey}:${formatType}`;
              createTextNotebookCommands.set(updatedKernelKey, []);
              kernelFileTypes.map((kernelFileType) => {
                // Merge fileType object from kernel and Jupytext format and push
                // it to createTextNotebookCommands
                const updatedKernelFileType = { ...kernelFileType };
                updatedKernelFileType.fileExt = `${updatedKernelFileType.fileExt}:${formatType}`;
                updatedKernelFileType.paletteLabel = `${updatedKernelFileType.paletteLabel} with ${fileType.paletteLabel}`;
                updatedKernelFileType.caption = `${updatedKernelFileType.caption} with ${fileType.caption}`;
                updatedKernelFileType.launcherLabel = `${updatedKernelFileType.launcherLabel} - ${fileType.launcherLabel}`;
                createTextNotebookCommands
                  .get(updatedKernelKey)
                  .push(updatedKernelFileType);
                if (launcherItems.includes(format)) {
                  launcherItems.push(updatedKernelFileType.fileExt);
                }
              });
            }
          );
        } else {
          if (createTextNotebookCommands.get(format) === undefined) {
            createTextNotebookCommands.set(format, []);
          }
          createTextNotebookCommands.get(format).push(fileType);
        }
      });
    }
  );
  return createTextNotebookCommands;
}

/**
 * Create New Text Notebook file
 */
export const createNewTextNotebook = async (
  cwd: string,
  kernelId: string,
  kernelName: string,
  format: string,
  commands: CommandRegistry
) => {
  const model = await commands.execute(CommandIDs.newUntitled, {
    path: cwd,
    type: 'notebook',
    // We should not have auto in format at this point. If somehow we end up having
    // it, ensure we replace by py as Python kernel exists always
    ext: format.replace('auto', 'py'),
  });
  if (model !== undefined) {
    const widget = (await commands.execute('docmanager:open', {
      path: model.path,
      factory: FACTORY,
      kernel: { id: kernelId, name: kernelName },
    })) as unknown as IDocumentWidget;
    widget.isUntitled = true;
    return widget;
  }
};
