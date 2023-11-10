/**
 * Configuration for Playwright using default from @jupyterlab/galata
 */
const baseConfig = require('@jupyterlab/galata/lib/playwright-config');

module.exports = {
  ...baseConfig,
  projects: [
    {
      name: 'jupytext',
      testMatch: 'tests/*.ts',
      testIgnore: '**/.ipynb_checkpoints/**',
      timeout: 60000,
      // use: {
      //   launchOptions: {
      //     // Force slow motion
      //     slowMo: 1000,
      //   },
      // },
    },
  ],
  // Visual comparison of screenshots can be flaky. Use a tolerance
  expect: {
    toMatchSnapshot: {
      maxDiffPixelRatio: 0.02,
    },
  },
  webServer: {
    command: 'jlpm start',
    url: 'http://localhost:8888/lab',
    timeout: 120 * 1000,
    reuseExistingServer: !process.env.CI,
  },
  // Switch to 'always' to keep raw assets for all tests
  preserveOutput: 'failures-only', // Breaks HTML report if use.video == 'on'
  // Try one retry as some tests are flaky
  // retries: process.env.CI ? 1 : 0,
};
