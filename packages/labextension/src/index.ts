import { JupyterFrontEnd, JupyterFrontEndPlugin } from "@jupyterlab/application";

import { ICommandPalette } from "@jupyterlab/apputils";

import { INotebookTracker } from "@jupyterlab/notebook";

import * as nbformat from "@jupyterlab/nbformat";

interface JupytextRepresentation {
  format_name: string;
  extension: string;
};

interface JupytextSection {
  formats?: string;
  notebook_metadata_filter?: string;
  cell_metadata_filter?: string;
  text_representation?: JupytextRepresentation
};

const JUPYTEXT_FORMATS = [
  {
    format: "ipynb",
    label: "Pair Notebook with ipynb document"
  },
    {
    format: "auto:light",
    label: "Pair Notebook with light Script"
  },
  {
    format: "auto:percent",
    label: "Pair Notebook with percent Script"
  },
  {
    format: "auto:hydrogen",
    label: "Pair Notebook with Hydrogen Script"
  },
  {
    format: "auto:nomarker",
    label: "Pair Notebook with nomarker Script"
  },
  {
    format: "md",
    label: "Pair Notebook with Markdown"
  },
  {
    format: "md:myst",
    label: "Pair Notebook with MyST Markdown"
  },
  {
    format: "Rmd",
    label: "Pair Notebook with R Markdown"
  },
  {
    format: "qmd",
    label: "Pair Notebook with Quarto (qmd)"
  },
  {
    format: "custom",
    label: "Custom pairing"
  },
  {
    format: "none",
    label: "Unpair Notebook"
  }
];

function get_jupytext_formats(notebook_tracker: INotebookTracker): Array<string> {
  if (!notebook_tracker.currentWidget) return [];

  if (!notebook_tracker.currentWidget.context.model.metadata.has("jupytext"))
    return [];

  const jupytext: JupytextSection = (notebook_tracker.currentWidget.context.model.metadata.get(
      "jupytext"
  ) as unknown) as JupytextSection;
  let formats: Array<string> = jupytext && jupytext.formats ? jupytext.formats.split(',') : [];
  return formats.filter(function (fmt) {
    return fmt !== '';
  });
}

