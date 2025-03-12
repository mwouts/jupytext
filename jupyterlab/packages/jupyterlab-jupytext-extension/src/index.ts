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

import { IEditorLanguageRegistry } from '@jupyterlab/codemirror';

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

import { IMainMenu } from '@jupyterlab/mainmenu';

import { ITranslator, nullTranslator } from '@jupyterlab/translation';

import { LabIcon } from '@jupyterlab/ui-components';

import { DisposableSet } from '@lumino/disposable';

import { Menu } from '@lumino/widgets';

import { JSONExt, ReadonlyJSONValue } from '@lumino/coreutils';

import { IRisePreviewFactory } from 'jupyterlab-rise';

import {
  JUPYTEXT_EXTENSION_ID,
  JUPYTEXT_PAIR_COMMANDS_FILETYPE_DATA,
  JUPYTEXT_FORMATS,
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
  getAvailableKernelLanguages,
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
    IMainMenu,
    IDefaultFileBrowser,
    ITranslator,
    ICommandPalette,
    IRisePreviewFactory,
  ],
  requires: [
    NotebookPanel.IContentFactory,
    IEditorServices,
    IDocumentManager,
    IEditorLanguageRegistry,
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
    languages: IEditorLanguageRegistry,
    rendermime: IRenderMimeRegistry,
    notebookFactory: NotebookWidgetFactory.IFactory,
    notebookTracker: INotebookTracker,
    settingRegistry: ISettingRegistry,
    toolbarRegistry: IToolbarWidgetRegistry,
    launcher: ILauncher | null,
    mainmenu: IMainMenu | null,
    defaultBrowser: IDefaultFileBrowser | null,
    translator: ITranslator | null,
    palette: ICommandPalette | null,
    riseFactory: IRisePreviewFactory | null,
  ) => {
    console.log('JupyterLab extension jupytext is activating...');
    const trans = (translator ?? nullTranslator).load('jupytext');

    // Load settings
    const includeFormats = TEXT_NOTEBOOKS_LAUNCHER_ICONS;
    if (settingRegistry) {
      const settings = await settingRegistry.load(extension.id);
      for (const format of JUPYTEXT_FORMATS) {
        const addFormat = settings.get(format).composite as boolean;
        if (addFormat && !includeFormats.includes(format)) {
          includeFormats.push(format);
        } else if (!addFormat && includeFormats.includes(format)) {
          includeFormats.splice(includeFormats.indexOf(format), 1);
        }
      }
    }

    // Unpack necessary components
    const { commands, serviceManager, docRegistry } = app;

    // Initialise Jupytext create notebook submenu and add it to File menu
    const jupytextCreateMenu = new Menu({ commands: app.commands });
    jupytextCreateMenu.id = 'jp-mainmenu-jupytext-new-menu';
    jupytextCreateMenu.title.label = trans.__('New Text Notebook');
    mainmenu.fileMenu.addItem({
      rank: 0.97,
      type: 'submenu',
      submenu: jupytextCreateMenu,
    });

    // Initialise Jupytext menu and add it to main menu
    const jupytextMenu = new Menu({ commands: app.commands });
    mainmenu.fileMenu.addItem({
      rank: 0.98,
      type: 'submenu',
      submenu: jupytextMenu,
    });
    jupytextMenu.id = 'jp-mainmenu-jupytext-menu';
    jupytextMenu.title.label = trans.__('Jupytext');

    // Get all Jupytext formats
    let rank = 0;
    const separatorIndex: number[] = [];
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
                trans,
              );
            },
          });

          console.debug(
            'Registering pairing command=' + command + ' with rank=' + rank,
          );
          palette?.addItem({
            command,
            args: { isPalette: true },
            rank: rank + 1,
            category: 'Jupytext',
          });
          // Add to jupytext pair menu
          jupytextMenu.addItem({
            command: command,
          });
          if (fileType.separator) {
            separatorIndex.push(rank);
          }
          rank += 1;
        });
      },
    );

    // Add separators in jupytext pair menu
    separatorIndex.map((index, idx) => {
      jupytextMenu.insertItem(index + idx + 1, {
        type: 'separator',
      });
    });

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
    jupytextMenu.addItem({
      type: 'separator',
    });
    jupytextMenu.addItem({
      command: CommandIDs.metadata,
    });
    jupytextMenu.addItem({
      type: 'separator',
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
    jupytextMenu.addItem({
      command: CommandIDs.faq,
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
      command: CommandIDs.reference,
      args: { isPalette: true },
      rank: 100,
      category: 'Jupytext',
    });
    jupytextMenu.addItem({
      command: CommandIDs.reference,
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
    // We dont need to add this command to palettte as it is a utility one
    // which does not have direct usage
    // palette?.addItem({
    //   command: CommandIDs.newUntitled,
    //   rank: 50,
    //   category: 'Jupytext',
    // });

    // Get a map of available kernel languages in current widget
    const availableKernelLanguages = await getAvailableKernelLanguages(
      languages,
      serviceManager,
    );

    // Get a map of all create text notebook commands
    const createTextNotebookCommands =
      await getAvailableCreateTextNotebookCommands(
        includeFormats,
        availableKernelLanguages,
      );

    // Register Jupytext text notebooks file types
    registerFileTypes(availableKernelLanguages, docRegistry, trans);

    // Get all kernel file types to add to Jupytext factory
    const kernelLanguageNames = [];
    for (const kernelLanguage of availableKernelLanguages.keys()) {
      kernelLanguageNames.push(kernelLanguage);
    }

    // Create a factory for Jupytext
    createFactory(
      kernelLanguageNames,
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
      riseFactory,
    );

    // Register all the commands that create text notebooks with different formats
    // Nicked from notebook-extension package in JupyterLab
    // https://github.com/jupyterlab/jupyterlab/blob/c106f0a19110efad7c5e1b136144985819e21100/packages/notebook-extension/src/index.ts#L1902-L1965
    createTextNotebookCommands.forEach((fileTypes: IFileTypeData[], _) => {
      fileTypes.map((fileType: IFileTypeData) => {
        const format = fileType.fileExt;
        const command = `jupytext:create-new-text-notebook-${format}`;
        const iconName = fileType.iconName;
        const kernelIcon = fileType.kernelIcon;
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
              if (iconName) {
                return LabIcon.resolve({
                  icon: iconName as string,
                });
              }
              if (kernelIcon) {
                return kernelIcon;
              }
              return LabIcon.resolve({
                icon: 'ui-components:kernel',
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
              commands,
            );
          },
        });

        console.debug(
          'Registering create new text notebook command=' +
            command +
            ' with rank=' +
            rank,
        );
        palette?.addItem({
          command,
          args: { isPalette: true },
          rank: rank,
          category: 'Jupytext',
        });
        if (includeFormats.includes(format)) {
          jupytextCreateMenu.addItem({
            command: command,
            args: { isMainMenu: true },
          });
          // Add separator after each kernel type
          if (fileType.separator) {
            jupytextCreateMenu.addItem({
              type: 'separator',
            });
          }
        }

        // Add a launcher item if the launcher is available.
        if (launcher && includeFormats.includes(format)) {
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
                  category: trans.__('Jupytext'),
                  rank: rank++,
                  kernelIconUrl,
                  metadata: {
                    kernel: JSONExt.deepCopy(
                      specs.kernelspecs[fileType.kernelName]?.metadata || {},
                    ) as ReadonlyJSONValue,
                  },
                }),
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
