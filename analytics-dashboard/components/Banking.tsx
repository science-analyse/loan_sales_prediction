'use client';

import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart, Line, Area } from 'recharts';
import { analyticsApi, formatters, type BankingMetric } from '@/lib/api';

const LoadingSpinner = () => (
  <div className="flex items-center justify-center h-96">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
  </div>
);

export default function Banking() {
  const [data, setData] = useState<BankingMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const bankingData = await analyticsApi.getBankingMetrics();
        setData(bankingData);
        setError(null);
      } catch (err) {
        setError('Failed to fetch banking metrics. Please ensure the API server is running.');
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
      {/* Loan Sales Bar Chart */}
      <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
        <h3 className="text-xl font-bold text-white mb-6">Quarterly Loan Sales</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data}>
            <defs>
              <linearGradient id="loanSalesBar" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={1}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.6}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="quarter" stroke="#94a3b8" style={{ fontSize: '12px' }} />
            <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} tickFormatter={(value) => formatters.compact(value)} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
              labelStyle={{ color: '#f1f5f9' }}
              formatter={(value: number) => formatters.currency(value)}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            <Bar dataKey="loan_sales" fill="url(#loanSalesBar)" name="Loan Sales" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* NPL Ratio and ROA */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
          <h3 className="text-xl font-bold text-white mb-6">Non-Performing Loan Ratio</h3>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={data}>
              <defs>
                <linearGradient id="nplGradient" x1="0" y1="0" x2="0" y2="1">
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
                formatter={(value: number) => `${value.toFixed(2)}%`}
              />
              <Area type="monotone" dataKey="npl_ratio" stroke="#ef4444" fillOpacity={1} fill="url(#nplGradient)" name="NPL Ratio %" />
              <Line type="monotone" dataKey="npl_ratio" stroke="#ef4444" strokeWidth={2} dot={{ fill: '#ef4444', r: 4 }} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
          <h3 className="text-xl font-bold text-white mb-6">Return on Assets (ROA)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={data}>
              <defs>
                <linearGradient id="roaGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="quarter" stroke="#94a3b8" style={{ fontSize: '12px' }} />
              <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} tickFormatter={(value) => `${value}%`} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                labelStyle={{ color: '#f1f5f9' }}
                formatter={(value: number) => `${value.toFixed(2)}%`}
              />
              <Area type="monotone" dataKey="roa" stroke="#10b981" fillOpacity={1} fill="url(#roaGradient)" name="ROA %" />
              <Line type="monotone" dataKey="roa" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981', r: 4 }} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Customer Count and Deposits */}
      <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
        <h3 className="text-xl font-bold text-white mb-6">Customer Count vs Total Deposits</h3>
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={data}>
            <defs>
              <linearGradient id="customerBar" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={1}/>
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.6}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="quarter" stroke="#94a3b8" style={{ fontSize: '12px' }} />
            <YAxis
              yAxisId="left"
              stroke="#94a3b8"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => formatters.compact(value)}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="#94a3b8"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => formatters.compact(value)}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
              labelStyle={{ color: '#f1f5f9' }}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            <Bar yAxisId="left" dataKey="customer_count" fill="url(#customerBar)" name="Customer Count" radius={[8, 8, 0, 0]} />
            <Line yAxisId="right" type="monotone" dataKey="deposits" stroke="#8b5cf6" strokeWidth={3} name="Total Deposits" dot={{ fill: '#8b5cf6', r: 5 }} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Performance Indicators */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
          <h3 className="text-xl font-bold text-white mb-6">Loan Sales vs Deposits</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <defs>
                <linearGradient id="loanBar" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={1}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.6}/>
                </linearGradient>
                <linearGradient id="depositBar" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={1}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.6}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="quarter" stroke="#94a3b8" style={{ fontSize: '12px' }} />
              <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} tickFormatter={(value) => formatters.compact(value)} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                labelStyle={{ color: '#f1f5f9' }}
                formatter={(value: number) => formatters.currency(value)}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar dataKey="loan_sales" fill="url(#loanBar)" name="Loan Sales" radius={[8, 8, 0, 0]} />
              <Bar dataKey="deposits" fill="url(#depositBar)" name="Deposits" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Key Metrics Summary */}
        <div className="space-y-4">
          <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 backdrop-blur-lg rounded-xl p-6 border border-blue-500/30">
            <p className="text-slate-300 text-sm mb-2">Total Loan Sales</p>
            <p className="text-3xl font-bold text-blue-400">
              {formatters.currency(data.reduce((sum, d) => sum + d.loan_sales, 0))}
            </p>
            <p className="text-slate-400 text-xs mt-2">Cumulative across all quarters</p>
          </div>

          <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 backdrop-blur-lg rounded-xl p-6 border border-purple-500/30">
            <p className="text-slate-300 text-sm mb-2">Average NPL Ratio</p>
            <p className="text-3xl font-bold text-purple-400">
              {(data.reduce((sum, d) => sum + d.npl_ratio, 0) / data.length).toFixed(2)}%
            </p>
            <p className="text-slate-400 text-xs mt-2">Average non-performing loans</p>
          </div>

          <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 backdrop-blur-lg rounded-xl p-6 border border-green-500/30">
            <p className="text-slate-300 text-sm mb-2">Average ROA</p>
            <p className="text-3xl font-bold text-green-400">
              {(data.reduce((sum, d) => sum + d.roa, 0) / data.length).toFixed(2)}%
            </p>
            <p className="text-slate-400 text-xs mt-2">Average return on assets</p>
          </div>
        </div>
      </div>
    </div>
  );
}
