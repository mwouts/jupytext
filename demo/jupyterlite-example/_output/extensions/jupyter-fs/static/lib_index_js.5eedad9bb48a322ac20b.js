"use strict";
(self["webpackChunkjupyter_fs"] = self["webpackChunkjupyter_fs"] || []).push([["lib_index_js"],{

/***/ "./lib/auth.js":
/*!*********************!*\
  !*** ./lib/auth.js ***!
  \*********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   AskDialog: () => (/* binding */ AskDialog),
/* harmony export */   DoubleBraceTemplate: () => (/* binding */ DoubleBraceTemplate),
/* harmony export */   askRequired: () => (/* binding */ askRequired)
/* harmony export */ });
/* harmony import */ var _material_ui_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @material-ui/core */ "webpack/sharing/consume/default/@material-ui/core/@material-ui/core");
/* harmony import */ var _material_ui_core__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _icons__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./icons */ "./lib/icons.js");
/******************************************************************************
 *
 * Copyright (c) 2019, the jupyter-fs authors.
 *
 * This file is part of the jupyter-fs library, distributed under the terms of
 * the Apache License 2.0.  The full license can be found in the LICENSE file.
 *
 */



class Template {
    constructor(template) {
        this.template = template;
        this.pattern = /(?:)/;
    }
    substitute(dict) {
        return this.template.replace(this.pattern, (_, p1) => dict[p1]);
    }
    tokens() {
        const toks = [];
        let match;
        // eslint-disable-next-line no-cond-assign
        while ((match = this.pattern.exec(this.template))) {
            toks.push(match[1]);
        }
        return toks;
    }
}
class DoubleBraceTemplate extends Template {
    constructor() {
        super(...arguments);
        this.pattern = /{{(\S+?)}}/g;
    }
}
function tokensFromUrl(url) {
    return new DoubleBraceTemplate(url).tokens();
}
function _askRequired(spec) {
    var _a;
    return spec.auth === "ask" && !spec.init && !!((_a = spec.missingTokens) === null || _a === void 0 ? void 0 : _a.length);
}
function askRequired(specs) {
    for (const spec of specs) {
        if (_askRequired(spec)) {
            return true;
        }
    }
    return false;
}
class AskDialog extends react__WEBPACK_IMPORTED_MODULE_1__.Component {
    constructor(props, options) {
        super(props);
        this.state = AskDialog.initialState({ open: true, options });
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_1__.createElement("div", null,
            react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.Dialog, { className: "jfs-ask-dialog", open: this.state.open, onClose: this._onClose.bind(this) },
                react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.DialogTitle, { className: "jfs-ask jfs-ask-dialog-title" }, "Please enter token values for filesystem resources"),
                react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.DialogContent, { className: "jfs-ask jfs-ask-dialog-content" }, this._form()),
                react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.DialogActions, { className: "jfs-ask jfs-ask-dialog-actions" },
                    react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.Button, { className: "jfs-ask jfs-ask-dialog-actions-button-cancel", onClick: this._onClose.bind(this), color: "primary" }, "Cancel"),
                    react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.Button, { className: "jfs-ask jfs-ask-dialog-actions-button-submit", onClick: this._onSubmit.bind(this), color: "primary" }, "Submit")))));
    }
    _form() {
        return (react__WEBPACK_IMPORTED_MODULE_1__.createElement("form", { className: "jfs-ask jfs-ask-form", onSubmit: this._onSubmit.bind(this), noValidate: true, autoComplete: "off" }, this._formInner()));
    }
    _formInner() {
        return this.props.resources.map(resource => {
            // ask for credentials if needed, or state why not
            const decodedUrl = decodeURIComponent(resource.url);
            const askReq = _askRequired(resource);
            const inputs = askReq ? this._inputs(resource.url) : [];
            const tokens = tokensFromUrl(resource.url);
            let reason = "";
            if (resource.init && this.props.options.cache) {
                reason = "already initialized";
            }
            else if (!tokens.length) {
                reason = "no template parameters";
            }
            const summary = `${resource.name}:${reason && ` ${reason}`}`;
            return [
                react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.ExpansionPanel, { className: "jfs-ask jfs-ask-panel", disabled: !!reason, expanded: !reason, key: `${resource.name}_panel` },
                    react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.ExpansionPanelSummary, { className: "jfs-ask jfs-ask-panel-summary" },
                        react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.Typography, null, summary),
                        !reason &&
                            react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.Tooltip, { title: decodedUrl },
                                react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.Typography, { noWrap: true }, decodedUrl))),
                    react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.ExpansionPanelDetails, { className: "jfs-ask jfs-ask-panel-details" }, inputs)),
            ];
        });
    }
    _inputs(url) {
        return tokensFromUrl(url).map(token => {
            var _a, _b, _c;
            return (react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.TextField, { className: "jfs-ask jfs-ask-input", autoFocus: true, fullWidth: true, key: `${url}_${token}`, label: token, margin: "dense", name: token, onChange: this._onChange(url).bind(this), type: ((_a = this.state.visibility[url]) === null || _a === void 0 ? void 0 : _a[token]) ? "text" : "password", value: ((_b = this.state.values[url]) === null || _b === void 0 ? void 0 : _b[token]) || "", InputProps: {
                    endAdornment: (react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.InputAdornment, { position: "end" },
                        react__WEBPACK_IMPORTED_MODULE_1__.createElement(_material_ui_core__WEBPACK_IMPORTED_MODULE_0__.IconButton, { onClick: this._onClickVisiblity(url, token).bind(this), onMouseDown: this._onMouseDownVisibility.bind(this), edge: "end" }, ((_c = this.state.visibility[url]) === null || _c === void 0 ? void 0 : _c[token]) ? (react__WEBPACK_IMPORTED_MODULE_1__.createElement(_icons__WEBPACK_IMPORTED_MODULE_2__.visibilityIcon.react, null)) : (react__WEBPACK_IMPORTED_MODULE_1__.createElement(_icons__WEBPACK_IMPORTED_MODULE_2__.visibilityOffIcon.react, null))))),
                } }));
        });
    }
    _onChange(url) {
        return function (event) {
            const target = event.target;
            this._setValue(url, target.name, target.value);
        };
    }
    _onClickVisiblity(url, key) {
        return function () {
            this._toggleVisibility(url, key);
        };
    }
    _onMouseDownVisibility(event) {
        event.preventDefault();
    }
    _onOpen() {
        this.setState({ open: true });
    }
    _onClose() {
        // close the dialog and blank the form
        this.setState(AskDialog.initialState({ options: this.state.options }));
        this.props.handleClose();
    }
    async _onSubmit(event) {
        event.preventDefault();
        this.props.handleSubmit(this.state.values);
        this._onClose();
    }
    _setValue(url, key, value) {
        const urlValues = { ...this.state.values[url], [key]: value };
        this.setState({
            values: { ...this.state.values, [url]: urlValues },
        });
    }
    _toggleVisibility(url, key) {
        var _a;
        const urlVis = {
            ...this.state.visibility[url],
            [key]: !((_a = this.state.visibility[url]) === null || _a === void 0 ? void 0 : _a[key]),
        };
        this.setState({
            visibility: { ...this.state.visibility, [url]: urlVis },
        });
    }
}
AskDialog.displayName = "AskDialog";
/**
 * A namespace for AskDialog statics.
 */
(function (AskDialog) {
    /**
     * The initial state for a new AskDialog
     */
    AskDialog.initialState = ({ open = false, options, }) => ({
        open,
        options: { ...options },
        values: {},
        visibility: {},
    });
})(AskDialog || (AskDialog = {}));


/***/ }),

/***/ "./lib/clipboard.js":
/*!**************************!*\
  !*** ./lib/clipboard.js ***!
  \**************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   JupyterClipboard: () => (/* binding */ JupyterClipboard)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _tree_finder_base__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @tree-finder/base */ "webpack/sharing/consume/default/@tree-finder/base/@tree-finder/base");
/* harmony import */ var _tree_finder_base__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_tree_finder_base__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _contents_utils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./contents_utils */ "./lib/contents_utils.js");
/******************************************************************************
 *
 * Copyright (c) 2019, the jupyter-fs authors.
 *
 * This file is part of the jupyter-fs library, distributed under the terms of
 * the Apache License 2.0.  The full license can be found in the LICENSE file.
 *
 */
/* eslint-disable @typescript-eslint/no-non-null-assertion */




class JupyterClipboard {
    constructor(tracker) {
        this._model = new _tree_finder_base__WEBPACK_IMPORTED_MODULE_2__.ClipboardModel();
        this._drive = new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.Drive();
        this._tracker = tracker;
        // eslint-disable-next-line @typescript-eslint/no-misused-promises
        this._model.deleteSub.subscribe(async (memo) => {
            await Promise.all(memo.map(s => this._onDelete(s)));
            const contentsModel = this._tracker.currentWidget.treefinder.model;
            const toRefresh = (0,_contents_utils__WEBPACK_IMPORTED_MODULE_3__.getRefreshTargets)(memo, contentsModel.root, true);
            this.model.refresh(contentsModel, toRefresh);
        });
        // eslint-disable-next-line @typescript-eslint/no-misused-promises
        this._model.pasteSub.subscribe(async ({ destination, doCut, memo }) => {
            const destPath = destination.kind === "dir" ? destination.path : destination.path.slice(0, -1);
            const destPathstr = _tree_finder_base__WEBPACK_IMPORTED_MODULE_2__.Path.fromarray(destPath);
            await Promise.all(memo.map(s => this._onPaste(s, destPathstr, doCut)));
            const contentsModel = this._tracker.currentWidget.treefinder.model;
            let toRefresh = (0,_contents_utils__WEBPACK_IMPORTED_MODULE_3__.getRefreshTargets)([destination], contentsModel.root, false);
            // Only refresh sources if cutting:
            if (doCut && toRefresh !== undefined) {
                const extra = (0,_contents_utils__WEBPACK_IMPORTED_MODULE_3__.getRefreshTargets)(memo, contentsModel.root, false);
                if (extra === undefined) {
                    toRefresh = undefined;
                }
                else {
                    toRefresh.push(...extra);
                }
            }
            this.model.refresh(contentsModel, toRefresh);
        });
    }
    refresh(tm, memo) {
        tm !== null && tm !== void 0 ? tm : (tm = this._tracker.currentWidget.treefinder.model);
        this.model.refresh(tm, memo);
    }
    // TODO: remove in favor of this.model.refreshSelection once tree-finder v0.0.14 is out
    refreshSelection(tm) {
        this.refresh(tm, tm.selection.map(x => x.row));
    }
    get model() {
        return this._model;
    }
    async _onDelete(src) {
        const srcPathstr = _tree_finder_base__WEBPACK_IMPORTED_MODULE_2__.Path.fromarray(src.path);
        try {
            await this._drive.delete(srcPathstr);
        }
        catch (err) {
            await (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)("Delete Failed", err);
        }
    }
    async _onPaste(src, destPathstr, doCut) {
        const srcPathstr = _tree_finder_base__WEBPACK_IMPORTED_MODULE_2__.Path.fromarray(src.path);
        try {
            await this._drive.copy(srcPathstr, destPathstr);
            if (doCut) {
                await this._drive.delete(srcPathstr);
            }
        }
        catch (err) {
            await (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)("Paste Error", err);
        }
    }
}


/***/ }),

/***/ "./lib/commands.js":
/*!*************************!*\
  !*** ./lib/commands.js ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   commandIDs: () => (/* binding */ commandIDs),
/* harmony export */   commandNames: () => (/* binding */ commandNames),
/* harmony export */   createDynamicCommands: () => (/* binding */ createDynamicCommands),
/* harmony export */   createStaticCommands: () => (/* binding */ createStaticCommands),
/* harmony export */   getFactories: () => (/* binding */ getFactories),
/* harmony export */   idFromResource: () => (/* binding */ idFromResource)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_algorithm__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/algorithm */ "webpack/sharing/consume/default/@lumino/algorithm");
/* harmony import */ var _lumino_algorithm__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_algorithm__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _tree_finder_base__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @tree-finder/base */ "webpack/sharing/consume/default/@tree-finder/base/@tree-finder/base");
/* harmony import */ var _tree_finder_base__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_tree_finder_base__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _treefinder__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./treefinder */ "./lib/treefinder.js");
/* harmony import */ var _contents_utils__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./contents_utils */ "./lib/contents_utils.js");
/* harmony import */ var _snippets__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./snippets */ "./lib/snippets.js");
/******************************************************************************
 *
 * Copyright (c) 2019, the jupyter-fs authors.
 *
 * This file is part of the jupyter-fs library, distributed under the terms of
 * the Apache License 2.0.  The full license can be found in the LICENSE file.
 *
 */
/* eslint-disable @typescript-eslint/no-non-null-assertion */










// define the command ids as a constant tuple
const commandNames = [
    "copy",
    "cut",
    "delete",
    "open",
    "openWith",
    "paste",
    "refresh",
    "rename",
    "download",
    "createFolder",
    "createFile",
    // "navigate",
    "copyFullPath",
    "copyRelativePath",
    "restore",
    "toggleColumnPath",
    "toggleColumn",
    "newLauncher",
];
const commandIDs = Object.fromEntries(commandNames.map(name => [name, `treefinder:${name}`]));
const COLUMN_NAMES = [
    "size",
    "last_modified",
    "writable",
    "mimetype",
];
function idFromResource(resource) {
    return [resource.name.split(" ").join(""), resource.drive].join("_");
}
const currentWidgetSelectionIsWritable = (tracker) => {
    var _a;
    if (!tracker.currentWidget) {
        return false;
    }
    const selection = (_a = tracker.currentWidget.treefinder.model) === null || _a === void 0 ? void 0 : _a.selection;
    if (selection) {
        return selection.every((x) => x.row.writable);
    }
    return false;
};
function toggleColumnCommandId(column) {
    return `${commandIDs.toggleColumn}-${column}`;
}
function _getRelativePaths(selectedFiles) {
    const allPaths = [];
    for (const file of selectedFiles) {
        const relativePath = file.getPathAtDepth(1).join("/");
        allPaths.push(relativePath);
    }
    return allPaths;
}
function _digestString(value) {
    return value.split("").reduce((a, b) => (((a << 5) - a) + b.charCodeAt(0)) | 0, 0).toString(16);
}
async function _commandKeyForSnippet(snippet) {
    return `jupyterfs:snippet-${snippet.label}-${_digestString(snippet.label + snippet.caption + snippet.pattern.source + snippet.template)}`;
}
function _openWithKeyForFactory(factory) {
    return `jupyterfs:openwith-${factory}`;
}
function _normalizedUrlForSnippet(content, baseUrl) {
    const path = (0,_contents_utils__WEBPACK_IMPORTED_MODULE_7__.splitPathstrDrive)(content.pathstr)[1];
    return `${baseUrl}/${path}${content.hasChildren ? "/" : ""}`;
}
/**
 * Create commands that will have the same IDs indepent of settings/resources
 *
 * These commands do not need to be recreated on settings/resource updates
 */
