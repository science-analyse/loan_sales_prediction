'use client';

import { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart, Line } from 'recharts';
import { analyticsApi, type EconomicIndicator } from '@/lib/api';

const LoadingSpinner = () => (
  <div className="flex items-center justify-center h-96">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
  </div>
);

export default function Economic() {
  const [data, setData] = useState<EconomicIndicator[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const economicData = await analyticsApi.getEconomicIndicators();
        setData(economicData);
        setError(null);
      } catch (err) {
        setError('Failed to fetch economic indicators. Please ensure the API server is running.');
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

  return (
    <div className="space-y-8">
      {/* GDP Growth and Inflation */}
      <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
        <h3 className="text-xl font-bold text-white mb-6">GDP Growth & Inflation Rate</h3>
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={data}>
            <defs>
              <linearGradient id="gdpGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
              </linearGradient>
              <linearGradient id="inflationGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="quarter" stroke="#94a3b8" style={{ fontSize: '12px' }} />
            <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} tickFormatter={(value) => `${value}%`} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
              labelStyle={{ color: '#f1f5f9' }}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            <Area type="monotone" dataKey="gdp_growth" stroke="#10b981" fillOpacity={1} fill="url(#gdpGradient)" name="GDP Growth %" />
            <Line type="monotone" dataKey="inflation" stroke="#ef4444" strokeWidth={2} name="Inflation %" dot={{ fill: '#ef4444', r: 4 }} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Unemployment Rate */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
          <h3 className="text-xl font-bold text-white mb-6">Unemployment Rate</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data}>
              <defs>
                <linearGradient id="unemploymentGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="quarter" stroke="#94a3b8" style={{ fontSize: '12px' }} />
              <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} tickFormatter={(value) => `${value}%`} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                labelStyle={{ color: '#f1f5f9' }}
              />
              <Area type="monotone" dataKey="unemployment" stroke="#f59e0b" fillOpacity={1} fill="url(#unemploymentGradient)" name="Unemployment %" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Oil Price */}
        <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
          <h3 className="text-xl font-bold text-white mb-6">Oil Price (USD/Barrel)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data}>
              <defs>
                <linearGradient id="oilGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="quarter" stroke="#94a3b8" style={{ fontSize: '12px' }} />
              <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} tickFormatter={(value) => `$${value}`} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                labelStyle={{ color: '#f1f5f9' }}
              />
              <Area type="monotone" dataKey="oil_price" stroke="#8b5cf6" fillOpacity={1} fill="url(#oilGradient)" name="Oil Price" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Exchange Rate */}
      <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
        <h3 className="text-xl font-bold text-white mb-6">Exchange Rate (AZN/USD)</h3>
        <ResponsiveContainer width="100%" height={350}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="exchangeGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="quarter" stroke="#94a3b8" style={{ fontSize: '12px' }} />
            <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} domain={['dataMin - 0.05', 'dataMax + 0.05']} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
              labelStyle={{ color: '#f1f5f9' }}
            />
            <Area type="monotone" dataKey="exchange_rate" stroke="#06b6d4" fillOpacity={1} fill="url(#exchangeGradient)" name="Exchange Rate" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
          <p className="text-slate-400 text-sm mb-2">Average GDP Growth</p>
          <p className="text-2xl font-bold text-green-400">
            {(data.reduce((sum, d) => sum + d.gdp_growth, 0) / data.length).toFixed(2)}%
          </p>
        </div>
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
          <p className="text-slate-400 text-sm mb-2">Average Inflation</p>
          <p className="text-2xl font-bold text-red-400">
            {(data.reduce((sum, d) => sum + d.inflation, 0) / data.length).toFixed(2)}%
          </p>
        </div>
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
          <p className="text-slate-400 text-sm mb-2">Average Oil Price</p>
          <p className="text-2xl font-bold text-purple-400">
            ${(data.reduce((sum, d) => sum + d.oil_price, 0) / data.length).toFixed(2)}
          </p>
        </div>
      </div>
    </div>
  );
}
