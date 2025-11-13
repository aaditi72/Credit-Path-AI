const rec = result.recommendation;

const colorMap = {
  "LOW RISK": "green",
  "MODERATE RISK": "orange",
  "HIGH RISK": "red"
};

resultCard.innerHTML = `
  <div class="border-l-4 pl-4 border-${colorMap[rec.risk_category.toUpperCase()] || 'gray'}-500">
    <h3 class="text-lg font-semibold text-gray-700">
      Decision: <span class="text-${colorMap[rec.risk_category.toUpperCase()] || 'gray'}-600">${rec.decision}</span>
    </h3>

    <p class="text-sm text-gray-500 mb-2">
      Risk Category: <b>${rec.risk_category}</b>
    </p>

    <p class="text-sm text-gray-500 mb-2">
      Default Probability: <b>${(rec.probability * 100).toFixed(2)}%</b>
    </p>

    <h4 class="text-md font-semibold text-gray-700 mt-4">Reasoning:</h4>
    <ul class="list-disc pl-5 text-gray-600 text-sm space-y-1">
      ${rec.reasoning.map(r => `<li>${r}</li>`).join("")}
    </ul>
  </div>
`;
