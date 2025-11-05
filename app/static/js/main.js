// Global state
let modelsData = null;
let allModels = [];
let currentPredictionData = null;
let historicalChart = null;
let scenariosChart = null;

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Initializing Loan Sales Prediction App');

    // Load models and statistics
    await loadModels();
    await loadStatistics();
    setupEventListeners();
});

// Load models from API
async function loadModels() {
    try {
        const response = await fetch('/api/models');
        const data = await response.json();

        modelsData = data;
        allModels = [...data.models.ml, ...data.models.ts];

        // Populate model dropdown
        populateModelDropdown(data);

        // Populate models info grid
        populateModelsGrid(data);

        console.log(`✅ Loaded ${data.total} models`);
    } catch (error) {
        console.error('❌ Error loading models:', error);
        showError('Failed to load models');
    }
}

// Populate model dropdown
function populateModelDropdown(data) {
    const select = document.getElementById('model');
    select.innerHTML = '';

    // Recommended models
    if (data.categories.recommended.length > 0) {
        const optgroup = document.createElement('optgroup');
        optgroup.label = '📊 Recommended (Top Performers)';

        data.categories.recommended.forEach((modelName, index) => {
            const option = document.createElement('option');
            option.value = modelName;
            option.textContent = modelName;
            if (index === 0) option.textContent += ' ⭐';
            optgroup.appendChild(option);
        });

        select.appendChild(optgroup);
    }

    // Advanced ML models
    if (data.categories.advanced_ml.length > 0) {
        const optgroup = document.createElement('optgroup');
        optgroup.label = '🔬 Advanced ML Models';

        data.categories.advanced_ml.forEach(modelName => {
            const option = document.createElement('option');
            option.value = modelName;
            option.textContent = modelName;
            optgroup.appendChild(option);
        });

        select.appendChild(optgroup);
    }

    // Time series models
    if (data.categories.time_series.length > 0) {
        const optgroup = document.createElement('optgroup');
        optgroup.label = '📈 Time Series Models';

        data.categories.time_series.forEach(modelName => {
            const option = document.createElement('option');
            option.value = modelName;
            option.textContent = modelName;
            optgroup.appendChild(option);
        });

        select.appendChild(optgroup);
    }

    // Experimental models
    if (data.categories.experimental.length > 0) {
        const optgroup = document.createElement('optgroup');
        optgroup.label = '⚠️ Experimental (Not Recommended)';

        data.categories.experimental.forEach(modelName => {
            const option = document.createElement('option');
            option.value = modelName;
            option.textContent = modelName;
            optgroup.appendChild(option);
        });

        select.appendChild(optgroup);
    }
}

// Populate models info grid
function populateModelsGrid(data) {
    const grid = document.getElementById('models-grid');
    grid.innerHTML = '';

    // Show top 6 models (filter out models with no metrics)
    const topModels = [...allModels]
        .filter(m => m.metrics && m.metrics.test_r2 !== undefined)
        .sort((a, b) => (b.metrics?.test_r2 || -999) - (a.metrics?.test_r2 || -999))
        .slice(0, 6);

    topModels.forEach((model, index) => {
        const card = createModelCard(model, index + 1);
        grid.appendChild(card);
    });
}

// Create model card
function createModelCard(model, rank) {
    const card = document.createElement('div');
    card.className = 'model-card';

    const typeClass = model.type === 'ml' ? 'type-ml' : 'type-ts';
    const typeName = model.type === 'ml' ? 'ML' : 'Time Series';

    card.innerHTML = `
        <div class="model-card-header">
            <div class="model-name">${rank}. ${model.name}</div>
            <span class="model-type-badge ${typeClass}">${typeName}</span>
        </div>
        <div class="model-metrics">
            <div class="model-metric">
                <span class="model-metric-label">R²</span>
                <span class="model-metric-value">${model.metrics?.test_r2 ? model.metrics.test_r2.toFixed(4) : 'N/A'}</span>
            </div>
            <div class="model-metric">
                <span class="model-metric-label">MAPE</span>
                <span class="model-metric-value">${model.metrics?.test_mape ? model.metrics.test_mape.toFixed(2) + '%' : 'N/A'}</span>
            </div>
        </div>
    `;

    return card;
}

