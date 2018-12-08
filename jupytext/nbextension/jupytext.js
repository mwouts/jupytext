/* Jupyter notebook extension that allows to configure Jupytext

Inspired from the toc2 extension at https://github.com/ipython-contrib/jupyter_contrib_nbextensions

Test the extension in a Jupyter notebook by adding two cells:

```python
# 1. Install the extension
import notebook.nbextensions
notebook.nbextensions.install_nbextension('jupytext.js', user=True)
# Or, more convenient for developing: replace the installed file with a symbolic link to this one
```

```python
# 2. Load the extension
%%javascript
Jupyter.utils.load_extensions('jupytext')
```

*/

define([
    'require',
    'jquery',
    'base/js/namespace',
    'base/js/events',
], function (
    requirejs,
    $,
    Jupyter,
    events
) {
        "use strict";

        var show_notebook_settings_dialog = function () {

            var modal = $('<div class="modal fade" role="dialog"/>');
            var dialog_content = $("<div/>")
                .addClass("modal-content")
                .appendTo($('<div class="modal-dialog">').appendTo(modal));
            $('<div class="modal-header">')
                .append('<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>')
                .append('<h3 class="modal-title">Jupytext configuration for the current notebook</h3>')
                .on('mousedown', function () { $('.modal').draggable({ handle: '.modal-header' }); })
                .appendTo(dialog_content);

            console.log("comment_magics status", Jupyter.notebook.metadata.jupytext.comment_magics);
            var comment_magics_default = (!("comment_magics" in Jupyter.notebook.metadata.jupytext)) ? "checked" : "";
            var comment_magics_true = (Jupyter.notebook.metadata.jupytext.comment_magics === true) ? "checked" : "";
            var comment_magics_false = (Jupyter.notebook.metadata.jupytext.comment_magics === false) ? "checked" : "";

            $('<div>')
                .addClass('modal-body')
                .append('<h3>Notebook formats</h3>')
                .append(`<input type="checkbox" id="jupytext-formats-ipynb"/> <label>Jupyter notebook (.ipynb)</label><br>
                         <input type="checkbox" id="jupytext-formats-script"/> <label>Python script (.py)</label> with format
                            <select id="jupytext-formats-script-format">
                                <option value="light">light</option>
                                <option value="percent">percent</option>
                                <option value="spin">spin (.R only)</option>
                                <option value="sphinx">sphinx (.py only)</option>
                            </select><br>
                    <input type="checkbox" id="jupytext-formats-markdown"/> <label>Markdown document (.md)</label> <br>
                    <input type="checkbox" id="jupytext-formats-Rmarkdown"/> <label>R Markdown notebook (.Rmd)</label>`)
                // TODO: Replace 'Python script (.py)' above with a value that is taken from Jupyter.notebook.metadata.language_info
                // TODO (later): spin/sphinx only available for .R or .py formats
                // TODO: Set the initial values above from Jupyter.notebook.metadata.jupytext.formats
                // TODO: Create or update Jupyter.notebook.metadata.jupytext.formats to match the selected values

                .append(`<h3>Jupyter magic commands</h3>
                    <input type="radio" id="jupytext-comment-magics-default" name="jupytext-comment-magics" value="default" ${comment_magics_default}>Default (commented in scripts and Rmd)
                    <input type="radio" id="jupytext-comment-magics-true" name="jupytext-comment-magics" value="true" ${comment_magics_true}>Commented
                    <input type="radio" id="jupytext-comment-magics-false" name="jupytext-comment-magics" value="false" ${comment_magics_false}>Not commented`)
                // TODO: Create, update or delete Jupyter.notebook.metadata.jupytext.comment_magics to match the selected value

                .append('<h3>Metadata filters</h3>')
                .append('<h4>Notebook metadata</h4>')
                // TODO (Later): Choose between default/all/none/checklist filled with keys of Jupyter.notebook.metadata
                .append(`<input type="radio" name="jupytext-metadata-filter-notebook" value="default" checked="true">Default
                <input type="radio" name="jupytext-metadata-filter-notebook" value="none">None
                <input type="radio" name="jupytext-metadata-filter-notebook" value="all">All`)
                .append('<h4>Cell metadata</h4>')
                // TODO (Later): Choose between default/all/none/checklist filled with keys of metatadata in one of Jupyter.notebook.cells
                .append(`<input type="radio" name="jupytext-metadata-filter-cell" value="default" checked="true">Default:
                <input type="radio" name="jupytext-metadata-filter-cell" value="none">None
                <input type="radio" name="jupytext-metadata-filter-cell" value="all">All`)

                .append('<h3>Debug: display jupytext metadata</h3>')
                .append($('<div id="jupytext-metadata"/>').html(JSON.stringify(Jupyter.notebook.metadata.jupytext)))

                .appendTo(dialog_content);
            $('<div class="modal-footer">')
                .append('<button class="btn btn-default btn-sm btn-primary" data-dismiss="modal">Ok</button>')
                .appendTo(dialog_content);


            // focus button on open
            modal.on('shown.bs.modal', function () {
                setTimeout(function () {
                    dialog_content.find('.modal-footer button').last().focus();
                    $("#jupytext-formats-ipynb").on("change", function () {
                        console.log("jupytext-formats-ipynb changed");
                    });
                    // see this tutorial for selected value https://www.codexworld.com/how-to/get-text-value-of-selected-option-using-jquery/
                    $('#jupytext-dropdownList').on('change', function () {
                        var optionValue = $(this).val();
                        alert(optionValue)
                        //var optionText = $('#dropdownList option[value="'+optionValue+'"]').text();
                        // var optionText = $("#dropdownList option:selected").text();
                        // alert("Selected Option Text: "+optionText);
                    });
                }, 0);
            });

            return modal.modal({ backdrop: 'static' });
        };

        var jupytext_button = function () {
            if (!Jupyter.toolbar) {
                $([Jupyter.events]).on("app_initialized.NotebookApp", jupytext_button);
                return;
            }
            if ($("#jupytext_button").length === 0) {
                $(IPython.toolbar.add_buttons_group([
                    Jupyter.keyboard_manager.actions.register({
                        'help': 'Jupytext',
                        'icon': 'fa-clone', // fa-wrench fa-clone fa-file-alt fa-file-export fa-object-group fa-readme
                        'handler': show_notebook_settings_dialog,
                    }, 'jupytext-button', 'jupytext')
                ])).find('.btn').attr('id', 'jupytext_button');
            }
        };

        var jupytext_init = function () {
            jupytext_button();
        }

        var load_ipython_extension = function () {
            // Wait for the notebook to be fully loaded
            if (Jupyter.notebook !== undefined && Jupyter.notebook._fully_loaded) {
                // this tests if the notebook is fully loaded
                console.log("[jupytext] Notebook fully loaded -- jupytext extension initialized ")
                jupytext_init();
            } else {
                console.log("[jupytext] Waiting for notebook availability")
                events.on("notebook_loaded.Notebook", function () {
                    console.log("[jupytext] jupytext initialized (via notebook_loaded)")
                    jupytext_init();
                })
            }
        };

        return {
            load_ipython_extension: load_ipython_extension
        };
    });
