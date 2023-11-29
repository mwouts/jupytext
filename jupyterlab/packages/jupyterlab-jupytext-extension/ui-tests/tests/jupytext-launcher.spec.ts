import { expect, test } from '@jupyterlab/galata';

test.describe('Jupytext Launcher Category', () => {
  test.use({ autoGoto: false, viewport: { height: 1020, width: 1280 } });
  test('should have Jupytext category in launcher', async ({ page }) => {
    await page.goto();
    await page.waitForSelector('.jp-LauncherCard-label');

    const imageName = 'launcher-category.png';
    expect(await page.screenshot()).toMatchSnapshot(imageName.toLowerCase());
  });
});