function createStaticCommands(app, tracker, clipboard) {
    return [
        app.commands.addCommand(commandIDs.copy, {
            execute: args => clipboard.model.copySelection(tracker.currentWidget.treefinder.model),
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.copyIcon,
            label: "Copy",
            isVisible: () => {
                var _a;
                const widget = tracker.currentWidget;
                if (!widget) {
                    return false;
                }
                // Copy of folders are unsupported
                if ((_a = widget.treefinder.model) === null || _a === void 0 ? void 0 : _a.selection.some(v => v.row.kind === "dir")) {
                    return false;
                }
                return true;
            },
            isEnabled: () => !!tracker.currentWidget,
        }),
        app.commands.addCommand(commandIDs.cut, {
            execute: args => clipboard.model.cutSelection(tracker.currentWidget.treefinder.model),
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.cutIcon,
            label: "Cut",
            isEnabled: () => currentWidgetSelectionIsWritable(tracker),
        }),
        app.commands.addCommand(commandIDs.delete, {
            execute: async (args) => {
                const treefinder = tracker.currentWidget.treefinder;
                const model = treefinder.model;
                const message = model.selection.length === 1
                    ? `Are you sure you want to permanently delete: ${model.selection[0].name}?`
                    : `Are you sure you want to permanently delete the ${model.selection.length} selected items?`;
                const result = await (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                    title: "Delete",
                    body: message,
                    buttons: [
                        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.cancelButton({ label: "Cancel" }),
                        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.warnButton({ label: "Delete" }),
                    ],
                    // By default focus on "Cancel" to protect from accidental deletion
                    defaultButton: 0,
                });
                if (!treefinder.isDisposed && result.button.accept) {
                    clipboard.model.deleteSelection(model);
                }
            },
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.closeIcon.bindprops({ stylesheet: "menuItem" }),
            label: "Delete",
            isEnabled: () => currentWidgetSelectionIsWritable(tracker),
        }),
        app.commands.addCommand(commandIDs.open, {
            execute: args => { var _a; return tracker.currentWidget.treefinder.model.openSub.next(((_a = tracker.currentWidget.treefinder.selection) === null || _a === void 0 ? void 0 : _a.map(c => c.row)) || []); },
            label: "Open",
            isEnabled: () => !!tracker.currentWidget,
        }),
        app.commands.addCommand(commandIDs.paste, {
            execute: args => clipboard.model.pasteSelection(tracker.currentWidget.treefinder.model),
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.pasteIcon,
            label: "Paste",
            isEnabled: () => !!tracker.currentWidget,
        }),
        app.commands.addCommand(commandIDs.rename, {
            execute: args => {
                const widget = tracker.currentWidget;
                const oldContent = widget.treefinder.selection[0];
                void _treefinder__WEBPACK_IMPORTED_MODULE_6__.TreeFinderSidebar.doRename(widget, oldContent).then(newContent => {
                    var _a;
                    (_a = widget.treefinder.model) === null || _a === void 0 ? void 0 : _a.renamerSub.next({ name: newContent.name, target: oldContent });
                    // TODO: Model state of TreeFinderWidget should be updated by renamerSub process.
                    oldContent.row = newContent;
                });
            },
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.editIcon,
            label: "Rename",
            isEnabled: () => currentWidgetSelectionIsWritable(tracker),
        }),
        app.commands.addCommand(commandIDs.download, {
            execute: async (args) => {
                const widget = tracker.currentWidget;
                const selection = widget.treefinder.selection;
                await Promise.allSettled(selection.map(s => widget.download(s.pathstr, s.hasChildren)));
            },
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.downloadIcon,
            label: "Download",
            isEnabled: () => {
                var _a, _b, _c;
                return !!((_c = (_b = (_a = tracker.currentWidget) === null || _a === void 0 ? void 0 : _a.treefinder.model) === null || _b === void 0 ? void 0 : _b.selection) === null || _c === void 0 ? void 0 : _c.some(s => !s.hasChildren));
            },
        }),
        app.commands.addCommand(commandIDs.createFolder, {
            execute: async (args) => {
                var _a;
                const widget = tracker.currentWidget;
                const model = widget.treefinder.model;
                let target = (_a = model.selectedLast) !== null && _a !== void 0 ? _a : model.root;
                if (!target.hasChildren) {
                    target = await (0,_contents_utils__WEBPACK_IMPORTED_MODULE_7__.getContentParent)(target, model.root);
                }
                const path = _tree_finder_base__WEBPACK_IMPORTED_MODULE_5__.Path.fromarray(target.row.path);
                let row;
                try {
                    row = await widget.treefinder.contentsProxy.newUntitled({
                        type: "directory",
                        path,
                    });
                }
                catch (e) {
                    void (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)("Could not create folder", e);
                    return;
                }
                target.invalidate();
                const content = await (0,_contents_utils__WEBPACK_IMPORTED_MODULE_7__.revealAndSelectPath)(model, row.path);
                // Is this really needed?
                model.refreshSub.next((0,_contents_utils__WEBPACK_IMPORTED_MODULE_7__.getRefreshTargets)([target.row], model.root) || []);
                // Scroll into view if not visible
                await _treefinder__WEBPACK_IMPORTED_MODULE_6__.TreeFinderSidebar.scrollIntoView(widget.treefinder, content.pathstr);
                const newContent = await _treefinder__WEBPACK_IMPORTED_MODULE_6__.TreeFinderSidebar.doRename(widget, content);
                model.renamerSub.next({ name: newContent.name, target: content });
                // TODO: Model state of TreeFinderWidget should be updated by renamerSub process.
                content.row = newContent;
            },
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.newFolderIcon,
            label: "New Folder",
            isEnabled: () => !!tracker.currentWidget,
        }),
        app.commands.addCommand(commandIDs.createFile, {
            execute: async (args) => {
                var _a;
                const widget = tracker.currentWidget;
                const model = widget.treefinder.model;
                let target = (_a = model.selectedLast) !== null && _a !== void 0 ? _a : model.root;
                if (!target.hasChildren) {
                    target = await (0,_contents_utils__WEBPACK_IMPORTED_MODULE_7__.getContentParent)(target, model.root);
                }
                const path = _tree_finder_base__WEBPACK_IMPORTED_MODULE_5__.Path.fromarray(target.row.path);
                let row;
                try {
                    row = await widget.treefinder.contentsProxy.newUntitled({
                        type: "file",
                        path,
                    });
                }
                catch (e) {
                    void (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)("Could not create file", e);
                    return;
                }
                target.invalidate();
                const content = await (0,_contents_utils__WEBPACK_IMPORTED_MODULE_7__.revealAndSelectPath)(model, row.path);
                // Is this really needed?
                model.refreshSub.next((0,_contents_utils__WEBPACK_IMPORTED_MODULE_7__.getRefreshTargets)([target.row], model.root) || []);
                // Scroll into view if not visible
                await _treefinder__WEBPACK_IMPORTED_MODULE_6__.TreeFinderSidebar.scrollIntoView(widget.treefinder, content.pathstr);
                const newContent = await _treefinder__WEBPACK_IMPORTED_MODULE_6__.TreeFinderSidebar.doRename(widget, content);
                model.renamerSub.next({ name: newContent.name, target: content });
                // TODO: Model state of TreeFinderWidget should be updated by renamerSub process.
                content.row = newContent;
            },
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.fileIcon,
            label: "New File",
            isEnabled: () => !!tracker.currentWidget,
        }),
        app.commands.addCommand(commandIDs.refresh, {
            execute: args => {
                if (args["selection"]) {
                    clipboard.refreshSelection(tracker.currentWidget.treefinder.model);
                }
                else {
                    clipboard.refresh(tracker.currentWidget.treefinder.model);
                }
            },
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.refreshIcon,
            label: args => args["selection"] ? "Refresh Selection" : "Refresh",
            isEnabled: () => !!tracker.currentWidget,
        }),
        app.commands.addCommand(commandIDs.copyFullPath, {
            execute: async (args) => {
                const widget = tracker.currentWidget;
                const trimEnd = (path) => path.trimEnd().replace(/\/+$/, "");
                const fullPaths = _getRelativePaths(widget.treefinder.selection).map(relativePath => { var _a; return [trimEnd((_a = widget.url) !== null && _a !== void 0 ? _a : ""), relativePath].join("/"); });
                await navigator.clipboard.writeText(fullPaths.join("\n"));
            },
            label: "Copy Full Path",
            isEnabled: () => !!tracker.currentWidget,
        }),
        app.commands.addCommand(commandIDs.copyRelativePath, {
            execute: async (args) => {
                const widget = tracker.currentWidget;
                const relativePaths = _getRelativePaths(widget.treefinder.selection);
                await navigator.clipboard.writeText(relativePaths.join("\n"));
            },
            label: "Copy Relative Path",
            isEnabled: () => !!tracker.currentWidget,
        }),
        app.commands.addCommand(commandIDs.toggleColumnPath, {
            execute: args => { },
            label: "path",
            isEnabled: () => false,
            isToggled: () => true,
        }),
        app.commands.addCommand(commandIDs.restore, {
            execute: async (args) => {
                const rootPath = args.rootPath;
                const dirsToOpen = rootPath.split("/");
                const sidebar = tracker.findByDrive(args.id);
                if (!sidebar) {
                    throw new Error(`Could not restore JupyterFS browser: ${args.id}`);
                }
                const treefinderwidget = sidebar.treefinder;
                const model = treefinderwidget.model;
                // If preferredDir not specified, proceed with the restore
                if (!sidebar.preferredDir) {
                    await (0,_contents_utils__WEBPACK_IMPORTED_MODULE_7__.openDirRecursive)(model, dirsToOpen);
                    await tracker.save(sidebar);
                }
            },
        }),
        app.commands.addCommand(commandIDs.newLauncher, {
            execute: async (args) => {
                void app.commands.execute("launcher:create");
            },
            label: "New Launcher",
            isEnabled: () => true,
        }),
    ].reduce((set, d) => {
        set.add(d);
        return set;
    }, new _lumino_disposable__WEBPACK_IMPORTED_MODULE_3__.DisposableSet());
}
/**
 * Create commands whose count/IDs depend on settings/resources
 */
async function createDynamicCommands(app, tracker, clipboard, resources, settings) {
    var _a;
    const columnCommands = [];
    const toggleState = {};
    const colsToDisplay = (_a = settings === null || settings === void 0 ? void 0 : settings.composite.display_columns) !== null && _a !== void 0 ? _a : ["size"];
    const columnsMenu = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__.Menu({ commands: app.commands });
    columnsMenu.title.label = "Show/Hide Columns";
    columnsMenu.title.icon = _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.filterListIcon;
    columnsMenu.addItem({ command: commandIDs.toggleColumnPath });
    for (const column of COLUMN_NAMES) {
        columnsMenu.addItem({ command: toggleColumnCommandId(column) });
        toggleState[column] = colsToDisplay.includes(column);
        columnCommands.push(app.commands.addCommand(toggleColumnCommandId(column), {
            execute: async (args) => {
                toggleState[column] = !toggleState[column];
                await (settings === null || settings === void 0 ? void 0 : settings.set("display_columns", COLUMN_NAMES.filter(k => toggleState[k])));
            },
            label: column,
            isToggleable: true,
            isToggled: () => toggleState[column],
        }));
    }
    const snippetsMenu = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__.Menu({ commands: app.commands });
    snippetsMenu.title.label = "Snippets";
    const snippets = await (0,_snippets__WEBPACK_IMPORTED_MODULE_8__.getAllSnippets)(settings);
    const snippetCommands = [];
    const snippetIds = new Set();
    for (const snippet of snippets) {
        const key = await _commandKeyForSnippet(snippet);
        if (snippetIds.has(key)) {
            console.warn("Discarding duplicate snippet", snippet);
            continue;
        }
        snippetIds.add(key);
        snippetsMenu.addItem({ command: key });
        snippetCommands.push(app.commands.addCommand(key, {
            execute: async (args) => {
                const sidebar = tracker.currentWidget;
                const content = sidebar.treefinder.selection[0];
                const instantiated = (0,_snippets__WEBPACK_IMPORTED_MODULE_8__.instantiateSnippet)(snippet.template, sidebar.url, sidebar.type, content.pathstr);
                await navigator.clipboard.writeText(instantiated);
            },
            label: snippet.label,
            caption: snippet.caption,
            isVisible: () => {
                const sidebar = tracker.currentWidget;
                const selection = sidebar === null || sidebar === void 0 ? void 0 : sidebar.treefinder.selection;
                // discard if not for backend type
                if (snippet.type !== "" && snippet.type !== (sidebar === null || sidebar === void 0 ? void 0 : sidebar.type)) {
                    return false;
                }
                // include if matches pattern
                if (selection === null || selection === void 0 ? void 0 : selection.length) {
                    return snippet.pattern.test(_normalizedUrlForSnippet(selection[0], sidebar.url));
                }
                return false;
            },
        }));
    }
    const openWithCommands = [];
    const openWithMenu = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__.Menu({ commands: app.commands });
    openWithMenu.title.label = "Open With";
    openWithMenu.id = "treefinder:open-with";
    const { docRegistry } = app;
    let items = [];
    function updateOpenWithMenu(contextMenu) {
        var _a, _b;
        const openWith = (_b = (_a = contextMenu.menu.items.find(item => {
            var _a;
            return item.type === "submenu" &&
                ((_a = item.submenu) === null || _a === void 0 ? void 0 : _a.id) === "treefinder:open-with";
        })) === null || _a === void 0 ? void 0 : _a.submenu) !== null && _b !== void 0 ? _b : null;
        if (!openWith) {
            return; // Bail early if the open with menu is not displayed
        }
        // clear the current menu items
        // items.forEach(item => item.dispose());
        items.length = 0;
        // Ensure that the menu is empty
        openWith.clearItems();
        // clear the commands
        openWithCommands.forEach(item => item.dispose());
        openWithCommands.length = 0;
        // get the widget factories that could be used to open all of the items
        // in the current filebrowser selection
        const widget = tracker.currentWidget;
        const treefinder = widget.treefinder;
        const model = treefinder.model;
        const factories = tracker.currentWidget
            ? intersection((0,_lumino_algorithm__WEBPACK_IMPORTED_MODULE_2__.map)(model.selection, i => getFactories(docRegistry, widget, i)))
            : new Set();
        // make new menu items from the widget factories
        items = [...factories].map(factory => {
            const key = _openWithKeyForFactory(factory.label || factory.name);
            const label = factory.label || factory.name;
            if (!app.commands.hasCommand(key)) {
                openWithCommands.push(app.commands.addCommand(key, {
                    execute: args => Promise.all(Array.from((0,_lumino_algorithm__WEBPACK_IMPORTED_MODULE_2__.map)(model.selection, item => app.commands.execute("docmanager:open", { path: _tree_finder_base__WEBPACK_IMPORTED_MODULE_5__.Path.fromarray(item.row.path), ...args })))),
                    label,
                    isVisible: () => true,
                }));
            }
            else {
                // Update label in case it has changed
                // eslint-disable-next-line no-console
                console.log("Skipping existing command:", key);
            }
            return openWith.addItem({
                args: { factory: factory.name, label: factory.label || factory.name },
                command: key,
            });
        });
    }
    app.contextMenu.opened.connect(updateOpenWithMenu);
    const selector = ".jp-tree-finder-sidebar";
    let contextMenuRank = 1;
    return [
        ...columnCommands,
        ...snippetCommands,
        // context menu items
        app.contextMenu.addItem({
            command: commandIDs.open,
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            type: "submenu",
            submenu: openWithMenu,
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            command: commandIDs.copy,
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            command: commandIDs.cut,
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            command: commandIDs.paste,
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            command: commandIDs.delete,
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            command: commandIDs.rename,
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            command: commandIDs.download,
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            type: "separator",
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            command: commandIDs.copyFullPath,
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            command: commandIDs.copyRelativePath,
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            type: "submenu",
            submenu: snippetsMenu,
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            type: "separator",
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            command: commandIDs.createFile,
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            command: commandIDs.createFolder,
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            type: "separator",
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            type: "submenu",
            submenu: columnsMenu,
            selector,
            rank: contextMenuRank++,
        }),
        app.contextMenu.addItem({
            args: { selection: true },
            command: commandIDs.refresh,
            selector,
            rank: contextMenuRank++,
        }),
    ].reduce((set, d) => {
        set.add(d);
        return set;
    }, new _lumino_disposable__WEBPACK_IMPORTED_MODULE_3__.DisposableSet());
}
function getFactories(docRegistry, widget, item) {
    const path = [widget.url.trimEnd().replace(/\/+$/, ""), item.getPathAtDepth(1).join("/")].join("/");
    const factories = docRegistry.preferredWidgetFactories(path);
    const notebookFactory = docRegistry.getWidgetFactory("notebook");
    if (notebookFactory &&
        item.row.kind === "notebook" &&
        factories.indexOf(notebookFactory) === -1) {
        factories.unshift(notebookFactory);
    }
    return factories;
}
function intersection(iterables) {
    let accumulator;
    for (const current of iterables) {
        // Initialize accumulator.
        if (accumulator === undefined) {
            accumulator = new Set(current);
            continue;
        }
        // Return early if empty.
        if (accumulator.size === 0) {
            return accumulator;
        }
        // Keep the intersection of accumulator and current.
        const intersection_set = new Set();
        for (const value of current) {
            if (accumulator.has(value)) {
                intersection_set.add(value);
            }
        }
        accumulator = intersection_set;
    }
    return accumulator !== null && accumulator !== void 0 ? accumulator : new Set();
}


/***/ }),

/***/ "./lib/contents_proxy.js":
/*!*******************************!*\
  !*** ./lib/contents_proxy.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ContentsProxy: () => (/* binding */ ContentsProxy)
/* harmony export */ });
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _tree_finder_base__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @tree-finder/base */ "webpack/sharing/consume/default/@tree-finder/base/@tree-finder/base");
/* harmony import */ var _tree_finder_base__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_tree_finder_base__WEBPACK_IMPORTED_MODULE_2__);



/**
 * Wrapper for a drive onto the contents manager.
 */
