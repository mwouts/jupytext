/*-----------------------------------------------------------------------------
| Copyright (c) Jupyter Development Team.
| Distributed under the terms of the Modified BSD License.
|----------------------------------------------------------------------------*/

// We copy some of the pageconfig parsing logic in @jupyterlab/coreutils
// below, since this must run before any other files are loaded (including
// @jupyterlab/coreutils).

/**
 * Get global configuration data for the Jupyter application.
 *
 * @param name - The name of the configuration option.
 *
 * @returns The config value or an empty string if not found.
 *
 * #### Notes
 * All values are treated as strings. For browser based applications, it is
 * assumed that the page HTML includes a script tag with the id
 * `jupyter-config-data` containing the configuration as valid JSON.
 */

let _CONFIG_DATA = null;
function getOption(name) {
  if (_CONFIG_DATA === null) {
    let configData = {};
    // Use script tag if available.
    if (typeof document !== 'undefined' && document) {
      const el = document.getElementById('jupyter-config-data');

      if (el) {
        configData = JSON.parse(el.textContent || '{}');
      }
    }
    _CONFIG_DATA = configData;
  }

  return _CONFIG_DATA[name] || '';
}

/**
 * Hide the loading indicator once the app is fully loaded
 */
function hideAppLoadingIndicator() {
  const indicator = document.getElementById('jupyterlite-loading-indicator');
  if (indicator) {
    indicator.classList.add('hidden');
    indicator.addEventListener('animationend', () => {
      indicator.remove();
      // Remove theme classes after the loading indicator is removed
      document.body.classList.remove('jp-mod-dark', 'jp-mod-light');
    }, { once: true });
  }
}

/**
 * Apply theme to loading indicator based on saved settings in IndexedDB
 */
async function applyThemeToAppLoadingIndicator() {
  const indicator = document.getElementById('jupyterlite-loading-indicator');
  if (!indicator) {
    return;
  }

  // Hide the indicator by default
  indicator.classList.add('hidden');

  const showLoadingIndicator = getOption('showLoadingIndicator');
  // Only show the indicator if explicitly set to true
  if (showLoadingIndicator === true) {
    indicator.classList.remove('hidden');
  } else {
    return;
  }

  try {
    const baseUrl = getOption('baseUrl');
    const defaultStorageName = `JupyterLite Storage - ${baseUrl}`;
    const storageName = getOption('settingsStorageName') || defaultStorageName;

    const localforageModule = await import('localforage');
    const localforage = localforageModule.default;

    const settingsDB = localforage.createInstance({
      name: storageName,
      storeName: 'settings'
    });

    const key = '@jupyterlab/apputils-extension:themes';
    const settings = await settingsDB.getItem(key);

    let isDarkTheme = false;

    if (settings) {
      // Use regex to find "theme": "name of theme" pattern, since the
      // settings are stored as a raw string
      const themeRegex = /"theme"\s*:\s*"([^"]+)"/i;
      const matches = settings.match(themeRegex);

      if (matches && matches[1]) {
        const themeName = matches[1].toLowerCase();
        isDarkTheme =
          themeName.includes('dark') ||
          themeName.includes('night') ||
          themeName.includes('black');
      }
    }

    document.body.classList.remove('jp-mod-dark', 'jp-mod-light');

    if (isDarkTheme) {
      document.body.classList.add('jp-mod-dark');
    } else {
      document.body.classList.add('jp-mod-light');
    }
  } catch (e) {
    console.warn('Could not apply theme to loading indicator:', e);
    // Fallback to light theme on error
    document.body.classList.remove('jp-mod-dark');
    document.body.classList.add('jp-mod-light');
  }
}

// eslint-disable-next-line no-undef
__webpack_public_path__ = getOption('fullStaticUrl') + '/';

function loadScript(url) {
  return new Promise((resolve, reject) => {
    const newScript = document.createElement('script');
    newScript.onerror = reject;
    newScript.onload = resolve;
    newScript.async = true;
    document.head.appendChild(newScript);
    newScript.src = url;
  });
}

async function loadComponent(url, scope) {
  await loadScript(url);

  // From https://webpack.js.org/concepts/module-federation/#dynamic-remote-containers
  await __webpack_init_sharing__('default');
  const container = window._JUPYTERLAB[scope];
  // Initialize the container, it may provide shared modules and may need ours
  await container.init(__webpack_share_scopes__.default);
}

void (async function bootstrap() {
  await applyThemeToAppLoadingIndicator();

  // This is all the data needed to load and activate plugins. This should be
  // gathered by the server and put onto the initial page template.
  const extension_data = getOption('federated_extensions');

  // We first load all federated components so that the shared module
  // deduplication can run and figure out which shared modules from all
  // components should be actually used. We have to do this before importing
  // and using the module that actually uses these components so that all
  // dependencies are initialized.
  let labExtensionUrl = getOption('fullLabextensionsUrl');
  const extensions = await Promise.allSettled(
    extension_data.map(async data => {
      await loadComponent(`${labExtensionUrl}/${data.name}/${data.load}`, data.name);
    })
  );

  extensions.forEach(p => {
    if (p.status === 'rejected') {
      // There was an error loading the component
      console.error(p.reason);
    }
  });

  // Now that all federated containers are initialized with the main
  // container, we can import the main function.
  let main = (await import('./index.js')).main;
  await main();

  hideAppLoadingIndicator();
})();
