'use client';

import { useEffect, useState } from 'react';
import { analyticsApi, type CorrelationData } from '@/lib/api';
import { Info } from 'lucide-react';

const LoadingSpinner = () => (
  <div className="flex items-center justify-center h-96">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
  </div>
);

// Color scale for correlation values
const getCorrelationColor = (value: number): string => {
  const absValue = Math.abs(value);

  if (value > 0) {
    // Positive correlation: blue shades
    if (absValue >= 0.8) return 'bg-blue-600';
    if (absValue >= 0.6) return 'bg-blue-500';
    if (absValue >= 0.4) return 'bg-blue-400';
    if (absValue >= 0.2) return 'bg-blue-300';
    return 'bg-blue-200';
  } else if (value < 0) {
    // Negative correlation: red shades
    if (absValue >= 0.8) return 'bg-red-600';
    if (absValue >= 0.6) return 'bg-red-500';
    if (absValue >= 0.4) return 'bg-red-400';
    if (absValue >= 0.2) return 'bg-red-300';
    return 'bg-red-200';
  }

  return 'bg-slate-700';
};

const getTextColor = (value: number): string => {
  const absValue = Math.abs(value);

  if (absValue >= 0.4) {
    return 'text-white';
  }
  return 'text-slate-300';
};

const getCorrelationStrength = (value: number): string => {
  const absValue = Math.abs(value);

  if (absValue >= 0.8) return 'Very Strong';
  if (absValue >= 0.6) return 'Strong';
  if (absValue >= 0.4) return 'Moderate';
  if (absValue >= 0.2) return 'Weak';
  return 'Very Weak';
};

export default function Correlations() {
  const [data, setData] = useState<CorrelationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredCell, setHoveredCell] = useState<{ row: number; col: number } | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const correlationData = await analyticsApi.getCorrelations();
        setData(correlationData);
        setError(null);
      } catch (err) {
        setError('Failed to fetch correlation data. Please ensure the API server is running.');
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

  if (!data || !data.variables || !data.matrix) {
    return (
      <div className="bg-yellow-500/10 border border-yellow-500/50 rounded-xl p-6 text-center">
        <p className="text-yellow-400">No correlation data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Information Card */}
      <div className="bg-blue-500/10 border border-blue-500/50 rounded-xl p-6">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
          <div className="space-y-2">
            <h4 className="text-lg font-semibold text-blue-300">Correlation Matrix</h4>
            <p className="text-slate-300 text-sm">
              This heatmap shows the correlation coefficients between different variables.
              Values range from -1 (perfect negative correlation) to +1 (perfect positive correlation).
            </p>
            <div className="flex flex-wrap gap-4 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-blue-600 rounded"></div>
                <span className="text-slate-300 text-sm">Strong Positive</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-blue-300 rounded"></div>
                <span className="text-slate-300 text-sm">Weak Positive</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-slate-700 rounded"></div>
                <span className="text-slate-300 text-sm">No Correlation</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-300 rounded"></div>
                <span className="text-slate-300 text-sm">Weak Negative</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-600 rounded"></div>
                <span className="text-slate-300 text-sm">Strong Negative</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Correlation Heatmap */}
      <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
        <h3 className="text-xl font-bold text-white mb-6">Correlation Heatmap</h3>

        <div className="overflow-x-auto">
          <div className="inline-block min-w-full">
            <div className="grid gap-1" style={{
              gridTemplateColumns: `200px repeat(${data.variables.length}, minmax(100px, 1fr))`
            }}>
              {/* Header row */}
              <div className="bg-slate-700/50 rounded p-3"></div>
              {data.variables.map((variable, index) => (
                <div
                  key={index}
                  className="bg-slate-700/50 rounded p-3 text-center"
                >
                  <span className="text-slate-300 text-sm font-semibold transform -rotate-45 inline-block whitespace-nowrap">
                    {variable}
                  </span>
                </div>
              ))}

              {/* Matrix rows */}
              {data.variables.map((rowVariable, rowIndex) => (
                <div key={`row-${rowIndex}`} className="contents">
                  {/* Row label */}
                  <div className="bg-slate-700/50 rounded p-3 flex items-center">
                    <span className="text-slate-300 text-sm font-semibold">
                      {rowVariable}
                    </span>
                  </div>

                  {/* Correlation cells */}
                  {data.matrix[rowIndex].map((value, colIndex) => {
                    const isHovered = hoveredCell?.row === rowIndex && hoveredCell?.col === colIndex;
                    const isDiagonal = rowIndex === colIndex;

                    return (
                      <div
                        key={`cell-${rowIndex}-${colIndex}`}
                        className={`
                          ${getCorrelationColor(value)}
                          rounded p-3 text-center transition-all duration-200 cursor-pointer
                          ${isHovered ? 'ring-2 ring-white transform scale-105 z-10' : ''}
                          ${isDiagonal ? 'ring-1 ring-slate-600' : ''}
                        `}
                        onMouseEnter={() => setHoveredCell({ row: rowIndex, col: colIndex })}
                        onMouseLeave={() => setHoveredCell(null)}
                        title={`${rowVariable} vs ${data.variables[colIndex]}: ${value.toFixed(3)}`}
                      >
                        <span className={`text-sm font-semibold ${getTextColor(value)}`}>
                          {value.toFixed(2)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Hover details */}
        {hoveredCell && (
          <div className="mt-6 bg-slate-700/50 rounded-xl p-4 border border-slate-600">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-slate-400 text-sm">Variables</p>
                <p className="text-white font-semibold">
                  {data.variables[hoveredCell.row]} × {data.variables[hoveredCell.col]}
                </p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Correlation Coefficient</p>
                <p className="text-white font-semibold text-lg">
                  {data.matrix[hoveredCell.row][hoveredCell.col].toFixed(4)}
                </p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Strength</p>
                <p className="text-white font-semibold">
                  {getCorrelationStrength(data.matrix[hoveredCell.row][hoveredCell.col])}
                </p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Direction</p>
                <p className="text-white font-semibold">
                  {data.matrix[hoveredCell.row][hoveredCell.col] > 0
                    ? 'Positive'
                    : data.matrix[hoveredCell.row][hoveredCell.col] < 0
                    ? 'Negative'
                    : 'None'}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Key Insights */}
      <div className="card-hover bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700">
        <h3 className="text-xl font-bold text-white mb-6">Key Correlations</h3>
        <div className="space-y-4">
          {data.variables.map((variable, rowIndex) => {
            // Find strongest correlations (excluding self-correlation)
            const correlations = data.matrix[rowIndex]
              .map((value, colIndex) => ({
                variable: data.variables[colIndex],
                value,
                colIndex
              }))
              .filter((item, index) => index !== rowIndex) // Exclude self
              .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
              .slice(0, 2); // Top 2 correlations

            if (correlations.length === 0) return null;

            return (
              <div key={rowIndex} className="bg-slate-700/30 rounded-lg p-4">
                <h4 className="text-white font-semibold mb-2">{variable}</h4>
                <div className="space-y-2">
                  {correlations.map((corr, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-slate-300 text-sm">
                        {corr.value > 0 ? 'Positively' : 'Negatively'} correlated with{' '}
                        <span className="text-white font-medium">{corr.variable}</span>
                      </span>
                      <span
                        className={`text-sm font-semibold px-3 py-1 rounded ${
                          Math.abs(corr.value) >= 0.6
                            ? corr.value > 0 ? 'bg-blue-500/30 text-blue-300' : 'bg-red-500/30 text-red-300'
                            : 'bg-slate-600/30 text-slate-300'
                        }`}
                      >
                        {corr.value.toFixed(3)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