class ContentsProxy {
    constructor(contentsManager, drive, onGetChildren) {
        this.contentsManager = contentsManager;
        this.drive = drive;
        this.onGetChildren = onGetChildren;
    }
    async get(path, options) {
        path = ContentsProxy.toFullPath(path, this.drive);
        return ContentsProxy.toJupyterContentRow(await this.contentsManager.get(path, options), this.contentsManager, this.drive, this.onGetChildren);
    }
    async save(path, options) {
        path = ContentsProxy.toFullPath(path, this.drive);
        return ContentsProxy.toJupyterContentRow(await this.contentsManager.save(path, options), this.contentsManager, this.drive, this.onGetChildren);
    }
    async rename(path, newPath) {
        path = ContentsProxy.toFullPath(path, this.drive);
        newPath = ContentsProxy.toFullPath(newPath, this.drive);
        return ContentsProxy.toJupyterContentRow(await this.contentsManager.rename(path, newPath), this.contentsManager, this.drive, this.onGetChildren);
    }
    async newUntitled(options) {
        options.path = options.path && ContentsProxy.toFullPath(options.path, this.drive);
        return ContentsProxy.toJupyterContentRow(await this.contentsManager.newUntitled(options), this.contentsManager, this.drive, this.onGetChildren);
    }
    async downloadUrl(path) {
        path = ContentsProxy.toFullPath(path, this.drive);
        return await this.contentsManager.getDownloadUrl(path);
    }
}
(function (ContentsProxy) {
    function toFullPath(path, drive) {
        if (!drive || path.startsWith(`${drive}:`)) {
            if (path.startsWith(`${drive}:/`)) {
                return path.replace(`${drive}:/`, `${drive}:`);
            }
            return path;
        }
        else if (path.startsWith(`${drive}/`)) {
            return [drive, path.slice(drive.length + 1)].join(":");
        }
        else {
            return [drive, path].join(":");
        }
    }
    ContentsProxy.toFullPath = toFullPath;
    function toLocalPath(path) {
        const [first, ...rest] = path.split("/");
        return [first.split(":").pop(), ...rest].join("/");
    }
    ContentsProxy.toLocalPath = toLocalPath;
    function toJupyterContentRow(row, contentsManager, drive, onGetChildren) {
        const { path, type, ...rest } = row;
        const pathWithDrive = toFullPath(path, drive).replace(/\/$/, "");
        const kind = type === "directory" ? "dir" : type;
        return {
            path: _tree_finder_base__WEBPACK_IMPORTED_MODULE_2__.Path.toarray(pathWithDrive),
            kind,
            ...rest,
            ...(kind === "dir" ? {
                getChildren: async () => {
                    let contents;
                    const done = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.PromiseDelegate();
                    if (onGetChildren) {
                        const pathstr = _tree_finder_base__WEBPACK_IMPORTED_MODULE_2__.Path.toarray(pathWithDrive).join("/"); // maybe clean up the different path formats we have...
                        onGetChildren(pathstr, done.promise);
                    }
                    try {
                        contents = await contentsManager.get(pathWithDrive, { content: true });
                        done.resolve();
                    }
                    catch (error) {
                        void (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showErrorMessage)("Failed to get directory contents", error);
                        done.reject("Failed to get directory contents");
                        return [];
                    }
                    return contents.content.map(c => toJupyterContentRow(c, contentsManager, drive, onGetChildren));
                },
            } : {}),
        };
    }
    ContentsProxy.toJupyterContentRow = toJupyterContentRow;
})(ContentsProxy || (ContentsProxy = {}));


/***/ }),

/***/ "./lib/contents_utils.js":
/*!*******************************!*\
  !*** ./lib/contents_utils.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   getContentParent: () => (/* binding */ getContentParent),
/* harmony export */   getRefreshTargets: () => (/* binding */ getRefreshTargets),
/* harmony export */   openDirRecursive: () => (/* binding */ openDirRecursive),
/* harmony export */   revealAndSelectPath: () => (/* binding */ revealAndSelectPath),
/* harmony export */   revealPath: () => (/* binding */ revealPath),
/* harmony export */   splitPathstrDrive: () => (/* binding */ splitPathstrDrive)
/* harmony export */ });
/******************************************************************************
 *
 * Copyright (c) 2019, the jupyter-fs authors.
 *
 * This file is part of the jupyter-fs library, distributed under the terms of
 * the Apache License 2.0.  The full license can be found in the LICENSE file.
 *
 */
/* eslint-disable @typescript-eslint/no-non-null-assertion */
/**
 * Utilities for manipulating the tree-finder contents model
 */
/**
 * Walk the path from root, yielding all rows along the way
 *
 * @param path The path to walk to
 * @param root The root to start from
 */
async function* walkPath(path, root) {
    // Walk the path from the root
    const pathstr = path.join("/");
    if (!pathstr.startsWith(root.pathstr)) {
        throw new Error(`Path ${pathstr} not in ${root.pathstr}`);
    }
    let node = root;
    yield node;
    for (let i = root.row.path.length; i < path.length; ++i) {
        const children = await node.getChildren();
        const child = children === null || children === void 0 ? void 0 : children.find(c => c.name === path[i]);
        if (!child) {
            throw new Error(`Path ${pathstr} not in ${node.pathstr}`);
        }
        node = child;
        yield node;
    }
}
/**
 * Expand the contents nodes until path is exposed.
 *
 * This means that even if the final element of the path is a directory, its expanded state will
 * not change.
 *
 * @param contents The contents model that the path is in
 * @param path The path to expose, relative to the root (i.e. first entry matches path of root)
 */
async function revealPath(contents, path) {
    let node;
    const promises = [];
    for await (node of walkPath(path, contents.root)) {
        if (!node.isExpand && node.hasChildren) {
            promises.push(node.expand());
        }
    }
    await Promise.all(promises);
    return node;
}
/**
 * Expand the contents nodes until path is exposed, and select the node of that path.
 *
 * This means that even if the final element of the path is a directory, its expanded state will
 * not change.
 *
 * @param contents The contents model that the path is in
 * @param path The path to expose, relative to the root (i.e. first entry matches path of root)
 * @param add Whether or not to add the path to the current selection, or to replace the current selection @see TreeFinder.SelectionModel.select
 */
async function revealAndSelectPath(contents, path, add) {
    const node = await revealPath(contents, path);
    contents.selectionModel.select(node, add);
    return node;
}
/**
 * Recursively opens directories in a contents model
 *
 * @param model The contents model where directories are to be opened
 * @param path Array of directory names to be opened in order
 */
async function openDirRecursive(model, path) {
    const promises = [];
    for await (const node of walkPath(path, model.root)) {
        if (node.pathstr !== model.root.pathstr) {
            promises.push(model.openDir(node.row));
        }
    }
    await Promise.all(promises);
}
/**
 * Get the parent contents row for the given contents row.
 *
 * Note: This will cause contents API calls if any dir has been invalidated between root and the parent.
 *
 * @param child The content node's whose parent we are looking for
 * @param root The root node of the path
 */
async function getContentParent(child, root) {
    // Walk from the root to the parent
    let node;
    for await (node of walkPath(child.row.path.slice(0, -1), root)) {
        // no-op
    }
    return node;
}
/**
 * Get targets to use for a call to tree-finder's refresh
 *
 * @param invalidateTargets The targets that need to be refreshed
 * @param root The root node of the contents tree
 * @param targetParents Whether the parents are the ones that should be invalidated
 * @returns
 */
function getRefreshTargets(invalidateTargets, root, targetParents = false) {
    const rootRefreshThreshold = root.row.path.length + (targetParents ? 1 : 0);
    const rootNeedsRefresh = invalidateTargets.some(t => t.path.length <= rootRefreshThreshold + (t.getChildren ? 0 : 1));
    if (rootNeedsRefresh) {
        return undefined;
    }
    if (targetParents) {
        // tree-finder doesn't correctly refresh parents of folders, so we work around it for now
        // (in more detail, tree-finder will only refresh the folder if the entry does not have a
        // getChildren entry, go figure...)
        return invalidateTargets.map(t => ({ ...t, getChildren: undefined }));
    }
    return invalidateTargets;
}
/**
 * Split a "pathstr" into its drive and path components
 */
function splitPathstrDrive(pathstr) {
    const splitloc = pathstr.indexOf("/");
    if (splitloc === -1) {
        return [pathstr, ""];
    }
    // split, and trim leading forward slashes on the path component
    return [pathstr.slice(0, splitloc), pathstr.slice(splitloc + 1).replace(/^[/]*/, "")];
}


/***/ }),

/***/ "./lib/drag.js":
/*!*********************!*\
  !*** ./lib/drag.js ***!
  \*********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   DragDropWidget: () => (/* binding */ DragDropWidget),
/* harmony export */   DragDropWidgetBase: () => (/* binding */ DragDropWidgetBase),
/* harmony export */   DragWidget: () => (/* binding */ DragWidget),
/* harmony export */   DropWidget: () => (/* binding */ DropWidget),
/* harmony export */   TABLE_HEADER_MIME: () => (/* binding */ TABLE_HEADER_MIME),
/* harmony export */   belongsToUs: () => (/* binding */ belongsToUs),
/* harmony export */   findChild: () => (/* binding */ findChild)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_dragdrop__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/dragdrop */ "webpack/sharing/consume/default/@lumino/dragdrop");
/* harmony import */ var _lumino_dragdrop__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_dragdrop__WEBPACK_IMPORTED_MODULE_2__);
/******************************************************************************
 *
 * Copyright (c) 2019, the jupyter-fs authors.
 *
 * This file is part of the jupyter-fs library, distributed under the terms of
 * the Apache License 2.0.  The full license can be found in the LICENSE file.
 *
 */
/*
Originally copied from jupyter's nbdime package, under the following license terms:

This project is licensed under the terms of the Modified BSD License
(also known as New or Revised or 3-Clause BSD), as follows:

- Copyright (c) 2001-2015, IPython Development Team
- Copyright (c) 2015-, Jupyter Development Team

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

Neither the name of the Jupyter Development Team nor the names of its
contributors may be used to endorse or promote products derived from this
software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## About the Jupyter Development Team

The Jupyter Development Team is the set of all contributors to the Jupyter project.
This includes all of the Jupyter subprojects.

The core team that coordinates development on GitHub can be found here:
https://github.com/jupyter/.
*/




/**
 * The class name added to the DropWidget
 */
const DROP_WIDGET_CLASS = "jfs-DropWidget";
/**
 * The class name added to the DragWidget
 */
const DRAG_WIDGET_CLASS = "jfs-DragWidget";
/**
 * The class name added to something which can be used to drag a box
 */
const DRAG_HANDLE = "jfs-mod-dragHandle";
/**
 * The class name of the default drag handle
 */
const DEFAULT_DRAG_HANDLE_CLASS = "jfs-DragWidget-dragHandle";
/**
 * The class name added to a drop target.
 */
const DROP_TARGET_CLASS = "jfs-mod-dropTarget";
/**
 * The threshold in pixels to start a drag event.
 */
const DRAG_THRESHOLD = 5;
/**
 * The mime type for a table header drag object.
 */
const TABLE_HEADER_MIME = "application/x-jupyterfs-thead";
/**
 * Determine whether node is equal to or a descendant of our widget, and that it does
 * not belong to a nested drag widget.
 */
function belongsToUs(node, parentClass, parentNode) {
    let candidate = node;
    // Traverse DOM until drag widget encountered:
    while (candidate && !candidate.classList.contains(parentClass)) {
        candidate = candidate.parentElement;
    }
    return !!candidate && candidate === parentNode;
}
/**
 * Find the direct child node of `parent`, which has `node` as a descendant.
 * Alternatively, parent can be a collection of children.
 *
 * Returns null if not found.
 */
function findChild(parent, node) {
    // Work our way up the DOM to an element which has this node as parent
    const parentIsArray = Array.isArray(parent);
    const isDirectChild = (element) => {
        if (parentIsArray) {
            return parent.indexOf(element) > -1;
        }
        else {
            return element.parentElement === parent;
        }
    };
    let candidate = node;
    let child = null;
    while (candidate && candidate !== parent) {
        if (isDirectChild(candidate)) {
            child = candidate;
            break;
        }
        candidate = candidate.parentElement;
    }
    return child;
}
/**
 * A widget class which allows the user to drop mime data onto it.
 *
 * To complete the class, the following functions need to be implemented:
 *  - processDrop: Process pre-screened drop events
 *
 * The functionallity of the class can be extended by overriding the following
 * functions:
 *  - findDropTarget(): Override if anything other than the direct children
 *    of the widget's node are to be the drop targets.
 *
 * For maximum control, `evtDrop` can be overriden.
 */
class DropWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    /**
     * Construct a drop widget.
     */
    constructor(options = {}) {
        var _a;
        super(options);
        this.acceptDropsFromExternalSource =
            options.acceptDropsFromExternalSource === true;
        this.addClass(DROP_WIDGET_CLASS);
        this.acceptedDropMimeTypes = (_a = options.acceptedDropMimeTypes) !== null && _a !== void 0 ? _a : [];
    }
    /**
     * Handle the DOM events for the widget.
     *
     * @param event - The DOM event sent to the widget.
     *
     * #### Notes
     * This method implements the DOM `EventListener` interface and is
     * called in response to events on the drop widget's node. It should
     * not be called directly by user code.
     */
    handleEvent(event) {
        switch (event.type) {
            case "lm-dragenter":
                this._evtDragEnter(event);
                break;
            case "lm-dragleave":
                this._evtDragLeave(event);
                break;
            case "lm-dragover":
                this._evtDragOver(event);
                break;
            case "lm-drop":
                this.evtDrop(event);
                break;
            default:
                break;
        }
    }
    validateSource(event) {
        return this.acceptDropsFromExternalSource || event.source === this;
    }
    /**
     * Find a drop target from a given drag event target.
     *
     * Returns null if no valid drop target was found.
     *
     * The default implementation returns the direct child that is the parent of
     * `node`, or `node` if it is itself a direct child. It also checks that the
     * needed mime type is included
     */
    findDropTarget(input, mimeData) {
        if (!this.acceptedDropMimeTypes.some(mimetype => mimeData.hasData(mimetype))) {
            return null;
        }
        if (this._isValidTargetHeader(input, mimeData.getData(TABLE_HEADER_MIME))) {
            input.classList.add(DROP_TARGET_CLASS);
        }
        else {
            return null;
        }
        // No need to findChild for reordering of columns
        if (mimeData.types().includes(TABLE_HEADER_MIME)) {
            return input;
        }
        else {
            return findChild(this.node, input);
        }
    }
    /**
     * Handle the `'lm-drop'` event for the widget.
     *
     * Responsible for pre-processing event before calling `processDrop`.
     *
     * Should normally only be overriden if you cannot achive your goal by
     * other overrides.
     */
    evtDrop(event) {
        let target = event.target;
        while (target && target.parentElement) {
            if (target.classList.contains(DROP_TARGET_CLASS)) {
                target.classList.remove(DROP_TARGET_CLASS);
                break;
            }
            target = target.parentElement;
        }
        if (!target || !belongsToUs(target, DROP_WIDGET_CLASS, this.node)) {
            // Ignore event
            return;
        }
        // If configured to, only accept internal moves:
        if (!this.validateSource(event)) {
            event.dropAction = "none";
            event.preventDefault();
            event.stopPropagation();
            return;
        }
        this.processDrop(target, event);
    }
    /**
     * Handle `after_attach` messages for the widget.
     */
    onAfterAttach(msg) {
        const node = this.node;
        node.addEventListener("lm-dragenter", this);
        node.addEventListener("lm-dragleave", this);
        node.addEventListener("lm-dragover", this);
        node.addEventListener("lm-drop", this);
    }
    /**
     * Handle `before_detach` messages for the widget.
     */
    onBeforeDetach(msg) {
        const node = this.node;
        node.removeEventListener("lm-dragenter", this);
        node.removeEventListener("lm-dragleave", this);
        node.removeEventListener("lm-dragover", this);
        node.removeEventListener("lm-drop", this);
    }
    /**
     * Handle the `'lm-dragenter'` event for the widget.
     */
    _evtDragEnter(event) {
        if (!this.validateSource(event)) {
            return;
        }
        const target = this.findDropTarget(event.target, event.mimeData);
        if (target === null) {
            return;
        }
        this._clearDropTarget();
        target.classList.add(DROP_TARGET_CLASS);
        event.preventDefault();
        event.stopPropagation();
    }
    /**
     * Handle the `'lm-dragleave'` event for the widget.
     */
    _evtDragLeave(event) {
        event.preventDefault();
        event.stopPropagation();
        this._clearDropTarget();
    }
    /**
     * Handle the `'lm-dragover'` event for the widget.
     */
    _evtDragOver(event) {
        if (!this.validateSource(event)) {
            return;
        }
        this._clearDropTarget();
        const target = this.findDropTarget(event.target, event.mimeData);
        if (target === null) {
            return;
        }
        event.preventDefault();
        event.stopPropagation();
        event.dropAction = event.proposedAction;
    }
    /**
     * Checks if the target is a header, and it is not 'path' or itself
     */
    _isValidTargetHeader(target, draggedColumn) {
        return target.classList.contains("tf-header-name") &&
            target.innerText !== draggedColumn &&
            target.innerText !== "path";
    }
    /**
     * Clear existing drop target from out children.
     *
     * #### Notes
     * This function assumes there are only one active drop target
     */
    _clearDropTarget() {
        const elements = this.node.getElementsByClassName(DROP_TARGET_CLASS);
        if (elements.length) {
            elements[0].classList.remove(DROP_TARGET_CLASS);
        }
    }
}
/**
 * An internal base class for implementing drag operations on top
 * of drop class.
 */
