import antfu from '@antfu/eslint-config'

export default antfu({
  // Enable all rules from @antfu/eslint-config
  typescript: true,
  vue: true,

  // Disable certain rules
  rules: {
    'no-console': 'off',
    'no-debugger': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/no-unused-vars': ['warn', {
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
    }],
    'vue/multi-word-component-names': 'off',
    'vue/no-v-html': 'off',
    'style/brace-style': 'off',
    'style/comma-dangle': 'off',
    'style/member-delimiter-style': 'off',
    'antfu/if-newline': 'off',
    'antfu/top-level-function': 'off',
    'curly': 'off',
    'brace-style': 'off',
    'arrow-parens': 'off',
    'style/arrow-parens': 'off',
    'no-tabs': 'off',
    'no-mixed-spaces-and-tabs': 'off',
    'quotes': ['error', 'single'],
    'semi': ['error', 'always'],
    'space-before-function-paren': ['error', 'always'],
  },

  // Files to ignore
  ignores: [
    'dist',
    'node_modules',
    '*.min.*',
    'DjangoAdmin2',
    'coverage',
    'public',
    '__snapshots__',
    'temp',
    '*.d.ts',
    '*.config.js',
    'components.d.ts',
    'auto-imports.d.ts',
    'package-lock.json',
    'pnpm-lock.yaml',
    'yarn.lock',
    '.vscode',
    '.idea',
    '.git',
  ],
})
