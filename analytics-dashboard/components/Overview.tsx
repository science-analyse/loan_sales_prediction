'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Users, Activity, Percent } from 'lucide-react';
import { analyticsApi, formatters, type QuarterlyData } from '@/lib/api';

interface KPICardProps {
  title: string;
  value: string;
  change: number;
  icon: React.ReactNode;
  color: string;
}

const KPICard = ({ title, value, change, icon, color }: KPICardProps) => {
  const isPositive = change >= 0;

  return (
    <div className={`card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700 hover:border-${color}-500/50`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-slate-400 text-sm font-medium mb-2">{title}</p>
          <h3 className="text-3xl font-bold text-white mb-2">{value}</h3>
          <div className="flex items-center gap-2">
            {isPositive ? (
              <TrendingUp className={`w-4 h-4 text-${color}-400`} />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-400" />
            )}
            <span className={`text-sm font-medium ${isPositive ? `text-${color}-400` : 'text-red-400'}`}>
              {isPositive ? '+' : ''}{change.toFixed(2)}%
            </span>
            <span className="text-slate-500 text-sm">vs last quarter</span>
          </div>
        </div>
        <div className={`p-3 bg-${color}-500/10 rounded-lg`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

const LoadingSpinner = () => (
  <div className="flex items-center justify-center h-96">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
  </div>
);

export default function Overview() {
  const [data, setData] = useState<QuarterlyData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const quarterlyData = await analyticsApi.getQuarterlyData();
        setData(quarterlyData);
        setError(null);
      } catch (err) {
        setError('Failed to fetch data. Please ensure the API server is running.');
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

  // Calculate KPIs from latest data
  const latestData = data[data.length - 1];
  const previousData = data[data.length - 2];

  const calculateChange = (current: number, previous: number) => {
    if (!previous) return 0;
    return ((current - previous) / previous) * 100;
  };

  const kpis = [
    {
      title: 'Total Loan Sales',
      value: formatters.currency(latestData?.loan_sales || 0),
      change: calculateChange(latestData?.loan_sales, previousData?.loan_sales),
      icon: <DollarSign className="w-6 h-6 text-blue-400" />,
      color: 'blue',
    },
    {
      title: 'GDP Growth',
      value: formatters.percentage(latestData?.gdp_growth || 0, 1),
      change: calculateChange(latestData?.gdp_growth, previousData?.gdp_growth),
      icon: <Activity className="w-6 h-6 text-green-400" />,
      color: 'green',
    },
    {
      title: 'NPL Ratio',
      value: formatters.percentage(latestData?.npl_ratio || 0, 2),
      change: calculateChange(latestData?.npl_ratio, previousData?.npl_ratio),
      icon: <Percent className="w-6 h-6 text-purple-400" />,
      color: 'purple',
    },
    {
      title: 'Customer Count',
      value: formatters.compact(latestData?.customer_count || 0),
      change: calculateChange(latestData?.customer_count, previousData?.customer_count),
      icon: <Users className="w-6 h-6 text-cyan-400" />,
      color: 'cyan',
    },
  ];

  return (
    <div className="space-y-8">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpis.map((kpi, index) => (
          <KPICard key={index} {...kpi} />
        ))}
      </div>

      {/* Trend Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Loan Sales Trend */}
        <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
          <h3 className="text-xl font-bold text-white mb-6">Loan Sales Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="quarter" stroke="#94a3b8" style={{ fontSize: '12px' }} />
              <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} tickFormatter={(value) => formatters.compact(value)} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                labelStyle={{ color: '#f1f5f9' }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Line type="monotone" dataKey="loan_sales" stroke="#3b82f6" strokeWidth={2} name="Loan Sales" dot={{ fill: '#3b82f6', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* GDP Growth Trend */}
        <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
          <h3 className="text-xl font-bold text-white mb-6">GDP Growth Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="quarter" stroke="#94a3b8" style={{ fontSize: '12px' }} />
              <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} tickFormatter={(value) => `${value}%`} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                labelStyle={{ color: '#f1f5f9' }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Line type="monotone" dataKey="gdp_growth" stroke="#10b981" strokeWidth={2} name="GDP Growth %" dot={{ fill: '#10b981', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* NPL Ratio Trend */}
        <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
          <h3 className="text-xl font-bold text-white mb-6">NPL Ratio Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="quarter" stroke="#94a3b8" style={{ fontSize: '12px' }} />
              <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} tickFormatter={(value) => `${value}%`} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                labelStyle={{ color: '#f1f5f9' }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Line type="monotone" dataKey="npl_ratio" stroke="#8b5cf6" strokeWidth={2} name="NPL Ratio %" dot={{ fill: '#8b5cf6', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Customer Count Trend */}
        <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
          <h3 className="text-xl font-bold text-white mb-6">Customer Growth</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="quarter" stroke="#94a3b8" style={{ fontSize: '12px' }} />
              <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} tickFormatter={(value) => formatters.compact(value)} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                labelStyle={{ color: '#f1f5f9' }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Line type="monotone" dataKey="customer_count" stroke="#06b6d4" strokeWidth={2} name="Customers" dot={{ fill: '#06b6d4', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