// Load statistics
async function loadStatistics() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        document.getElementById('total-models').textContent = data.total_models;

        if (data.best_overall && data.best_overall.r2) {
            document.getElementById('best-r2').textContent = data.best_overall.r2.toFixed(4);
        } else {
            document.getElementById('best-r2').textContent = 'N/A';
        }

        console.log('✅ Statistics loaded');
    } catch (error) {
        console.error('❌ Error loading statistics:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    const form = document.getElementById('prediction-form');
    form.addEventListener('submit', handlePrediction);

    const compareBtn = document.getElementById('compare-btn');
    compareBtn.addEventListener('click', openComparisonModal);
}

// Handle prediction
async function handlePrediction(e) {
    e.preventDefault();

    const year = parseInt(document.getElementById('year').value);
    const quarter = parseInt(document.getElementById('quarter').value);
    const model = document.getElementById('model').value;

    if (!model) {
        showError('Please select a model');
        return;
    }

    // Show loading
    showLoading();

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model, year, quarter })
        });

        const data = await response.json();

        if (data.success) {
            showSingleResult(data);
        } else {
            showError(data.error || 'Prediction failed');
        }
    } catch (error) {
        console.error('❌ Prediction error:', error);
        showError('Failed to make prediction');
    }
}

// Show single prediction result
function showSingleResult(data) {
    const resultsSection = document.getElementById('results-section');
    const singleResult = document.getElementById('single-result');
    const comparisonResults = document.getElementById('comparison-results');
    const loadingState = document.getElementById('loading-state');
    const errorState = document.getElementById('error-state');

    // Show results section
    resultsSection.style.display = 'block';
    singleResult.style.display = 'block';
    comparisonResults.style.display = 'none';
    loadingState.style.display = 'none';
    errorState.style.display = 'none';

    // Update values
    document.getElementById('prediction-value').textContent = `${data.prediction_formatted} AZN`;
    document.getElementById('prediction-period').textContent = `${data.year} Q${data.quarter}`;
    document.getElementById('prediction-model').textContent = data.model;

    // Update metrics (with fallbacks for missing metrics)
    document.getElementById('metric-r2').textContent = data.metrics?.test_r2 ? data.metrics.test_r2.toFixed(4) : 'N/A';
    document.getElementById('metric-rmse').textContent = data.metrics?.test_rmse ? formatNumber(data.metrics.test_rmse) : 'N/A';
    document.getElementById('metric-mae').textContent = data.metrics?.test_mae ? formatNumber(data.metrics.test_mae) : 'N/A';
    document.getElementById('metric-mape').textContent = data.metrics?.test_mape ? `${data.metrics.test_mape.toFixed(2)}%` : 'N/A';

    // Display scenarios
    displayScenarios(data.scenarios);

    // Display historical data
    displayHistoricalData(data.historical, data.year, data.quarter);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Display prediction scenarios
function displayScenarios(scenarios) {
    const scenariosContainer = document.getElementById('scenarios-container');
    if (!scenariosContainer) {
        // Create scenarios section if it doesn't exist
        const singleResult = document.getElementById('single-result');
        const newSection = document.createElement('div');
        newSection.id = 'scenarios-section';
        newSection.className = 'scenarios-section';
        newSection.innerHTML = `
            <h3>📊 Prediction Scenarios</h3>
            <div id="scenarios-container" class="scenarios-grid"></div>
        `;
        // Insert after metrics
        const metricsGrid = singleResult.querySelector('.metrics-grid');
        metricsGrid.after(newSection);
    }

    const container = document.getElementById('scenarios-container');
    container.innerHTML = `
        <div class="scenario-card scenario-pessimistic">
            <div class="scenario-label">⚠️ Pessimistic</div>
            <div class="scenario-value">${scenarios.pessimistic_formatted} AZN</div>
        </div>
        <div class="scenario-card scenario-base">
            <div class="scenario-label">🎯 Base Prediction</div>
            <div class="scenario-value">${scenarios.base_formatted} AZN</div>
        </div>
        <div class="scenario-card scenario-optimistic">
            <div class="scenario-label">🚀 Optimistic</div>
            <div class="scenario-value">${scenarios.optimistic_formatted} AZN</div>
        </div>
    `;
}

// Display historical data
function displayHistoricalData(historical, currentYear, currentQuarter) {
    const historicalContainer = document.getElementById('historical-container');
    if (!historicalContainer) {
        // Create historical section if it doesn't exist
        const singleResult = document.getElementById('single-result');
        const newSection = document.createElement('div');
        newSection.id = 'historical-section';
        newSection.className = 'historical-section';
        newSection.innerHTML = `
            <h3>📈 Historical Data (Q${currentQuarter})</h3>
            <div id="historical-container" class="historical-grid"></div>
        `;
        // Insert after scenarios
        const scenariosSection = document.getElementById('scenarios-section');
        if (scenariosSection) {
            scenariosSection.after(newSection);
        }
    }

    const container = document.getElementById('historical-container');

    if (historical && historical.length > 0) {
        container.innerHTML = historical.map(record => `
            <div class="historical-card">
                <div class="historical-year">${record.year} Q${record.quarter}</div>
                <div class="historical-value">${record.sales_formatted} AZN</div>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<p class="no-data">No historical data available for this quarter</p>';
    }
}

// Open comparison modal
function openComparisonModal() {
    const modal = document.getElementById('comparison-modal');
    const checkboxContainer = document.getElementById('model-checkboxes');

    // Clear existing checkboxes
    checkboxContainer.innerHTML = '';

    // Get top 5 models for pre-selection (filter out models with no metrics)
    const topModels = [...allModels]
        .filter(m => m.metrics && m.metrics.test_r2 !== undefined)
        .sort((a, b) => (b.metrics?.test_r2 || -999) - (a.metrics?.test_r2 || -999))
        .slice(0, 5)
        .map(m => m.name);

    // Create checkboxes
    allModels.forEach((model, index) => {
        const item = document.createElement('div');
        item.className = 'checkbox-item';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `model-${index}`;
        checkbox.value = model.name;

        // Pre-select top 5
        if (topModels.includes(model.name)) {
            checkbox.checked = true;
        }

        const label = document.createElement('label');
        label.htmlFor = `model-${index}`;
        label.className = 'checkbox-label';

        const typeClass = model.type === 'ml' ? 'type-ml' : 'type-ts';
        const typeName = model.type === 'ml' ? 'ML' : 'TS';

        label.innerHTML = `
            <span>${model.name}</span>
            <span class="model-type-badge ${typeClass}">${typeName}</span>
        `;

        item.appendChild(checkbox);
        item.appendChild(label);
        checkboxContainer.appendChild(item);
    });

    modal.classList.add('active');
}

// Close comparison modal
function closeComparisonModal() {
    const modal = document.getElementById('comparison-modal');
    modal.classList.remove('active');
}

// Run comparison
async function runComparison() {
    const checkboxes = document.querySelectorAll('#model-checkboxes input[type="checkbox"]:checked');
    const selectedModels = Array.from(checkboxes).map(cb => cb.value);

    if (selectedModels.length < 2) {
        alert('Please select at least 2 models to compare');
        return;
    }

    if (selectedModels.length > 5) {
        alert('Please select maximum 5 models to compare');
        return;
    }

    closeComparisonModal();

    const year = parseInt(document.getElementById('year').value);
    const quarter = parseInt(document.getElementById('quarter').value);

    // Show loading
    showLoading();

    try {
        const response = await fetch('/api/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ models: selectedModels, year, quarter })
        });

        const data = await response.json();

        if (data.success) {
            showComparisonResults(data);
        } else {
            showError('Comparison failed');
        }
    } catch (error) {
        console.error('❌ Comparison error:', error);
        showError('Failed to compare models');
    }
}

// Show comparison results
function showComparisonResults(data) {
    const resultsSection = document.getElementById('results-section');
    const singleResult = document.getElementById('single-result');
    const comparisonResults = document.getElementById('comparison-results');
    const loadingState = document.getElementById('loading-state');
    const errorState = document.getElementById('error-state');

    // Show results section
    resultsSection.style.display = 'block';
    singleResult.style.display = 'none';
    comparisonResults.style.display = 'block';
    loadingState.style.display = 'none';
    errorState.style.display = 'none';

    // Update period
    document.getElementById('comparison-period').textContent =
        `Comparing predictions for ${data.year} Q${data.quarter}`;

    // Display historical data for comparison
    displayComparisonHistorical(data.historical, data.year, data.quarter);

    // Populate table
    const tbody = document.getElementById('comparison-table-body');
    tbody.innerHTML = '';

    data.results.forEach((result, index) => {
        const row = document.createElement('tr');

        const rankClass = index === 0 ? 'rank-1' : index === 1 ? 'rank-2' : index === 2 ? 'rank-3' : 'rank-other';
        const typeClass = result.type === 'ml' ? 'type-ml' : 'type-ts';
        const typeName = result.type === 'ml' ? 'ML' : 'TS';

        // Show scenarios if available
        const scenariosHtml = result.scenarios ? `
            <div class="scenarios-mini">
                <span class="scenario-mini pessimistic" title="Pessimistic">${result.scenarios.pessimistic_formatted}</span>
                <span class="scenario-mini optimistic" title="Optimistic">${result.scenarios.optimistic_formatted}</span>
            </div>
        ` : '';

        row.innerHTML = `
            <td>
                <span class="rank-badge ${rankClass}">${index + 1}</span>
            </td>
            <td>${result.model}</td>
            <td>
                <span class="model-type-badge ${typeClass}">${typeName}</span>
            </td>
            <td>
                <strong>${result.prediction_formatted} AZN</strong>
                ${scenariosHtml}
            </td>
            <td>${result.metrics?.test_r2 ? result.metrics.test_r2.toFixed(4) : 'N/A'}</td>
            <td>${result.metrics?.test_mape ? result.metrics.test_mape.toFixed(2) + '%' : 'N/A'}</td>
        `;

        tbody.appendChild(row);
    });

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Display historical data in comparison view
function displayComparisonHistorical(historical, currentYear, currentQuarter) {
    const comparisonResults = document.getElementById('comparison-results');
    let historicalSection = document.getElementById('comparison-historical-section');

    if (!historicalSection) {
        historicalSection = document.createElement('div');
        historicalSection.id = 'comparison-historical-section';
        historicalSection.className = 'historical-section';

        // Insert before the table
        const table = comparisonResults.querySelector('.comparison-table-container');
        comparisonResults.insertBefore(historicalSection, table);
    }

    historicalSection.innerHTML = `
        <h3>📈 Historical Data (Q${currentQuarter})</h3>
        <div class="historical-grid">
            ${historical && historical.length > 0 ? historical.map(record => `
                <div class="historical-card">
                    <div class="historical-year">${record.year} Q${record.quarter}</div>
                    <div class="historical-value">${record.sales_formatted} AZN</div>
                </div>
            `).join('') : '<p class="no-data">No historical data available</p>'}
        </div>
    `;
}

// Show loading state
function showLoading() {
    const resultsSection = document.getElementById('results-section');
    const singleResult = document.getElementById('single-result');
    const comparisonResults = document.getElementById('comparison-results');
    const loadingState = document.getElementById('loading-state');
    const errorState = document.getElementById('error-state');

    resultsSection.style.display = 'block';
    singleResult.style.display = 'none';
    comparisonResults.style.display = 'none';
    loadingState.style.display = 'block';
    errorState.style.display = 'none';

    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Show error state
function showError(message) {
    const resultsSection = document.getElementById('results-section');
    const singleResult = document.getElementById('single-result');
    const comparisonResults = document.getElementById('comparison-results');
    const loadingState = document.getElementById('loading-state');
    const errorState = document.getElementById('error-state');

    resultsSection.style.display = 'block';
    singleResult.style.display = 'none';
    comparisonResults.style.display = 'none';
    loadingState.style.display = 'none';
    errorState.style.display = 'block';

    document.getElementById('error-text').textContent = message;

    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Format number with commas
function formatNumber(num) {
    return Math.round(num).toLocaleString('en-US');
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('comparison-modal');
    if (e.target === modal) {
        closeComparisonModal();
    }
});
