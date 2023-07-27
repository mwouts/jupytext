import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from "@jupyterlab/application";

import {
  ICommandPalette,
  ISessionContextDialogs,
  showErrorMessage,
  IToolbarWidgetRegistry,
  createToolbarFactory,
} from "@jupyterlab/apputils";

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { IEditorServices } from "@jupyterlab/codeeditor";

import * as nbformat from "@jupyterlab/nbformat";

import {
  INotebookTracker,
  INotebookWidgetFactory,
  NotebookPanel,
  NotebookWidgetFactory,
} from "@jupyterlab/notebook";
import { IRenderMimeRegistry } from "@jupyterlab/rendermime";

import {
  ITranslator,
  nullTranslator,
  TranslationBundle,
} from "@jupyterlab/translation";

import { markdownIcon } from "@jupyterlab/ui-components";

interface IJupytextFormat {
  /**
   * Conversion format
   */
  format: string;
  /**
   * Command label
   */
  label: string;
}

interface IJupytextRepresentation {
  format_name: string;
  extension: string;
}

interface IJupytextSection {
  formats?: string;
  notebook_metadata_filter?: string;
  cell_metadata_filter?: string;
  text_representation?: IJupytextRepresentation;
}

function getJupytextFormats(trans: TranslationBundle): IJupytextFormat[] {
  return [
    {
      format: "ipynb",
      label: trans.__("Pair Notebook with ipynb document"),
    },
    {
      format: "auto:light",
      label: trans.__("Pair Notebook with light Script"),
    },
    {
      format: "auto:percent",
      label: trans.__("Pair Notebook with percent Script"),
    },
    {
      format: "auto:hydrogen",
      label: trans.__("Pair Notebook with Hydrogen Script"),
    },
    {
      format: "auto:nomarker",
      label: trans.__("Pair Notebook with nomarker Script"),
    },
    {
      format: "md",
      label: trans.__("Pair Notebook with Markdown"),
    },
    {
      format: "md:myst",
      label: trans.__("Pair Notebook with MyST Markdown"),
    },
    {
      format: "Rmd",
      label: trans.__("Pair Notebook with R Markdown"),
    },
    {
      format: "qmd",
      label: trans.__("Pair Notebook with Quarto (qmd)"),
    },
    {
      format: "custom",
      label: trans.__("Custom pairing"),
    },
    {
      format: "none",
      label: trans.__("Unpair Notebook"),
    },
  ];
}

/**
 * Supported file formats.
 */
const LANGUAGE_INDEPENDENT_NOTEBOOK_EXTENSIONS = ["ipynb", "md", "Rmd", "qmd"];

// will get updated upon activation
// default is true, and we will turn this off only iff
// app.name is "JupyterLab" and the version is 3.x or below
let JLAB4 = true;

function get_jupytext_formats(notebook_tracker: INotebookTracker): Array<string> {
  if (!notebook_tracker.currentWidget) return [];

  const model = notebook_tracker.currentWidget.context.model;

  // xxx not sure this is useful
  // if metadata.get("jupytext") used to return something that is void
  // then we're in the clear
  // if (! JLAB4)
  //   if (! (model.metadata as any)?.has("jupytext"))
  //     return [];

  const jupytext: IJupytextSection = (JLAB4
    ? (model as any).getMetadata("jupytext")
    : (model.metadata as any)?.get('jupytext')) as IJupytextSection;
  if ( ! jupytext )
    return [];
  let formats: Array<string> = jupytext && jupytext.formats ? jupytext.formats.split(',') : [];
  return formats.filter(function (fmt) {
    return fmt !== '';
  });
}

