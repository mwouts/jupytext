/* Jupyter notebook extension that allows to configure Jupytext

Inspired from the toc2 extension at https://github.com/ipython-contrib/jupyter_contrib_nbextensions

Test the extension in a Jupyter notebook by adding two cells:

```python
# 1. Install the extension
import notebook.nbextensions
notebook.nbextensions.install_nbextension('.../jupytext/nbextension/jupytext.js', user=True)
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
], function(
    requirejs,
    $,
    Jupyter,
    events
) {
    "use strict";

    var jupytext_button = function() {
        if (!Jupyter.toolbar) {
            $([Jupyter.events]).on("app_initialized.NotebookApp", jupytext_button);
            return;
        }
        if ($("#jupytext_button").length === 0) {
            Jupyter.toolbar.add_buttons_group([{
                    'label' : 'Jupytext',
                    'help'   : 'Configure Jupytext',
                    'icon'   : 'fa-wrench'
                },
            ]);
        }
    };

    var jupytext_init = function() {
        jupytext_button();
    }

    var load_ipython_extension = function() {
        // Wait for the notebook to be fully loaded
        if (Jupyter.notebook !== undefined && Jupyter.notebook._fully_loaded) {
            // this tests if the notebook is fully loaded
            console.log("[jupytext] Notebook fully loaded -- jupytext extension initialized ")
            jupytext_init();
        } else {
            console.log("[jupytext] Waiting for notebook availability")
            events.on("notebook_loaded.Notebook", function() {
                console.log("[jupytext] jupytext initialized (via notebook_loaded)")
                jupytext_init();
            })
        }
    };

    return {
        load_ipython_extension: load_ipython_extension
    };
});