class DragDropWidgetBase extends DropWidget {
    /**
     * Construct a drag and drop base widget.
     */
    constructor(options = {}) {
        super(options);
        /**
         * Drag data stored in _startDrag
         */
        this.drag = null;
        this.dragHandleClass = DRAG_HANDLE;
        this.defaultSupportedActions = "all";
        this.defaultProposedAction = "move";
        /**
         * Data stored on mouse down to determine if drag treshold has
         * been overcome, and to initialize drag once it has.
         */
        this._clickData = null;
        this.addClass(DRAG_WIDGET_CLASS);
    }
    /**
     * Dispose of the resources held by the directory listing.
     */
    dispose() {
        this.drag = null;
        this._clickData = null;
        super.dispose();
    }
    /**
     * Handle the DOM events for the widget.
     *
     * @param event - The DOM event sent to the widget.
     *
     * #### Notes
     * This method implements the DOM `EventListener` interface and is
     * called in response to events on the drag widget's node. It should
     * not be called directly by user code.
     */
    handleEvent(event) {
        switch (event.type) {
            case "mousedown":
                this._evtDragMousedown(event);
                break;
            case "mouseup":
                this._evtDragMouseup(event);
                break;
            case "mousemove":
                this._evtDragMousemove(event);
                break;
            default:
                super.handleEvent(event);
                break;
        }
    }
    /**
     * Finds the drag target (the node to move) from a drag handle.
     *
     * Returns null if no valid drag target was found.
     *
     * The default implementation returns the handle directly.
     */
    findDragTarget(handle) {
        return handle;
    }
    /**
     * Returns the drag image to use when dragging using the given handle.
     *
     * The default implementation returns a clone of the drag target.
     */
    getDragImage(handle) {
        const target = this.findDragTarget(handle);
        if (target) {
            return target.cloneNode(true);
        }
        return null;
    }
    /**
     * Called when a drag has completed with this widget as a source
     */
    onDragComplete(action) {
        this.drag = null;
    }
    /**
     * Handle `after_attach` messages for the widget.
     */
    onAfterAttach(msg) {
        const node = this.node;
        node.addEventListener("mousedown", this);
        super.onAfterAttach(msg);
    }
    /**
     * Handle `before_detach` messages for the widget.
     */
    onBeforeDetach(msg) {
        const node = this.node;
        node.removeEventListener("click", this);
        node.removeEventListener("dblclick", this);
        document.removeEventListener("mousemove", this, true);
        document.removeEventListener("mouseup", this, true);
        super.onBeforeDetach(msg);
    }
    /**
     * Start a drag event.
     *
     * Called when dragging and DRAG_THRESHOLD is met.
     *
     * Should normally only be overriden if you cannot achieve your goal by
     * other overrides.
     */
    startDrag(handle, clientX, clientY) {
        // Create the drag image.
        const dragImage = this.getDragImage(handle);
        // Set up the drag event.
        this.drag = new _lumino_dragdrop__WEBPACK_IMPORTED_MODULE_2__.Drag({
            dragImage: dragImage || undefined,
            mimeData: new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__.MimeData(),
            supportedActions: this.defaultSupportedActions,
            proposedAction: this.defaultProposedAction,
            source: this,
        });
        this.addMimeData(handle, this.drag.mimeData);
        // Start the drag and remove the mousemove listener.
        void this.drag.start(clientX, clientY).then(action => this.onDragComplete(action));
        document.removeEventListener("mousemove", this, true);
        document.removeEventListener("mouseup", this, true);
    }
    /**
     * Check if node, or any of nodes ancestors are a drag handle
     *
     * If it is a drag handle, it returns the handle, if not returns null.
     */
    _findDragHandle(node) {
        let handle = null;
        // Traverse up DOM to check if click is on a drag handle
        let candidate = node;
        while (candidate && candidate !== this.node) {
            if (candidate.classList.contains(this.dragHandleClass)) {
                handle = candidate;
                break;
            }
            candidate = candidate.parentElement;
        }
        // Finally, check that handle does not belong to a nested drag widget
        if (handle !== null && !belongsToUs(handle, DRAG_WIDGET_CLASS, this.node)) {
            // Handle belongs to a nested drag widget:
            handle = null;
        }
        return handle;
    }
    /**
     * Handle the `'mousedown'` event for the widget.
     */
    _evtDragMousedown(event) {
        const target = event.target;
        const handle = this._findDragHandle(target);
        if (handle === null) {
            return;
        }
        // Left mouse press for drag start.
        if (event.button === 0) {
            this._clickData = { pressX: event.clientX, pressY: event.clientY,
                handle };
            document.addEventListener("mouseup", this, true);
            document.addEventListener("mousemove", this, true);
            event.preventDefault();
        }
    }
    /**
     * Handle the `'mouseup'` event for the widget.
     */
    _evtDragMouseup(event) {
        if (event.button !== 0 || !this.drag) {
            document.removeEventListener("mousemove", this, true);
            document.removeEventListener("mouseup", this, true);
            this.drag = null;
            return;
        }
        event.preventDefault();
        event.stopPropagation();
    }
    /**
     * Handle the `'mousemove'` event for the widget.
     */
    _evtDragMousemove(event) {
        // Bail if we are already dragging.
        if (this.drag) {
            return;
        }
        event.preventDefault();
        event.stopPropagation();
        // Check for a drag initialization.
        const data = this._clickData;
        if (!data) {
            throw new Error("Missing drag data");
        }
        const dx = Math.abs(event.clientX - data.pressX);
        const dy = Math.abs(event.clientY - data.pressY);
        if (dx < DRAG_THRESHOLD && dy < DRAG_THRESHOLD) {
            return;
        }
        this.startDrag(data.handle, event.clientX, event.clientY);
        this._clickData = null;
    }
}
/**
 * A widget which allows the user to initiate drag operations.
 *
 * Any descendant element with the drag handle class `'jfs-mod-dragHandle'`
 * will serve as a handle that can be used for dragging. If DragWidgets are
 * nested, handles will only belong to the closest parent DragWidget. For
 * convenience, the functions `makeHandle`, `unmakeHandle` and
 * `createDefaultHandle` can be used to indicate which elements should be
 * made handles. `createDefaultHandle` will create a new element as a handle
 * with a default styling class applied. Optionally, `childrenAreDragHandles`
 * can be set to indicate that all direct children are themselve drag handles.
 *
 * To complete the class, the following functions need to be implemented:
 * - addMimeData: Adds mime data to new drag events
 *
 * The functionallity of the class can be extended by overriding the following
 * functions:
 *  - findDragTarget(): Override if anything other than the direct children
 *    of the widget's node are to be drag targets.
 *  - getDragImage: Override to change the drag image (the default is a
 *    copy of the drag target).
 *  - onDragComplete(): Callback on drag source when a drag has completed.
 */
class DragWidget extends DragDropWidgetBase {
    /**
     * Construct a drag widget.
     */
    constructor(options = {}) {
        // Implementation removes DropWidget options
        super(options);
    }
    /**
     * No-op on DragWidget, as it does not support dropping
     */
    processDrop(dropTarget, event) {
        // Intentionally empty
    }
    /**
     * Simply returns null for DragWidget, as it does not support dropping
     */
    findDropTarget(input, mimeData) {
        return null;
    }
}
/**
 * A widget which allows the user to rearrange widgets in the widget by
 * drag and drop. An internal drag and drop of a widget will cause it
 * to be inserted (by `insertWidget`) in the index of the widget it was
 * dropped on.
 *
 * Any descendant element with the drag handle class `'jfs-mod-dragHandle'`
 * will serve as a handle that can be used for dragging. If DragWidgets are
 * nested, handles will only belong to the closest parent DragWidget. For
 * convenience, the functions `makeHandle`, `unmakeHandle` and
 * `createDefaultHandle` can be used to indicate which elements should be
 * made handles. `createDefaultHandle` will create a new element as a handle
 * with a default styling class applied. Optionally, `childrenAreDragHandles`
 * can be set to indicate that all direct children are themselve drag handles.
 *
 * The functionallity of the class can be extended by overriding the following
 * functions:
 *  - addMimeData: Override to add other drag data to the mime bundle.
 *    This is often a necessary step for allowing dragging to external
 *    drop targets.
 *  - processDrop: Override if you need to handle other mime data than the
 *    default. For allowing drops from external sources, the field
 *    `acceptDropsFromExternalSource` should be set as well.
 *  - findDragTarget(): Override if anything other than the direct children
 *    of the widget's node are to be drag targets.
 *  - findDropTarget(): Override if anything other than the direct children
 *    of the widget's node are to be the drop targets.
 *  - getIndexOfChildNode(): Override to change the key used to represent
 *    the drag and drop target (default is index of child widget).
 *  - move(): Override to change how a move is handled.
 *  - getDragImage: Override to change the drag image (the default is a
 *    copy of the drag target).
 *  - onDragComplete(): Callback on drag source when a drag has completed.
 *
 * To drag and drop other things than all direct children, the following functions
 * should be overriden: `findDragTarget`, `findDropTarget` and possibly
 * `getIndexOfChildNode` and `move` to allow for custom to/from keys.
 *
 * For maximum control, `startDrag` and `evtDrop` can be overriden.
 */
class DragDropWidget extends DragDropWidgetBase {
    /**
     * Processes a drop event.
     *
     * This function is called after checking:
     *  - That the `dropTarget` is a valid drop target
     *  - The value of `event.source` if `acceptDropsFromExternalSource` is false
     *
     * The default implementation assumes calling `getIndexOfChildNode` with
     * `dropTarget` will be valid. It will call `move` with that index as `to`,
     * and the index stored in the mime data as `from`.
     *
     * Override this if you need to handle other mime data than the default.
     */
    processDrop(dropTarget, event) {
        if (!DropWidget.isValidAction(event.supportedActions, "move") ||
            event.proposedAction === "none") {
            // The default implementation only handles move action
            // OR Accept proposed none action, and perform no-op
            event.dropAction = "none";
            event.preventDefault();
            event.stopPropagation();
            return;
        }
        if (!this.validateSource(event)) {
            // Source indicates external drop, incorrect use in subclass
            throw new Error("Invalid source!");
        }
        // We have an acceptable drop, handle:
        const action = this.move(event.mimeData, dropTarget);
        event.preventDefault();
        event.stopPropagation();
        event.dropAction = action;
    }
}
/**
 * The namespace for the `DropWidget` class statics.
 */
(function (DropWidget) {
    /**
     * Validate a drop action against a SupportedActions type
     */
    function isValidAction(supported, action) {
        switch (supported) {
            case "all":
                return true;
            case "link-move":
                return action === "move" || action === "link";
            case "copy-move":
                return action === "move" || action === "copy";
            case "copy-link":
                return action === "link" || action === "copy";
            default:
                return action === supported;
        }
    }
    DropWidget.isValidAction = isValidAction;
})(DropWidget || (DropWidget = {}));
/**
 * The namespace for the `DragWidget` class statics.
 */
(function (DragWidget) {
    /**
     * Mark a widget as a drag handle.
     *
     * Using this, any child-widget can be a drag handle, as long as mouse events
     * are propagated from it to the DragWidget.
     */
    function makeHandle(handle) {
        handle.addClass(DRAG_HANDLE);
    }
    DragWidget.makeHandle = makeHandle;
    /**
     * Unmark a widget as a drag handle
     */
    function unmakeHandle(handle) {
        handle.removeClass(DRAG_HANDLE);
    }
    DragWidget.unmakeHandle = unmakeHandle;
    /**
     * Create a default handle widget for dragging (see styling in DragWidget.css).
     *
     * The handle will need to be styled to ensure a minimum size
     */
    function createDefaultHandle() {
        const widget = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget();
        widget.addClass(DEFAULT_DRAG_HANDLE_CLASS);
        makeHandle(widget);
        return widget;
    }
    DragWidget.createDefaultHandle = createDefaultHandle;
})(DragWidget || (DragWidget = {}));


/***/ }),

/***/ "./lib/filesystem.js":
/*!***************************!*\
  !*** ./lib/filesystem.js ***!
  \***************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   FSComm: () => (/* binding */ FSComm)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);
/******************************************************************************
 *
 * Copyright (c) 2019, the jupyter-fs authors.
 *
 * This file is part of the jupyter-fs library, distributed under the terms of
 * the Apache License 2.0.  The full license can be found in the LICENSE file.
 *
 */


class FSCommBase {
    constructor() {
        this._settings = undefined;
    }
    get baseUrl() {
        return this.settings.baseUrl;
    }
    get resourcesUrl() {
        return _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(this.baseUrl, "jupyterfs/resources");
    }
    get settings() {
        if (!this._settings) {
            this._settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
        }
        return this._settings;
    }
}
class FSComm extends FSCommBase {
    static get instance() {
        if (FSComm._instance === undefined) {
            FSComm._instance = new FSComm();
        }
        return FSComm._instance;
    }
    async getResourcesRequest() {
        const settings = this.settings;
        const fullUrl = this.resourcesUrl;
        return _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(fullUrl, { method: "GET" }, settings).then(response => {
            if (response.status !== 200) {
                return response.text().then(data => {
                    throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data);
                });
            }
            return response.json();
        });
    }
    async initResourceRequest(args) {
        const settings = this.settings;
        const fullUrl = this.resourcesUrl;
        return _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(fullUrl, {
            body: JSON.stringify(args),
            headers: {
                "Content-Type": "application/json",
            },
            method: "POST",
        }, settings).then(response => {
            if (response.status !== 200) {
                return response.text().then(data => {
                    throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data);
                });
            }
            return response.json();
        });
    }
}


/***/ }),

/***/ "./lib/icons.js":
/*!**********************!*\
  !*** ./lib/icons.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   driveIcon: () => (/* binding */ driveIcon),
/* harmony export */   fileTreeIcon: () => (/* binding */ fileTreeIcon),
/* harmony export */   jupyterFsIcon: () => (/* binding */ jupyterFsIcon),
/* harmony export */   visibilityIcon: () => (/* binding */ visibilityIcon),
/* harmony export */   visibilityOffIcon: () => (/* binding */ visibilityOffIcon)
/* harmony export */ });
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _style_icons_drive_svg__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../style/icons/drive.svg */ "./style/icons/drive.svg");
/* harmony import */ var _style_icons_file_tree_svg__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../style/icons/file-tree.svg */ "./style/icons/file-tree.svg");
/* harmony import */ var _style_icons_jupyter_fs_svg__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../style/icons/jupyter-fs.svg */ "./style/icons/jupyter-fs.svg");
/* harmony import */ var _style_icons_visibility_svg__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../style/icons/visibility.svg */ "./style/icons/visibility.svg");
/* harmony import */ var _style_icons_visibility_off_svg__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../style/icons/visibility-off.svg */ "./style/icons/visibility-off.svg");
/******************************************************************************
 *
 * Copyright (c) 2019, the jupyter-fs authors.
 *
 * This file is part of the jupyter-fs library, distributed under the terms of
 * the Apache License 2.0.  The full license can be found in the LICENSE file.
 *
 */






const driveIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({ name: "jfs:drive", svgstr: _style_icons_drive_svg__WEBPACK_IMPORTED_MODULE_1__ });
const fileTreeIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({ name: "jfs:file-tree", svgstr: _style_icons_file_tree_svg__WEBPACK_IMPORTED_MODULE_2__ });
const jupyterFsIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({ name: "jfs:jupyter-fs", svgstr: _style_icons_jupyter_fs_svg__WEBPACK_IMPORTED_MODULE_3__ });
const visibilityIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({ name: "jfs:visibility", svgstr: _style_icons_visibility_svg__WEBPACK_IMPORTED_MODULE_4__ });
const visibilityOffIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({ name: "jfs:visibility-off", svgstr: _style_icons_visibility_off_svg__WEBPACK_IMPORTED_MODULE_5__ });


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   browser: () => (/* binding */ browser),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   progressStatus: () => (/* binding */ progressStatus)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/docmanager */ "webpack/sharing/consume/default/@jupyterlab/docmanager");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/statusbar */ "webpack/sharing/consume/default/@jupyterlab/statusbar");
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var semver__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! semver */ "webpack/sharing/consume/default/semver/semver");
/* harmony import */ var semver__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(semver__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var _commands__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./commands */ "./lib/commands.js");
/* harmony import */ var _progress__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./progress */ "./lib/progress.js");
/* harmony import */ var _settings__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./settings */ "./lib/settings.js");
/* harmony import */ var _snippets__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./snippets */ "./lib/snippets.js");
/* harmony import */ var _treefinder__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ./treefinder */ "./lib/treefinder.js");
/* harmony import */ var _tokens__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ./tokens */ "./lib/tokens.js");
/* harmony import */ var _resources__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! ./resources */ "./lib/resources.js");
/******************************************************************************
 *
 * Copyright (c) 2019, the jupyter-fs authors.
 *
 * This file is part of the jupyter-fs library, distributed under the terms of
 * the Apache License 2.0.  The full license can be found in the LICENSE file.
 *
 */
/* eslint-disable @typescript-eslint/no-non-null-assertion */















