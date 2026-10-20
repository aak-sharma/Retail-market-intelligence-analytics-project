const datasetInput = document.getElementById("dataset");
const fileName = document.getElementById("file-name");

if (datasetInput && fileName) {
  datasetInput.addEventListener("change", () => {
    fileName.textContent = datasetInput.files.length
      ? datasetInput.files[0].name
      : "Choose Superstore CSV";
  });
}

// Refit Plotly charts when the viewport changes.
window.addEventListener("resize", () => {
  ["trend-chart", "category-chart"].forEach((id) => {
    const chart = document.getElementById(id);
    if (chart && window.Plotly) Plotly.Plots.resize(chart);
  });
});
