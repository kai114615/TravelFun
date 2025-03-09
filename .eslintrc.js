module.exports = {
  root: true,
  env: {
    'browser': true,
    'es2021': true,
    'node': true,
    'vue/setup-compiler-macros': true,
  },
  extends: [
    'plugin:vue/vue3-recommended',
    'eslint:recommended',
    '@vue/typescript/recommended',
    '@vue/prettier',
    '@vue/prettier/@typescript-eslint',
  ],
  parserOptions: {
    ecmaVersion: 2021,
  },
  rules: {
    'no-console': 'off',
    'no-debugger': 'off',
    'space-before-function-paren': 'off',
    'vue/multi-word-component-names': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/no-unused-vars': 'off',
    'unused-imports/no-unused-vars': 'off',
    'node/prefer-global/process': 'off',
    'regexp/no-super-linear-backtracking': 'off',
    'ts/ban-ts-comment': 'off',
    'vue/html-self-closing': ['error', {
      html: {
        void: 'always',
        normal: 'always',
        component: 'always'
      }
    }]
  },
};
