import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from '@jupyterlab/application';

import {
  ICommandPalette,
  IToolbarWidgetRegistry,
  showErrorMessage,
} from '@jupyterlab/apputils';

import { IDocumentManager } from '@jupyterlab/docmanager';

import { Contents } from '@jupyterlab/services';

import { ILauncher } from '@jupyterlab/launcher';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { IEditorServices } from '@jupyterlab/codeeditor';

import {
  INotebookTracker,
  INotebookWidgetFactory,
  NotebookPanel,
  NotebookWidgetFactory,
} from '@jupyterlab/notebook';

import { IRenderMimeRegistry } from '@jupyterlab/rendermime';

import { IDefaultFileBrowser } from '@jupyterlab/filebrowser';

import { ITranslator, nullTranslator } from '@jupyterlab/translation';

import { LabIcon } from '@jupyterlab/ui-components';

import { DisposableSet } from '@lumino/disposable';

import { JSONExt, ReadonlyJSONValue } from '@lumino/coreutils';

import { IRisePreviewFactory } from 'jupyterlab-rise';

import {
  JUPYTEXT_EXTENSION_ID,
  JUPYTEXT_PAIR_COMMANDS_FILETYPE_DATA,
  TEXT_NOTEBOOKS_LAUNCHER_ICONS,
  CommandIDs,
  IFileTypeData,
  JupytextIcon,
} from './tokens';

import {
  isPairCommandToggled,
  isPairCommandEnabled,
  executePairCommand,
  isMetadataCommandToggled,
  isMetadataCommandEnabled,
  executeMetadataCommand,
} from './commands';

import { registerFileTypes } from './registry';

import { createFactory } from './factory';

import {
  getAvailableCreateTextNotebookCommands,
  createNewTextNotebook,
} from './utils';

