'use client';

import { useEffect, useState } from 'react';
import { ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { analyticsApi, formatters, type SimpleForecast } from '@/lib/api';
import { TrendingUp, AlertCircle } from 'lucide-react';

const LoadingSpinner = () => (
  <div className="flex items-center justify-center h-96">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
  </div>
);

export default function Forecast() {
  const [data, setData] = useState<SimpleForecast | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const forecastData = await analyticsApi.getSimpleForecast();
        setData(forecastData);
        setError(null);
      } catch (err) {
        setError('Failed to fetch forecast data. Please ensure the API server is running.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <LoadingSpinner />;

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-6 text-center">
        <p className="text-red-400">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-yellow-500/10 border border-yellow-500/50 rounded-xl p-6 text-center">
        <p className="text-yellow-400">No forecast data available</p>
      </div>
    );
  }

  // Combine historical and forecast data for visualization
  const combinedData = [
    ...data.historical.map(d => ({
      quarter: d.quarter,
      actual: d.actual,
      predicted: null,
      lower_bound: null,
      upper_bound: null,
    })),
    ...data.forecast.map(d => ({
      quarter: d.quarter,
      actual: null,
      predicted: d.predicted,
      lower_bound: d.lower_bound,
      upper_bound: d.upper_bound,
    })),
  ];

  // Calculate forecast statistics
  const lastHistorical = data.historical[data.historical.length - 1];
  const firstForecast = data.forecast[0];
  const lastForecast = data.forecast[data.forecast.length - 1];

  const growthRate = lastHistorical && lastForecast
    ? ((lastForecast.predicted - (lastHistorical.actual || 0)) / (lastHistorical.actual || 1)) * 100
    : 0;

  const avgForecast = data.forecast.reduce((sum, d) => sum + d.predicted, 0) / data.forecast.length;

  return (
    <div className="space-y-8">
      {/* Forecast Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card-hover bg-gradient-to-br from-blue-500/20 to-blue-600/20 backdrop-blur-lg rounded-xl p-6 border border-blue-500/30">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-slate-300 text-sm mb-2">Latest Historical</p>
              <p className="text-3xl font-bold text-blue-400">
                {formatters.currency(lastHistorical?.actual || 0)}
              </p>
              <p className="text-slate-400 text-xs mt-2">{lastHistorical?.quarter}</p>
            </div>
            <div className="p-3 bg-blue-500/20 rounded-lg">
              <TrendingUp className="w-6 h-6 text-blue-400" />
            </div>
          </div>
        </div>

        <div className="card-hover bg-gradient-to-br from-purple-500/20 to-purple-600/20 backdrop-blur-lg rounded-xl p-6 border border-purple-500/30">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-slate-300 text-sm mb-2">Next Quarter Forecast</p>
              <p className="text-3xl font-bold text-purple-400">
                {formatters.currency(firstForecast?.predicted || 0)}
              </p>
              <p className="text-slate-400 text-xs mt-2">{firstForecast?.quarter}</p>
            </div>
            <div className="p-3 bg-purple-500/20 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-400" />
            </div>
          </div>
        </div>

        <div className="card-hover bg-gradient-to-br from-green-500/20 to-green-600/20 backdrop-blur-lg rounded-xl p-6 border border-green-500/30">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-slate-300 text-sm mb-2">Expected Growth</p>
              <p className="text-3xl font-bold text-green-400">
                {growthRate > 0 ? '+' : ''}{growthRate.toFixed(2)}%
              </p>
              <p className="text-slate-400 text-xs mt-2">Over forecast period</p>
            </div>
            <div className="p-3 bg-green-500/20 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Main Forecast Chart */}
      <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white">Loan Sales Forecast with Confidence Intervals</h3>
          <div className="flex items-center gap-2 text-slate-400 text-sm">
            <AlertCircle className="w-4 h-4" />
            <span>Shaded area represents prediction confidence</span>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={500}>
          <ComposedChart data={combinedData}>
            <defs>
              <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.05}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="quarter" stroke="#94a3b8" style={{ fontSize: '12px' }} />
            <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} tickFormatter={(value) => formatters.compact(value)} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
              labelStyle={{ color: '#f1f5f9' }}
              formatter={(value: number) => [formatters.currency(value), '']}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />

            {/* Confidence interval area */}
            <Area
              type="monotone"
              dataKey="upper_bound"
              stroke="none"
              fill="url(#confidenceGradient)"
              fillOpacity={1}
              name="Upper Bound"
            />
            <Area
              type="monotone"
              dataKey="lower_bound"
              stroke="none"
              fill="url(#confidenceGradient)"
              fillOpacity={1}
              name="Lower Bound"
            />

            {/* Historical actual values */}
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#3b82f6"
              strokeWidth={3}
              name="Historical Actual"
              dot={{ fill: '#3b82f6', r: 5 }}
              connectNulls={false}
            />

            {/* Forecasted values */}
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="#8b5cf6"
              strokeWidth={3}
              strokeDasharray="5 5"
              name="Forecast"
              dot={{ fill: '#8b5cf6', r: 5 }}
              connectNulls={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Forecast Details Table */}
      <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
        <h3 className="text-xl font-bold text-white mb-6">Detailed Forecast</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="pb-3 text-slate-300 font-semibold">Quarter</th>
                <th className="pb-3 text-slate-300 font-semibold">Predicted Value</th>
                <th className="pb-3 text-slate-300 font-semibold">Lower Bound</th>
                <th className="pb-3 text-slate-300 font-semibold">Upper Bound</th>
                <th className="pb-3 text-slate-300 font-semibold">Confidence Range</th>
              </tr>
            </thead>
            <tbody>
              {data.forecast.map((item, index) => {
                const range = (item.upper_bound && item.lower_bound)
                  ? item.upper_bound - item.lower_bound
                  : 0;
                const rangePercent = range / item.predicted * 100;

                return (
                  <tr key={index} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                    <td className="py-3 text-slate-200">{item.quarter}</td>
                    <td className="py-3 text-purple-400 font-semibold">
                      {formatters.currency(item.predicted)}
                    </td>
                    <td className="py-3 text-slate-400">
                      {item.lower_bound ? formatters.currency(item.lower_bound) : '-'}
                    </td>
                    <td className="py-3 text-slate-400">
                      {item.upper_bound ? formatters.currency(item.upper_bound) : '-'}
                    </td>
                    <td className="py-3 text-slate-400">
                      {range > 0 ? `±${rangePercent.toFixed(1)}%` : '-'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Forecast Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
          <h4 className="text-lg font-semibold text-white mb-4">Forecast Summary</h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Forecast Periods:</span>
              <span className="text-white font-semibold">{data.forecast.length} quarters</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Average Forecast:</span>
              <span className="text-white font-semibold">{formatters.currency(avgForecast)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Min Forecast:</span>
              <span className="text-white font-semibold">
                {formatters.currency(Math.min(...data.forecast.map(d => d.predicted)))}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Max Forecast:</span>
              <span className="text-white font-semibold">
                {formatters.currency(Math.max(...data.forecast.map(d => d.predicted)))}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
          <h4 className="text-lg font-semibold text-white mb-4">Model Information</h4>
          <div className="space-y-3">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-blue-400 mt-0.5" />
              <div>
                <p className="text-slate-300 text-sm">
                  Forecasts are generated using historical patterns and economic indicators.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-purple-400 mt-0.5" />
              <div>
                <p className="text-slate-300 text-sm">
                  Confidence intervals represent the range of likely outcomes based on model uncertainty.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-green-400 mt-0.5" />
              <div>
                <p className="text-slate-300 text-sm">
                  The model incorporates GDP growth, inflation, and banking metrics for predictions.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
