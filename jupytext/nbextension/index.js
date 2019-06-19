// A Jupyter notebook extension for Jupytext
// Refer to the documentation at
// https://github.com/mwouts/jupytext/blob/master/jupytext/nbextension/README.md

define([
    'jquery',
    'base/js/namespace',
    'base/js/events'
], function (
    $,
    Jupyter,
    events
) {
    "use strict";

    function checkSelectedJupytextFormat() {

        var formats = Jupyter.notebook.metadata.jupytext ? Jupyter.notebook.metadata.jupytext.formats : null;
        if (!formats)
            formats = 'none';

        if (Jupyter.notebook.metadata.language_info) {
            var script_ext = Jupyter.notebook.metadata.language_info.file_extension;

            if (formats === 'ipynb,' + script_ext.substring(1) + ':light')
                formats = 'ipynb,auto:light';
            else if (formats === 'ipynb,' + script_ext.substring(1) + ':percent')
                formats = 'ipynb,auto:percent';
            else if (formats === 'ipynb,' + script_ext.substring(1) + ':hydrogen')
                formats = 'ipynb,auto:hydrogen';
            else if (!['ipynb,auto:light', 'ipynb,auto:percent', 'ipynb,auto:hydrogen',
                'ipynb,md', 'ipynb,Rmd', 'none'].includes(formats))
                formats = 'custom';
        }

        console.log('Jupytext.formats=' + formats);

        $('[id^=jupytext_pair_]' + '>.fa').toggleClass('fa-check', false);
        $('#jupytext_pair_' + formats.replace(':', '_').replace(',', '_') + ' > .fa').toggleClass('fa-check', true);
    }

    function checkAutosave() {
        console.log('Jupyter.notebook.autosave_interval=' + Jupyter.notebook.autosave_interval);
        $('#autosave > .fa').toggleClass('fa-check', Jupyter.notebook.autosave_interval > 0);
    }

    function checkIncludeMetadata() {
        if (!Jupyter.notebook.metadata.jupytext || !Jupyter.notebook.metadata.jupytext.notebook_metadata_filter) {
            $('#jupytext_metadata > .fa').toggleClass('fa-check', true);
            $('#jupytext_metadata').remove('disabled');
            return;
        }
        if (Jupyter.notebook.metadata.jupytext.notebook_metadata_filter === "-all") {
            $('#jupytext_metadata > .fa').toggleClass('fa-check', false);
            $('#jupytext_metadata').remove('disabled');
            return;
        }

        // Custom metadata filter => we disable the option
        $('#jupytext_metadata > .fa').toggleClass('fa-check', true);
        $('#jupytext_metadata').addClass('disabled');
    }

    function onClickedJupytextPair(data) {
        var formats = $(this).data('formats');
        if (formats === 'custom') {
            alert("Please use the notebook metadata editor for this (Menu: Edit/Edit Notebook Metadata).");
            return;
        }
        if (formats === 'none') {
            if (!Jupyter.notebook.metadata.jupytext)
                return;
        } else if (Jupyter.notebook.metadata.jupytext && formats === Jupyter.notebook.metadata.jupytext.formats)
            formats = 'none';

        if (formats === 'none') {
            if (Jupyter.notebook.metadata.jupytext.formats)
                delete Jupyter.notebook.metadata.jupytext['formats'];
            if (Jupyter.notebook.metadata.jupytext === {})
                delete Jupyter.notebook.metadata['jupytext'];
        } else {
            if (!Jupyter.notebook.metadata.jupytext)
                Jupyter.notebook.metadata.jupytext = {};
            Jupyter.notebook.metadata.jupytext['formats'] = formats;
        }

        checkSelectedJupytextFormat();
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
                if (Jupyter.notebook.metadata.jupytext === {})
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
        checkSelectedJupytextFormat();
        checkAutosave();
        checkIncludeMetadata();
    }

    function jupytext_pair(formats, text, active) {
        return $('<li/>')
            .addClass(active ? null : 'disabled')
            .append($('<a/>')
                .attr('id', 'jupytext_pair_' + formats.replace(':', '_').replace(',', '_'))
                .text(text)
                .attr('title',
                    (formats === 'none') ? 'Jupytext not configured' :
                        (formats === 'custom' ? 'Custom Jupytext configuration' :
                            'jupytext.formats=' + formats))
                .data('formats', formats)
                .css('width', '280px')
                .attr('href', '#')
                .on('click', onClickedJupytextPair)
                .prepend($('<i/>').addClass('fa menu-icon pull-right'))
            );
    }

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

            $('#trust_notebook').before('<li id="jupytext_sub_menu"/>');
            $('#jupytext_sub_menu').addClass('dropdown-submenu').append(JupytextMenu).append(JupytextActions);
            JupytextActions.append(jupytext_link);
            JupytextActions.append($('<li/>').addClass('divider'));
            JupytextActions.append(toggle_autosave);
            JupytextActions.append($('<li/>').addClass('divider'));

            var notebook_extension = Jupyter.notebook.notebook_path.split('.').pop();
            var active = (notebook_extension === 'ipynb' || (notebook_extension !== 'md' && notebook_extension !== 'Rmd'));
            JupytextActions.append(jupytext_pair('ipynb,auto:light', 'Pair Notebook with light Script', active));
            JupytextActions.append(jupytext_pair('ipynb,auto:percent', 'Pair Notebook with percent Script', active));
            JupytextActions.append(jupytext_pair('ipynb,auto:hydrogen', 'Pair Notebook with Hydrogen Script', active));

            active = (notebook_extension === 'ipynb' || notebook_extension === 'md');
            JupytextActions.append(jupytext_pair('ipynb,md', 'Pair Notebook with Markdown', active));

            active = (notebook_extension === 'ipynb' || notebook_extension === 'Rmd');
            JupytextActions.append(jupytext_pair('ipynb,Rmd', 'Pair Notebook with R Markdown', active));

            JupytextActions.append(jupytext_pair('custom', 'Custom pairing', true));
            JupytextActions.append($('<li/>').addClass('divider'));
            JupytextActions.append(toggle_metadata);
            JupytextActions.append($('<li/>').addClass('divider'));
            JupytextActions.append(jupytext_pair('none', 'Unpair notebook', true));

            $('#jupytext_sub_menu').after('<li class="divider"/>');

            checkSelectedJupytextFormat();
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
