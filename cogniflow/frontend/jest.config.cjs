module.exports = {
  testEnvironment: "jsdom",
  setupFilesAfterEnv: ["<rootDir>/src/__tests__/setup.js"],
  testMatch: ["**/?(*.)+(test).[jt]s?(x)"],
  moduleFileExtensions: ["js", "jsx"],
  transform: {
    "^.+\\.(js|jsx)$": "babel-jest",
  },
  transformIgnorePatterns: [
    "node_modules/(?!(react-markdown|remark-|mdast-|micromark|unist-|vfile|hast-|estree-|property-information|space-separated-tokens|comma-separated-tokens|decode-named-character-reference|character-entities|bail|trough|unified|longest-streak|ccount|is-plain-obj|devlop|web-namespaces))",
  ],
};