function get_selected_formats(notebook_tracker: INotebookTracker): Array<string> {
  if (!notebook_tracker.currentWidget) return [];

  let formats = get_jupytext_formats(notebook_tracker);

  const model = notebook_tracker.currentWidget.context.model;

  const lang = ( JLAB4
      ? (model as any).getMetadata('language_info')
      : (model.metadata as any)?.get('language_info')
  ) as nbformat.ILanguageInfoMetadata;
  if (lang && lang.file_extension) {
    const script_ext = lang.file_extension.substring(1);
    formats = formats.map(function (fmt) {
      if (fmt === script_ext)
        return 'auto:light';
      return fmt.replace(script_ext + ':', 'auto:');
    });
  }

  let notebook_extension: string | undefined = notebook_tracker.currentWidget.context.path.split('.').pop();
  if (!notebook_extension)
    return formats;

  notebook_extension =
    LANGUAGE_INDEPENDENT_NOTEBOOK_EXTENSIONS.indexOf(notebook_extension) == -1 ? "auto" : notebook_extension;
  for (const i in formats) {
    const ext = formats[i].split(':')[0];
    if (ext == notebook_extension)
      return formats;
  }

  // the notebook extension was not found among the formats
  if (LANGUAGE_INDEPENDENT_NOTEBOOK_EXTENSIONS.indexOf(notebook_extension) != -1)
    formats.push(notebook_extension);
  else {
    let format_name = 'light';
    // xxx same here, the test is probably not needed
    // if (notebook_tracker.currentWidget.context.model.metadata.has("jupytext")) {
    const model = notebook_tracker.currentWidget.context.model;
    const jupytext: IJupytextSection = (JLAB4
      ? (model as any).getMetadata('jupytext')
      : (model.metadata as any)?.get('jupytext')) as IJupytextSection;
    if (jupytext && jupytext.text_representation && jupytext.text_representation.format_name)
      format_name = jupytext.text_representation.format_name;
    // }
    formats.push('auto:' + format_name);
  }
  return formats;
};

