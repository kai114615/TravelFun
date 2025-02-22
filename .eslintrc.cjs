module.exports = {
  extends: '@antfu',
  rules: {
    // 調整 console.log 政策：允許警告但不阻止提交
    'no-console': 'warn',

    // 解決重複報錯 (unused-vars) 問題，合併 @typescript-eslint 規則
    'unused-imports/no-unused-vars': 'off',
    '@typescript-eslint/no-unused-vars': [
      'warn',
      { varsIgnorePattern: '^_', argsIgnorePattern: '^_' }
    ],

    // 修正 Vue 未使用變數報錯
    'vue/no-unused-vars': 'warn',
    'vue/no-unused-refs': 'warn',

    // 修正 Vue 組件命名與屬性排序報錯
    'vue/component-name-in-template-casing': ['error', 'PascalCase', { ignores: ['n-tag'] }],
    'vue/attributes-order': 'warn',

    // 保持原本的分號規則
    'semi': ['error', 'never'],
    '@typescript-eslint/semi': 'off',
  },
};
