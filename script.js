const fs = require("fs");

const directory = "./";

const datasetNames = [
  "literature.json",
  "medical-articles.json",
  "moviescripts.json",
  "news-press-releases.json",
];

const models = ["GPT-4", "SpaCy", "NLTK", "LLAMA3"];

const metrics = {
  totalSVOs: require("./metrics/totalSVOs"),
  commonVerbs: require("./metrics/commonVerbs"),
  commonStem: require("./metrics/commonStem"),
  commonObject: require("./metrics/commonObjects"),
};

let results = {};

for (let datasetName of datasetNames) {
  const loadedData = {};

  for (let model of models) {
    loadedData[model] = JSON.parse(
      fs.readFileSync(directory + model + "/" + datasetName)
    );
  }

  for (let [name, func] of Object.entries(metrics)) {
    if (!results[name]) results[name] = {};
    results[name][datasetName] = func(loadedData);
  }
}

fs.writeFileSync(directory + "results.json", JSON.stringify(results, null, 2));

console.log("Comparison complete. Results saved to results.json.");
