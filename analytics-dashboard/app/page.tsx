'use client';

import { useState } from 'react';
import { BarChart3, TrendingUp, Building2, LineChart, Network } from 'lucide-react';
import Overview from '@/components/Overview';
import Economic from '@/components/Economic';
import Banking from '@/components/Banking';
import Forecast from '@/components/Forecast';
import Correlations from '@/components/Correlations';

type TabType = 'overview' | 'economic' | 'banking' | 'forecast' | 'correlations';

interface Tab {
  id: TabType;
  label: string;
  icon: React.ReactNode;
}

const tabs: Tab[] = [
  {
    id: 'overview',
    label: 'Overview',
    icon: <BarChart3 className="w-5 h-5" />,
  },
  {
    id: 'economic',
    label: 'Economic',
    icon: <TrendingUp className="w-5 h-5" />,
  },
  {
    id: 'banking',
    label: 'Banking',
    icon: <Building2 className="w-5 h-5" />,
  },
  {
    id: 'forecast',
    label: 'Forecast',
    icon: <LineChart className="w-5 h-5" />,
  },
  {
    id: 'correlations',
    label: 'Correlations',
    icon: <Network className="w-5 h-5" />,
  },
];

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <Overview />;
      case 'economic':
        return <Economic />;
      case 'banking':
        return <Banking />;
      case 'forecast':
        return <Forecast />;
      case 'correlations':
        return <Correlations />;
      default:
        return <Overview />;
    }
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold gradient-text mb-2">
                Analytics Dashboard
              </h1>
              <p className="text-slate-400">
                Loan Sales Prediction & Economic Indicators for Azerbaijan
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 bg-slate-800/50 px-4 py-2 rounded-lg border border-slate-700">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-slate-300 text-sm">API Connected</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="border-b border-slate-700/50 bg-slate-900/30 backdrop-blur-lg sticky top-[88px] z-40">
        <div className="container mx-auto px-4">
          <nav className="flex gap-2 overflow-x-auto py-4">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 whitespace-nowrap
                  ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg shadow-blue-500/30'
                      : 'bg-slate-800/50 text-slate-400 hover:text-white hover:bg-slate-700/50 border border-slate-700'
                  }
                `}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="animate-fadeIn">
          {renderContent()}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700/50 bg-slate-900/50 backdrop-blur-lg mt-16">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-slate-400 text-sm">
              Analytics Dashboard - Loan Sales Prediction System
            </p>
            <div className="flex items-center gap-4 text-slate-400 text-sm">
              <span>Built with Next.js 16</span>
              <span>•</span>
              <span>Powered by FastAPI</span>
              <span>•</span>
              <span>Recharts</span>
            </div>
          </div>
        </div>
      </footer>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out;
        }
      `}</style>
    </div>
  );
}
