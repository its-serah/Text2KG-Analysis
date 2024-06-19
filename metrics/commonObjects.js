const { commonInCSL, commonWithReference } = require("./comparators");

module.exports = commonWithReference({
  reference: "GPT-4",
  compareFunc: commonInCSL("object"),
});