// tslint:disable: variable-name
const BROWSER_ID = "jupyter-fs:plugin";
const browser = {
    autoStart: true,
    id: BROWSER_ID,
    requires: [
        _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_2__.IDocumentManager,
        _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.JupyterFrontEnd.IPaths,
        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.IWindowResolver,
        _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILayoutRestorer,
        _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.IRouter,
        _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3__.ISettingRegistry,
        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.IThemeManager,
    ],
    optional: [_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_6__.IFormRendererRegistry],
    provides: _tokens__WEBPACK_IMPORTED_MODULE_13__.ITreeFinderMain,
    async activate(app, manager, paths, resolver, restorer, router, settingRegistry, themeManager, editorRegistry) {
        var _a;
        const widgetMap = {};
        let commands;
        // Attempt to load application settings
        let settings;
        try {
            settings = await settingRegistry.load(BROWSER_ID);
        }
        catch (error) {
            // eslint-disable-next-line no-console
            console.warn(`Failed to load settings for the jupyter-fs extension.\n${error}`);
            return { tracker: _treefinder__WEBPACK_IMPORTED_MODULE_12__.TreeFinderSidebar.tracker };
        }
        // Migrate any old settings
        const initialOptions = settings === null || settings === void 0 ? void 0 : settings.composite.options;
        if ((settings && semver__WEBPACK_IMPORTED_MODULE_7__.lt((initialOptions === null || initialOptions === void 0 ? void 0 : initialOptions.writtenVersion) || "0.0.0", settings.version))) {
            settings = await (0,_settings__WEBPACK_IMPORTED_MODULE_10__.migrateSettings)(settings);
        }
        if (editorRegistry) {
            editorRegistry.addRenderer(`${BROWSER_ID}.snippets`, { fieldRenderer: _snippets__WEBPACK_IMPORTED_MODULE_11__.snippetFormRender });
        }
        let columns = (_a = settings === null || settings === void 0 ? void 0 : settings.composite.display_columns) !== null && _a !== void 0 ? _a : ["size"];
        const sharedSidebarProps = {
            app,
            manager,
            paths,
            resolver,
            restorer,
            router,
            columns,
            settings,
        };
        (0,_commands__WEBPACK_IMPORTED_MODULE_8__.createStaticCommands)(app, _treefinder__WEBPACK_IMPORTED_MODULE_12__.TreeFinderSidebar.tracker, _treefinder__WEBPACK_IMPORTED_MODULE_12__.TreeFinderSidebar.clipboard);
        async function refreshWidgets({ resources, options }) {
            var _a;
            if (options.verbose) {
                // eslint-disable-next-line no-console
                console.info(`jupyter-fs frontend received resources:\n${JSON.stringify(resources)}`);
            }
            columns = (_a = settings === null || settings === void 0 ? void 0 : settings.composite.display_columns) !== null && _a !== void 0 ? _a : ["size"];
            sharedSidebarProps.columns = columns;
            // create the fs resource frontends (ie FileTree instances)
            for (const r of resources) {
                // make one composite disposable for all fs resource frontends
                const id = (0,_commands__WEBPACK_IMPORTED_MODULE_8__.idFromResource)(r);
                let w = widgetMap[id];
                if (!w || w.isDisposed) {
                    const sidebarProps = { ...sharedSidebarProps, url: r.url, type: r.type, settings: settings };
                    w = _treefinder__WEBPACK_IMPORTED_MODULE_12__.TreeFinderSidebar.sidebarFromResource(r, sidebarProps);
                    widgetMap[id] = w;
                }
                else {
                    w.treefinder.columns = columns;
                }
            }
            commands = await (0,_commands__WEBPACK_IMPORTED_MODULE_8__.createDynamicCommands)(app, _treefinder__WEBPACK_IMPORTED_MODULE_12__.TreeFinderSidebar.tracker, _treefinder__WEBPACK_IMPORTED_MODULE_12__.TreeFinderSidebar.clipboard, resources, settings);
        }
        async function refresh() {
            var _a, _b;
            // get user settings from json file
            let resources = ((_a = settings === null || settings === void 0 ? void 0 : settings.composite.resources) !== null && _a !== void 0 ? _a : []).map(_settings__WEBPACK_IMPORTED_MODULE_10__.unpartialResource);
            const options = (_b = settings === null || settings === void 0 ? void 0 : settings.composite.options) !== null && _b !== void 0 ? _b : {};
            function cleanup(all = false) {
                if (commands) {
                    commands.dispose();
                    commands = undefined;
                }
                const keys = resources.map(_commands__WEBPACK_IMPORTED_MODULE_8__.idFromResource);
                for (const key of Object.keys(widgetMap)) {
                    if (all || keys.indexOf(key) === -1) {
                        widgetMap[key].dispose();
                        delete widgetMap[key];
                    }
                }
            }
            try {
                resources = (await (0,_resources__WEBPACK_IMPORTED_MODULE_14__.initResources)(resources, options)).filter(r => r.init);
                cleanup();
                await refreshWidgets({ resources, options });
            }
            catch (e) {
                console.error("Failed to refresh widgets!", e);
                cleanup(true);
            }
        }
        // when ready, restore using command
        const refreshed = refresh();
        void restorer.restore(_treefinder__WEBPACK_IMPORTED_MODULE_12__.TreeFinderSidebar.tracker, {
            command: _commands__WEBPACK_IMPORTED_MODULE_8__.commandIDs.restore,
            args: widget => {
                var _a;
                return ({
                    id: widget.id,
                    rootPath: (_a = widget.treefinder.model) === null || _a === void 0 ? void 0 : _a.root.pathstr,
                });
            },
            name: widget => widget.id,
            when: refreshed,
        });
        if (settings) {
            // rerun setup whenever relevant settings change
            settings.changed.connect(() => {
                void refresh();
            });
        }
        // Inject lab icons
        const style = document.createElement("style");
        style.setAttribute("id", "jupyter-fs-icon-inject");
        // Hackish, but needed since free-finder insists on pseudo elements for icons.
        function iconStyleContent(folderStr, fileStr, notebookStr) {
            // Note: We aren't able to style the hover/select colors with this.
            return `
      .jp-tree-finder {
        --tf-dir-icon: url('data:image/svg+xml,${encodeURIComponent(folderStr)}');
        --tf-file-icon: url('data:image/svg+xml,${encodeURIComponent(fileStr)}');
        --tf-notebook-icon: url('data:image/svg+xml,${encodeURIComponent(notebookStr)}');
      }
      `;
        }
        let initialThemeLoad = true;
        themeManager.themeChanged.connect(() => {
            // Update SVG icon fills (since we put them in pseudo-elements we cannot style with CSS)
            const primary = getComputedStyle(document.documentElement).getPropertyValue("--jp-ui-font-color1");
            style.textContent = iconStyleContent(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_6__.folderIcon.svgstr.replace(/fill="([^"]{0,7})"/, `fill="${primary}"`), _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_6__.fileIcon.svgstr.replace(/fill="([^"]{0,7})"/, `fill="${primary}"`), _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_6__.notebookIcon.svgstr.replace(/fill="([^"]{0,7})"/, `fill="${primary}"`));
            // Refresh widgets in case font/border sizes etc have changed
            if (initialThemeLoad) {
                initialThemeLoad = false;
                // Don't refresh on first load since we will do it below after initial creation
                // in the onAfterAttach lifecycle method.
            }
            else {
                Object.keys(widgetMap).map(key => widgetMap[key].treefinder.load());
            }
        });
        style.textContent = iconStyleContent(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_6__.folderIcon.svgstr, _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_6__.fileIcon.svgstr, _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_6__.notebookIcon.svgstr);
        document.head.appendChild(style);
        // eslint-disable-next-line no-console
        console.log("JupyterLab extension jupyter-fs is activated!");
        return { tracker: _treefinder__WEBPACK_IMPORTED_MODULE_12__.TreeFinderSidebar.tracker };
    },
};
const PROGRESS_ID = "jupyter-fs:progress";
const progressStatus = {
    autoStart: true,
    id: PROGRESS_ID,
    requires: [
        _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_5__.ITranslator,
    ],
    optional: [
        _tokens__WEBPACK_IMPORTED_MODULE_13__.ITreeFinderMain,
        _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_4__.IStatusBar,
    ],
    activate(app, translator, main, statusbar) {
        if (!statusbar || !main) {
            return;
        }
        const item = new _progress__WEBPACK_IMPORTED_MODULE_9__.FileUploadStatus({
            tracker: main.tracker,
            translator,
        });
        statusbar.registerStatusItem(PROGRESS_ID, {
            item,
            align: "middle",
            isActive: () => { var _a; return !!((_a = item.model) === null || _a === void 0 ? void 0 : _a.items.length); },
            activeStateChanged: item.model.stateChanged,
        });
    },
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ([
    browser,
    progressStatus,
]);


/***/ }),

/***/ "./lib/progress.js":
/*!*************************!*\
  !*** ./lib/progress.js ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   FileUploadStatus: () => (/* binding */ FileUploadStatus)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/statusbar */ "webpack/sharing/consume/default/@jupyterlab/statusbar");
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _lumino_algorithm__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/algorithm */ "webpack/sharing/consume/default/@lumino/algorithm");
/* harmony import */ var _lumino_algorithm__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_algorithm__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_4__);
/******************************************************************************
 *
 * Copyright (c) 2019, the jupyter-fs authors.
 *
 * This file is part of the jupyter-fs library, distributed under the terms of
 * the Apache License 2.0.  The full license can be found in the LICENSE file.
 *
 */
/* eslint-disable @typescript-eslint/no-non-null-assertion */
/* Based on code from JupyterLab, copied under the following license:

Copyright (c) 2015-2021 Project Jupyter Contributors
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/





/**
 * Half-spacing between items in the overall status item.
 */
const HALF_SPACING = 4;
/**
 * A pure function component for a FileUpload status item.
 *
 * @param props: the props for the component.
 *
 * @returns a tsx component for the file upload status.
 */
function FileUploadComponent(props) {
    const translator = props.translator || _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__.nullTranslator;
    const trans = translator.load("jupyterlab");
    const items = [react__WEBPACK_IMPORTED_MODULE_4___default().createElement(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_1__.TextItem, { source: trans.__("Uploading…") })];
    items.push(...props.items.map(i => i.complete ?
        react__WEBPACK_IMPORTED_MODULE_4___default().createElement(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_1__.TextItem, { source: trans.__("Complete!") }) :
        react__WEBPACK_IMPORTED_MODULE_4___default().createElement(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_1__.ProgressBar, { percentage: i.progress })));
    return (react__WEBPACK_IMPORTED_MODULE_4___default().createElement(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_1__.GroupItem, { spacing: HALF_SPACING }, ...items));
}
/**
 * The time for which to show the "Complete!" message after uploading.
 */
const UPLOAD_COMPLETE_MESSAGE_MILLIS = 2000;
/**
 * Status bar item to display file upload progress.
 */
class FileUploadStatus extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.VDomRenderer {
    /**
     * Construct a new FileUpload status item.
     */
    constructor(opts) {
        super(new FileUploadStatus.Model(opts.tracker.currentWidget));
        this._onTreeFinderChange = (tracker, sidebar) => {
            if (sidebar === null) {
                this.model.sidebar = null;
            }
            else {
                this.model.sidebar = sidebar;
            }
        };
        this.translator = opts.translator || _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__.nullTranslator;
        this._tracker = opts.tracker;
        this._tracker.currentChanged.connect(this._onTreeFinderChange);
    }
    /**
     * Render the FileUpload status.
     */
    render() {
        const items = this.model.items;
        if (items.length > 0) {
            return (react__WEBPACK_IMPORTED_MODULE_4___default().createElement(FileUploadComponent, { items: this.model.items, translator: this.translator }));
        }
        else {
            return react__WEBPACK_IMPORTED_MODULE_4___default().createElement((react__WEBPACK_IMPORTED_MODULE_4___default().Fragment), null);
        }
    }
    dispose() {
        super.dispose();
        this._tracker.currentChanged.disconnect(this._onTreeFinderChange);
    }
}
/**
 * A namespace for FileUpload class statics.
 */
(function (FileUploadStatus) {
    /**
     * The VDomModel for the FileUpload renderer.
     */
    class Model extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.VDomModel {
        /**
         * Construct a new model.
         */
        constructor(sidebar) {
            super();
            /**
             * Handle an uploadChanged event in the filebrowser model.
             */
            this._uploadChanged = (uploader, uploads) => {
                if (uploads.name === "start") {
                    this._items.push({
                        path: uploads.newValue.path,
                        progress: uploads.newValue.progress * 100,
                        complete: false,
                    });
                }
                else if (uploads.name === "update") {
                    const idx = _lumino_algorithm__WEBPACK_IMPORTED_MODULE_3__.ArrayExt.findFirstIndex(this._items, val => val.path === uploads.oldValue.path);
                    if (idx !== -1) {
                        this._items[idx].progress = uploads.newValue.progress * 100;
                    }
                }
                else if (uploads.name === "finish") {
                    const finishedItem = _lumino_algorithm__WEBPACK_IMPORTED_MODULE_3__.ArrayExt.findFirstValue(this._items, val => val.path === uploads.oldValue.path);
                    if (finishedItem) {
                        finishedItem.complete = true;
                        setTimeout(() => {
                            _lumino_algorithm__WEBPACK_IMPORTED_MODULE_3__.ArrayExt.removeFirstOf(this._items, finishedItem);
                            this.stateChanged.emit(void 0);
                        }, UPLOAD_COMPLETE_MESSAGE_MILLIS);
                    }
                }
                else if (uploads.name === "failure") {
                    _lumino_algorithm__WEBPACK_IMPORTED_MODULE_3__.ArrayExt.removeFirstWhere(this._items, val => val.path === uploads.newValue.path);
                }
                this.stateChanged.emit(void 0);
            };
            this._items = [];
            this._sidebar = null;
            this.sidebar = sidebar;
        }
        /**
         * The currently uploading items.
         */
        get items() {
            return this._items;
        }
        /**
         * The current file browser model.
         */
        get sidebar() {
            return this._sidebar;
        }
        set sidebar(browserModel) {
            const oldSidebar = this._sidebar;
            if (oldSidebar) {
                oldSidebar.treefinder.uploader.uploadChanged.disconnect(this._uploadChanged);
            }
            this._sidebar = browserModel;
            this._items = [];
            if (this._sidebar !== null) {
                this._sidebar.treefinder.uploader.uploadChanged.connect(this._uploadChanged);
            }
            this.stateChanged.emit(void 0);
        }
    }
    FileUploadStatus.Model = Model;
})(FileUploadStatus || (FileUploadStatus = {}));


/***/ }),

/***/ "./lib/resources.js":
/*!**************************!*\
  !*** ./lib/resources.js ***!
  \**************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   initResources: () => (/* binding */ initResources)
/* harmony export */ });
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react_dom__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react-dom */ "webpack/sharing/consume/default/react-dom");
/* harmony import */ var react_dom__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_dom__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _auth__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./auth */ "./lib/auth.js");
/* harmony import */ var _filesystem__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./filesystem */ "./lib/filesystem.js");





/**
 * Init resource on the server, and prompt for credentials via a dialog if needed.
 *
 * @param resources The resources to initialize to.
 * @param options The initialization options to use.
 * @returns All resources, whether inited or not
 */
async function initResources(resources, options) {
    const delegate = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.PromiseDelegate();
    // send user specs to backend; await return containing resources
    // defined by user settings + resources defined by server config
    resources = await _filesystem__WEBPACK_IMPORTED_MODULE_4__.FSComm.instance.initResourceRequest({
        resources,
        options: {
            ...options,
            _addServerside: true,
        },
    });
    if ((0,_auth__WEBPACK_IMPORTED_MODULE_3__.askRequired)(resources)) {
        // ask for url template values, if required
        const dialogElem = document.createElement("div");
        document.body.appendChild(dialogElem);
        let submitted = false;
        const handleClose = () => {
            try {
                react_dom__WEBPACK_IMPORTED_MODULE_2__.unmountComponentAtNode(dialogElem);
                dialogElem.remove();
                if (!submitted) {
                    delegate.resolve(resources);
                }
            }
            catch (e) {
                delegate.reject(e);
            }
        };
        const handleSubmit = async (values) => {
            try {
                submitted = true;
                resources = await _filesystem__WEBPACK_IMPORTED_MODULE_4__.FSComm.instance.initResourceRequest({
                    resources: resources.map(r => ({ ...r, tokenDict: values[r.url] })),
                    options,
                });
                delegate.resolve(resources);
            }
            catch (e) {
                delegate.reject(e);
            }
        };
        react_dom__WEBPACK_IMPORTED_MODULE_2__.render(react__WEBPACK_IMPORTED_MODULE_1__.createElement(_auth__WEBPACK_IMPORTED_MODULE_3__.AskDialog, { handleClose: handleClose, handleSubmit: handleSubmit, options: options, resources: resources }), dialogElem);
    }
    else {
        delegate.resolve(resources);
    }
    return delegate.promise;
}


/***/ }),

/***/ "./lib/settings.js":
/*!*************************!*\
  !*** ./lib/settings.js ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   migrateSettings: () => (/* binding */ migrateSettings),
