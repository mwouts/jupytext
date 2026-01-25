"use strict";
(self["webpackChunkjupyterlab_jupytext"] = self["webpackChunkjupyterlab_jupytext"] || []).push([["lib_index_js"],{

/***/ "./lib/commands.js"
/*!*************************!*\
  !*** ./lib/commands.js ***!
  \*************************/
(__unused_webpack_module, exports, __webpack_require__) {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.isPairCommandToggled = isPairCommandToggled;
exports.isPairCommandEnabled = isPairCommandEnabled;
exports.executePairCommand = executePairCommand;
exports.isMetadataCommandToggled = isMetadataCommandToggled;
exports.isMetadataCommandEnabled = isMetadataCommandEnabled;
exports.executeMetadataCommand = executeMetadataCommand;
const apputils_1 = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
const tokens_1 = __webpack_require__(/*! ./tokens */ "./lib/tokens.js");
/**
 * Get Jupytext format of current widget if it is a text notebook
 */
function getWidgetJupytextFormats(notebookTracker) {
    const model = notebookTracker.currentWidget.context.model;
    const jupytext = model.getMetadata('jupytext');
    if (!jupytext) {
        return [];
    }
    const formats = jupytext.formats
        ? jupytext.formats.split(',')
        : [];
    return formats.filter((format) => {
        return format !== '';
    });
}
/**
 * Get file extension of current notebook widget
 */
function getNotebookFileExtension(notebookTracker) {
    let notebookFileExtension = notebookTracker.currentWidget.context.path.split('.').pop();
    if (!notebookFileExtension) {
        return '';
    }
    notebookFileExtension = tokens_1.LANGUAGE_INDEPENDENT_NOTEBOOK_EXTENSIONS.includes(notebookFileExtension)
        ? notebookFileExtension
        : 'auto';
    return notebookFileExtension;
}
/**
 * Get a list of all selected formats
 */
function getSelectedFormats(notebookTracker) {
    var _a;
    if (!notebookTracker.currentWidget) {
        return [];
    }
    let formats = getWidgetJupytextFormats(notebookTracker);
    const model = notebookTracker.currentWidget.context.model;
    const languageInfo = model.getMetadata('language_info');
    if (languageInfo && languageInfo.file_extension) {
        const scriptExt = languageInfo.file_extension.substring(1);
        formats = formats.map((format) => {
            // By default use percent format
            if (format === scriptExt) {
                return 'auto:percent';
            }
            // Replace language specific extension with auto
            return format.replace(`${scriptExt}:`, 'auto:');
        });
    }
    const notebookFileExtension = getNotebookFileExtension(notebookTracker);
    if (!notebookFileExtension) {
        return formats;
    }
    // Remove variant after : in format
    const formatExtensions = formats.map((format) => {
        return format.split(':')[0];
    });
    // If current notebook file extension in formats, return
    if (formatExtensions.includes(notebookFileExtension)) {
        return formats;
    }
    // When notebook loads for the first time, ipynb extension would not be
    // in the formats. Here we add it and return formats
    if (tokens_1.LANGUAGE_INDEPENDENT_NOTEBOOK_EXTENSIONS.includes(notebookFileExtension)) {
        formats.push(notebookFileExtension);
    }
    else {
        const model = notebookTracker.currentWidget.context.model;
        const jupytext = model.getMetadata('jupytext');
        const formatName = jupytext
            ? ((_a = jupytext === null || jupytext === void 0 ? void 0 : jupytext.text_representation) === null || _a === void 0 ? void 0 : _a.formatName) || 'percent'
            : 'percent';
        formats.push(`auto:${formatName}`);
    }
    return formats;
}
/**
 * Toggle pair command
 */
function isPairCommandToggled(format, notebookTracker) {
    if (!notebookTracker.currentWidget) {
        return false;
    }
    // Get selected formats on current widget
    const selectedFormats = getSelectedFormats(notebookTracker);
    if (format === 'custom') {
        for (const selectedFormat of selectedFormats) {
            if (!tokens_1.JUPYTEXT_FORMATS.includes(selectedFormat)) {
                return true;
            }
        }
        return false;
    }
    return selectedFormats.includes(format);
}
/**
 * Enable pair command
 */
function isPairCommandEnabled(format, notebookTracker) {
    if (!notebookTracker.currentWidget) {
        return false;
    }
    const notebookFileExtension = notebookTracker.currentWidget.context.path.split('.').pop();
    if (format === notebookFileExtension) {
        return false;
    }
    // Get selected formats on current widget
    const selectedFormats = getSelectedFormats(notebookTracker);
    if (format === 'none') {
        return selectedFormats.length > 1;
    }
    return true;
}
/**
 * Execute pair command
 */
function executePairCommand(command, format, notebookTracker, trans) {
    if (!notebookTracker.currentWidget) {
        return;
    }
    const model = notebookTracker.currentWidget.context.model;
    let jupytext = model.getMetadata('jupytext');
    // Get selected formats on current widget
    let selectedFormats = getSelectedFormats(notebookTracker);
    // Toggle the selected format
    console.debug('Jupytext: executing command=' + command);
    if (format === 'custom') {
        (0, apputils_1.showErrorMessage)(trans.__('Error'), trans.__('Please edit the notebook metadata directly if you wish a custom configuration.'));
        return;
    }
    // Get current notebook widget extension
    const notebookFileExtension = getNotebookFileExtension(notebookTracker);
    // Toggle the selected format
    const index = selectedFormats.indexOf(format);
    if (format === 'none') {
        // Only keep one format - one that matches the current extension
        for (const selectedFormat of selectedFormats) {
            if (selectedFormat.split(':')[0] === notebookFileExtension) {
                selectedFormats = [selectedFormat];
                break;
            }
        }
    }
    else if (index !== -1) {
        selectedFormats.splice(index, 1);
        // The current file extension can't be unpaired
        let extFound = false;
        for (const selectedFormat of selectedFormats) {
            if (selectedFormat.split(':')[0] === notebookFileExtension) {
                extFound = true;
                break;
            }
        }
        if (!extFound) {
            return;
        }
    }
    else {
        // We can't have the same extension multiple times
        const newFormats = [];
        for (const selectedFormat of selectedFormats) {
            if (selectedFormat.split(':')[0] !== format.split(':')[0]) {
                newFormats.push(selectedFormat);
            }
        }
        selectedFormats = newFormats;
        selectedFormats.push(format);
    }
    if (selectedFormats.length === 1) {
        if (notebookFileExtension !== 'auto') {
            selectedFormats = [];
        }
        else if (jupytext === null || jupytext === void 0 ? void 0 : jupytext.text_representation) {
            jupytext.text_representation.formatName =
                selectedFormats[0].split(':')[1];
            selectedFormats = [];
        }
    }
    if (selectedFormats.length === 0) {
        // an older version was re-fetching the jupytext metadata here
        // but this is not necessary, as the metadata is already available
        if (!jupytext) {
            return;
        }
        if (jupytext.formats) {
            delete jupytext.formats;
        }
        if (Object.keys(jupytext).length === 0) {
            model.deleteMetadata('jupytext');
        }
        model.setMetadata('jupytext', jupytext);
        return;
    }
    // set the desired format
    if (jupytext) {
        jupytext.formats = selectedFormats.join();
    }
    else {
        jupytext = { formats: selectedFormats.join() };
    }
    model.setMetadata('jupytext', jupytext);
}
/**
 * Toggle metadata command
 */
function isMetadataCommandToggled(notebookTracker) {
    if (!notebookTracker.currentWidget) {
        return false;
    }
    const model = notebookTracker.currentWidget.context.model;
    const jupytextMetadata = model.getMetadata('jupytext');
    if (!jupytextMetadata) {
        return false;
    }
    const jupytext = jupytextMetadata;
    if (jupytext.notebook_metadata_filter === '-all') {
        return false;
    }
    return true;
}
/**
 * Enable metadata command
 */
function isMetadataCommandEnabled(notebookTracker) {
    if (!notebookTracker.currentWidget) {
        return false;
    }
    const model = notebookTracker.currentWidget.context.model;
    const jupytextMetadata = model.getMetadata('jupytext');
    if (!jupytextMetadata) {
        return false;
    }
    const jupytext = jupytextMetadata;
    if (jupytext.notebook_metadata_filter === undefined) {
        return true;
    }
    if (jupytext.notebook_metadata_filter === '-all') {
        return true;
    }
    return false;
}
/**
 * Execute metadata command
 */
function executeMetadataCommand(notebookTracker) {
    var _a;
    console.debug('Jupytext: toggling YAML header');
    if (!notebookTracker.currentWidget) {
        return;
    }
    const model = notebookTracker.currentWidget.context.model;
    const jupytextMetadata = model.getMetadata('jupytext');
    if (!jupytextMetadata) {
        return;
    }
    const jupytext = ((_a = jupytextMetadata) !== null && _a !== void 0 ? _a : {});
    if (jupytext.notebook_metadata_filter) {
        delete jupytext.notebook_metadata_filter;
        if (jupytext.notebook_metadata_filter === '-all') {
            delete jupytext.notebook_metadata_filter;
        }
    }
    else {
        jupytext.notebook_metadata_filter = '-all';
        if (jupytext.notebook_metadata_filter === undefined) {
            jupytext.notebook_metadata_filter = '-all';
        }
    }
    model.setMetadata('jupytext', jupytext);
}


/***/ },

/***/ "./lib/factory.js"
/*!************************!*\
  !*** ./lib/factory.js ***!
  \************************/
(__unused_webpack_module, exports, __webpack_require__) {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.createFactory = createFactory;
const apputils_1 = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
const notebook_1 = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
const tokens_1 = __webpack_require__(/*! ./tokens */ "./lib/tokens.js");
function createFactory(kernelFileTypeNames, toolbarRegistry, settingRegistry, docRegistry, notebookTracker, notebookFactory, contentFactory, editorServices, rendermime, translator, trans, riseFactory) {
    var _a, _b, _c;
    const allFileTypes = tokens_1.FILE_TYPES.concat(kernelFileTypeNames);
    // primarily this block is copied/pasted from jlab4 code and specifically
    // jupyterlab/packages/notebook-extension/src/index.ts
    // inside the function `activateWidgetFactory` at line 1150 as of this writing
    //
    const toolbarFactory = (0, apputils_1.createToolbarFactory)(toolbarRegistry, settingRegistry, 'Notebook', '@jupyterlab/notebook-extension:panel', translator);
    // Duplicate notebook factory to apply it on Jupytext notebooks
    // Mirror: https://github.com/jupyterlab/jupyterlab/blob/8a8c3752564f37493d4eb6b4c59008027fa83880/packages/notebook-extension/src/index.ts#L860
    const factory = new notebook_1.NotebookWidgetFactory({
        name: tokens_1.FACTORY,
        label: trans.__(tokens_1.FACTORY),
        fileTypes: allFileTypes,
        modelName: (_a = notebookFactory.modelName) !== null && _a !== void 0 ? _a : 'notebook',
        preferKernel: (_b = notebookFactory.preferKernel) !== null && _b !== void 0 ? _b : true,
        canStartKernel: (_c = notebookFactory.canStartKernel) !== null && _c !== void 0 ? _c : true,
        rendermime,
        contentFactory,
        editorConfig: notebookFactory.editorConfig,
        notebookConfig: notebookFactory.notebookConfig,
        mimeTypeService: editorServices.mimeTypeService,
        toolbarFactory: toolbarFactory,
        translator,
    });
    docRegistry.addWidgetFactory(factory);
    // The list of extensions in the Jupytext Notebook factory.
    const factoryExtensions = [];
    const updateWidgetExtensions = () => {
        // Dispose of all existing extensions.
        factoryExtensions.forEach((extension) => extension.dispose());
        // Add all the widgets extensions in the Notebook factory.
        for (const extension of docRegistry.widgetExtensions('Notebook')) {
            docRegistry.addWidgetExtension(tokens_1.FACTORY, extension);
        }
    };
    // Listen for changes in Notebook factory extensions.
    docRegistry.changed.connect((_, change) => {
        if (change.type === 'widgetExtension' && change.name === 'Notebook') {
            updateWidgetExtensions();
        }
    });
    updateWidgetExtensions();
    // Register widget created with the new factory in the notebook tracker
    // This is required to activate notebook commands (and therefore shortcuts)
    let id = 0; // The ID counter for notebook panels.
    const ft = docRegistry.getFileType('notebook');
    factory.widgetCreated.connect((sender, widget) => {
        var _a, _b;
        // If the notebook panel does not have an ID, assign it one.
        widget.id = widget.id || `notebook-jupytext-${++id}`;
        // Set up the title icon
        widget.title.icon = ft === null || ft === void 0 ? void 0 : ft.icon;
        widget.title.iconClass = (_a = ft === null || ft === void 0 ? void 0 : ft.iconClass) !== null && _a !== void 0 ? _a : '';
        widget.title.iconLabel = (_b = ft === null || ft === void 0 ? void 0 : ft.iconLabel) !== null && _b !== void 0 ? _b : '';
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
        for (const fileType of allFileTypes) {
            riseFactory.addFileType(fileType);
        }
    }
}


/***/ },

/***/ "./lib/index.js"
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
(__unused_webpack_module, exports, __webpack_require__) {


Object.defineProperty(exports, "__esModule", ({ value: true }));
const apputils_1 = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
const docmanager_1 = __webpack_require__(/*! @jupyterlab/docmanager */ "webpack/sharing/consume/default/@jupyterlab/docmanager");
const codemirror_1 = __webpack_require__(/*! @jupyterlab/codemirror */ "webpack/sharing/consume/default/@jupyterlab/codemirror");
const launcher_1 = __webpack_require__(/*! @jupyterlab/launcher */ "webpack/sharing/consume/default/@jupyterlab/launcher");
const settingregistry_1 = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
const codeeditor_1 = __webpack_require__(/*! @jupyterlab/codeeditor */ "webpack/sharing/consume/default/@jupyterlab/codeeditor");
const notebook_1 = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
const rendermime_1 = __webpack_require__(/*! @jupyterlab/rendermime */ "webpack/sharing/consume/default/@jupyterlab/rendermime");
const filebrowser_1 = __webpack_require__(/*! @jupyterlab/filebrowser */ "webpack/sharing/consume/default/@jupyterlab/filebrowser");
const mainmenu_1 = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
const translation_1 = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
const ui_components_1 = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
const disposable_1 = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
const widgets_1 = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
const coreutils_1 = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
const jupyterlab_rise_1 = __webpack_require__(/*! jupyterlab-rise */ "webpack/sharing/consume/default/jupyterlab-rise/jupyterlab-rise");
const tokens_1 = __webpack_require__(/*! ./tokens */ "./lib/tokens.js");
const commands_1 = __webpack_require__(/*! ./commands */ "./lib/commands.js");
const registry_1 = __webpack_require__(/*! ./registry */ "./lib/registry.js");
const factory_1 = __webpack_require__(/*! ./factory */ "./lib/factory.js");
const utils_1 = __webpack_require__(/*! ./utils */ "./lib/utils.js");
/**
 * Initialization data for the jupyterlab-jupytext extension.
 */
const extension = {
    id: tokens_1.JUPYTEXT_EXTENSION_ID,
    autoStart: true,
    optional: [
        launcher_1.ILauncher,
        mainmenu_1.IMainMenu,
        filebrowser_1.IDefaultFileBrowser,
        translation_1.ITranslator,
        apputils_1.ICommandPalette,
        jupyterlab_rise_1.IRisePreviewFactory,
    ],
    requires: [
        notebook_1.NotebookPanel.IContentFactory,
        codeeditor_1.IEditorServices,
        docmanager_1.IDocumentManager,
        codemirror_1.IEditorLanguageRegistry,
        rendermime_1.IRenderMimeRegistry,
        notebook_1.INotebookWidgetFactory,
        notebook_1.INotebookTracker,
        settingregistry_1.ISettingRegistry,
        apputils_1.IToolbarWidgetRegistry,
    ],
    activate: async (app, contentFactory, editorServices, docManager, languages, rendermime, notebookFactory, notebookTracker, settingRegistry, toolbarRegistry, launcher, mainmenu, defaultBrowser, translator, palette, riseFactory) => {
        console.log('JupyterLab extension jupytext is activating...');
        const trans = (translator !== null && translator !== void 0 ? translator : translation_1.nullTranslator).load('jupytext');
        // Load settings
        const includeFormats = tokens_1.TEXT_NOTEBOOKS_LAUNCHER_ICONS;
        if (settingRegistry) {
            const settings = await settingRegistry.load(extension.id);
            for (const format of tokens_1.JUPYTEXT_FORMATS) {
                const addFormat = settings.get(format).composite;
                if (addFormat && !includeFormats.includes(format)) {
                    includeFormats.push(format);
                }
                else if (!addFormat && includeFormats.includes(format)) {
                    includeFormats.splice(includeFormats.indexOf(format), 1);
                }
            }
        }
        // Unpack necessary components
        const { commands, serviceManager, docRegistry } = app;
        // Initialise Jupytext create notebook submenu and add it to File menu
        const jupytextCreateMenu = new widgets_1.Menu({ commands: app.commands });
        jupytextCreateMenu.id = 'jp-mainmenu-jupytext-new-menu';
        jupytextCreateMenu.title.label = trans.__('New Text Notebook');
        mainmenu.fileMenu.addItem({
            rank: 0.97,
            type: 'submenu',
            submenu: jupytextCreateMenu,
        });
        // Add create text notebook submenu to context menu
        // Rank 53 as 52 is used for classic notebook
        // https://github.com/jupyterlab/jupyterlab/blob/4d34bbbea2afc7385169d92bf7bc0c9e0face3a9/packages/notebook-extension/schema/tracker.json#L363-L369
        app.contextMenu.addItem({
            submenu: jupytextCreateMenu,
            type: 'submenu',
            selector: '.jp-DirListing-content',
            rank: 53,
        });
        // Initialise Jupytext menu and add it to main menu
        const jupytextMenu = new widgets_1.Menu({ commands: app.commands });
        mainmenu.fileMenu.addItem({
            rank: 0.98,
            type: 'submenu',
            submenu: jupytextMenu,
        });
        jupytextMenu.id = 'jp-mainmenu-jupytext-menu';
        jupytextMenu.title.label = trans.__('Jupytext');
        // Get all Jupytext formats
        let rank = 0;
        const separatorIndex = [];
        tokens_1.JUPYTEXT_PAIR_COMMANDS_FILETYPE_DATA.forEach((value, key) => {
            value.map((fileType) => {
                const format = key;
                const command = `jupytext:pair-nb-with-${format}`;
                commands.addCommand(command, {
                    label: (args) => {
                        var _a, _b;
                        if (args.isPalette) {
                            return ((_a = fileType.paletteLabel) !== null && _a !== void 0 ? _a : trans.__('Pair notebook'));
                        }
                        return (_b = fileType.caption) !== null && _b !== void 0 ? _b : trans.__('Pair notebook');
                    },
                    caption: trans.__(fileType.caption),
                    icon: (args) => {
                        if (args.isPalette) {
                            return undefined;
                        }
                        else {
                            return fileType.iconName
                                ? ui_components_1.LabIcon.resolve({
                                    icon: fileType.iconName,
                                })
                                : undefined;
                        }
                    },
                    isToggled: () => {
                        return (0, commands_1.isPairCommandToggled)(format, notebookTracker);
                    },
                    isEnabled: () => {
                        return (0, commands_1.isPairCommandEnabled)(format, notebookTracker);
                    },
                    execute: () => {
                        return (0, commands_1.executePairCommand)(command, format, notebookTracker, trans);
                    },
                });
                console.debug('Registering pairing command=' + command + ' with rank=' + rank);
                palette === null || palette === void 0 ? void 0 : palette.addItem({
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
        });
        // Add separators in jupytext pair menu
        separatorIndex.map((index, idx) => {
            jupytextMenu.insertItem(index + idx + 1, {
                type: 'separator',
            });
        });
        // Metadata in text representation
        commands.addCommand(tokens_1.CommandIDs.metadata, {
            label: trans.__('Include Metadata'),
            icon: (args) => {
                if (args.isPalette) {
                    return undefined;
                }
                else {
                    return tokens_1.JupytextIcon;
                }
            },
            isToggled: () => {
                return (0, commands_1.isMetadataCommandToggled)(notebookTracker);
            },
            isEnabled: () => {
                return (0, commands_1.isMetadataCommandEnabled)(notebookTracker);
            },
            execute: () => {
                return (0, commands_1.executeMetadataCommand)(notebookTracker);
            },
        });
        palette === null || palette === void 0 ? void 0 : palette.addItem({
            command: tokens_1.CommandIDs.metadata,
            args: { isPalette: true },
            rank: 98,
            category: 'Jupytext',
        });
        jupytextMenu.addItem({
            type: 'separator',
        });
        jupytextMenu.addItem({
            command: tokens_1.CommandIDs.metadata,
        });
        jupytextMenu.addItem({
            type: 'separator',
        });
        // Register Jupytext FAQ command
        commands.addCommand(tokens_1.CommandIDs.faq, {
            label: trans.__('Jupytext FAQ'),
            icon: (args) => {
                if (args.isPalette) {
                    return undefined;
                }
                else {
                    return tokens_1.JupytextIcon;
                }
            },
            execute: () => {
                window.open('https://jupytext.readthedocs.io/en/latest/faq.html');
            },
        });
        palette === null || palette === void 0 ? void 0 : palette.addItem({
            command: tokens_1.CommandIDs.faq,
            args: { isPalette: true },
            rank: 99,
            category: 'Jupytext',
        });
        jupytextMenu.addItem({
            command: tokens_1.CommandIDs.faq,
        });
        // Register Jupytext Reference
        commands.addCommand(tokens_1.CommandIDs.reference, {
            label: trans.__('Jupytext Reference'),
            icon: (args) => {
                if (args.isPalette) {
                    return undefined;
                }
                else {
                    return tokens_1.JupytextIcon;
                }
            },
            execute: () => {
                window.open('https://jupytext.readthedocs.io/en/latest/');
            },
        });
        palette === null || palette === void 0 ? void 0 : palette.addItem({
            command: tokens_1.CommandIDs.reference,
            args: { isPalette: true },
            rank: 100,
            category: 'Jupytext',
        });
        jupytextMenu.addItem({
            command: tokens_1.CommandIDs.reference,
        });
        // Register a new command to create untitled file. This snippet is taken
        // from docManager package https://github.com/jupyterlab/jupyterlab/blob/c106f0a19110efad7c5e1b136144985819e21100/packages/docmanager-extension/src/index.tsx#L679-L680
        // We are "duplicating" it as base command adds extension to the options
        // only if it is of type file. But we are interested in creating notebook type
        // files with different Jupytext supported extensions. So we create a dedicated
        // create new text notebook command here and make sure we pass extension in options
        commands.addCommand(tokens_1.CommandIDs.newUntitled, {
            execute: async (args) => {
                const errorTitle = args['error'] || trans.__('Error');
                const path = typeof args['path'] === 'undefined' ? '' : args['path'];
                const options = {
                    type: args['type'],
                    path,
                };
                // Ensure we pass extension to command always
                options.ext = args['ext'] || '.txt';
                return docManager.services.contents
                    .newUntitled(options)
                    .catch((error) => (0, apputils_1.showErrorMessage)(errorTitle, error));
            },
            label: (args) => args['label'] || `New ${args['type']}`,
        });
        // We dont need to add this command to palettte as it is a utility one
        // which does not have direct usage
        // palette?.addItem({
        //   command: CommandIDs.newUntitled,
        //   rank: 50,
        //   category: 'Jupytext',
        // });
        // Get a map of available kernel languages in current widget
        const availableKernelLanguages = await (0, utils_1.getAvailableKernelLanguages)(languages, serviceManager);
        // Get a map of all create text notebook commands
        const createTextNotebookCommands = await (0, utils_1.getAvailableCreateTextNotebookCommands)(includeFormats, availableKernelLanguages);
        // Register Jupytext text notebooks file types
        (0, registry_1.registerFileTypes)(availableKernelLanguages, docRegistry, trans);
        // Get all kernel file types to add to Jupytext factory
        const kernelLanguageNames = [];
        for (const kernelLanguage of availableKernelLanguages.keys()) {
            kernelLanguageNames.push(kernelLanguage);
        }
        // Create a factory for Jupytext
        (0, factory_1.createFactory)(kernelLanguageNames, toolbarRegistry, settingRegistry, docRegistry, notebookTracker, notebookFactory, contentFactory, editorServices, rendermime, translator, trans, riseFactory);
        // Register all the commands that create text notebooks with different formats
        // Nicked from notebook-extension package in JupyterLab
        // https://github.com/jupyterlab/jupyterlab/blob/c106f0a19110efad7c5e1b136144985819e21100/packages/notebook-extension/src/index.ts#L1902-L1965
        createTextNotebookCommands.forEach((fileTypes, _) => {
            fileTypes.map((fileType) => {
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
                        }
                        else {
                            if (iconName) {
                                return ui_components_1.LabIcon.resolve({
                                    icon: iconName,
                                });
                            }
                            if (kernelIcon) {
                                return kernelIcon;
                            }
                            return ui_components_1.LabIcon.resolve({
                                icon: 'ui-components:kernel',
                            });
                        }
                    },
                    execute: (args) => {
                        var _a;
                        const cwd = args['cwd'] || ((_a = defaultBrowser === null || defaultBrowser === void 0 ? void 0 : defaultBrowser.model.path) !== null && _a !== void 0 ? _a : '');
                        const kernelId = args['kernelId'] || '';
                        const kernelName = args['kernelName'] || '';
                        return (0, utils_1.createNewTextNotebook)(cwd, kernelId, kernelName, format, commands);
                    },
                });
                console.debug('Registering create new text notebook command=' +
                    command +
                    ' with rank=' +
                    rank);
                palette === null || palette === void 0 ? void 0 : palette.addItem({
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
                        let disposables = null;
                        const onSpecsChanged = () => {
                            var _a, _b, _c;
                            if (disposables) {
                                disposables.dispose();
                                disposables = null;
                            }
                            const specs = serviceManager.kernelspecs.specs;
                            if (!specs) {
                                return;
                            }
                            disposables = new disposable_1.DisposableSet();
                            const kernelIconUrl = ((_a = specs.kernelspecs[fileType.kernelName]) === null || _a === void 0 ? void 0 : _a.resources['logo-svg']) ||
                                ((_b = specs.kernelspecs[fileType.kernelName]) === null || _b === void 0 ? void 0 : _b.resources['logo-64x64']);
                            disposables.add(launcher.add({
                                command: command,
                                args: { isLauncher: true, kernelName: fileType.kernelName },
                                category: trans.__('Jupytext'),
                                rank: rank++,
                                kernelIconUrl,
                                metadata: {
                                    kernel: coreutils_1.JSONExt.deepCopy(((_c = specs.kernelspecs[fileType.kernelName]) === null || _c === void 0 ? void 0 : _c.metadata) || {}),
                                },
                            }));
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
exports["default"] = extension;


/***/ },

/***/ "./lib/registry.js"
/*!*************************!*\
  !*** ./lib/registry.js ***!
  \*************************/
(__unused_webpack_module, exports, __webpack_require__) {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.registerFileTypes = registerFileTypes;
const ui_components_1 = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
function registerFileTypes(availableKernelLanguages, docRegistry, trans) {
    // Add kernel file types to registry
    availableKernelLanguages.forEach((kernelFileTypes, kernelLanguage) => {
        // Do not add python as it will be already there by default
        if (kernelLanguage !== 'python') {
            kernelFileTypes.map((kernelFileType) => {
                docRegistry.addFileType({
                    name: kernelLanguage,
                    contentType: 'file',
                    displayName: trans.__(kernelFileType.paletteLabel.split('New')[1].trim()),
                    extensions: [`.${kernelFileType.fileExt}`],
                    icon: kernelFileType.kernelIcon || ui_components_1.kernelIcon,
                });
            });
        }
    });
    // Add markdown file types to registry
    docRegistry.addFileType({
        name: 'myst',
        contentType: 'notebook',
        displayName: trans.__('MyST Markdown Notebook'),
        extensions: ['.myst', '.mystnb', '.mnb'],
        icon: ui_components_1.markdownIcon,
    }, ['Notebook']);
    docRegistry.addFileType({
        name: 'r-markdown',
        contentType: 'notebook',
        displayName: trans.__('R Markdown Notebook'),
        // Extension file are transformed to lower case...
        extensions: ['.Rmd'],
        icon: ui_components_1.markdownIcon,
    }, ['Notebook']);
    docRegistry.addFileType({
        name: 'quarto',
        contentType: 'notebook',
        displayName: trans.__('Quarto Notebook'),
        extensions: ['.qmd'],
        icon: ui_components_1.markdownIcon,
    }, ['Notebook']);
}


/***/ },

/***/ "./lib/tokens.js"
/*!***********************!*\
  !*** ./lib/tokens.js ***!
  \***********************/
(__unused_webpack_module, exports, __webpack_require__) {


var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.TEXT_NOTEBOOKS_LAUNCHER_ICONS = exports.JUPYTEXT_FORMATS = exports.JUPYTEXT_CREATE_TEXT_NOTEBOOK_FILETYPE_DATA = exports.AUTO_LANGUAGE_FILETYPE_DATA = exports.JUPYTEXT_PAIR_COMMANDS_FILETYPE_DATA = exports.SERVER_SETTINGS = exports.JupytextIcon = exports.CommandIDs = exports.NS = exports.FILE_TYPES = exports.LANGUAGE_INDEPENDENT_NOTEBOOK_EXTENSIONS = exports.FACTORY = exports.JUPYTEXT_EXTENSION_ID = void 0;
const services_1 = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
const ui_components_1 = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
const logo_svg_1 = __importDefault(__webpack_require__(/*! ../style/icons/logo.svg */ "./style/icons/logo.svg"));
/**
 * Jupytext extension ID
 */
exports.JUPYTEXT_EXTENSION_ID = 'jupyterlab-jupytext:plugin';
/**
 * Jupytext widget factory
 */
exports.FACTORY = 'Jupytext Notebook';
/**
 * Supported file formats.
 */
exports.LANGUAGE_INDEPENDENT_NOTEBOOK_EXTENSIONS = [
    'ipynb',
    'md',
    'Rmd',
    'qmd',
];
/**
 * Supported file types names.
 */
exports.FILE_TYPES = [
    'markdown',
    'myst',
    'r-markdown',
    'quarto',
    'julia',
    'python',
    'r',
];
/**
 * The short namespace for commands, etc.
 */
exports.NS = 'jupytext';
/**
 * Command IDs of Jupytext
 */
var CommandIDs;
(function (CommandIDs) {
    CommandIDs.metadata = `${exports.NS}:metadata`;
    CommandIDs.reference = `${exports.NS}:reference`;
    CommandIDs.faq = `${exports.NS}:faq`;
    CommandIDs.newUntitled = `${exports.NS}:new-untitled-text-notebook`;
})(CommandIDs || (exports.CommandIDs = CommandIDs = {}));
/**
 * Jupytext logo icon
 */
exports.JupytextIcon = new ui_components_1.LabIcon({
    name: `${exports.NS}:icon:logo`,
    svgstr: logo_svg_1.default,
});
/**
 * Current Jupyter server settings
 */
exports.SERVER_SETTINGS = services_1.ServerConnection.makeSettings();
/**
 * Supported Jupytext pairings along with metadata.
 */
exports.JUPYTEXT_PAIR_COMMANDS_FILETYPE_DATA = new Map([
    [
        'ipynb',
        [
            {
                fileExt: 'ipynb',
                paletteLabel: 'Pair with ipynb',
                caption: 'Pair Notebook with ipynb document',
                iconName: 'ui-components:notebook',
                separator: true,
            },
        ],
    ],
    [
        'auto:percent',
        [
            {
                fileExt: 'auto:percent',
                paletteLabel: 'Pair with percent script',
                caption: 'Pair Notebook with Percent Format',
                iconName: 'ui-components:text-editor',
            },
        ],
    ],
    [
        'auto:light',
        [
            {
                fileExt: 'auto:light',
                paletteLabel: 'Pair with light script',
                caption: 'Pair Notebook with Light Format',
                iconName: 'ui-components:text-editor',
            },
        ],
    ],
    [
        'auto:nomarker',
        [
            {
                fileExt: 'auto:nomarker',
                paletteLabel: 'Pair with nomarker script',
                caption: 'Pair Notebook with Nomarker Format',
                iconName: 'ui-components:text-editor',
                separator: true,
            },
        ],
    ],
    [
        'py:marimo',
        [
            {
                fileExt: 'py:marimo',
                paletteLabel: 'Pair with Marimo Python script',
                caption: 'Pair Notebook with Marimo Python script',
                iconName: 'ui-components:text-editor',
                separator: true,
            },
        ],
    ],
    [
        'md',
        [
            {
                fileExt: 'md',
                paletteLabel: 'Pair with md',
                caption: 'Pair Notebook with Markdown',
                iconName: 'ui-components:markdown',
            },
        ],
    ],
    [
        'md:myst',
        [
            {
                fileExt: 'md:myst',
                paletteLabel: 'Pair with myst md',
                caption: 'Pair Notebook with MyST Markdown',
                iconName: 'ui-components:markdown',
                separator: true,
            },
        ],
    ],
    [
        'Rmd',
        [
            {
                fileExt: 'Rmd',
                paletteLabel: 'Pair with Rmd',
                caption: 'Pair Notebook with R Markdown',
                iconName: 'ui-components:markdown',
            },
        ],
    ],
    [
        'qmd',
        [
            {
                fileExt: 'qmd',
                paletteLabel: 'Pair with qmd',
                caption: 'Pair Notebook with Quarto (qmd)',
                iconName: 'ui-components:markdown',
                separator: true,
            },
        ],
    ],
    [
        'custom',
        [
            {
                fileExt: 'custom',
                paletteLabel: 'Custom pair',
                caption: 'Custom Pairing',
                iconName: 'ui-components:text-editor',
            },
        ],
    ],
    [
        'none',
        [
            {
                fileExt: 'none',
                paletteLabel: 'Unpair',
                caption: 'Unpair Current Notebook',
            },
        ],
    ],
]);
/**
 * Supported kernels file types metadata
 */
exports.AUTO_LANGUAGE_FILETYPE_DATA = new Map([
    [
        'python',
        [
            {
                fileExt: 'py',
                paletteLabel: 'New Python Text Notebook',
                caption: 'Create a new Python Text Notebook',
                iconName: 'ui-components:python',
                launcherLabel: 'Python',
                kernelName: 'python3',
            },
        ],
    ],
    [
        'julia',
        [
            {
                fileExt: 'jl',
                paletteLabel: 'New Julia Text Notebook',
                caption: 'Create a new Julia Text Notebook',
                iconName: 'ui-components:julia',
                launcherLabel: 'Julia',
                kernelName: 'julia',
            },
        ],
    ],
    [
        'R',
        [
            {
                fileExt: 'R',
                paletteLabel: 'New R Text Notebook',
                caption: 'Create a new R Text Notebook',
                iconName: 'ui-components:r-kernel',
                launcherLabel: 'R',
                kernelName: 'ir',
            },
        ],
    ],
]);
/**
 * Supported Jupytext create new text notebooks file types
 */
exports.JUPYTEXT_CREATE_TEXT_NOTEBOOK_FILETYPE_DATA = new Map([
    [
        'auto:percent',
        [
            {
                fileExt: 'auto:percent',
                paletteLabel: 'Percent Format',
                caption: 'Percent Format',
                launcherLabel: 'Percent Format',
            },
        ],
    ],
    [
        'auto:light',
        [
            {
                fileExt: 'auto:light',
                paletteLabel: 'Light Format',
                caption: 'Light Format',
                launcherLabel: 'Light Format',
            },
        ],
    ],
    [
        'auto:nomarker',
        [
            {
                fileExt: 'auto:nomarker',
                paletteLabel: 'Nomarker Format',
                caption: 'Nomarker Format',
                launcherLabel: 'Nomarker Format',
            },
        ],
    ],
    [
        'py:marimo',
        [
            {
                fileExt: 'py:marimo',
                paletteLabel: 'Marimo Format',
                caption: 'Marimo Format',
                launcherLabel: 'Marimo Format',
            },
        ],
    ],
    [
        'md',
        [
            {
                fileExt: 'md',
                paletteLabel: 'New Markdown Text Notebook',
                caption: 'Create a new Markdown Text Notebook',
                iconName: 'ui-components:markdown',
                launcherLabel: 'Markdown',
            },
        ],
    ],
    [
        'md:myst',
        [
            {
                fileExt: 'md:myst',
                paletteLabel: 'New MyST Markdown Text Notebook',
                caption: 'Create a new MyST Markdown Text Notebook',
                iconName: 'ui-components:markdown',
                launcherLabel: 'MyST Markdown',
            },
        ],
    ],
    [
        'Rmd',
        [
            {
                fileExt: 'Rmd',
                paletteLabel: 'New R Markdown Text Notebook',
                caption: 'Create a new R Markdown Text Notebook',
                iconName: 'ui-components:markdown',
                launcherLabel: 'R Markdown',
            },
        ],
    ],
    [
        'qmd',
        [
            {
                fileExt: 'qmd',
                paletteLabel: 'New Quarto Markdown Text Notebook',
                caption: 'Create a new Quarto Markdown Text Notebook',
                iconName: 'ui-components:markdown',
                launcherLabel: 'Quarto Markdown',
            },
        ],
    ],
]);
/**
 * Supported Jupytext format extensions bar custom and none
 */
exports.JUPYTEXT_FORMATS = Array.from(exports.JUPYTEXT_PAIR_COMMANDS_FILETYPE_DATA.keys())
    .map((format) => {
    return format;
})
    .filter((format) => {
    return !['custom', 'none'].includes(format);
});
/**
 * List of formats that would be added to launcher icons
 */
exports.TEXT_NOTEBOOKS_LAUNCHER_ICONS = exports.JUPYTEXT_FORMATS.filter((format) => {
    return !['ipynb', 'auto:nomarker', 'qmd', 'custom', 'none'].includes(format);
});


/***/ },

/***/ "./lib/utils.js"
/*!**********************!*\
  !*** ./lib/utils.js ***!
  \**********************/
(__unused_webpack_module, exports, __webpack_require__) {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.createNewTextNotebook = void 0;
exports.getAvailableKernelLanguages = getAvailableKernelLanguages;
exports.getAvailableCreateTextNotebookCommands = getAvailableCreateTextNotebookCommands;
const services_1 = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
const ui_components_1 = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
const coreutils_1 = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
const buffer_1 = __webpack_require__(/*! buffer */ "webpack/sharing/consume/default/buffer/buffer");
const tokens_1 = __webpack_require__(/*! ./tokens */ "./lib/tokens.js");
/**
 * Get kernel icon SVG string
 */
async function getKernelIconBase64String(kernelIconUrl) {
    // Seems like URL prefix is already included in kernelIconUrl. We need to strip
    // it off as baseUrl will already has url prefix.
    kernelIconUrl = `/kernelspecs${kernelIconUrl.split('kernelspecs')[1]}`;
    const url = coreutils_1.URLExt.join(tokens_1.SERVER_SETTINGS.baseUrl, kernelIconUrl);
    const response = await services_1.ServerConnection.makeRequest(url, {}, tokens_1.SERVER_SETTINGS);
    const blob = await response.arrayBuffer();
    const contentType = response.headers.get('content-type');
    return `data:${contentType};base64,${buffer_1.Buffer.from(blob).toString('base64')}`;
}
/**
 * Make a SVG string from base64 image
 */
function base64ToSvgStr(width, imageBase64) {
    return `<svg xmlns="http://www.w3.org/2000/svg"
  xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="none" viewBox="0 0 ${width} ${width}">
  <g id="layer1">
     <image xlink:href="${imageBase64}"/>
  </g>
</svg>`.replace(/\n/g, ' ');
}
/**
 * Get kernel Icon
 */
async function getKernelIcon(specModel) {
    // First check for logo-svg
    if (specModel.resources['logo-svg']) {
        const svgStr = await getKernelIconBase64String(specModel.resources['logo-svg']);
        return new ui_components_1.LabIcon({
            name: `${tokens_1.NS}:icon:${specModel.name}`,
            svgstr: svgStr,
        });
    }
    // Else check if 64x64 kernel icon is available
    if (specModel.resources['logo-64x64']) {
        const iconBase64String = await getKernelIconBase64String(specModel.resources['logo-64x64']);
        return new ui_components_1.LabIcon({
            name: `${tokens_1.NS}:icon:${specModel.name}`,
            svgstr: base64ToSvgStr(64, iconBase64String),
        });
    }
    // Finally check for 32x32 kernel icon
    if (specModel.resources['logo-32x32']) {
        const iconBase64String = await getKernelIconBase64String(specModel.resources['logo-32x32']);
        return new ui_components_1.LabIcon({
            name: `${tokens_1.NS}:icon:${specModel.name}`,
            svgstr: base64ToSvgStr(32, iconBase64String),
        });
    }
    // If not found, make a generic kernel icon
    return ui_components_1.LabIcon.resolve({
        icon: 'ui-components:kernel',
    });
}
/**
 * Get all available kernel languages so that we replace auto format
 * with these language file extensions
 */
async function getAvailableKernelLanguages(languages, serviceManager) {
    var _a, _b;
    const specsManager = serviceManager.kernelspecs;
    await specsManager.ready;
    const fileTypes = new Map();
    const specs = (_b = (_a = specsManager.specs) === null || _a === void 0 ? void 0 : _a.kernelspecs) !== null && _b !== void 0 ? _b : {};
    for (const [spec, specModel] of Object.entries(specs)) {
        if (specModel) {
            // First check if kernel is one of the pre-defined types (Python, R, Julia)
            const exts = tokens_1.AUTO_LANGUAGE_FILETYPE_DATA.get(specModel.language);
            if (exts !== undefined) {
                fileTypes.set(specModel.language, exts);
            }
            else {
                // If not, try to get languageInfo from codemirror languages
                const languageInfo = languages.findByName(specModel.language);
                // If we managed to find the language, construct the FileTypeData
                // Here we make an assumption that first extension in
                // languageInfo.extensions is the most common one.
                if (languageInfo) {
                    // We attempt to get kernelIcon here for specModel.resources
                    // If none provided, we return generic kernel icon
                    const kernelIcon = await getKernelIcon(specModel);
                    const displayName = languageInfo.displayName || specModel.display_name;
                    const exts = [
                        {
                            fileExt: languageInfo.extensions[0],
                            paletteLabel: `New ${displayName} Text Notebook`,
                            caption: `Create a new ${displayName} Text Notebook`,
                            kernelIcon: kernelIcon,
                            launcherLabel: displayName,
                            kernelName: spec,
                        },
                    ];
                    fileTypes.set(specModel.language, exts);
                }
            }
        }
    }
    return fileTypes;
}
/**
 * Get all available 'Create New Text Notebook' commands based on configured
 * formats and available kernels
 */
async function getAvailableCreateTextNotebookCommands(includeFormats, availableKernelLanguages) {
    const numKernels = availableKernelLanguages.size;
    // Initialise a map of 'Create New Text Notebook' command filetypes
    const createTextNotebookCommands = new Map();
    // Iterate through all JUPYTEXT_CREATE_TEXT_NOTEBOOK_FILETYPE_DATA file types.
    tokens_1.JUPYTEXT_CREATE_TEXT_NOTEBOOK_FILETYPE_DATA.forEach((fileTypes, format) => {
        fileTypes.map((fileType) => {
            // If format is auto, we need to add all currently available kernels
            // For instance if there are Python and R kernels available, format
            // auto:percent will be replaced by py:percent and R:percent
            if (format.startsWith('auto')) {
                const formatType = format.split(':')[1];
                let mapIndex = 0;
                availableKernelLanguages.forEach((kernelLanguages, kernelKey) => {
                    const updatedKernelKey = `${kernelKey}:${formatType}`;
                    createTextNotebookCommands.set(updatedKernelKey, []);
                    mapIndex += 1;
                    kernelLanguages.map((kernelLanguageFileType) => {
                        // Merge fileType object from kernel and Jupytext format and push
                        // it to createTextNotebookCommands
                        const updatedKernelLanguageFileType = {
                            ...kernelLanguageFileType,
                        };
                        updatedKernelLanguageFileType.fileExt = `${updatedKernelLanguageFileType.fileExt}:${formatType}`;
                        updatedKernelLanguageFileType.paletteLabel = `${updatedKernelLanguageFileType.paletteLabel} with ${fileType.paletteLabel}`;
                        updatedKernelLanguageFileType.caption = `${updatedKernelLanguageFileType.caption} with ${fileType.caption}`;
                        updatedKernelLanguageFileType.launcherLabel = `${updatedKernelLanguageFileType.launcherLabel} - ${fileType.launcherLabel}`;
                        if (numKernels === mapIndex) {
                            updatedKernelLanguageFileType.separator = true;
                        }
                        createTextNotebookCommands
                            .get(updatedKernelKey)
                            .push(updatedKernelLanguageFileType);
                        // Update includeFormats with the language specific formats
                        // Effectiviely we will add formats like py:light, js:light here
                        if (includeFormats.includes(format)) {
                            includeFormats.push(updatedKernelLanguageFileType.fileExt);
                        }
                    });
                });
            }
            else {
                if (createTextNotebookCommands.get(format) === undefined) {
                    createTextNotebookCommands.set(format, []);
                }
                createTextNotebookCommands.get(format).push(fileType);
            }
        });
    });
    return createTextNotebookCommands;
}
/**
 * Create New Text Notebook file
 */
const createNewTextNotebook = async (cwd, kernelId, kernelName, format, commands) => {
    const model = await commands.execute(tokens_1.CommandIDs.newUntitled, {
        path: cwd,
        type: 'notebook',
        // We should not have auto in format at this point. If somehow we end up having
        // it, ensure we replace by py as Python kernel exists always
        ext: format.replace('auto', 'py'),
    });
    if (model !== undefined) {
        const widget = (await commands.execute('docmanager:open', {
            path: model.path,
            factory: tokens_1.FACTORY,
            kernel: { id: kernelId, name: kernelName },
        }));
        widget.isUntitled = true;
        return widget;
    }
};
exports.createNewTextNotebook = createNewTextNotebook;


/***/ },

/***/ "./style/icons/logo.svg"
/*!******************************!*\
  !*** ./style/icons/logo.svg ***!
  \******************************/
(module) {

module.exports = "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 124 91\">\n  <g fill=\"none\" fill-rule=\"nonzero\">\n    <path fill=\"#FACDAF\" d=\"M.4 21.6v-3.2h15.64v3.2z\"/>\n    <path fill=\"#FA6400\" d=\"M38.64 5.16c-.827 0-1.453-.213-1.88-.64-.427-.427-.64-1.053-.64-1.88 0-.8.22-1.413.66-1.84.44-.427 1.06-.64 1.86-.64s1.413.213 1.84.64c.427.427.64 1.04.64 1.84 0 .827-.213 1.453-.64 1.88-.427.427-1.04.64-1.84.64zm2.04 4.04L40.64 32c0 1.707-.373 3.2-1.12 4.48-.747 1.28-1.72 2.253-2.92 2.92-1.2.667-2.493 1-3.88 1-1.573 0-3.053-.44-4.44-1.32-1.387-.88-2.493-2.213-3.32-4L28 33.72c.48 1.093 1.147 1.92 2 2.48s1.773.84 2.76.84c1.253 0 2.313-.44 3.18-1.32.867-.88 1.3-2.12 1.3-3.72V12l-4.68-.28V9.2h8.12zM66.48 32v-3.28c-.613 1.173-1.547 2.113-2.8 2.82a8.093 8.093 0 01-4.04 1.06c-1.6 0-3.04-.507-4.32-1.52-1.28-1.013-2.28-2.373-3-4.08-.72-1.707-1.08-3.56-1.08-5.56V9.16h3.64v13.12c0 1.28.273 2.48.82 3.6.547 1.12 1.3 2.02 2.26 2.7.96.68 2.053 1.02 3.28 1.02 1.147 0 2.067-.32 2.76-.96.693-.64 1.52-1.747 2.48-3.32V9.2h3.4v20.16c0 1.227.08 2.107.24 2.64h-3.64zM87.64 8.56c3.2 0 5.687 1 7.46 3 1.773 2 2.66 4.8 2.66 8.4 0 2.507-.433 4.713-1.3 6.62s-2.1 3.38-3.7 4.42-3.44 1.56-5.52 1.56c-2.56 0-4.707-.76-6.44-2.28V40l-3.4.24V9.2h4.28c-.213.293-.413.713-.6 1.26A4.777 4.777 0 0080.8 12v.08c.853-1.227 1.827-2.12 2.92-2.68s2.4-.84 3.92-.84zm-.4 20.76c1.36 0 2.58-.4 3.66-1.2 1.08-.8 1.927-1.907 2.54-3.32.613-1.413.92-3.027.92-4.84 0-2.533-.613-4.567-1.84-6.1-1.227-1.533-2.853-2.3-4.88-2.3-1.44 0-2.753.393-3.94 1.18-1.187.787-2.153 1.9-2.9 3.34v9.72c.507 1.227 1.28 2.12 2.32 2.68 1.04.56 2.413.84 4.12.84zM119.6 9.2h3.8l-.136.533c-.655 2.483-1.876 6.146-3.664 10.987-1.92 5.2-3.853 10.04-5.8 14.52-1.28 3.52-3.493 5.28-6.64 5.28-.64 0-1.24-.053-1.8-.16l.56-2.64c.213.053.52.08.92.08 1.813 0 3.16-1.187 4.04-3.56l1.4-3.44h-.04l-.263-.686c-.538-1.384-1.317-3.263-2.337-5.636l-1.22-2.829c-1.266-2.964-2.24-5.348-2.92-7.149-.76-2.013-1.26-3.78-1.5-5.3h3.36c.22 1.418.67 3.037 1.349 4.858l.191.502c.787 2.027 1.94 4.813 3.46 8.36l1.56 3.6a282.728 282.728 0 003.66-10.18l.305-.917c.88-2.685 1.451-4.759 1.715-6.223z\"/>\n    <path fill=\"#BDDD9B\" d=\"M16.04 79.24H9.72v6.24h-3.2v-6.24H.32v-3.2h6.2V69.8h3.2v6.24h6.32z\"/>\n    <path fill=\"#6DD400\" d=\"M44.76 85.28c-.827 1.787-1.933 3.12-3.32 4-1.387.88-2.867 1.32-4.44 1.32a7.861 7.861 0 01-3.88-1c-1.2-.667-2.173-1.64-2.92-2.92-.747-1.28-1.12-2.773-1.12-4.48V70.28H25.4V67.2h3.68v-8.64l3.4.24v8.4h9.72v3.08h-9.72V82.2c0 1.6.433 2.84 1.3 3.72.867.88 1.927 1.32 3.18 1.32.987 0 1.907-.28 2.76-.84.853-.56 1.52-1.387 2-2.48l3.04 1.36zm16.4-18.72c3.227 0 5.66 1.013 7.3 3.04 1.64 2.027 2.393 4.893 2.26 8.6l-.08 1.96-16.24.08c0 1.413.287 2.673.86 3.78.573 1.107 1.38 1.967 2.42 2.58s2.227.92 3.56.92c1.093 0 2.193-.247 3.3-.74 1.107-.493 2.26-1.327 3.46-2.5l2.04 2.48a11.684 11.684 0 01-3.94 2.84c-1.507.667-3.087 1-4.74 1-2 0-3.787-.44-5.36-1.32a9.391 9.391 0 01-3.68-3.68c-.88-1.573-1.32-3.36-1.32-5.36V78.2c.107-3.733 1.02-6.607 2.74-8.62 1.72-2.013 4.193-3.02 7.42-3.02zm5.92 10.6c.133-2.453-.333-4.333-1.4-5.64-1.067-1.307-2.693-1.96-4.88-1.96-2.107 0-3.667.653-4.68 1.96s-1.573 3.187-1.68 5.64h12.64zM93.04 90l-5.6-8.8L81.8 90h-3.64l7.52-11.6-7.12-11.2h3.6l5.32 8.36 5.4-8.36h3.6l-7.2 11.2 7.4 11.6h-3.64zm30.92-4.72c-.827 1.787-1.933 3.12-3.32 4-1.387.88-2.867 1.32-4.44 1.32a7.861 7.861 0 01-3.88-1c-1.2-.667-2.173-1.64-2.92-2.92-.747-1.28-1.12-2.773-1.12-4.48V70.28h-3.68V67.2h3.68v-8.64l3.4.24v8.4h9.72v3.08h-9.72V82.2c0 1.6.433 2.84 1.3 3.72.867.88 1.927 1.32 3.18 1.32.987 0 1.907-.28 2.76-.84.853-.56 1.52-1.387 2-2.48l3.04 1.36z\"/>\n  </g>\n</svg>\n";

/***/ }

}]);
//# sourceMappingURL=lib_index_js.be7727ec53f52cd4c79b.js.map