import { expect, test } from '@jupyterlab/galata';

test('Open the settings editor with a Jupytext query', async ({ page }) => {
  await page.evaluate(async () => {
    await window.jupyterapp.commands.execute('settingeditor:open', {
      query: 'Jupytext',
    });
  });

  expect(
    await page.locator('.jp-PluginList .jp-FilterBox input').inputValue()
  ).toEqual('Jupytext');

  await expect(page.locator('.jp-SettingsForm')).toHaveCount(1);

  const pluginList = page.locator('.jp-PluginList');

  expect(await pluginList.screenshot()).toMatchSnapshot(
    'jupytext-settings-plugin-list.png'
  );

  const settingsPanel = page.locator('.jp-SettingsPanel');

  expect(await settingsPanel.screenshot()).toMatchSnapshot(
    'jupytext-settings-panel.png'
  );
});