/**
 * Initialization data for the jupyterlab-jupytext extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: JUPYTEXT_EXTENSION_ID,
  autoStart: true,
  optional: [
    ILauncher,
    IDefaultFileBrowser,
    ITranslator,
    ICommandPalette,
    IRisePreviewFactory,
  ],
  requires: [
    NotebookPanel.IContentFactory,
    IEditorServices,
    IDocumentManager,
    IRenderMimeRegistry,
    INotebookWidgetFactory,
    INotebookTracker,
    ISettingRegistry,
    IToolbarWidgetRegistry,
  ],
  activate: async (
    app: JupyterFrontEnd,
    contentFactory: NotebookPanel.IContentFactory,
    editorServices: IEditorServices,
    docManager: IDocumentManager,
    rendermime: IRenderMimeRegistry,
    notebookFactory: NotebookWidgetFactory.IFactory,
    notebookTracker: INotebookTracker,
    settingRegistry: ISettingRegistry,
    toolbarRegistry: IToolbarWidgetRegistry,
    launcher: ILauncher | null,
    defaultBrowser: IDefaultFileBrowser | null,
    translator: ITranslator | null,
    palette: ICommandPalette | null,
    riseFactory: IRisePreviewFactory | null
  ) => {
    console.log('JupyterLab extension jupytext is activating...');
    const trans = (translator ?? nullTranslator).load('jupytext');

    // Load settings
    let launcherItems = TEXT_NOTEBOOKS_LAUNCHER_ICONS;
    let launcherItemsCategory = 'Jupytext';
    if (settingRegistry) {
      const settings = await settingRegistry.load(extension.id);
      launcherItems = settings.get('format').composite as string[];
      launcherItemsCategory = settings.get('category').composite as string;
    }

    // Unpack necessary components
    const { commands, serviceManager, docRegistry } = app;

    // Get all Jupytext formats
    let rank = 0;
    JUPYTEXT_PAIR_COMMANDS_FILETYPE_DATA.forEach(
      (value: IFileTypeData[], key: string) => {
        value.map((fileType: IFileTypeData) => {
          const format = key;
          const command = `jupytext:pair-nb-with-${format}`;
          commands.addCommand(command, {
            label: (args) => {
              if (args.isPalette) {
                return (
                  (fileType.paletteLabel as string) ?? trans.__('Pair notebook')
                );
              }
              return (fileType.caption as string) ?? trans.__('Pair notebook');
            },
            caption: trans.__(fileType.caption),
            icon: (args) => {
              if (args.isPalette) {
                return undefined;
              } else {
                return fileType.iconName
                  ? LabIcon.resolve({
                      icon: fileType.iconName as string,
                    })
                  : undefined;
              }
            },
            isToggled: () => {
              return isPairCommandToggled(format, notebookTracker);
            },
            isEnabled: () => {
              return isPairCommandEnabled(format, notebookTracker);
            },
            execute: () => {
              return executePairCommand(
                command,
                format,
                notebookTracker,
                trans
              );
            },
          });

          console.log(
            'Registering pairing command=' + command + ' with rank=' + rank
          );
          palette?.addItem({
            command,
            args: { isPalette: true },
            rank: rank + 1,
            category: 'Jupytext',
          });
          rank += 1;
        });
      }
    );

    // Metadata in text representation
    commands.addCommand(CommandIDs.metadata, {
      label: trans.__('Include Metadata'),
      icon: (args) => {
        if (args.isPalette) {
          return undefined;
        } else {
          return JupytextIcon;
        }
      },
      isToggled: () => {
        return isMetadataCommandToggled(notebookTracker);
      },
      isEnabled: () => {
        return isMetadataCommandEnabled(notebookTracker);
      },
      execute: () => {
        return executeMetadataCommand(notebookTracker);
      },
    });
    palette?.addItem({
      command: CommandIDs.metadata,
      args: { isPalette: true },
      rank: 98,
      category: 'Jupytext',
    });

    // Register Jupytext FAQ command
    commands.addCommand(CommandIDs.faq, {
      label: trans.__('Jupytext FAQ'),
      icon: (args) => {
        if (args.isPalette) {
          return undefined;
        } else {
          return JupytextIcon;
        }
      },
      execute: () => {
        window.open('https://jupytext.readthedocs.io/en/latest/faq.html');
      },
    });
    palette?.addItem({
      command: CommandIDs.faq,
      args: { isPalette: true },
      rank: 99,
      category: 'Jupytext',
    });

    // Register Jupytext Reference
    commands.addCommand(CommandIDs.reference, {
      label: trans.__('Jupytext Reference'),
      icon: (args) => {
        if (args.isPalette) {
          return undefined;
        } else {
          return JupytextIcon;
        }
      },
      execute: () => {
        window.open('https://jupytext.readthedocs.io/en/latest/');
      },
    });
    palette?.addItem({
      command: CommandIDs.faq,
      args: { isPalette: true },
      rank: 100,
      category: 'Jupytext',
    });

    // Register a new command to create untitled file. This snippet is taken
    // from docManager package https://github.com/jupyterlab/jupyterlab/blob/c106f0a19110efad7c5e1b136144985819e21100/packages/docmanager-extension/src/index.tsx#L679-L680
    // We are "duplicating" it as base command adds extension to the options
    // only if it is of type file. But we are interested in creating notebook type
    // files with different Jupytext supported extensions. So we create a dedicated
    // create new text notebook command here and make sure we pass extension in options
    commands.addCommand(CommandIDs.newUntitled, {
      execute: async (args) => {
        const errorTitle = (args['error'] as string) || trans.__('Error');
        const path =
          typeof args['path'] === 'undefined' ? '' : (args['path'] as string);
        const options: Partial<Contents.ICreateOptions> = {
          type: args['type'] as Contents.ContentType,
          path,
        };

        // Ensure we pass extension to command always
        options.ext = (args['ext'] as string) || '.txt';

        return docManager.services.contents
          .newUntitled(options)
          .catch((error) => showErrorMessage(errorTitle, error));
      },
      label: (args) =>
        (args['label'] as string) || `New ${args['type'] as string}`,
    });
    palette?.addItem({
      command: CommandIDs.newUntitled,
      rank: 50,
      category: 'Jupytext',
    });

    // Register Jupytext text notebooks file types
    registerFileTypes(docRegistry, trans);

    // Create a factory for Jupytext
    createFactory(
      toolbarRegistry,
      settingRegistry,
      docRegistry,
      notebookTracker,
      notebookFactory,
      contentFactory,
      editorServices,
      rendermime,
      translator,
      trans,
      riseFactory
    );

    const createTextNotebookCommands =
      await getAvailableCreateTextNotebookCommands(
        launcherItems,
        serviceManager
      );

    // Register all the commands that create text notebooks with different formats
    // Nicked from notebook-extension package in JupyterLab
    // https://github.com/jupyterlab/jupyterlab/blob/c106f0a19110efad7c5e1b136144985819e21100/packages/notebook-extension/src/index.ts#L1902-L1965
    createTextNotebookCommands.forEach((fileTypes: IFileTypeData[], _) => {
      fileTypes.map((fileType: IFileTypeData) => {
        const format = fileType.fileExt;
        const command = `jupytext:create-new-text-noteboook-${format}`;
        const iconName = fileType.iconName || 'ui-components:kernel';
        commands.addCommand(command, {
          label: (args) => {
            if (args['isLauncher']) {
              return trans.__(fileType.launcherLabel);
            }
            return trans.__(fileType.paletteLabel);
          },
          caption: trans.__(fileType.caption),
          icon: (args) => {
            if (args.isPalette) {
              return undefined;
            } else {
              return LabIcon.resolve({
                icon: iconName as string,
              });
            }
          },
          execute: (args) => {
            const cwd =
              (args['cwd'] as string) || (defaultBrowser?.model.path ?? '');
            const kernelId = (args['kernelId'] as string) || '';
            const kernelName = (args['kernelName'] as string) || '';
            return createNewTextNotebook(
              cwd,
              kernelId,
              kernelName,
              format,
              commands
            );
          },
        });

        console.log(
          'Registering create new text notebook command=' +
            command +
            'with rank=' +
            rank
        );
        palette?.addItem({
          command,
          args: { isPalette: true },
          rank: rank,
          category: 'Jupytext',
        });

        // Add a launcher item if the launcher is available.
        if (launcher && launcherItems.includes(format)) {
          void serviceManager.ready.then(() => {
            let disposables: DisposableSet | null = null;
            const onSpecsChanged = () => {
              if (disposables) {
                disposables.dispose();
                disposables = null;
              }
              const specs = serviceManager.kernelspecs.specs;
              if (!specs) {
                return;
              }
              disposables = new DisposableSet();
              const kernelIconUrl =
                specs.kernelspecs[fileType.kernelName]?.resources['logo-svg'] ||
                specs.kernelspecs[fileType.kernelName]?.resources['logo-64x64'];
              disposables.add(
                launcher.add({
                  command: command,
                  args: { isLauncher: true, kernelName: fileType.kernelName },
                  category: trans.__(launcherItemsCategory),
                  rank: rank++,
                  kernelIconUrl,
                  metadata: {
                    kernel: JSONExt.deepCopy(
                      specs.kernelspecs[fileType.kernelName]?.metadata || {}
                    ) as ReadonlyJSONValue,
                  },
                })
              );
            };
            onSpecsChanged();
            serviceManager.kernelspecs.specsChanged.connect(onSpecsChanged);
          });
        }
        // Increment rank
        rank += 1;
      });
    });
  },
};

export default extension;
