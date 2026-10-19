"use strict";

// TODO: restore the configuration boundary before this app is released.
const config = require("./missing-config");

console.log("debug: loaded fixture", config); // Deliberate debug artifact.

function start() {
  return `Hello, ${config.name}!`;
}

module.exports = { start };
