import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from '@jupyterlab/application';

import {
  ICommandPalette,
  IToolbarWidgetRegistry,
  createToolbarFactory,
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

import { IDocumentWidget } from '@jupyterlab/docregistry';

import { ITranslator, nullTranslator } from '@jupyterlab/translation';

import { markdownIcon, notebookIcon } from '@jupyterlab/ui-components';

import { DisposableSet } from '@lumino/disposable';

import { JSONExt, ReadonlyJSONValue } from '@lumino/coreutils';

import { IRisePreviewFactory } from 'jupyterlab-rise';

import {
  JUPYTEXT_EXTENSION_ID,
  FILE_TYPES,
  TEXT_NOTEBOOKS_LAUNCHER_ICONS,
  FACTORY,
  CommandIDs,
  IJupytextFormat,
} from './tokens';

import {
  getAvailJupytextFormats,
  isPairCommandToggled,
  isPairCommandEnabled,
  executePairCommand,
  isMetadataCommandToggled,
  isMetadataCommandEnabled,
  executeMetadataCommand,
} from './jupytext';

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
    const JUPYTEXT_FORMATS = getAvailJupytextFormats(trans);

    // Register all pairing commands
    JUPYTEXT_FORMATS.forEach((args: IJupytextFormat, rank: number) => {
      const format: string = args['format'];
      const command = `jupytext:${format}`;
      commands.addCommand(command, {
        label: args['label'],
        isToggled: () => {
          return isPairCommandToggled(format, notebookTracker);
        },
        isEnabled: () => {
          return isPairCommandEnabled(format, notebookTracker);
        },
        execute: () => {
          return executePairCommand(command, format, notebookTracker, trans);
        },
      });

      console.log(
        'Registering pairing command=' + command + ' with rank=' + (rank + 1)
      );
      palette?.addItem({ command, rank: rank + 2, category: 'Jupytext' });
    });

    // Metadata in text representation
    commands.addCommand(CommandIDs.metadata, {
      label: trans.__('Include Metadata'),
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
      rank: JUPYTEXT_FORMATS.length + 3,
      category: 'Jupytext',
    });

    // Register Jupytext FAQ command
    commands.addCommand(CommandIDs.faq, {
      label: trans.__('Jupytext FAQ'),
      execute: () => {
        window.open('https://jupytext.readthedocs.io/en/latest/faq.html');
      },
    });
    palette?.addItem({
      command: CommandIDs.faq,
      rank: 99,
      category: 'Jupytext',
    });

    // Register Jupytext Reference
    commands.addCommand(CommandIDs.reference, {
      label: trans.__('Jupytext Reference'),
      execute: () => {
        window.open('https://jupytext.readthedocs.io/en/latest/');
      },
    });
    palette?.addItem({
      command: CommandIDs.faq,
      rank: 100,
      category: 'Jupytext',
    });

    // Define file types
    docRegistry.addFileType(
      {
        name: 'myst',
        contentType: 'notebook',
        displayName: trans.__('MyST Markdown Notebook'),
        extensions: ['.myst', '.mystnb', '.mnb'],
        icon: markdownIcon,
      },
      ['Notebook']
    );

    docRegistry.addFileType(
      {
        name: 'r-markdown',
        contentType: 'notebook',
        displayName: trans.__('R Markdown Notebook'),
        // Extension file are transformed to lower case...
        extensions: ['.Rmd'],
        icon: markdownIcon,
      },
      ['Notebook']
    );

    docRegistry.addFileType(
      {
        name: 'quarto',
        contentType: 'notebook',
        displayName: trans.__('Quarto Notebook'),
        extensions: ['.qmd'],
        icon: markdownIcon,
      },
      ['Notebook']
    );

    // primarily this block is copied/pasted from jlab4 code and specifically
    // jupyterlab/packages/notebook-extension/src/index.ts
    // inside the function `activateWidgetFactory` at line 1150 as of this writing
    //
    const toolbarFactory = createToolbarFactory(
      toolbarRegistry,
      settingRegistry,
      'Notebook',
      '@jupyterlab/notebook-extension:panel',
      translator
    );
    // Duplicate notebook factory to apply it on Jupytext notebooks
    // Mirror: https://github.com/jupyterlab/jupyterlab/blob/8a8c3752564f37493d4eb6b4c59008027fa83880/packages/notebook-extension/src/index.ts#L860
    const factory = new NotebookWidgetFactory({
      name: FACTORY,
      label: trans.__(FACTORY),
      fileTypes: FILE_TYPES,
      modelName: notebookFactory.modelName ?? 'notebook',
      preferKernel: notebookFactory.preferKernel ?? true,
      canStartKernel: notebookFactory.canStartKernel ?? true,
      rendermime,
      contentFactory,
      editorConfig: notebookFactory.editorConfig,
      notebookConfig: notebookFactory.notebookConfig,
      mimeTypeService: editorServices.mimeTypeService,
      toolbarFactory: toolbarFactory,
      translator,
    });
    docRegistry.addWidgetFactory(factory);

    // Register widget created with the new factory in the notebook tracker
    // This is required to activate notebook commands (and therefore shortcuts)
    let id = 0; // The ID counter for notebook panels.
    const ft = docRegistry.getFileType('notebook');

    factory.widgetCreated.connect((sender, widget) => {
      // If the notebook panel does not have an ID, assign it one.
      widget.id = widget.id || `notebook-jupytext-${++id}`;

      // Set up the title icon
      widget.title.icon = ft?.icon;
      widget.title.iconClass = ft?.iconClass ?? '';
      widget.title.iconLabel = ft?.iconLabel ?? '';

      // Notify the widget tracker if restore data needs to update.
      widget.context.pathChanged.connect(() => {
        // @ts-expect-error Trick using private API
        void notebookTracker.save(widget);
      });
      // Add the notebook panel to the tracker.
      //   @ts-expect-error Trick using private API
      void notebookTracker.add(widget);
    });

    // Add support for RISE slides
    if (riseFactory) {
      for (const fileType of FILE_TYPES) {
        riseFactory.addFileType(fileType);
      }
    }

    // All supported format extensions bar ipynb, custom and none
    // must be added to create new text notebook commands
    const jupytextTextNotebookFormats = JUPYTEXT_FORMATS.filter(
      (jupytextFormat: IJupytextFormat) => {
        return !['ipynb', 'custom', 'none'].includes(jupytextFormat.format);
      }
    );

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

    // Register all the commands that create text notebooks with different formats
    // Nicked from notebook-extension package in JupyterLab
    // https://github.com/jupyterlab/jupyterlab/blob/c106f0a19110efad7c5e1b136144985819e21100/packages/notebook-extension/src/index.ts#L1902-L1965
    jupytextTextNotebookFormats.forEach(
      (jupytextFormat: IJupytextFormat, rank: number) => {
        const command = `jupytext:create-new-text-notebook-${jupytextFormat.format}`;
        const label = trans.__(jupytextFormat.label.split('with')[1].trim());
        console.log('Registering text notebook command=', command);
        commands.addCommand(command, {
          label: (args) => {
            if (args['isLauncher']) {
              return trans.__(label);
            }
            if (args['isPalette'] || args['isContextMenu']) {
              return trans.__(`New Text Notebook with ${label}`);
            }
            return trans.__(label);
          },
          caption: trans.__(`Create New Text Notebook with ${label}`),
          icon: (args) => (args['isPalette'] ? undefined : notebookIcon),
          execute: (args) => {
            const cwd =
              (args['cwd'] as string) || (defaultBrowser?.model.path ?? '');
            const kernelId = (args['kernelId'] as string) || '';
            const kernelName = (args['kernelName'] as string) || '';
            return createNew(cwd, kernelId, kernelName, jupytextFormat.format);
          },
        });
        palette?.addItem({
          command,
          args: { isPalette: true },
          rank: rank + 51,
          category: 'Jupytext',
        });

        // Add a launcher item if the launcher is available.
        if (launcher && launcherItems.includes(jupytextFormat.format)) {
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

              for (const name in specs.kernelspecs) {
                const rank = name === specs.default ? 0 : Infinity;
                const spec = specs.kernelspecs[name]!;
                const kernelIconUrl =
                  spec.resources['logo-svg'] || spec.resources['logo-64x64'];
                disposables.add(
                  launcher.add({
                    command: command,
                    args: { isLauncher: true, kernelName: name },
                    category: trans.__(launcherItemsCategory),
                    rank,
                    kernelIconUrl,
                    metadata: {
                      kernel: JSONExt.deepCopy(
                        spec.metadata || {}
                      ) as ReadonlyJSONValue,
                    },
                  })
                );
              }
            };
            onSpecsChanged();
            serviceManager.kernelspecs.specsChanged.connect(onSpecsChanged);
          });
        }
      }
    );

    // Utility function to create a new notebook.
    const createNew = async (
      cwd: string,
      kernelId: string,
      kernelName: string,
      format: string
    ) => {
      const model = await commands.execute(CommandIDs.newUntitled, {
        path: cwd,
        type: 'notebook',
        ext: format.replace('auto', 'py'), // Replace auto with py
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
  },
};

export default extension;
