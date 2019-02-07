// A Jupyter notebook extension for Jupytext
// Refer to the documentation at https://github.com/mwouts/jupytext_nbextension

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

        function checkSelectedJupytextFormat() {

            var formats = Jupyter.notebook.metadata.jupytext ? Jupyter.notebook.metadata.jupytext.formats : null
            if (!formats)
                formats = 'none'

            if (Jupyter.notebook.metadata.language_info) {
                var script_ext = Jupyter.notebook.metadata.language_info.file_extension;

                if (formats == 'ipynb,' + script_ext.substring(1) + ':light')
                    formats = 'ipynb,auto:light'
                else if (formats == 'ipynb,' + script_ext.substring(1) + ':percent')
                    formats = 'ipynb,auto:percent'
                else if (formats == 'ipynb,' + script_ext.substring(1) + ':hydrogen')
                    formats = 'ipynb,auto:hydrogen'
                else if (!['ipynb,auto:light', 'ipynb,auto:percent', 'ipynb,auto:hydrogen',
                    'ipynb,md', 'ipynb,Rmd', 'none'].includes(formats))
                    formats = 'custom'
            }

            console.log('Jupytext.formats=' + formats)

            $('[id^=jupytext_pair_]' + '>.fa').toggleClass('fa-check', false)
            $('#jupytext_pair_' + formats.replace(':', '_').replace(',', '_') + ' > .fa').toggleClass('fa-check', true)
        }

        function onClickedJupytextPair(data) {
            var formats = $(this).data('formats')
            if (formats == 'custom') {
                alert("Please use the notebook metadata editor for this (Menu: Edit/Edit Notebook Metadata).")
                return
            }
            if (formats == 'none') {
                if (!Jupyter.notebook.metadata.jupytext)
                    return
            }
            else if (Jupyter.notebook.metadata.jupytext && formats == Jupyter.notebook.metadata.jupytext.formats)
                return

            if (formats == 'none') {
                if (Jupyter.notebook.metadata.jupytext.formats)
                    delete Jupyter.notebook.metadata.jupytext['formats'];
                if (Jupyter.notebook.metadata.jupytext == {})
                    delete Jupyter.notebook.metadata['jupytext']
            }
            else {
                if (!Jupyter.notebook.metadata.jupytext)
                    Jupyter.notebook.metadata.jupytext = {};
                Jupyter.notebook.metadata.jupytext['formats'] = formats
            }

            checkSelectedJupytextFormat();
            Jupyter.notebook.set_dirty();
        }

        var jupytext_menu = function () {
            if ($('#jupytext_menu').length == 0) {

                var JupytextMenu = $('<a/>').attr('href', '#')
                    .addClass('dropdown-toogle')
                    .attr('data-toggle', 'dropdown')
                    .attr('aria-expanded', 'false')
                    .text('Jupytext')
                    .attr('title', 'Jupyter notebooks as Markdown documents, Julia, Python or R scripts')

                var JupytextActions = $('<ul/>')
                    .attr('id', 'jupytext_actions')
                    .addClass("dropdown-menu")                    

                function jupytext_pair(formats, text) {
                    return $('<li/>').append($('<a/>')
                        .attr('id', 'jupytext_pair_' + formats.replace(':', '_').replace(',', '_'))
                        .text(text)
                        .attr('title',
                            (formats == 'none') ? 'Jupytext not configured' :
                                (formats == 'custom' ? 'Custom Jupytext configuration' :
                                    'jupytext.formats=' + formats))
                        .data('formats', formats)
                        .css('width', '280px')
                        .attr('href', '#')
                        .on('click', onClickedJupytextPair)
                        .prepend($('<i/>').addClass('fa menu-icon pull-right'))
                    )
                };

                var jupytext_link = $('<li/>').append($('<a/>')
                    .text('Jupytext reference')
                    .attr('title', "Jupytext's documentation. Opens in a new window.")
                    .on('click', function () { window.open('https://jupytext.readthedocs.io/en/latest/') })
                    .prepend($('<i/>').addClass('pull-right')));

                $('#trust_notebook').before('<li id="jupytext_sub_menu"/>');
                $('#jupytext_sub_menu').addClass('dropdown-submenu').append(JupytextMenu).append(JupytextActions)
                JupytextActions.append(jupytext_link)
                JupytextActions.append($('<li/>').addClass('divider'))
                JupytextActions.append(jupytext_pair('ipynb,auto:light', 'Pair Notebook with light Script'))
                JupytextActions.append(jupytext_pair('ipynb,auto:percent', 'Pair Notebook with percent Script'))
                JupytextActions.append(jupytext_pair('ipynb,auto:hydrogen', 'Pair Notebook with hydrogen Script'))
                JupytextActions.append(jupytext_pair('ipynb,md', 'Pair Notebook with Markdown'))
                JupytextActions.append(jupytext_pair('ipynb,Rmd', 'Pair Notebook with R Markdown'))
                JupytextActions.append(jupytext_pair('custom', 'Custom pairing'))
                JupytextActions.append($('<li/>').addClass('divider'))
                JupytextActions.append(jupytext_pair('none', 'Unpair notebook'))

                $('#jupytext_sub_menu').after('<li class="divider"/>');

                checkSelectedJupytextFormat();
            };
        }

        var load_ipython_extension = function () {
            // Wait for the notebook to be fully loaded
            if (Jupyter.notebook !== undefined && Jupyter.notebook._fully_loaded) {
                // this tests if the notebook is fully loaded
                console.log("[jupytext] Notebook fully loaded -- jupytext extension initialized ")
                jupytext_menu();
            } else {
                console.log("[jupytext] Waiting for notebook availability")
                events.on("notebook_loaded.Notebook", function () {
                    console.log("[jupytext] jupytext initialized (via notebook_loaded)")
                    jupytext_menu();
                })
            }
        };

        return {
            load_ipython_extension: load_ipython_extension
        };
    });
