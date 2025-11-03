import { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { getAdvancedModelsInfo, getAdvancedForecast } from '../services/api';

const AdvancedModels = () => {
  const [modelsInfo, setModelsInfo] = useState(null);
  const [selectedModel, setSelectedModel] = useState('');
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [periods, setPeriods] = useState(4);

  useEffect(() => {
    loadModelsInfo();
  }, []);

  const loadModelsInfo = async () => {
    try {
      setLoading(true);
      const response = await getAdvancedModelsInfo();
      setModelsInfo(response.data);
      if (response.data.status === 'ready' && response.data.models.length > 0) {
        setSelectedModel(response.data.best_model);
      }
    } catch (error) {
      console.error('Error loading models info:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleForecast = async () => {
    if (!selectedModel) return;

    try {
      setForecastLoading(true);
      const response = await getAdvancedForecast(selectedModel, periods);
      setForecast(response.data);
    } catch (error) {
      console.error('Forecast error:', error);
      alert('Proqnoz xətası: ' + (error.response?.data?.detail || error.message));
    } finally {
      setForecastLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (!num) return '0';
    return new Intl.NumberFormat('az-AZ').format(Math.round(num));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Modelləri yüklənir...</p>
        </div>
      </div>
    );
  }

  if (!modelsInfo || modelsInfo.status === 'not_trained') {
    return (
      <div className="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-8 text-center">
        <div className="text-6xl mb-4">⚠️</div>
        <h2 className="text-2xl font-bold text-yellow-900 mb-2">Modellər Hələ Training edilməyib</h2>
        <p className="text-yellow-700 mb-4">
          Advanced modellər istifadə etmək üçün əvvəlcə training notebook-u run edin.
        </p>
        <div className="bg-white rounded-lg p-4 text-left max-w-2xl mx-auto">
          <p className="font-semibold mb-2">🔧 Addımlar:</p>
          <ol className="list-decimal list-inside space-y-2 text-sm">
            <li>Terminal-da notebooks/predictions folder-ə get</li>
            <li><code className="bg-gray-100 px-2 py-1 rounded">jupyter notebook advanced_forecasting_models.ipynb</code> run edin</li>
            <li>Notebook-da bütün cell-ləri run edin (Cell → Run All)</li>
            <li>Training tamamlandıqdan sonra bu səhifəni yeniləyin</li>
          </ol>
        </div>
      </div>
    );
  }

  const modelDetails = modelsInfo.models?.find(m => m.id === selectedModel);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border-2 border-purple-200">
        <h2 className="text-2xl font-bold text-purple-900 mb-2 flex items-center gap-2">
          <span className="text-3xl">🤖</span>
          Advanced ML & Time Series Models
        </h2>
        <p className="text-purple-700">
          Random Forest, XGBoost, ARIMA, SARIMA və SARIMAX modelləri ilə professional proqnozlaşdırma
        </p>
        <div className="mt-3 flex items-center gap-4 text-sm">
          <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full font-semibold">
            ✅ {modelsInfo.models?.length} Model Hazırdır
          </span>
          <span className="text-purple-600">
            🏆 Ən yaxşı model: {modelsInfo.best_model}
          </span>
          <span className="text-gray-600">
            📅 Training tarixi: {modelsInfo.training_date}
          </span>
        </div>
      </div>

      {/* Model Selection */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
          <span className="text-2xl">🎯</span>
          Model Seçimi
        </h3>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Model Selector */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Proqnoz Modeli
            </label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              {modelsInfo.models?.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.name} - {model.type} ({model.test_mape?.toFixed(2)}% MAPE)
                </option>
              ))}
            </select>

            <div className="mt-4">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Proqnoz Dövrləri
              </label>
              <select
                value={periods}
                onChange={(e) => setPeriods(Number(e.target.value))}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value={1}>1 Rüb</option>
                <option value={2}>2 Rüb</option>
                <option value={4}>4 Rüb (1 İl)</option>
                <option value={8}>8 Rüb (2 İl)</option>
              </select>
            </div>

            <button
              onClick={handleForecast}
              disabled={forecastLoading || !selectedModel}
              className="mt-4 w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg hover:from-purple-700 hover:to-blue-700 font-semibold shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {forecastLoading ? '🔄 Proqnoz hazırlanır...' : '🚀 Proqnoz Et'}
            </button>
          </div>

          {/* Model Info */}
          {modelDetails && (
            <div className="bg-gradient-to-br from-purple-50 to-white p-5 rounded-lg border-2 border-purple-200">
              <h4 className="font-bold text-purple-900 mb-3 flex items-center gap-2">
                <span className="text-xl">📊</span>
                {modelDetails.name}
              </h4>
              <p className="text-sm text-gray-700 mb-4">{modelDetails.description}</p>

              <div className="grid grid-cols-2 gap-3">
                <div className="bg-white p-3 rounded-lg shadow-sm">
                  <p className="text-xs text-gray-600 uppercase">Test MAE</p>
                  <p className="text-lg font-bold text-blue-600">{formatNumber(modelDetails.test_mae)}</p>
                </div>
                <div className="bg-white p-3 rounded-lg shadow-sm">
                  <p className="text-xs text-gray-600 uppercase">Test R²</p>
                  <p className="text-lg font-bold text-green-600">{modelDetails.test_r2?.toFixed(4)}</p>
                </div>
                <div className="bg-white p-3 rounded-lg shadow-sm col-span-2">
                  <p className="text-xs text-gray-600 uppercase">Test MAPE</p>
                  <p className="text-lg font-bold text-orange-600">{modelDetails.test_mape?.toFixed(2)}%</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Forecast Results */}
      {forecast && (
        <div className="space-y-6">
          {/* Forecast Chart */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <span className="text-2xl">📈</span>
              Proqnoz Nəticələri - {forecast.model.name}
            </h3>

            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={forecast.proqnozlar}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="dövr" />
                <YAxis />
                <Tooltip
                  formatter={(value) => formatNumber(value)}
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="yuxarı_sərhəd_95"
                  stackId="1"
                  stroke="#93c5fd"
                  fill="#dbeafe"
                  name="Yuxarı Sərhəd (95%)"
                />
                <Area
                  type="monotone"
                  dataKey="proqnoz"
                  stackId="2"
                  stroke="#8b5cf6"
                  fill="#c4b5fd"
                  name="Proqnoz"
                />
                <Area
                  type="monotone"
                  dataKey="aşağı_sərhəd_95"
                  stackId="3"
                  stroke="#93c5fd"
                  fill="#dbeafe"
                  name="Aşağı Sərhəd (95%)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Forecast Table */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <span className="text-2xl">📋</span>
              Detallı Proqnoz Cədvəli
            </h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dövr</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">İl</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rüb</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Proqnoz</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Aşağı (95%)</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Yuxarı (95%)</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {forecast.proqnozlar.map((item, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap font-medium">{item.dövr}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{item.il}</td>
                      <td className="px-6 py-4 whitespace-nowrap">Q{item.rüb}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-right font-bold text-purple-600">
                        {formatNumber(item.proqnoz)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-gray-600">
                        {formatNumber(item.aşağı_sərhəd_95)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-gray-600">
                        {formatNumber(item.yuxarı_sərhəd_95)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Feature Importance (for ML models) */}
          {forecast.feature_importance && (
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <span className="text-2xl">🎯</span>
                Feature Importance - Top 10
              </h3>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={forecast.feature_importance} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" />
                  <YAxis dataKey="feature" type="category" width={150} />
                  <Tooltip
                    formatter={(value) => value.toFixed(4)}
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                  />
                  <Bar dataKey="importance" fill="#8b5cf6" radius={[0, 8, 8, 0]} />
                </BarChart>
              </ResponsiveContainer>
              <p className="text-sm text-gray-600 mt-4">
                💡 Feature Importance göstərir ki, modelin proqnozlarında hansı dəyişənlər daha çox rol oynayır.
                Daha yüksək dəyər = Daha vacib feature.
              </p>
            </div>
          )}

          {/* Model Explanation */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border-2 border-blue-200">
            <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
              <span className="text-2xl">📚</span>
              Model Haqqında
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-semibold text-gray-700">Model Tipi</p>
                <p className="text-base text-gray-900">{forecast.model_type}</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-700">Test Performansı</p>
                <p className="text-base text-gray-900">MAE: {formatNumber(forecast.model.test_mae)}, MAPE: {forecast.model.test_mape?.toFixed(2)}%</p>
              </div>
              <div className="col-span-2">
                <p className="text-sm font-semibold text-gray-700 mb-2">Təsvir</p>
                <p className="text-sm text-gray-700">{forecast.model.description}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* All Models Comparison */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
          <span className="text-2xl">⚖️</span>
          Bütün Modellərin Müqayisəsi
        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Model</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tip</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">MAE</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">R²</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">MAPE %</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {modelsInfo.models?.map((model, idx) => (
                <tr
                  key={idx}
                  className={`hover:bg-gray-50 ${model.name === modelsInfo.best_model ? 'bg-green-50' : ''}`}
                >
                  <td className="px-6 py-4 whitespace-nowrap font-medium">
                    {model.name === modelsInfo.best_model && <span className="mr-2">🏆</span>}
                    {model.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{model.type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right font-semibold">{formatNumber(model.test_mae)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right font-semibold text-green-600">
                    {model.test_r2?.toFixed(4)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right font-semibold text-orange-600">
                    {model.test_mape?.toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-gray-600 mt-4">
          🏆 Ən yaxşı model ən kiçik MAE (Mean Absolute Error) dəyərinə görə seçilir
        </p>
      </div>
    </div>
  );
};

export default AdvancedModels;
