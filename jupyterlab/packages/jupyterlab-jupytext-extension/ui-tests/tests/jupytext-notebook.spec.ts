import { expect, test } from '@jupyterlab/galata';

// Define all formats that we would like to test
// We dont test Rmd and qmd formats here. Rmd cannot be
// opened by JupyterLab in the markdown format.
// Quarto must be available for qmd to work
const formats = [
  {
    createLabel: 'New Python Text Notebook with Light Format',
    pairLabel: 'Light Format',
    extension: '.py',
  },
  {
    createLabel: 'New Python Text Notebook with Percent Format',
    pairLabel: 'Percent Format',
    extension: '.py',
  },
  {
    createLabel: 'New Python Text Notebook with Hydrogen Format',
    pairLabel: 'Hydrogen Format',
    extension: '.py',
  },
  {
    createLabel: 'New Python Text Notebook with Nomarker Format',
    pairLabel: 'Nomarker Format',
    extension: '.py',
  },
  {
    createLabel: 'New Markdown Text Notebook',
    pairLabel: 'Markdown',
    extension: '.md',
  },
  {
    createLabel: 'New MyST Markdown Text Notebook',
    pairLabel: 'MyST Markdown',
    extension: '.md',
  },
];

// Get all possible menuPaths
const createNewMenuPaths = formats.map((format) => {
  return {
    menuPath: `Jupytext>New Text Notebook>${format.createLabel}`,
    extension: format.extension,
  };
});

const pairMenuPaths = formats.map((format) => {
  return {
    menuPath: `Jupytext>Pair Notebook>Pair Notebook with ${format.pairLabel}`,
    extension: format.extension,
  };
});

// Name of notebook file
const fileName = 'notebook.ipynb';

/**
 * Helper function to populate notebook cells and run them
 */
async function populateNotebook(page) {
  await page.notebook.setCell(0, 'raw', 'Just a raw cell');
  await page.notebook.addCell(
    'markdown',
    '## This is **bold** and *italic* [link to jupyter.org!](http://jupyter.org)'
  );
  await page.notebook.runCell(1, true);
  await page.notebook.addCell('code', '2 ** 3');
  await page.notebook.runCell(2, true);
}

test.describe('Jupytext Create Text Notebooks from Menu Tests', () => {
  createNewMenuPaths.forEach((paths) => {
    test(`Open menu item ${paths.menuPath}`, async ({ page }) => {
      // await page.goto();
      // Create new text notebook by clicking menupath item
      await page.menu.clickMenuItem(paths.menuPath);

      // Wait for the kernel dialog and accept it
      await page.waitForSelector('.jp-Dialog');
      await page.click('.jp-Dialog .jp-mod-accept');

      // Populate page
      await populateNotebook(page);
      // Save notebook
      await page.notebook.save();

      //   // Compare screenshots
      //   let imageName = `opened-${paths.menuPath.replace(/>/g, '-')}.png`;
      //   expect(await page.screenshot()).toMatchSnapshot(imageName.toLowerCase());

      // Try to open saved text notebook with Editor factory
      await page.filebrowser.open(`Untitled${paths.extension}`, 'Editor');

      // Compare text notebook contents
      const imageName = `opened-${paths.menuPath.replace(/>/g, '-')}-text.png`;
      expect(await page.screenshot()).toMatchSnapshot(imageName.toLowerCase());
    });
  });
});

test.describe('Jupytext Pair Notebooks from Menu Tests', () => {
  // Before each test start a new notebook and add some cell data
  test.beforeEach(async ({ page }) => {
    await page.notebook.createNew(fileName);
    await populateNotebook(page);
  });

  pairMenuPaths.forEach((paths) => {
    test(`Open menu item ${paths.menuPath}`, async ({ page }) => {
      // Click pairing command
      await page.menu.clickMenuItem(paths.menuPath);
      // Wait until we save notebook. Once we save it, paired file appears
      await page.notebook.save();
      // Try to open paired file
      await page.filebrowser.open(fileName.replace('.ipynb', paths.extension));

      const imageName = `paired-jupytext-${paths.menuPath.replace(
        />/g,
        '-'
      )}.png`;
      expect(await page.screenshot()).toMatchSnapshot(imageName.toLowerCase());
    });
  });
});
