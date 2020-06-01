// A Jupyter notebook extension for Jupytext
// Refer to the documentation at
// https://github.com/mwouts/jupytext/blob/master/jupytext/nbextension/README.md

// The most convenient way to edit this file is to edit the version installed by pip at
// share/jupyter/nbextensions/jupytext

define([
    'jquery',
    'base/js/namespace',
    'base/js/dialog',
    'base/js/events',
    'base/js/utils',
], function (
    $,
    Jupyter,
    dialog,
    events,
    utils
) {
    "use strict";

    function getSelectedJupytextFormats() {
        var str_formats = Jupyter.notebook.metadata.jupytext && Jupyter.notebook.metadata.jupytext.formats ? Jupyter.notebook.metadata.jupytext.formats : '';
        var unfiltered_formats = str_formats.split(',');
        var formats = [];
        for (var i in unfiltered_formats) {
            var fmt = unfiltered_formats[i];
            if (fmt)
                formats.push(fmt);
        }

        if (Jupyter.notebook.metadata.language_info) {
            var script_ext = Jupyter.notebook.metadata.language_info.file_extension.substring(1);
            formats = formats.map(function (fmt) {
                if (fmt === script_ext)
                    return 'auto:light';
                return fmt.replace(script_ext + ':', 'auto:');
            });
        }

        var notebook_extension = Jupyter.notebook.notebook_path.split('.').pop();
        notebook_extension = ['ipynb', 'md', 'Rmd'].indexOf(notebook_extension) == -1 ? 'auto' : notebook_extension;
        for (var i in formats) {
            var ext = formats[i].split(':')[0];
            if (ext == notebook_extension)
                return formats;
        }

        // the notebook extension was not found among the formats
        if (['ipynb', 'md', 'Rmd'].indexOf(notebook_extension) != -1)
            formats.push(notebook_extension);
        else {
            var format_name = Jupyter.notebook.metadata.jupytext && Jupyter.notebook.metadata.jupytext.text_representation
                && Jupyter.notebook.metadata.jupytext.text_representation.format_name ?
                Jupyter.notebook.metadata.jupytext.text_representation.format_name : 'light';
            formats.push('auto:' + format_name);
        }
        return formats;
    }

    function checkSelectedJupytextFormats() {

        var formats = getSelectedJupytextFormats();
        console.log('Jupytext.formats=' + formats.join());

        $('[id^=jupytext_pair_]' + '>.fa').toggleClass('fa-check', false);
        for (var i in formats) {
            var fmt = formats[i];
            $('#jupytext_pair_' + fmt.replace(':', '_') + ' > .fa').toggleClass('fa-check', true);

            // any custom format?
            if (['ipynb', 'auto:light', 'auto:percent', 'auto:hydrogen', 'auto:nomarker', 'md', 'Rmd', 'md:myst'].indexOf(fmt) == -1)
                $('#jupytext_pair_custom' + ' > .fa').toggleClass('fa-check', true);
        }

        // just one format?
        if (formats.length === 1)
            $('#jupytext_pair_none').parent().addClass('disabled');
        else
            $('#jupytext_pair_none').parent().removeClass('disabled');
    }

    function checkAutosave() {
        console.log('Jupyter.notebook.autosave_interval=' + Jupyter.notebook.autosave_interval);
        $('#autosave > .fa').toggleClass('fa-check', Jupyter.notebook.autosave_interval > 0);
    }

    function checkIncludeMetadata() {
        if (!Jupyter.notebook.metadata.jupytext || !Jupyter.notebook.metadata.jupytext.notebook_metadata_filter) {
            $('#jupytext_metadata > .fa').toggleClass('fa-check', true);
            $('#jupytext_metadata').parent().removeClass('disabled');
            return;
        }
        if (Jupyter.notebook.metadata.jupytext.notebook_metadata_filter === "-all") {
            $('#jupytext_metadata > .fa').toggleClass('fa-check', false);
            $('#jupytext_metadata').parent().removeClass('disabled');
            return;
        }
        // Custom metadata filter => we disable the option
        $('#jupytext_metadata > .fa').toggleClass('fa-check', true);
        $('#jupytext_metadata').parent().addClass('disabled');
    }

    function onClickedJupytextPair(data) {
        if (!Jupyter.notebook.notebook_path)
            return;
        var format = $(this).data('format');
        if (format === 'custom') {
            alert("Please use the notebook metadata editor for this (Menu: Edit/Edit Notebook Metadata).");
            return;
        }
        var formats = getSelectedJupytextFormats();
        var notebook_extension = Jupyter.notebook.notebook_path.split('.').pop();
        notebook_extension = ['ipynb', 'md', 'Rmd'].indexOf(notebook_extension) == -1 ? 'auto' : notebook_extension;

        // Toggle the selected format
        var index = formats.indexOf(format);
        if (format === 'none') {
            // Only keep one format - one that matches the current extension
            for (var i in formats) {
                var fmt = formats[i];
                if (fmt.split(':')[0] === notebook_extension) {
                    formats = [fmt];
                    break;
                }
            }
        }
        else if (index != -1) {
            formats.splice(index, 1);

            // The current file extension can't be unpaired
            var ext_found = false;
            for (var i in formats) {
                var fmt = formats[i];
                if (fmt.split(':')[0] === notebook_extension) {
                    ext_found = true;
                    break;
                }
            }

            if (!ext_found)
                return;
        } else {
            // We can't have the same extension multiple times
            var new_formats = [];
            for (var i in formats) {
                var fmt = formats[i];
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
            else {
                if (Jupyter.notebook.metadata.jupytext && Jupyter.notebook.metadata.jupytext.text_representation) {
                    var format_name = formats[0].split(':')[1];
                    Jupyter.notebook.metadata.jupytext.text_representation.format_name = format_name;
                    formats = [];
                }
            }
        }

        if (formats.length === 0) {
            if (!Jupyter.notebook.metadata.jupytext)
                return;
            if (Jupyter.notebook.metadata.jupytext.formats)
                delete Jupyter.notebook.metadata.jupytext['formats'];
            if (Object.keys(Jupyter.notebook.metadata.jupytext).length === 0)
                delete Jupyter.notebook.metadata['jupytext'];
        } else {
            if (!Jupyter.notebook.metadata.jupytext)
                Jupyter.notebook.metadata.jupytext = {};
            Jupyter.notebook.metadata.jupytext['formats'] = formats.join();
        }

        checkSelectedJupytextFormats();
        Jupyter.notebook.set_dirty();
    }

    function onToggleMetadata() {
        if (!Jupyter.notebook.metadata.jupytext) {
            Jupyter.notebook.metadata.jupytext = {
                "notebook_metadata_filter": "-all",
                "cell_metadata_filter": "-all"
            };
        } else {
            if (!Jupyter.notebook.metadata.jupytext.notebook_metadata_filter) {
                Jupyter.notebook.metadata.jupytext.notebook_metadata_filter = "-all";
                if (!Jupyter.notebook.metadata.jupytext.cell_metadata_filter)
                    Jupyter.notebook.metadata.jupytext.cell_metadata_filter = "-all";
            } else {
                delete Jupyter.notebook.metadata.jupytext['notebook_metadata_filter'];
                if (Jupyter.notebook.metadata.jupytext.cell_metadata_filter === "-all")
                    delete Jupyter.notebook.metadata.jupytext['cell_metadata_filter'];
                if (Object.keys(Jupyter.notebook.metadata.jupytext).length === 0)
                    delete Jupyter.notebook.metadata['jupytext'];
            }
        }

        checkIncludeMetadata();
        Jupyter.notebook.set_dirty();
    }

    function onToggleAutosave() {
        Jupyter.notebook.autosave_interval = Jupyter.notebook.autosave_interval > 0 ? 0 : 120000;
        checkAutosave();
    }

    function updateJupytextMenu() {
        checkSelectedJupytextFormats();
        checkAutosave();
        checkIncludeMetadata();
    }

    function jupytext_pair(format, text, active) {
        return $('<li/>')
            .addClass(typeof active === 'undefined' || active ? null : 'disabled')
            .append($('<a/>')
                .attr('id', 'jupytext_pair_' + format.replace(':', '_'))
                .text(text)
                .attr('title', format === 'custom' ? 'Custom Jupytext configuration' : 'jupytext.format=' + format)
                .data('format', format)
                .css('width', '280px')
                .attr('href', '#')
                .on('click', onClickedJupytextPair)
                .prepend($('<i/>').addClass('fa menu-icon pull-right'))
            );
    }

    function new_text_notebook(ext = '.md') {
        // Differences with KernelSelector.prototype.new_notebook from
        // https://github.com/jupyter/notebook/blob/
        // 6e9256b0641a85baf664e846515085bac2c082a3/notebook/static/notebook/js/kernelselector.js
        // - added ext argument
        // - kernel_name is the currently selected one
        // - "that" replaced with Jupyter

        var w = window.open('', IPython._target);
        // Create a new notebook in the same path as the current
        // notebook's path.
        var parent = utils.url_path_split(Jupyter.notebook.notebook_path)[0];
        Jupyter.notebook.contents.new_untitled(parent, { type: "notebook", ext: ext }).then(
            function (data) {
                var url = utils.url_path_join(
                    Jupyter.notebook.base_url, 'notebooks',
                    utils.encode_uri_components(data.path)
                );
                url += "?kernel_name=" + Jupyter.notebook.metadata.kernelspec.name;
                w.location = url;
            },
            function (error) {
                w.close();
                dialog.modal({
                    title: i18n.msg._('Creating Notebook Failed'),
                    body: i18n.msg.sprintf(i18n.msg._("The error was: %s"), error.message),
                    buttons: { 'OK': { 'class': 'btn-primary' } }
                });
            }
        );
    };

    function text_notebook_entry(title, ext = null) {
        const new_script_notebook_id = 'new_notebook_' + ext.replace('.', '').replace(':', '_');
        return $('<li/>')
            .append($('<a/>')
                .attr('id', new_script_notebook_id)
                .text(title)
                .attr('title', title)
                .data('ext', ext)
                .css('width', '280px')
                .attr('href', '#')
                .on('click', onClickedTextNotebook)
                .prepend($('<i/>').addClass('fa menu-icon pull-right'))
            );
    };

    function onClickedTextNotebook(data) {
        const ext = $(this).data('ext');
        if (ext) { new_text_notebook(ext); };
    };

    function updateNewScriptNotebookMenu() {
        var format_name;
        for (format_name of ['light', 'percent', 'hydrogen', 'nomarker']) {
            const new_script_notebook_menu = $('#new_notebook_auto_' + format_name);
            if (Jupyter.notebook.metadata.language_info) {
                var script_ext = Jupyter.notebook.metadata.language_info.file_extension + ':' + format_name;
                var language_name = Jupyter.notebook.metadata.language_info.name;
                language_name = language_name.charAt(0).toUpperCase() + language_name.slice(1);
                var title = language_name + ' Script in ' + format_name + ' format';
                new_script_notebook_menu.parent().removeClass('disabled');
                new_script_notebook_menu.data('ext', script_ext);
                new_script_notebook_menu.attr('title', title);
                new_script_notebook_menu.text(title);
            } else {
                new_script_notebook_menu.parent().addClass('disabled');
                new_script_notebook_menu.data('ext', null);
            }
            ;
        }
        ;
    };

    var jupytext_menu = function () {
        if ($('#jupytext_menu').length === 0) {

            var JupytextMenu = $('<a/>').attr('href', '#')
                .addClass('dropdown-toogle')
                .attr('data-toggle', 'dropdown')
                .attr('aria-expanded', 'false')
                .text('Jupytext')
                .attr('title', 'Jupyter notebooks as Markdown documents, Julia, Python or R scripts')
                .on('mouseover', updateJupytextMenu);

            var JupytextActions = $('<ul/>')
                .attr('id', 'jupytext_actions')
                .addClass("dropdown-menu");

            var jupytext_link = $('<li/>').append($('<a/>')
                .text('Jupytext reference')
                .attr('title', "Jupytext's documentation. Opens in a new window.")
                .on('click', function () {
                    window.open('https://jupytext.readthedocs.io/en/latest/')
                })
                .prepend($('<i/>').addClass('pull-right')));

            var jupytext_faq = $('<li/>').append($('<a/>')
                .text('Jupytext FAQ')
                .attr('title', "Frequently Asked Questions. Opens in a new window.")
                .on('click', function () {
                    window.open('https://jupytext.readthedocs.io/en/latest/faq.html')
                })
                .prepend($('<i/>').addClass('pull-right')));

            var toggle_autosave = $("<li/>").append(
                $("<a/>")
                    .attr("id", "autosave")
                    .text("Autosave notebook")
                    .attr("title", "Toggle autosave for this notebook")
                    .on("click", onToggleAutosave)
                    .prepend($("<i/>").addClass("fa menu-icon pull-right"))
            );

            var toggle_metadata = $("<li/>").append(
                $("<a/>")
                    .attr("id", "jupytext_metadata")
                    .text("Include metadata")
                    .attr("title", "Include notebook and cell metadata in the text file")
                    .on("click", onToggleMetadata)
                    .prepend($("<i/>").addClass("fa menu-icon pull-right"))
            );

            // New Text Notebook menu
            var NewTextNotebook = $('<a/>').attr('href', '#')
                .addClass('dropdown-toogle')
                .attr('data-toggle', 'dropdown')
                .attr('aria-expanded', 'false')
                .text('New Text Notebook')
                .attr('title', 'New Notebook saved as a text file')
                .on('mouseover', updateNewScriptNotebookMenu);

            var TextNotebooks = $('<ul/>')
                .attr('id', 'new_text_notebook_submenu')
                .addClass("dropdown-menu");

            $('#open_notebook').before('<li id="new_text_notebook"/>');
            $('#new_text_notebook').addClass('dropdown-submenu').append(NewTextNotebook).append(TextNotebooks);
            var format_name;
            for (format_name of ['light', 'percent', 'hydrogen', 'nomarker'])
                TextNotebooks.append(text_notebook_entry('Script in ' + format_name + ' format', '.auto:' + format_name));
            TextNotebooks.append($('<li/>').addClass('divider'));
            TextNotebooks.append(text_notebook_entry('Markdown', '.md'));
            TextNotebooks.append(text_notebook_entry('MyST Markdown', '.md:myst'));
            TextNotebooks.append($('<li/>').addClass('divider'));
            TextNotebooks.append(text_notebook_entry('R Markdown', '.Rmd'));

            // Jupytext menu
            $('#open_notebook').before('<li id="jupytext_sub_menu"/>');
            $('#jupytext_sub_menu').addClass('dropdown-submenu').append(JupytextMenu).append(JupytextActions);
            JupytextActions.append(jupytext_link);
            JupytextActions.append($('<li/>').addClass('divider'));
            JupytextActions.append(jupytext_faq);
            JupytextActions.append($('<li/>').addClass('divider'));
            JupytextActions.append(toggle_autosave);
            JupytextActions.append($('<li/>').addClass('divider'));

            var notebook_extension = Jupyter.notebook.notebook_path.split('.').pop();
            JupytextActions.append(jupytext_pair('ipynb', 'Pair Notebook with ipynb document', notebook_extension !== 'ipynb'));
            JupytextActions.append(jupytext_pair('auto:light', 'Pair Notebook with light Script'));
            JupytextActions.append(jupytext_pair('auto:percent', 'Pair Notebook with percent Script'));
            JupytextActions.append(jupytext_pair('auto:hydrogen', 'Pair Notebook with Hydrogen Script'));
            JupytextActions.append(jupytext_pair('auto:nomarker', 'Pair Notebook with nomarker Script'));
            JupytextActions.append(jupytext_pair('md', 'Pair Notebook with Markdown'));
            JupytextActions.append(jupytext_pair('md:myst', 'Pair Notebook with MyST Markdown'));
            JupytextActions.append(jupytext_pair('Rmd', 'Pair Notebook with R Markdown', notebook_extension !== 'Rmd'));
            JupytextActions.append(jupytext_pair('custom', 'Custom pairing'));
            JupytextActions.append($('<li/>').addClass('divider'));
            JupytextActions.append(toggle_metadata);
            JupytextActions.append($('<li/>').addClass('divider'));
            JupytextActions.append(jupytext_pair('none', 'Unpair notebook'));

            checkSelectedJupytextFormats();
            checkAutosave();
        }
    };

    var load_ipython_extension = function () {
        // Wait for the notebook to be fully loaded
        if (Jupyter.notebook !== undefined && Jupyter.notebook._fully_loaded) {
            // this tests if the notebook is fully loaded
            console.log("[jupytext] Notebook fully loaded -- jupytext extension initialized ");
            jupytext_menu();
        } else {
            console.log("[jupytext] Waiting for notebook availability");
            events.on("notebook_loaded.Notebook", function () {
                console.log("[jupytext] jupytext initialized (via notebook_loaded)");
                jupytext_menu();
            })
        }
    };

    return {
        load_ipython_extension: load_ipython_extension
    };
});
