const { defineConfig } = require('cypress')

module.exports = defineConfig({
  video: true,
  viewportHeight: 568,
  viewportWidth: 320,
  projectId: '8r2xra',
  defaultCommandTimeout: 4000,
  allowCypressEnv: false,
  env: {
    admin_url: '/admin/',
    admin_login_url: '/admin/login/',
    legend_url: '/legend',
    settings_url: '/settings',
  },
  e2e: {
    baseUrl: 'http://localhost:8000/',
    supportFile: 'cypress/support/commands.js',
    specPattern: 'cypress/e2e/**/*.{js,jsx,ts,tsx}',
    setupNodeEvents(on, config) {
      const configProcessScopedVariables = {}

      on('task', {
        set: (keySet) => {
          Object.entries(keySet).forEach(([key, value]) => {
            configProcessScopedVariables[key] = value
          })
          return null
        },
        get: (keys) => {
          const variablesToReturn = {}
          keys.forEach((key) => {
            variablesToReturn[key] = configProcessScopedVariables[key]
          })
          return variablesToReturn
        },
      })

      return config
    },
  },
})
