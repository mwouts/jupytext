import { IEditorLanguageRegistry } from '@jupyterlab/codemirror';

import {
  ServiceManager,
  ServerConnection,
  KernelSpec,
} from '@jupyterlab/services';

import { LabIcon } from '@jupyterlab/ui-components';

import { URLExt } from '@jupyterlab/coreutils';

import { IDocumentWidget } from '@jupyterlab/docregistry';

import { CommandRegistry } from '@lumino/commands';

import { Buffer } from 'buffer';

import {
  NS,
  SERVER_SETTINGS,
  AUTO_LANGUAGE_FILETYPE_DATA,
  JUPYTEXT_CREATE_TEXT_NOTEBOOK_FILETYPE_DATA,
  FACTORY,
  CommandIDs,
  IFileTypeData,
} from './tokens';

/**
 * Get kernel icon SVG string
 */
async function getKernelIconBase64String(
  kernelIconUrl: string
): Promise<string> {
  const url = URLExt.join(SERVER_SETTINGS.baseUrl, kernelIconUrl);
  const response = await ServerConnection.makeRequest(url, {}, SERVER_SETTINGS);
  const blob = await response.arrayBuffer();
  const contentType = response.headers.get('content-type');
  return `data:${contentType};base64,${Buffer.from(blob).toString('base64')}`;
}

/**
 * Make a SVG string from base64 image
 */
function base64ToSvgStr(width: number, imageBase64: string): string {
  return `<svg xmlns="http://www.w3.org/2000/svg"
  xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="none" viewBox="0 0 ${width} ${width}">
  <g id="layer1">
     <image xlink:href="${imageBase64}"/>
  </g>
</svg>`.replace(/\n/g, ' ');
}

/**
 * Get kernel Icon
 */
async function getKernelIcon(
  specModel: KernelSpec.ISpecModel
): Promise<LabIcon> {
  // First check for logo-svg
  if (specModel.resources['logo-svg']) {
    const svgStr = await getKernelIconBase64String(
      specModel.resources['logo-svg']
    );
    return new LabIcon({
      name: `${NS}:icon:${specModel.name}`,
      svgstr: svgStr,
    });
  }
  // Else check if 64x64 kernel icon is availble
  if (specModel.resources['logo-64x64']) {
    const iconBase64String = await getKernelIconBase64String(
      specModel.resources['logo-64x64']
    );
    return new LabIcon({
      name: `${NS}:icon:${specModel.name}`,
      svgstr: base64ToSvgStr(64, iconBase64String),
    });
  }
  // Finally check for 32x32 kernel icon
  if (specModel.resources['logo-32x32']) {
    const iconBase64String = await getKernelIconBase64String(
      specModel.resources['logo-32x32']
    );
    return new LabIcon({
      name: `${NS}:icon:${specModel.name}`,
      svgstr: base64ToSvgStr(32, iconBase64String),
    });
  }
  // If not found, make a generic kernel icon
  return LabIcon.resolve({
    icon: 'ui-components:kernel',
  });
}

/**
 * Get all available kernel file types so that we replace auto format
 * with these file extensions
 */
export async function getAvailableKernelFileTypes(
  languages: IEditorLanguageRegistry,
  serviceManager: ServiceManager.IManager
): Promise<Map<string, IFileTypeData[]>> {
  const specsManager = serviceManager.kernelspecs;
  await specsManager.ready;
  const fileTypes = new Map<string, IFileTypeData[]>();
  const specs = specsManager.specs?.kernelspecs ?? {};
  for (const [spec, specModel] of Object.entries(specs)) {
    if (specModel) {
      // First check if kernel is one of the pre-defined types (Python, R, Julia)
      const exts = AUTO_LANGUAGE_FILETYPE_DATA.get(specModel.language);
      if (exts !== undefined) {
        fileTypes.set(specModel.language, exts);
      } else {
        // If not, try to get languageInfo from codemirror languages
        const languageInfo = languages.findByName(specModel.language);
        // If we managed to find the language, construct the FileTypeData
        // Here we make an assumption that first extension in
        // languageInfo.extensions is the most common one.
        if (languageInfo) {
          // We attempt to get kernelIcon here for specModel.resources
          // If none provided, we return generic kernel icon
          const kernelIcon = await getKernelIcon(specModel);
          const exts: IFileTypeData[] = [
            {
              fileExt: languageInfo.extensions[0],
              paletteLabel: `New ${languageInfo.displayName} Text Notebook`,
              caption: `Create a new ${languageInfo.displayName} Text Notebook`,
              kernelIcon: kernelIcon,
              launcherLabel: specModel.display_name || languageInfo.displayName,
              kernelName: spec,
            },
          ];
          fileTypes.set(specModel.language, exts);
        }
      }
    }
  }
  return fileTypes;
}

/**
 * Get all available 'Create New Text Notebook' commands based on configured
 * formats and available kernels
 */
export async function getAvailableCreateTextNotebookCommands(
  launcherItems: string[],
  availableKernels: Map<string, IFileTypeData[]>
): Promise<Map<string, IFileTypeData[]>> {
  const numKernels = availableKernels.size;

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
          let mapIndex = 0;
          availableKernels.forEach(
            (kernelFileTypes: IFileTypeData[], kernelKey: string) => {
              const updatedKernelKey = `${kernelKey}:${formatType}`;
              createTextNotebookCommands.set(updatedKernelKey, []);
              mapIndex += 1;
              kernelFileTypes.map((kernelFileType) => {
                // Merge fileType object from kernel and Jupytext format and push
                // it to createTextNotebookCommands
                const updatedKernelFileType = { ...kernelFileType };
                updatedKernelFileType.fileExt = `${updatedKernelFileType.fileExt}:${formatType}`;
                updatedKernelFileType.paletteLabel = `${updatedKernelFileType.paletteLabel} with ${fileType.paletteLabel}`;
                updatedKernelFileType.caption = `${updatedKernelFileType.caption} with ${fileType.caption}`;
                updatedKernelFileType.launcherLabel = `${updatedKernelFileType.launcherLabel} - ${fileType.launcherLabel}`;
                if (numKernels === mapIndex) {
                  updatedKernelFileType.separator = true;
                }
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
