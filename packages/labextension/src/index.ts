import { JupyterFrontEnd, JupyterFrontEndPlugin } from "@jupyterlab/application";

import { ICommandPalette } from "@jupyterlab/apputils";

import { INotebookTracker } from "@jupyterlab/notebook";

import { nbformat } from "@jupyterlab/coreutils";

interface JupytextSection {
  formats?: string;
  notebook_metadata_filter?: string;
  cell_metadata_filter?: string;
}

const JUPYTEXT_FORMATS = [
  {
    formats: "ipynb,auto:light",
    label: "Pair Notebook with light Script"
  },
  {
    formats: "ipynb,auto:percent",
    label: "Pair Notebook with percent Script"
  },
  {
    formats: "ipynb,auto:hydrogen",
    label: "Pair Notebook with Hydrogen Script"
  },
  {
    formats: "ipynb,md",
    label: "Pair Notebook with Markdown"
  },
  {
    formats: "ipynb,Rmd",
    label: "Pair Notebook with R Markdown"
  },
  {
    formats: "custom",
    label: "Custom pairing"
  },
  {
    formats: "none",
    label: "Unpair Notebook"
  }
];

function get_selected_format(notebook_tracker: INotebookTracker): string {
  if (!notebook_tracker.currentWidget) return null;

  if (
    !notebook_tracker.currentWidget.context.model.metadata.has(
      "jupytext"
    )
  )
    return "none";

  const jupytext: JupytextSection = (notebook_tracker.currentWidget.context.model.metadata.get(
    "jupytext"
  ) as unknown) as JupytextSection;
  if (!jupytext.formats) return "none";

  const lang = notebook_tracker.currentWidget.context.model.metadata.get(
    "language_info"
  ) as nbformat.ILanguageInfoMetadata;
  return lang
    ? jupytext.formats.replace(
      "," + lang.file_extension.substring(1) + ":",
      ",auto:"
    )
    : jupytext.formats;
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
      const formats: string = args["formats"];
      const command: string = "jupytext:" + formats;
      app.commands.addCommand(command, {
        label: args["label"],
        isToggled: () => {
          if (!notebook_tracker.currentWidget) return false;
          const jupytext_formats = get_selected_format(notebook_tracker)

          if (formats == "custom")
            return (
              jupytext_formats &&
              [
                "none",
                "ipynb,auto:light",
                "ipynb,auto:percent",
                "ipynb,auto:hydrogen",
                "ipynb,md",
                "ipynb,Rmd"
              ].indexOf(jupytext_formats) < 0
            );

          return jupytext_formats == formats;
        },
        isEnabled: () => {
          if (!notebook_tracker.currentWidget)
              return false;
          if (formats == "custom" || formats == "none")
            return true;
          const notebook_extension: string = notebook_tracker.currentWidget.context.path.split('.').pop();
          if (notebook_extension == "ipynb")
            return true;
          if (notebook_extension == "md")
            return formats == "ipynb,md";
          if (notebook_extension == "Rmd")
            return formats == "ipynb,Rmd";
          return formats != "ipynb,md" && formats != "ipynb,Rmd";
        },
        execute: () => {
          const jupytext: JupytextSection = (notebook_tracker.currentWidget.context.model.metadata.get(
            "jupytext"
          ) as unknown) as JupytextSection;
          const jupytext_formats = get_selected_format(notebook_tracker);
          const target_format = jupytext_formats === formats ? "none": formats;
          console.log("Jupytext: executing command=" + command);
          if (formats == "custom") {
            alert(
              "Please edit the notebook metadata directly if you wish a custom configuration."
            );
            return;
          }

          if (target_format == "none") {
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
          if (jupytext) jupytext.formats = target_format;
          else
            notebook_tracker.currentWidget.context.model.metadata.set(
              "jupytext",
              { target_format }
            );
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
