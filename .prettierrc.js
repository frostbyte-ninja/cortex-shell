const config = {
  printWidth: 120,
  useTabs: false,
  tabWidth: 2,
  semi: true,
  singleQuote: false,
  quoteProps: "as-needed",
  trailingComma: "all",
  plugins: [require.resolve("prettier-plugin-toml")],
};

module.exports = config;
