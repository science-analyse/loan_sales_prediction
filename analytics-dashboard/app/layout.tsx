import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Analytics Dashboard - Loan Sales Prediction',
  description: 'Comprehensive analytics dashboard for loan sales and economic indicators in Azerbaijan',
  keywords: ['analytics', 'dashboard', 'loan sales', 'economic indicators', 'Azerbaijan'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
          {children}
        </div>
      </body>
    </html>
  );
}