/* harmony export */   unpartialResource: () => (/* binding */ unpartialResource)
/* harmony export */ });
/* harmony import */ var semver__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! semver */ "webpack/sharing/consume/default/semver/semver");
/* harmony import */ var semver__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(semver__WEBPACK_IMPORTED_MODULE_0__);
/******************************************************************************
 *
 * Copyright (c) 2019, the jupyter-fs authors.
 *
 * This file is part of the jupyter-fs library, distributed under the terms of
 * the Apache License 2.0.  The full license can be found in the LICENSE file.
 *
 */

/**
 * Migrate any settings from an older version of the package
 *
 * @param settings Our settings to consider for migratation
 * @returns The modified settings object
 */
async function migrateSettings(settings) {
    var _a, _b, _c;
    const options = settings === null || settings === void 0 ? void 0 : settings.composite.options;
    if (semver__WEBPACK_IMPORTED_MODULE_0__.lt((options === null || options === void 0 ? void 0 : options.writtenVersion) || "0.0.0", "0.4.0-alpha.8")) {
        // Migrate snippets to include defaults that were updated after version checked
        const defaultSnippets = ((_a = settings === null || settings === void 0 ? void 0 : settings.default("snippets")) !== null && _a !== void 0 ? _a : []);
        const defaultLabels = defaultSnippets.map(snippet => snippet.label);
        const userSnippets = ((_b = settings === null || settings === void 0 ? void 0 : settings.user.snippets) !== null && _b !== void 0 ? _b : []);
        // add the user defined snippets if they have different label to defaults
        const raw = (_c = userSnippets.reduce((combinedSnippetsArray, snippet) => {
            if (!defaultLabels.includes(snippet.label)) {
                combinedSnippetsArray.push(snippet);
            }
            return combinedSnippetsArray;
        }, [...defaultSnippets])) !== null && _c !== void 0 ? _c : [];
        await settings.set("snippets", raw);
    }
    // Update version
    await settings.set("options", {
        ...options,
        writtenVersion: settings.version,
    });
    return settings;
}
/**
 * Ensure undefined string values from settings that are required are translated to empty strings
 * @param settingsResoruce
 * @returns A filled in setting object
 */
function unpartialResource(settingsResource) {
    return { name: "", url: "", ...settingsResource };
}


/***/ }),

/***/ "./lib/snippets.js":
/*!*************************!*\
  !*** ./lib/snippets.js ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   getAllSnippets: () => (/* binding */ getAllSnippets),
/* harmony export */   getServerSnippets: () => (/* binding */ getServerSnippets),
/* harmony export */   getSettingsSnippets: () => (/* binding */ getSettingsSnippets),
/* harmony export */   instantiateSnippet: () => (/* binding */ instantiateSnippet),
/* harmony export */   snippetFormRender: () => (/* binding */ snippetFormRender)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _contents_utils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./contents_utils */ "./lib/contents_utils.js");
/******************************************************************************
 *
 * Copyright (c) 2023, the jupyter-fs authors.
 *
 * This file is part of the jupyter-fs library, distributed under the terms of
 * the Apache License 2.0.  The full license can be found in the LICENSE file.
 *
 */




function _mknode(obj, paths) {
    var _a;
    for (const path of paths) {
        obj = obj[path] = (_a = obj[path]) !== null && _a !== void 0 ? _a : {};
    }
    return obj;
}
/**
 * Trick to set uiSchema on our settings editor form elements.
 *
 * We use it to set the "template" to a "textarea" multiline input
 */
function snippetFormRender(props) {
    const ArrayField = props.registry.fields.ArrayField;
    const uiSchema = { ...props.uiSchema };
    const templateUiSchema = _mknode(uiSchema, ["items", "template"]);
    templateUiSchema["ui:widget"] = "textarea";
    return react__WEBPACK_IMPORTED_MODULE_2__.createElement(ArrayField, { ...props, uiSchema: uiSchema });
}
const processUrlRegex = /^(?<protocol>.+?):\/\/(?:[^@]+@)?(?<resource>.*)$/;
const templateTokenFinders = {};
/**
 * Get all the snippet specifications in the settings
 */
function getSettingsSnippets(settings) {
    var _a;
    const raw = ((_a = settings === null || settings === void 0 ? void 0 : settings.composite.snippets) !== null && _a !== void 0 ? _a : []);
    return raw.map(s => ({ ...s, pattern: new RegExp(s.pattern) }));
}
/**
 * Gets all the snippet specifications configured on the server
 */
async function getServerSnippets(settings) {
    if (!settings) {
        settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    }
    return _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, "/jupyterfs/snippets"), { method: "GET" }, settings).then(response => {
        if (!response.ok) {
            return Promise.reject(response);
        }
        return response.json();
    }).then(data => data.snippets.map(s => ({ ...s, pattern: new RegExp(s.pattern) })));
}
/**
 * Get the snippet specifications from all sources
 */
async function getAllSnippets(settings) {
    return (await getServerSnippets()).concat(getSettingsSnippets(settings));
}
/**
 * Instantiate the template of a snippet.
 *
 * @param template The template to instantiate
 * @param resource The resource the entry belongs to
 * @param path The local path of the entry
 */
function instantiateSnippet(template, url, type, pathstr) {
    const parsed = processUrlRegex.exec(url);
    const [drive, relativePath] = (0,_contents_utils__WEBPACK_IMPORTED_MODULE_3__.splitPathstrDrive)(pathstr);
    const args = {
        ...parsed === null || parsed === void 0 ? void 0 : parsed.groups,
        url,
        type,
        path: relativePath,
        full_url: `${url.replace(/\/$/, "")}/${relativePath}`,
        full_path: `${drive}:/${relativePath}`,
        drive,
    };
    let templated = template;
    for (const key of Object.keys(args)) {
        if (!(key in templateTokenFinders)) {
            // match `key` wrapped in double curly-braces (and optionally whitespace padding within the braces)
            templateTokenFinders[key] = new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, "g");
        }
        templated = templated.replace(templateTokenFinders[key], args[key]);
    }
    return templated;
}


/***/ }),

/***/ "./lib/tokens.js":
/*!***********************!*\
  !*** ./lib/tokens.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ITreeFinderMain: () => (/* binding */ ITreeFinderMain)
/* harmony export */ });
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__);

const ITreeFinderMain = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.Token("@jupyterlab/filebrowser:IFileBrowserFactory");


/***/ }),

/***/ "./lib/treefinder.js":
/*!***************************!*\
  !*** ./lib/treefinder.js ***!
  \***************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   TreeFinderSidebar: () => (/* binding */ TreeFinderSidebar),
/* harmony export */   TreeFinderTracker: () => (/* binding */ TreeFinderTracker),
/* harmony export */   TreeFinderWidget: () => (/* binding */ TreeFinderWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/docmanager */ "webpack/sharing/consume/default/@jupyterlab/docmanager");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _lumino_algorithm__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @lumino/algorithm */ "webpack/sharing/consume/default/@lumino/algorithm");
/* harmony import */ var _lumino_algorithm__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_lumino_algorithm__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _tree_finder_base__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @tree-finder/base */ "webpack/sharing/consume/default/@tree-finder/base/@tree-finder/base");
/* harmony import */ var _tree_finder_base__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(_tree_finder_base__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var _clipboard__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./clipboard */ "./lib/clipboard.js");
/* harmony import */ var _commands__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./commands */ "./lib/commands.js");
/* harmony import */ var _contents_proxy__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./contents_proxy */ "./lib/contents_proxy.js");
/* harmony import */ var _contents_utils__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./contents_utils */ "./lib/contents_utils.js");
/* harmony import */ var _drag__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ./drag */ "./lib/drag.js");
/* harmony import */ var _icons__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ./icons */ "./lib/icons.js");
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! ./utils */ "./lib/utils.js");
/* harmony import */ var _upload__WEBPACK_IMPORTED_MODULE_15__ = __webpack_require__(/*! ./upload */ "./lib/upload.js");

// import { PathExt, URLExt } from "@jupyterlab/coreutils";



// import JSZip from "jszip";