/**
 * Initialization data for the jupyterlab-jupytext extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: "jupyterlab-jupytext",
  autoStart: true,
  // IEditorTracker and IMarkdownViewerTracker are optionally requested only
  // to ensure this is called after they are activated and we properly overwrite
  // the default factory for non-notebook file format
  optional: [ITranslator, ICommandPalette],
  requires: [
    NotebookPanel.IContentFactory,
    IEditorServices,
    IRenderMimeRegistry,
    ISessionContextDialogs,
    INotebookWidgetFactory,
    INotebookTracker,
    ISettingRegistry,
    IToolbarWidgetRegistry,
    ICommandPalette,
    ITranslator,

  ],
  activate: (
    app: JupyterFrontEnd,
    contentFactory: NotebookPanel.IContentFactory,
    editorServices: IEditorServices,
    rendermime: IRenderMimeRegistry,
    sessionContextDialogs: ISessionContextDialogs,
    notebookFactory: NotebookWidgetFactory.IFactory,
    notebookTracker: INotebookTracker,
    settingRegistry: ISettingRegistry | null,
    toolbarRegistry: IToolbarWidgetRegistry,
    palette: ICommandPalette | null,
    translator: ITranslator | null,
  ) => {
    // https://semver.org/#semantic-versioning-specification-semver
    // npm semver requires pre-release versions to come with a hyphen
    // so 7.0.0rc2 won't work with semver
    // in addition, when running in the notebook7 context, app refers
    // to the notebook7 application, not the jupyterlab application
    if (app.name == "JupyterLab") {
      const app_numbers = app.version.match(/[0-9]+/);
      if (app_numbers) {
        JLAB4 = parseInt(app_numbers[0]) >= 4;
      }
    }
    console.log("JupyterLab extension jupytext is activating...");
    console.debug(`bundled jupytext labextension: JLAB4=${JLAB4}`);
    const trans = (translator ?? nullTranslator).load("jupytext");

    // Jupytext formats
    const JUPYTEXT_FORMATS = getJupytextFormats(trans);
    JUPYTEXT_FORMATS.forEach((args, rank) => {
      const format: string = args["format"];
      const command: string = "jupytext:" + format;
      app.commands.addCommand(command, {
        label: args["label"],
        isToggled: () => {
          if (!notebookTracker.currentWidget) return false;
          const jupytext_formats = get_selected_formats(notebookTracker);

          if (format == "custom"){
              for (const i in jupytext_formats) {
                  const fmt = jupytext_formats[i];
                  if (['ipynb', 'auto:light', 'auto:percent', 'auto:hydrogen', 'auto:nomarker', 'md', 'Rmd', 'qmd', 'md:myst'].indexOf(fmt)==-1)
                      return true;
              }
              return false;
          }
          return jupytext_formats.indexOf(format)!=-1;
        },
        isEnabled: () => {
            if (!notebookTracker.currentWidget)
                return false;

            const notebook_extension: string | undefined = notebookTracker.currentWidget.context.path.split('.').pop();
            if (format === notebook_extension)
                return false;

            if (format === 'none') {
                const formats = get_selected_formats(notebookTracker);
                return formats.length > 1;
            }

            return true;
        },
        execute: () => {
            if ( notebookTracker.currentWidget === null)
              return;
            const model = notebookTracker.currentWidget.context.model;
            const jupytext: IJupytextSection = (JLAB4
              ? (model as any).getMetadata('jupytext')
              : (model.metadata as any)?.get('jupytext')
            ) as IJupytextSection;
          let formats: Array<string> = get_selected_formats(notebookTracker);

          // Toggle the selected format
          console.log("Jupytext: executing command=" + command);
          if (format == "custom") {
            showErrorMessage(
              trans.__("Error"),
              trans.__(
                "Please edit the notebook metadata directly if you wish a custom configuration."
              )
            );
            return;
          }
        // Toggle the selected format
            let notebook_extension: string = notebookTracker.currentWidget.context.path.split('.').pop() as string;
            notebook_extension = LANGUAGE_INDEPENDENT_NOTEBOOK_EXTENSIONS.indexOf(notebook_extension) == -1 ? 'auto' : notebook_extension;

            // Toggle the selected format
            const index = formats.indexOf(format);
            if (format === 'none') {
                // Only keep one format - one that matches the current extension
                for (const i in formats) {
                    const fmt = formats[i];
                    if (fmt.split(':')[0] === notebook_extension) {
                        formats = [fmt];
                        break;
                    }
                }
            } else if (index != -1) {
                formats.splice(index, 1);

                // The current file extension can't be unpaired
                let ext_found = false;
                for (const i in formats) {
                    const fmt = formats[i];
                    if (fmt.split(':')[0] === notebook_extension) {
                        ext_found = true;
                        break;
                    }
                }

                if (!ext_found)
                    return;
            } else {
                // We can't have the same extension multiple times
                const new_formats = [];
                for (const i in formats) {
                    const fmt = formats[i];
                    if (fmt.split(':')[0] !== format.split(':')[0]) {
                        new_formats.push(fmt)
                    }
                }

                formats = new_formats;
                formats.push(format);
            }

          if (formats.length === 1) {
            if (notebook_extension !== 'auto')
              formats = [];
            else if (jupytext && jupytext.text_representation) {
              const format_name = formats[0].split(':')[1];
              jupytext.text_representation.format_name = format_name;
              formats = [];
            }
          }

          if (formats.length === 0) {
            // an older version was re-fetching the jupytext metadata here
            // but this is not necessary, as the metadata is already available
            if (!jupytext) return;

            if (jupytext.formats) {
              delete jupytext.formats;
            }

            if (Object.keys(jupytext).length == 0) {
              const model = notebookTracker.currentWidget.context.model;
              JLAB4
                ? (model as any).deleteMetadata("jupytext")
                : (model.metadata as any).delete("jupytext");
            }
            return;
          }

          // set the desired format
          if (jupytext) jupytext.formats = formats.join();
          else {
            const model = notebookTracker.currentWidget.context.model;
            JLAB4
              ? (model as any).setMetadata("jupytext", { formats: formats.join() })
              : (model.metadata as any)?.set( { formats: formats.join() });
            }
      }
      });

      console.log("Jupytext: adding command=" + command + " with rank=" + (rank + 1));
      palette?.addItem({ command, rank: rank + 2, category: "Jupytext" });
    });

    // Jupytext's documentation
    palette?.addItem({
      args: {
        text: trans.__("Jupytext Reference"),
        url: "https://jupytext.readthedocs.io/en/latest/"
      },
      command: "help:open",
      category: "Jupytext",
      rank: 0
    });

    palette?.addItem({
      args: {
        text: trans.__("Jupytext FAQ"),
        url: "https://jupytext.readthedocs.io/en/latest/faq.html"
      },
      command: "help:open",
      category: "Jupytext",
      rank: 1
    });

    // Metadata in text representation
    app.commands.addCommand("jupytext_metadata", {
      label: trans.__("Include Metadata"),
      isToggled: () => {
        if (!notebookTracker.currentWidget)
          return false;

        const model = notebookTracker.currentWidget.context.model;
        const jupytext_metadata = JLAB4
          ? (model as any).getMetadata("jupytext")
          : (model.metadata as any)?.get("jupytext")
        if (!jupytext_metadata)
          return false;

        const jupytext: IJupytextSection = (jupytext_metadata as unknown) as IJupytextSection;

        if (jupytext.notebook_metadata_filter === '-all')
          return false;

        return true;
      },
      isEnabled: () => {
        if (!notebookTracker.currentWidget)
          return false;

        const model = notebookTracker.currentWidget.context.model;
        const jupytext_metadata = JLAB4
          ? (model as any).getMetadata("jupytext")
          : (model.metadata as any)?.get("jupytext")
        if (!jupytext_metadata)
          return false;

        const jupytext: IJupytextSection = (jupytext_metadata as unknown) as IJupytextSection;

        if (jupytext.notebook_metadata_filter === undefined)
          return true;

        if (jupytext.notebook_metadata_filter === '-all')
          return true;

        return false;
      },
      execute: () => {
        console.log("Jupytext: toggling YAML header");
        if (!notebookTracker.currentWidget)
          return;

        const model = notebookTracker.currentWidget.context.model;
        const jupytext_metadata = JLAB4
          ? (model as any).getMetadata("jupytext")
          : (model.metadata as any)?.get("jupytext")
        if (!jupytext_metadata)
          return false;

        const jupytext: IJupytextSection = (jupytext_metadata as unknown) as IJupytextSection;

        if (jupytext.notebook_metadata_filter) {
          delete jupytext.notebook_metadata_filter;
          if (jupytext.cell_metadata_filter === '-all')
            delete jupytext.cell_metadata_filter;
          return
        }

        jupytext.notebook_metadata_filter = '-all'
        if (jupytext.cell_metadata_filter === undefined)
          jupytext.cell_metadata_filter = '-all';
      }
    });

    palette?.addItem({
      command: "jupytext_metadata",
      rank: JUPYTEXT_FORMATS.length + 3,
      category: "Jupytext",
    });

    // Define file types
    app.docRegistry.addFileType({
      name: "myst",
      displayName: trans.__("MyST Markdown Notebook"),
      extensions: [".myst", ".mystnb", ".mnb"],
      icon: markdownIcon
    });

    app.docRegistry.addFileType({
      name: "r-markdown",
      displayName: trans.__("R Markdown Notebook"),
      // Extension file are transformed to lower case...
      extensions: [".rmd"],
      icon: markdownIcon
    });

    app.docRegistry.addFileType({
      name: "quarto",
      displayName: trans.__("Quarto Notebook"),
      extensions: [".qmd"],
      icon: markdownIcon
    });

    // the way to create the toolbar factory is different in JupyterLab 3 and 4
    let toolbarFactory
    if (! JLAB4) {
      toolbarFactory = notebookFactory.toolbarFactory
    } else {
      // primarily this block is copied/pasted from jlab4 code and specifically
      // jupyterlab/packages/notebook-extension/src/index.ts
      // inside the function `activateWidgetFactory` at line 1150 as of this writing
      //
      const FACTORY = 'Notebook';
      const PANEL_SETTINGS = '@jupyterlab/notebook-extension:panel';

      toolbarFactory = createToolbarFactory(
        toolbarRegistry,
        settingRegistry,
        FACTORY,
        PANEL_SETTINGS,
        translator
      )
    }
    // Duplicate notebook factory to apply it on Jupytext notebooks
    //   Mirror: https://github.com/jupyterlab/jupyterlab/blob/8a8c3752564f37493d4eb6b4c59008027fa83880/packages/notebook-extension/src/index.ts#L860
    const factory = new NotebookWidgetFactory({
      name: "Jupytext Notebook",
      label: trans.__("Jupytext Notebook"), // mandatory in jlab4 (not in jlab3)
      fileTypes: ["markdown", "myst", "r-markdown", "quarto", "julia", "python", "r"],
      modelName: notebookFactory.modelName ?? "notebook",
      preferKernel: notebookFactory.preferKernel ?? true,
      canStartKernel: notebookFactory.canStartKernel ?? true,
      rendermime,
      contentFactory,
      editorConfig: notebookFactory.editorConfig,
      notebookConfig: notebookFactory.notebookConfig,
      mimeTypeService: editorServices.mimeTypeService,
      // sessionDialogs: sessionContextDialogs,
      toolbarFactory: toolbarFactory,
      // translator?: ITranslator,
    } as NotebookWidgetFactory.IOptions<NotebookPanel>);
    app.docRegistry.addWidgetFactory(factory);

    // Register widget created with the new factory in the notebook tracker
    //   This is required to activate notebook commands (and therefore shortcuts)
    let id = 0; // The ID counter for notebook panels.
    const ft = app.docRegistry.getFileType("notebook");

    factory.widgetCreated.connect((sender, widget) => {
      // If the notebook panel does not have an ID, assign it one.
      widget.id = widget.id || `notebook-jupytext-${++id}`;

      // Set up the title icon
      widget.title.icon = ft?.icon;
      widget.title.iconClass = ft?.iconClass ?? "";
      widget.title.iconLabel = ft?.iconLabel ?? "";

      // Notify the widget tracker if restore data needs to update.
      widget.context.pathChanged.connect(() => {
        // Trick using private API
        // @ts-ignore
        void notebookTracker.save(widget);
      });
      // Add the notebook panel to the tracker.
      //   Trick using private API
      //   @ts-ignore
      void notebookTracker.add(widget);
    });
  },
};

export default extension;