function get_selected_formats(notebook_tracker: INotebookTracker): Array<string> {
  if (!notebook_tracker.currentWidget) return [];

  let formats = get_jupytext_formats(notebook_tracker);

  const lang = notebook_tracker.currentWidget.context.model.metadata.get(
      "language_info"
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

  notebook_extension = ['ipynb', 'md', 'Rmd', 'qmd'].indexOf(notebook_extension) == -1 ? 'auto' : notebook_extension;
  for (const i in formats) {
    const ext = formats[i].split(':')[0];
    if (ext == notebook_extension)
      return formats;
  }

  // the notebook extension was not found among the formats
  if (['ipynb', 'md', 'Rmd', 'qmd'].indexOf(notebook_extension) != -1)
    formats.push(notebook_extension);
  else {
    let format_name = 'light';
    if (notebook_tracker.currentWidget.context.model.metadata.has("jupytext")) {
      const jupytext: JupytextSection = (notebook_tracker.currentWidget.context.model.metadata.get(
          "jupytext"
      ) as unknown) as JupytextSection;

      if (jupytext && jupytext.text_representation && jupytext.text_representation.format_name)
        format_name = jupytext.text_representation.format_name;
    }
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
  requires: [ICommandPalette, INotebookTracker],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    notebook_tracker: INotebookTracker
  ) => {
    console.log("JupyterLab extension jupyterlab-jupytext is activated");

    // Jupytext formats
    JUPYTEXT_FORMATS.forEach((args, rank) => {
      const format: string = args["format"];
      const command: string = "jupytext:" + format;
      app.commands.addCommand(command, {
        label: args["label"],
        isToggled: () => {
          if (!notebook_tracker.currentWidget) return false;
          const jupytext_formats = get_selected_formats(notebook_tracker);

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
            if (!notebook_tracker.currentWidget)
                return false;

            const notebook_extension: string | undefined = notebook_tracker.currentWidget.context.path.split('.').pop();
            if (format === notebook_extension)
                return false;

            if (format === 'none') {
                const formats = get_selected_formats(notebook_tracker);
                return formats.length > 1;
            }

            return true;
        },
        execute: () => {
            const jupytext: JupytextSection = (notebook_tracker.currentWidget.context.model.metadata.get(
            "jupytext"
          ) as unknown) as JupytextSection;
          let formats: Array<string> = get_selected_formats(notebook_tracker);

          // Toggle the selected format
          console.log("Jupytext: executing command=" + command);
          if (format == "custom") {
            alert(
              "Please edit the notebook metadata directly if you wish a custom configuration."
            );
            return;
          }
            // Toggle the selected format
            let notebook_extension: string = notebook_tracker.currentWidget.context.path.split('.').pop();
            notebook_extension = ['ipynb', 'md', 'Rmd', 'qmd'].indexOf(notebook_extension) == -1 ? 'auto' : notebook_extension;

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
            if (
              !notebook_tracker.currentWidget.context.model.metadata.has(
                "jupytext"
              )
            )
              return;

            if (jupytext.formats) {
              delete jupytext.formats;
            }

            if (Object.keys(jupytext).length == 0)
              notebook_tracker.currentWidget.context.model.metadata.delete(
                "jupytext"
              );
            return;
          }

          // set the desired format
          if (jupytext) jupytext.formats = formats.join();
          else
            notebook_tracker.currentWidget.context.model.metadata.set(
              "jupytext",
              { formats: formats.join() });
      }
      });

      console.log("Jupytext: adding command=" + command + " with rank=" + (rank + 1));
      palette.addItem({ command, rank: rank + 2, category: "Jupytext" });
    });

    // Jupytext's documentation
    palette.addItem({
      args: {
        text: "Jupytext Reference",
        url: "https://jupytext.readthedocs.io/en/latest/"
      },
      command: "help:open",
      category: "Jupytext",
      rank: 0
    });

    palette.addItem({
      args: {
        text: "Jupytext FAQ",
        url: "https://jupytext.readthedocs.io/en/latest/faq.html"
      },
      command: "help:open",
      category: "Jupytext",
      rank: 1
    });

    // Metadata in text representation
    app.commands.addCommand("jupytext_metadata", {
      label: "Include Metadata",
      isToggled: () => {
        if (!notebook_tracker.currentWidget)
          return false;

        if (!notebook_tracker.currentWidget.context.model.metadata.has("jupytext"))
          return false;

        const jupytext: JupytextSection = (notebook_tracker.currentWidget.context.model.metadata.get("jupytext") as unknown) as JupytextSection;

        if (jupytext.notebook_metadata_filter === '-all')
          return false;

        return true;
      },
      isEnabled: () => {
        if (!notebook_tracker.currentWidget)
          return false;

        if (!notebook_tracker.currentWidget.context.model.metadata.has("jupytext"))
          return false;

        const jupytext: JupytextSection = (notebook_tracker.currentWidget.context.model.metadata.get("jupytext") as unknown) as JupytextSection;

        if (jupytext.notebook_metadata_filter === undefined)
          return true;

        if (jupytext.notebook_metadata_filter === '-all')
          return true;

        return false;
      },
      execute: () => {
        console.log("Jupytext: toggling YAML header");
        if (!notebook_tracker.currentWidget)
          return;

        if (!notebook_tracker.currentWidget.context.model.metadata.has("jupytext"))
          return;

        const jupytext: JupytextSection = (notebook_tracker.currentWidget.context.model.metadata.get("jupytext") as unknown) as JupytextSection;

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

    palette.addItem({ command: "jupytext_metadata", rank: JUPYTEXT_FORMATS.length + 3, category: "Jupytext" });
  }
};

export default extension;
