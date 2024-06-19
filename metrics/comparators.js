function flattenCSL(record, name) {
  return (record.SVO_relationships || record.svo_relationships)
    .map((record) =>
      (record[name] ?? "")
        .split(",")
        .map((s) => s.trim())
        .filter((s) => s)
    )
    .flat(Infinity);
}

function commonWithReference({ reference, compareFunc }) {
  return function (datasets) {
    let common = Object.fromEntries(
      Object.entries(datasets).map(([name]) => [name, 0])
    );

    const datasetsToCompare = Object.entries(datasets).map(([name]) => name);

    const mappedDataset = Object.fromEntries(
      Object.entries(datasets).map(([name, files]) => [
        name,
        Object.fromEntries(
          Object.entries(files).map(([name, value]) => [
            name.match(/\d+/g).map(Number),
            value,
          ])
        ),
      ])
    );

    for (let name of Object.keys(mappedDataset[reference])) {
      const i = name;

      const referenceRecord = mappedDataset[reference][i];

      for (let name of datasetsToCompare) {
        const targetRecord = mappedDataset[name][i];

        if (!targetRecord) continue;

        common[name] += compareFunc({
          referenceRecord,
          targetRecord,
        });
      }
    }

    return common;
  };
}

function commonInCSL(propertyName) {
  return function ({ targetRecord, referenceRecord }) {
    const referenceAttributes = flattenCSL(referenceRecord, propertyName);
    const attributes = flattenCSL(targetRecord, propertyName);

    let count = 0;

    for (let attribute of attributes) {
      if (referenceAttributes.includes(attribute)) count++;
    }

    return count;
  };
}

module.exports = {
  commonInCSL,
  commonWithReference,
  flattenCSL,
};