class TreeFinderTracker extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.WidgetTracker {
    constructor() {
        super(...arguments);
        this._finders = new Map();
    }
    async add(finder) {
        this._finders.set(finder.id, finder);
        // eslint-disable-next-line @typescript-eslint/unbound-method
        finder.disposed.connect(this._onWidgetDisposed, this);
        return super.add(finder);
    }
    remove(finder) {
        this._finders.delete(finder.id);
        // eslint-disable-next-line @typescript-eslint/unbound-method
        finder.disposed.disconnect(this._onWidgetDisposed, this);
    }
    findByDrive(drive) {
        return this._finders.get(drive);
    }
    hasByDrive(drive) {
        return this._finders.has(drive);
    }
    _onWidgetDisposed(finder) {
        this.remove(finder);
    }
}
class TreeFinderWidget extends _drag__WEBPACK_IMPORTED_MODULE_12__.DragDropWidget {
    constructor({ app, columns, rootPath = "", translator, settings, }) {
        const { commands, serviceManager: { contents } } = app;
        const node = document.createElement("tree-finder-panel");
        const acceptedDropMimeTypes = [_drag__WEBPACK_IMPORTED_MODULE_12__.TABLE_HEADER_MIME];
        super({ node, acceptedDropMimeTypes });
        this.addClass("jp-tree-finder");
        // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
        this.contentsProxy = new _contents_proxy__WEBPACK_IMPORTED_MODULE_10__.ContentsProxy(contents, rootPath, this.onGetChildren.bind(this));
        this.settings = settings;
        this.translator = translator || _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__.nullTranslator;
        this._trans = this.translator.load("jupyterlab");
        this._commands = commands;
        this._expanding = new Map();
        this._columns = columns;
        this.rootPath = rootPath === "" ? rootPath : rootPath + ":";
        this._initialLoad = true;
        this._readyDelegate = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_5__.PromiseDelegate();
        void this._readyDelegate.promise.catch(reason => (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)("Failed to init browser", reason));
        void this._readyDelegate.promise.then(() => {
            // TODO: Model state of TreeFinderWidget should be updated by renamerSub process.
            //       Currently we hard-code the refresh here, but should be moved upstream!
            const contentsModel = this.model;
            contentsModel.renamerSub.subscribe(({ name, target }) => {
                void contentsModel.sort();
            });
        });
    }
    move(mimeData, target) {
        const source = mimeData.getData(_drag__WEBPACK_IMPORTED_MODULE_12__.TABLE_HEADER_MIME);
        const dest = target.innerText;
        void this._reorderColumns(source, dest);
        void this.nodeInit();
        return "move";
    }
    addMimeData(handle, mimeData) {
        const columnName = handle.innerText;
        mimeData.setData(_drag__WEBPACK_IMPORTED_MODULE_12__.TABLE_HEADER_MIME, columnName);
    }
    getDragImage(handle) {
        const target = this.findDragTarget(handle);
        let img = null;
        if (target) {
            img = target.cloneNode(true);
            img.classList.add("jp-thead-drag-image");
        }
        return img;
    }
    onGetChildren(path, done) {
        if (this._initialLoad) {
            const rootPathstr = _tree_finder_base__WEBPACK_IMPORTED_MODULE_7__.Path.toarray(this.rootPath).join("/");
            if (path === rootPathstr) {
                done.finally(() => {
                    this._initialLoad = false;
                    this.draw();
                });
            }
        }
        this._expanding.set(path, (this._expanding.get(path) || 0) + 1);
        // only redraw if bumped up from 0
        if (this._expanding.get(path) === 1) {
            this.draw();
        }
        done.finally(() => {
            this._expanding.set(path, (this._expanding.get(path) || 1) - 1);
            // only redraw if bumped down to 0
            if (this._expanding.get(path) === 0) {
                this.draw();
            }
        });
    }
    /**
     * Reorders the columns according to given inputs and saves to user settings
     * If `source` is dragged from left to right, it will be inserted to the right side of `dest`
     * Else if `source` is dragged from right to left, it will be inserted to the left side of `dest`
     */
    async _reorderColumns(source, dest) {
        var _a;
        const sIndex = this._columns.indexOf(source);
        const dIndex = this._columns.indexOf(dest);
        if (sIndex < dIndex) {
            this._columns.splice(dIndex + 1, 0, source);
            this._columns.splice(sIndex, 1);
        }
        else if (sIndex > dIndex) {
            this._columns.splice(sIndex, 1);
            this._columns.splice(dIndex, 0, source);
        }
        await ((_a = this.settings) === null || _a === void 0 ? void 0 : _a.set("display_columns", this._columns));
    }
    draw(props = {}) {
        var _a;
        (_a = this.model) === null || _a === void 0 ? void 0 : _a.requestDraw();
    }
    refresh() {
        var _a;
        (_a = this.model) === null || _a === void 0 ? void 0 : _a.refreshSub.next([]);
    }
    async nodeInit() {
        var _a;
        // The contents of root passed to node.init is not (currently) considered, so do not ask for it.
        let root = null;
        try {
            root = await this.contentsProxy.get(this.rootPath, { content: false });
        }
        catch (error) {
            return;
        }
        this._currentFolder = (_a = this.model) === null || _a === void 0 ? void 0 : _a.root.pathstr;
        await customElements.whenDefined("tree-finder-panel");
        this.node.init({
            root,
            gridOptions: {
                columnFormatters: {
                    last_modified: (x => _tree_finder_base__WEBPACK_IMPORTED_MODULE_7__.Format.timeSince(x)),
                    size: (x => x && _tree_finder_base__WEBPACK_IMPORTED_MODULE_7__.Format.bytesToHumanReadable(x)),
                    writable: (x => x ? "✓" : "╳"),
                },
                doWindowResize: true,
                showFilter: true,
            },
            modelOptions: {
                columnNames: this.columns,
            },
        });
        const grid = this.node.querySelector("tree-finder-grid");
        grid === null || grid === void 0 ? void 0 : grid.addStyleListener(() => {
            var _a, _b, _c;
            // Set root-level load indicator
            grid.classList.toggle("jfs-mod-loading", this._initialLoad);
            // Fix corner cleanup (workaround for underlying bug where we end up with two resize handles)
            const resizeSpans = grid.querySelectorAll(`thead tr > th:first-child > span.rt-column-resize`);
            const nHeaderRows = grid.querySelectorAll("thead tr").length;
            if (resizeSpans.length > nHeaderRows) {
                // something went wrong, and we ended up with double resize handles. Clear the classes from the first one:
                for (const span of grid.querySelectorAll(`thead tr > th:first-child > span.rt-column-resize:first-child`)) {
                    span.removeAttribute("class");
                }
            }
            // Fix focus and tabbing
            let lastSelectIdx = ((_a = this.model) === null || _a === void 0 ? void 0 : _a.selectedLast) ? (_b = this.model) === null || _b === void 0 ? void 0 : _b.contents.indexOf(this.model.selectedLast) : -1;
            const lostFocus = document.activeElement !== this.node;
            for (const rowHeader of grid.querySelectorAll("tr > th")) {
                const tableHeader = rowHeader.querySelector("span.tf-header-name");
                if (tableHeader) {
                    // If tableheader is path, do not make it draggable
                    if (tableHeader.innerText !== "path") {
                        tableHeader.classList.add(this.dragHandleClass);
                    }
                }
                const nameElement = rowHeader.querySelector("span.rt-group-name");
                // Ensure we can tab to all items
                nameElement === null || nameElement === void 0 ? void 0 : nameElement.setAttribute("tabindex", "0");
                // Ensure last selected element retains focus after redraw:
                if (lostFocus && nameElement && lastSelectIdx !== -1) {
                    const meta = grid.getMeta(rowHeader);
                    if (meta && meta.y === lastSelectIdx) {
                        nameElement.focus();
                        lastSelectIdx = -1;
                    }
                }
                // Add "loading" indicator for folders that are fetching children
                if (nameElement) {
                    const meta = grid.getMeta(rowHeader);
                    const content = (meta === null || meta === void 0 ? void 0 : meta.y) ? (_c = this.model) === null || _c === void 0 ? void 0 : _c.contents[meta.y] : undefined;
                    if (content) {
                        rowHeader.classList.toggle("jfs-mod-loading", !!nameElement && (this._expanding.get(content.pathstr) || 0) > 0);
                    }
                }
            }
        });
        if (this.uploader) {
            this.uploader.model = this.model;
        }
        else {
            this.uploader = new _upload__WEBPACK_IMPORTED_MODULE_15__.Uploader({
                contentsProxy: this.contentsProxy,
                model: this.model,
            });
        }
        if (this._currentFolder) {
            await (0,_contents_utils__WEBPACK_IMPORTED_MODULE_11__.openDirRecursive)(this.model, this._currentFolder.split("/"));
        }
        this.model.openSub.subscribe(rows => rows.forEach(row => {
            if (!row.getChildren) {
                void this._commands.execute("docmanager:open", { path: _tree_finder_base__WEBPACK_IMPORTED_MODULE_7__.Path.fromarray(row.path) });
            }
            else {
                const widget = TreeFinderSidebar.tracker.findByDrive(this.parent.id);
                void TreeFinderSidebar.tracker.save(widget);
            }
        }));
    }
    get columns() {
        return this._columns;
    }
    set columns(value) {
        if (_lumino_algorithm__WEBPACK_IMPORTED_MODULE_4__.ArrayExt.shallowEqual(this._columns, value)) {
            return;
        }
        this._columns = value;
        const m = this.model;
        m.options = {
            ...m.options,
            columnNames: this._columns,
        };
        m.initColumns();
        void this.nodeInit();
    }
    get ready() {
        return this._readyDelegate.promise;
    }
    get model() {
        return this.node.model;
    }
    get selection() {
        var _a;
        return (_a = this.model) === null || _a === void 0 ? void 0 : _a.selection;
    }
    get selectionPathstrs() {
        var _a;
        return (_a = this.model) === null || _a === void 0 ? void 0 : _a.selection.map(c => _tree_finder_base__WEBPACK_IMPORTED_MODULE_7__.Path.fromarray(c.row.path));
    }
    /**
     * Handle the DOM events for the tree view.
     *
     * @param event - The DOM event sent to the widget.
     *
     * #### Notes
     * This method implements the DOM `EventListener` interface and is
     * called in response to events on the panel's DOM node. It should
     * not be called directly by user code.
     */
    handleEvent(event) {
        switch (event.type) {
            case "keydown":
                this.evtKeydown(event);
                break;
            case "dragenter":
                this.evtNativeDragOverEnter(event);
            case "dragover":
                this.evtNativeDragOverEnter(event);
                break;
            case "dragleave":
            case "dragend":
                this.evtNativeDragLeaveEnd(event);
                break;
            case "drop":
                this.evtNativeDrop(event);
                break;
            default:
                super.handleEvent(event);
                break;
        }
    }
    async load() {
        if (this._initialLoad) {
            const node = this.node;
            await this.nodeInit();
            this._readyDelegate.resolve();
            node.addEventListener("keydown", this);
            node.addEventListener("dragenter", this);
            node.addEventListener("dragover", this);
            node.addEventListener("dragleave", this);
            node.addEventListener("dragend", this);
            node.addEventListener("drop", this);
        }
    }
    /**
     * A message handler invoked on an `'after-attach'` message.
     */
    onAfterAttach(msg) {
        super.onAfterAttach(msg);
        void this.load();
    }
    /**
     * A message handler invoked on a `'before-detach'` message.
     */
    onBeforeDetach(msg) {
        super.onBeforeDetach(msg);
        const node = this.node;
        node.removeEventListener("keydown", this);
        node.removeEventListener("dragover", this);
        node.removeEventListener("dragover", this);
        node.removeEventListener("dragleave", this);
        node.removeEventListener("dragend", this);
        node.removeEventListener("drop", this);
    }
    _findEventRowElement(event, selector) {
        let node = event.target;
        while (node.parentElement && node.parentElement !== this.node) {
            if (node.matches(selector)) {
                return node;
            }
            node = node.parentElement;
        }
    }
    selectNeighbour(diff, asRange) {
        const model = this.model;
        let last = model.selectedLast;
        // tree-finder has a bug where it doesn't update selectedLast in `selectRange`, hacky work-around for now:
        const { range, pivot } = model.selectionModel;
        // once bug is fixed, this conditional should never be true:
        if (pivot && pivot === (last === null || last === void 0 ? void 0 : last.pathstr) && range && range.length >= 1) {
            // get the part of range that is furthest away from pivot:
            const paths = model.contents.map(c => c.pathstr);
            const pivotIdx = paths.indexOf(pivot);
            const rangeStartIdx = paths.indexOf(range[0]);
            const rangeEndIdx = paths.indexOf(range[range.length - 1]);
            if (pivotIdx < rangeStartIdx) {
                last = model.contents[rangeEndIdx];
            }
            else {
                last = model.contents[rangeStartIdx];
            }
        }
        let idx = last
            ? model.contents.indexOf(last)
            : diff < 0
                ? model.contents.length - 1 // select last item
                : 0; // select first item
        if (last) {
            idx = idx + diff;
        }
        if (idx < 0 || idx >= model.contents.length) {
            return; // Do nothing if going past the edge
        }
        const next = model.contents[idx];
        if (asRange) {
            model.selectionModel.selectRange(next, model.contents);
        }
        else {
            model.selectionModel.select(next);
        }
        void TreeFinderSidebar.scrollIntoView(this, next.pathstr);
    }
    evtKeydown(event) {
        var _a, _b, _c, _d;
        // handle any keys unaffacted by renaming status above this check:
        if ((_a = this.parent) === null || _a === void 0 ? void 0 : _a.node.classList.contains("jfs-mod-renaming")) {
            return;
        }
        switch (event.key) {
            case "ArrowDown":
            case "ArrowUp":
                event.stopPropagation();
                event.preventDefault();
                this.selectNeighbour(event.key === "ArrowUp" ? -1 : 1, event.shiftKey);
                break;
            case "ArrowLeft":
                if ((_b = this.model) === null || _b === void 0 ? void 0 : _b.selectedLast) {
                    event.stopPropagation();
                    event.preventDefault();
                    const selectedLast = this.model.selectedLast;
                    // don't allow expansion or up/down nav if in select range mode:
                    if (!event.shiftKey) {
                        if (selectedLast.isExpand) {
                            void this.model.collapse(this.model.contents.indexOf(selectedLast));
                        }
                        else {
                            // navigate the selection to the next up (exluding to root)
                            void (0,_contents_utils__WEBPACK_IMPORTED_MODULE_11__.getContentParent)(selectedLast, this.model.root).then(parent => {
                                var _a, _b;
                                if (parent !== ((_a = this.model) === null || _a === void 0 ? void 0 : _a.root)) {
                                    (_b = this.model) === null || _b === void 0 ? void 0 : _b.selectionModel.select(parent);
                                    return TreeFinderSidebar.scrollIntoView(this, parent.pathstr);
                                }
                            });
                        }
                    }
                }
                break;
            case "ArrowRight":
                if ((_c = this.model) === null || _c === void 0 ? void 0 : _c.selectedLast) {
                    event.stopPropagation();
                    event.preventDefault();
                    const selectedLast = this.model.selectedLast;
                    // don't allow expansion or up/down nav if in select range mode:
                    if (!event.shiftKey) {
                        if (!selectedLast.isExpand) {
                            void this.model.expand(this.model.contents.indexOf(selectedLast));
                        }
                        else if (selectedLast.hasChildren) {
                            // navigate the selection to the first child
                            void selectedLast.getChildren().then(children => {
                                var _a;
                                if (children && children.length > 0) {
                                    (_a = this.model) === null || _a === void 0 ? void 0 : _a.selectionModel.select(children[0]);
                                    return TreeFinderSidebar.scrollIntoView(this, children[0].pathstr);
                                }
                            });
                        }
                    }
                }
                break;
            case " ": // space key
                // Toggle expansion if dir
                if ((_d = this.model) === null || _d === void 0 ? void 0 : _d.selectedLast) {
                    event.stopPropagation();
                    event.preventDefault();
                    const selectedLast = this.model.selectedLast;
                    if (selectedLast.hasChildren) {
                        const selectedIdx = this.model.contents.indexOf(selectedLast);
                        if (selectedLast.isExpand) {
                            void this.model.collapse(selectedIdx);
                        }
                        else {
                            void this.model.expand(selectedIdx);
                        }
                    }
                }
                break;
        }
    }
    evtNativeDragOverEnter(event) {
        const row = this._findEventRowElement(event, "tree-finder-grid tr");
        if (row) {
            row.classList.add("jfs-mod-native-drop");
        }
        event.preventDefault();
    }
    evtNativeDragLeaveEnd(event) {
        const row = this._findEventRowElement(event, ".jfs-mod-native-drop");
        if (row) {
            row.classList.remove("jfs-mod-native-drop");
        }
    }
    /**
     * Handle the `drop` event for the widget.
     */
    evtNativeDrop(event) {
        var _a, _b, _c;
        const row = this.node.querySelector(".jfs-mod-native-drop");
        if (row) {
            row.classList.remove("jfs-mod-native-drop");
        }
        const files = (_a = event.dataTransfer) === null || _a === void 0 ? void 0 : _a.files;
        if (!files || files.length === 0) {
            return;
        }
        const length = (_b = event.dataTransfer) === null || _b === void 0 ? void 0 : _b.items.length;
        if (!length) {
            return;
        }
        for (let i = 0; i < length; i++) {
            const entry = (_c = event.dataTransfer) === null || _c === void 0 ? void 0 : _c.items[i].webkitGetAsEntry();
            if (entry === null || entry === void 0 ? void 0 : entry.isDirectory) {
                void (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                    title: this._trans.__("Error Uploading Folder"),
                    body: this._trans.__("Drag and Drop is currently not supported for folders"),
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.cancelButton({ label: this._trans.__("Close") })],
                });
            }
        }
        event.preventDefault();
        // Translate row element to contents row
        let target = this.model.root;
        if (row) {
            const grid = this.node.querySelector("tree-finder-grid");
            const metadata = grid.getMeta(row.querySelector("th"));
            if (metadata.y) {
                target = this.model.contents[metadata.y];
            }
        }
        for (let i = 0; i < files.length; i++) {
            void this.uploader.upload(files[i], target);
        }
    }
}
class TreeFinderSidebar extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_6__.Widget {
    constructor({ app, columns, url, type, rootPath = "", caption = "TreeFinder", id = "jupyterlab-tree-finder", settings, preferredDir, }) {
        super();
        this.id = id;
        this.node.classList.add("jfs-mod-notRenaming");
        this.url = url;
        this.type = type;
        this.title.icon = _icons__WEBPACK_IMPORTED_MODULE_13__.fileTreeIcon;
        this.title.caption = caption;
        this.addClass("jp-tree-finder-sidebar");
        this.toolbar = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Toolbar();
        this.toolbar.addClass("jp-tree-finder-toolbar");
        this.preferredDir = preferredDir;
        this.treefinder = new TreeFinderWidget({ app, rootPath, columns, settings });
        this.layout = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_6__.PanelLayout();
        this.layout.addWidget(this.toolbar);
        this.layout.addWidget(this.treefinder);
    }
    restore() {
        void this.treefinder.ready.then(() => {
            this.treefinder.refresh();
            this.treefinder.draw({ reset: true });
        });
    }
    async download(path, folder) {
        if (folder) {
            // const zip = new JSZip();
            // await this.wrapFolder(zip, path); // folder packing
            // // generate and save zip, reset path
            // path = PathExt.basename(path);
            // writeZipFile(zip, path);
        }
        else {
            const url = await this.treefinder.contentsProxy.downloadUrl(path);
            const element = document.createElement("a");
            element.setAttribute("href", url);
            element.setAttribute("download", "");
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        }
    }
    // async wrapFolder(zip: JSZip, path: string) {
    //   const base = this.cm.get(this.basepath + path);
    //   const next = base.then(async res => {
    //     if (res.type === "directory") {
    //       const new_folder = zip.folder(res.name);
    //       for (const c in res.content) {
    //         await this.wrapFolder(new_folder, res.content[c].path);
    //       }
    //     } else {
    //       zip.file(res.name, res.content);
    //     }
    //   });
    //   await next;
    // }
    onAfterShow(msg) {
        var _a, _b;
        this.treefinder.refresh();
        this.treefinder.draw({ reset: true });
        // Temporary workaround for grid size issues
        ((_b = (_a = this.treefinder.node.querySelector("tree-finder-grid")) === null || _a === void 0 ? void 0 : _a.shadowRoot) === null || _b === void 0 ? void 0 : _b.querySelector("div.rt-scroll-table-clip")).style.height = "110%";
    }
    onResize(msg) {
        this.treefinder.draw();
    }
}
// eslint-disable-next-line @typescript-eslint/no-namespace
(function (TreeFinderSidebar) {
    const namespace = "jupyter-fs-treefinder";
    TreeFinderSidebar.tracker = new TreeFinderTracker({ namespace });
    TreeFinderSidebar.clipboard = new _clipboard__WEBPACK_IMPORTED_MODULE_8__.JupyterClipboard(TreeFinderSidebar.tracker);
    function sidebarFromResource(resource, props) {
        return sidebar({
            ...props,
            rootPath: resource.drive,
            caption: resource.name,
            id: (0,_commands__WEBPACK_IMPORTED_MODULE_9__.idFromResource)(resource),
            preferredDir: resource.preferredDir,
            url: resource.url,
            type: resource.type,
        });
    }
    TreeFinderSidebar.sidebarFromResource = sidebarFromResource;
    function sidebar({ app, 
    // manager,
    // paths,
    // resolver,
    // router,
    restorer, url, type, columns, settings, preferredDir, rootPath = "", caption = "TreeFinder", id = "jupyterlab-tree-finder", side = "left", }) {
        const widget = new TreeFinderSidebar({ app, rootPath, columns, caption, id, url, type, settings, preferredDir });
        void widget.treefinder.ready.then(() => TreeFinderSidebar.tracker.add(widget));
        app.shell.add(widget, side);
        const new_launcher_button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__.addIcon,
            onClick: () => {
                void app.commands.execute(_commands__WEBPACK_IMPORTED_MODULE_9__.commandIDs.newLauncher);
            },
            tooltip: "Open Launcher",
        });
        const new_file_button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__.newFolderIcon,
            onClick: () => {
                void app.commands.execute((_commands__WEBPACK_IMPORTED_MODULE_9__.commandIDs.createFolder));
            },
            tooltip: "New Folder",
        });
        const uploader_button = new _upload__WEBPACK_IMPORTED_MODULE_15__.UploadButton({ uploader: widget.treefinder.ready.then(() => widget.treefinder.uploader) });
        void widget.treefinder.ready.then(() => {
            widget.treefinder.uploader.uploadCompleted.connect((sender, args) => {
                // Do not select/scroll into view: Upload might be slow, so user might have moved on!
                // We do however want to expand the folder
                void (0,_contents_utils__WEBPACK_IMPORTED_MODULE_11__.revealPath)(widget.treefinder.model, args.path).then(() => widget.treefinder.model.flatten());
            });
        });
        const refresh_button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__.refreshIcon,
            onClick: () => {
                void app.commands.execute(_commands__WEBPACK_IMPORTED_MODULE_9__.commandIDs.refresh);
            },
            tooltip: "Refresh",
        });
        widget.toolbar.addItem("launcher", new_launcher_button);
        widget.toolbar.addItem("new file", new_file_button);
        widget.toolbar.addItem("upload", uploader_button);
        widget.toolbar.addItem("refresh", refresh_button);
        if (preferredDir) {
            void widget.treefinder.ready.then(async () => {
                let path = preferredDir.split("/");
                if (preferredDir.startsWith("/")) {
                    path = path.slice(1);
                }
                path.unshift(rootPath);
                await (0,_contents_utils__WEBPACK_IMPORTED_MODULE_11__.openDirRecursive)(widget.treefinder.model, path);
            });
        }
        // // remove context highlight on context menu exit
        // document.ondblclick = () => {
        //   app.commands.execute((widget.commandIDs.set_context + ":" + widget.id), { path: "" });
        // };
        // widget.node.onclick = event => {
        //   app.commands.execute((widget.commandIDs.select + ":" + widget.id), { path: "" });
        // };
        // setInterval(() => {
        //   app.commands.execute(widget.commandIDs.refresh);
        // }, 10000);
        // return a disposable containing all disposables associated
        // with this widget, ending with the widget itself
        return widget;
    }
    TreeFinderSidebar.sidebar = sidebar;
    async function doRename(widget, oldContent) {
        var _a;
        if (widget.node.classList.contains("jfs-mod-renaming")) {
            return oldContent.row;
        }
        const textNode = widget.node.querySelector("tr.tf-mod-select .rt-tree-container .rt-group-name").firstChild;
        const original = textNode.textContent.replace(/(.*)\/$/, "$1");
        const editNode = document.createElement("input");
        editNode.value = original;
        try {
            widget.node.classList.replace("jfs-mod-notRenaming", "jfs-mod-renaming");
            const newName = await (0,_utils__WEBPACK_IMPORTED_MODULE_14__.promptRename)(textNode, editNode, original);
            (_a = textNode.parentElement) === null || _a === void 0 ? void 0 : _a.focus();
            if (!newName || newName === oldContent.name) {
                return oldContent.row;
            }
            if (!(0,_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_1__.isValidFileName)(newName)) {
                void (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)("Rename Error", Error(newName + ' is not a valid name. Names must have nonzero length, and cannot include "/", "\\", or ":"'));
                return oldContent.row;
            }
            const oldPath = oldContent.getPathAtDepth(1).join("/");
            const newPath = oldPath.slice(0, -1 * original.length) + newName;
            const suffix = textNode.textContent.endsWith("/") ? "/" : "";
            let newContent;
            try {
                newContent = await widget.treefinder.contentsProxy.rename(oldPath + suffix, newPath + suffix);
            }
            catch (error) {
                if (error !== "File not renamed") {
                    void (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)("Rename Error", error);
                }
                newContent = oldContent.row;
            }
            textNode.textContent = newName + suffix;
            return newContent;
        }
        finally {
            widget.node.classList.replace("jfs-mod-renaming", "jfs-mod-notRenaming");
        }
    }
    TreeFinderSidebar.doRename = doRename;
    /**
     * If a path entry is not in view, scroll it into view
     *
     * @param treefinder The view
     * @param pathstr The entry to show
     */
    async function scrollIntoView(treefinder, pathstr) {
        // tree-finder uses rxjs bits that don't allow you to await, so to ensure sync draw:
        const model = treefinder.model;
        await model.flatten();
        const grid = treefinder.node.querySelector("tree-finder-grid");
        // eslint-disable-next-line @typescript-eslint/await-thenable
        await grid.draw();
        // Check if new row (selection) in view (if outside virtual window, it will fail):
        if (!treefinder.node.querySelector(".tf-mod-select .rt-tree-container .rt-group-name")) {
            // We need to scroll the selection into view!
            const rowIdx = model.contents.findIndex(s => s.pathstr === pathstr);
            if (rowIdx !== -1) {
                // TODO: Should we perform a minimum scroll, or do we always want entry as close to the top of the view as possible?
                await grid.scrollToCell(0, rowIdx, 1, model.contents.length);
            }
        }
    }
    TreeFinderSidebar.scrollIntoView = scrollIntoView;
})(TreeFinderSidebar || (TreeFinderSidebar = {}));


