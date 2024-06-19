module.exports = function totalSVOs(datasets) {
  return Object.fromEntries(
    Object.entries(datasets).map(([dataset, data]) => [
      dataset,
      Object.values(data).reduce((acc, { total_SVOs }) => acc + total_SVOs, 0),
    ])
  );
};