/***/ }),

/***/ "./lib/upload.js":
/*!***********************!*\
  !*** ./lib/upload.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   CHUNK_SIZE: () => (/* binding */ CHUNK_SIZE),
/* harmony export */   UploadButton: () => (/* binding */ UploadButton),
/* harmony export */   Uploader: () => (/* binding */ Uploader)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/docmanager */ "webpack/sharing/consume/default/@jupyterlab/docmanager");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _lumino_algorithm__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @lumino/algorithm */ "webpack/sharing/consume/default/@lumino/algorithm");
/* harmony import */ var _lumino_algorithm__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_lumino_algorithm__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _contents_utils__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./contents_utils */ "./lib/contents_utils.js");
/******************************************************************************
 *
 * Copyright (c) 2019, the jupyter-fs authors.
 *
 * This file is part of the jupyter-fs library, distributed under the terms of
 * the Apache License 2.0.  The full license can be found in the LICENSE file.
 *
 */
/* Based on code from JupyterLab, copied under the following license:

Copyright (c) 2015-2021 Project Jupyter Contributors
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/







/**
 * The size (in bytes) of the biggest chunk we should upload at once.
 */
const CHUNK_SIZE = 1024 * 1024;
class UploadButton extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton {
    /**
     * Construct a new file browser buttons widget.
     */
    constructor(options) {
        super({
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__.fileUploadIcon,
            label: options.label,
            onClick: () => {
                this._input.click();
            },
            tooltip: Private.translateToolTip(options.translator),
        });
        /**
         * The 'change' handler for the input field.
         */
        this._onInputChanged = () => {
            const files = Array.prototype.slice.call(this._input.files);
            const pending = files.map(async (file) => (await this._uploader).upload(file));
            void Promise.all(pending).catch(error => {
                void (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)(this._trans._p("showErrorMessage", "Upload Error"), error);
            });
        };
        /**
         * The 'click' handler for the input field.
         */
        this._onInputClicked = () => {
            // In order to allow repeated uploads of the same file (with delete in between),
            // we need to clear the input value to trigger a change event.
            this._input.value = "";
        };
        this._input = Private.createUploadInput();
        this.translator = options.translator || _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__.nullTranslator;
        this._trans = this.translator.load("jupyterlab");
        this._uploader = options.uploader;
        this._input.onclick = this._onInputClicked;
        this._input.onchange = this._onInputChanged;
        this.addClass("jp-id-upload");
    }
}
/**
 * A widget which provides an upload button.
 */
class Uploader {
    /**
     * Construct a new file browser buttons widget.
     */
    constructor(options) {
        this._uploads = [];
        this._uploadChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_5__.Signal(this);
        this._uploadCompleted = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_5__.Signal(this);
        this._disposed = false;
        this.model = options.model;
        this._contentsProxy = options.contentsProxy;
    }
    /**
     * A signal emitted when an upload progresses.
     */
    get uploadChanged() {
        return this._uploadChanged;
    }
    /**
     * A signal emitted when an upload completes.
     */
    get uploadCompleted() {
        return this._uploadCompleted;
    }
    /**
     * Is this instance disposed?
     */
    get isDisposed() {
        return this._disposed;
    }
    /**
     * Dispose of the resources held by the model.
     */
    dispose() {
        if (this.isDisposed) {
            return;
        }
        this._disposed = true;
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_5__.Signal.clearData(this);
    }
    /**
     * Upload a `File` object.
     *
     * @param file - The `File` object to upload.
     *
     * @returns A promise containing the new file contents model.
     */
    async upload(file, target) {
        await this._uploadCheckDisposed();
        target = target || this.model.selectedLast || this.model.root;
        if (!target.hasChildren) {
            target = await (0,_contents_utils__WEBPACK_IMPORTED_MODULE_6__.getContentParent)(target, this.model.root);
        }
        const path = target.pathstr ? target.pathstr + "/" + file.name : file.name;
        let res = null;
        try {
            // alternatively to try to get the file and check for 404, we can get the parent
            // and check if the file is in the list.
            res = await this._contentsProxy.get(path, { content: false });
        }
        catch (e) {
            // TODO: Check if e is a 404
        }
        if (res) {
            // drop drive when prompting:
            if (!await (0,_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_1__.shouldOverwrite)(path.slice(path.indexOf("/") + 1))) {
                return null;
            }
        }
        await this._uploadCheckDisposed();
        const chunkedUpload = file.size > CHUNK_SIZE;
        const uploaded = await this._upload(file, path, chunkedUpload);
        target.invalidate();
        this._uploadCompleted.emit({ path: uploaded.path });
        return uploaded;
    }
    /**
     * Perform the actual upload.
     */
    async _upload(file, path, chunked) {
        // Gather the file model parameters.
        const name = file.name;
        const type = "file";
        const format = "base64";
        const uploadInner = async (blob, chunk) => {
            await this._uploadCheckDisposed();
            const reader = new FileReader();
            reader.readAsDataURL(blob);
            await new Promise((resolve, reject) => {
                reader.onload = resolve;
                reader.onerror = event => reject(`Failed to upload "${file.name}":  ${event}`);
            });
            await this._uploadCheckDisposed();
            // remove header https://stackoverflow.com/a/24289420/907060
            const content = reader.result.split(",")[1];
            const model = {
                type,
                format,
                name,
                chunk,
                content,
            };
            return await this._contentsProxy.save(path, model);
        };
        if (!chunked) {
            try {
                return await uploadInner(file);
            }
            catch (err) {
                _lumino_algorithm__WEBPACK_IMPORTED_MODULE_4__.ArrayExt.removeFirstWhere(this._uploads, uploadIndex => file.name === uploadIndex.path);
                throw err;
            }
        }
        let finalModel;
        let upload = { path, progress: 0 };
        this._uploadChanged.emit({
            name: "start",
            newValue: upload,
            oldValue: null,
        });
        for (let start = 0; !finalModel; start += CHUNK_SIZE) {
            const end = start + CHUNK_SIZE;
            const lastChunk = end >= file.size;
            const chunk = lastChunk ? -1 : end / CHUNK_SIZE;
            const newUpload = { path, progress: start / file.size };
            this._uploads.splice(this._uploads.indexOf(upload));
            this._uploads.push(newUpload);
            this._uploadChanged.emit({
                name: "update",
                newValue: newUpload,
                oldValue: upload,
            });
            upload = newUpload;
            let currentModel;
            try {
                currentModel = await uploadInner(file.slice(start, end), chunk);
            }
            catch (err) {
                _lumino_algorithm__WEBPACK_IMPORTED_MODULE_4__.ArrayExt.removeFirstWhere(this._uploads, uploadIndex => file.name === uploadIndex.path);
                this._uploadChanged.emit({
                    name: "failure",
                    newValue: upload,
                    oldValue: null,
                });
                throw err;
            }
            if (lastChunk) {
                finalModel = currentModel;
            }
        }
        this._uploads.splice(this._uploads.indexOf(upload));
        this._uploadChanged.emit({
            name: "finish",
            newValue: null,
            oldValue: upload,
        });
        return finalModel;
    }
    _uploadCheckDisposed() {
        if (this.isDisposed) {
            return Promise.reject("Filemanager disposed. File upload canceled");
        }
        return Promise.resolve();
    }
}
/**
 * The namespace for module private data.
 */
var Private;
(function (Private) {
    /**
     * Create the upload input node for a file buttons widget.
     */
    function createUploadInput() {
        const input = document.createElement("input");
        input.type = "file";
        input.multiple = true;
        return input;
    }
    Private.createUploadInput = createUploadInput;
    /**
     * Translate upload tooltip.
     */
    function translateToolTip(translator) {
        translator = translator || _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__.nullTranslator;
        const trans = translator.load("jupyterlab");
        return trans.__("Upload Files");
    }
    Private.translateToolTip = translateToolTip;
})(Private || (Private = {}));


/***/ }),

/***/ "./lib/utils.js":
/*!**********************!*\
  !*** ./lib/utils.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   OpenDirectWidget: () => (/* binding */ OpenDirectWidget),
/* harmony export */   Patterns: () => (/* binding */ Patterns),
/* harmony export */   btoaNopad: () => (/* binding */ btoaNopad),
/* harmony export */   createOpenNode: () => (/* binding */ createOpenNode),
/* harmony export */   fileSizeString: () => (/* binding */ fileSizeString),
/* harmony export */   promptRename: () => (/* binding */ promptRename),
/* harmony export */   switchView: () => (/* binding */ switchView),
/* harmony export */   writeZipFile: () => (/* binding */ writeZipFile)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var file_saver__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! file-saver */ "webpack/sharing/consume/default/file-saver/file-saver");
/* harmony import */ var file_saver__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(file_saver__WEBPACK_IMPORTED_MODULE_2__);
/******************************************************************************
 *
 * Copyright (c) 2019, the jupyter-fs authors.
 *
 * This file is part of the jupyter-fs library, distributed under the terms of
 * the Apache License 2.0.  The full license can be found in the LICENSE file.
 *
 */



const Patterns = {
    tree: new RegExp(`^${_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getOption("treeUrl")}([^?]+)`),
    workspace: new RegExp(`^${_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getOption("workspacesUrl")}[^?/]+/tree/([^?]+)`),
};
/**
 * Version of btoa that omits any "=" padding chars at the end
 */
function btoaNopad(s) {
    return btoa(s).replace(/=+$/, "");
}
function createOpenNode() {
    const body = document.createElement("div");
    const existingLabel = document.createElement("label");
    existingLabel.textContent = "File Path:";
    const input = document.createElement("input");
    input.value = "";
    input.placeholder = "/path/to/file";
    body.appendChild(existingLabel);
    body.appendChild(input);
    return body;
}
function promptRename(text, edit, original) {
    const parent = text.parentElement;
    parent.replaceChild(edit, text);
    edit.focus();
    const index = edit.value.lastIndexOf('.');
    if (index === -1) {
        edit.setSelectionRange(0, edit.value.length);
    }
    else {
        edit.setSelectionRange(0, index);
    }
    return new Promise((resolve, reject) => {
        edit.onblur = () => {
            parent.replaceChild(text, edit);
            resolve(edit.value);
        };
        edit.onkeydown = (event) => {
            switch (event.keyCode) {
                case 13: // Enter
                    event.stopPropagation();
                    event.preventDefault();
                    edit.blur();
                    break;
                case 27: // Escape
                    event.stopPropagation();
                    event.preventDefault();
                    edit.value = original;
                    edit.blur();
                    break;
                case 38: // Up arrow
                    event.stopPropagation();
                    event.preventDefault();
                    if (edit.selectionStart !== edit.selectionEnd) {
                        edit.selectionStart = edit.selectionEnd = 0;
                    }
                    break;
                case 40: // Down arrow
                    event.stopPropagation();
                    event.preventDefault();
                    if (edit.selectionStart !== edit.selectionEnd) {
                        edit.selectionStart = edit.selectionEnd = edit.value.length;
                    }
                    break;
                default:
                    break;
            }
        };
    });
}
function fileSizeString(fileBytes) {
    if (fileBytes == null) {
        return "";
    }
    if (fileBytes < 1024) {
        return fileBytes + " B";
    }
    let i = -1;
    const byteUnits = [" KB", " MB", " GB", " TB"];
    do {
        fileBytes = fileBytes / 1024;
        i++;
    } while (fileBytes > 1024);
    return Math.max(fileBytes, 0.1).toFixed(1) + byteUnits[i];
}
function switchView(mode) {
    if (mode === "none") {
        return "";
    }
    else {
        return "none";
    }
}
function writeZipFile(zip, path) {
    zip.generateAsync({ type: "blob" }).then(content => {
        (0,file_saver__WEBPACK_IMPORTED_MODULE_2__.saveAs)(content, _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PathExt.basename(path));
    });
}
class OpenDirectWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__.Widget {
    constructor() {
        super({ node: createOpenNode() });
    }
    getValue() {
        return this.inputNode.value;
    }
    get inputNode() {
        return this.node.getElementsByTagName("input")[0];
    }
}


/***/ }),

/***/ "./style/icons/drive.svg":
/*!*******************************!*\
  !*** ./style/icons/drive.svg ***!
  \*******************************/
/***/ ((module) => {

module.exports = "<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\">\n  <path class=\"jp-icon3 jp-icon-selectable\" stroke=\"#616161\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" d=\"M22 12H2M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11zM6 16h.01M10 16h.01\"/>\n</svg>\n";

/***/ }),

/***/ "./style/icons/file-tree.svg":
/*!***********************************!*\
  !*** ./style/icons/file-tree.svg ***!
  \***********************************/
/***/ ((module) => {

module.exports = "<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"20\" viewBox=\"0 0 16 16\">\n  <path class=\"jp-icon3\" fill=\"#616161\" d=\"M16 10V6H5v1H3V4h9V0H0v4h2v10h3v2h11v-4H5v1H3V8h2v2z\"/>\n</svg>\n";

/***/ }),

/***/ "./style/icons/jupyter-fs.svg":
/*!************************************!*\
  !*** ./style/icons/jupyter-fs.svg ***!
  \************************************/
/***/ ((module) => {

module.exports = "<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"500\" viewBox=\"0 0 100 100\">\n  <rect class=\"jp-icon3\" stroke=\"#616161\" stroke-width=\"4\" width=\"91\" height=\"21\" fill=\"none\" rx=\"4\" x=\"4.5\" y=\"9.5\"/>\n  <circle class=\"jp-icon3\" fill=\"#616161\" cx=\"85\" cy=\"20\" r=\"3\"/>\n  <circle class=\"jp-icon3\" fill=\"#616161\" cx=\"73\" cy=\"20\" r=\"3\"/>\n\n  <rect class=\"jp-icon3\" stroke=\"#616161\" stroke-width=\"4\" width=\"91\" height=\"21\" fill=\"none\" rx=\"4\" x=\"4.5\" y=\"39.5\"/>\n  <circle class=\"jp-icon3\" fill=\"#616161\" cx=\"85\" cy=\"50\" r=\"3\"/>\n  <circle class=\"jp-icon3\" fill=\"#616161\" cx=\"73\" cy=\"50\" r=\"3\"/>\n\n  <rect class=\"jp-icon3\" stroke=\"#616161\" stroke-width=\"4\" width=\"91\" height=\"21\" fill=\"none\" rx=\"4\" x=\"4.5\" y=\"69.5\"/>\n  <circle class=\"jp-icon3\" fill=\"#616161\" cx=\"85\" cy=\"80\" r=\"3\"/>\n  <circle class=\"jp-icon3\" fill=\"#616161\" cx=\"73\" cy=\"80\" r=\"3\"/>\n</svg>\n";

/***/ }),

/***/ "./style/icons/visibility-off.svg":
/*!****************************************!*\
  !*** ./style/icons/visibility-off.svg ***!
  \****************************************/
/***/ ((module) => {

module.exports = "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" width=\"24\" height=\"24\">\n  <path class=\"jp-icon3\" fill=\"#616161\" d=\"M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z\"/>\n</svg>";

/***/ }),

/***/ "./style/icons/visibility.svg":
/*!************************************!*\
  !*** ./style/icons/visibility.svg ***!
  \************************************/
/***/ ((module) => {

module.exports = "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" width=\"24\" height=\"24\">\n  <path class=\"jp-icon3\" fill=\"#616161\" d=\"M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z\"/>\n</svg>";

/***/ })

}]);
//# sourceMappingURL=lib_index_js.5eedad9bb48a322ac20b.js.map