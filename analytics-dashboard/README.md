# Analytics Dashboard - Loan Sales Prediction

A comprehensive Next.js 16 analytics dashboard application for visualizing loan sales predictions and economic indicators in Azerbaijan.

## Features

### Tab Navigation
- **Overview**: KPI cards and trend charts for key metrics
- **Economic**: Economic indicators with area charts (GDP, inflation, unemployment, oil prices, exchange rates)
- **Banking**: Banking metrics with bar and line charts (loan sales, NPL ratio, ROA, customer count)
- **Forecast**: Loan sales forecasting with confidence intervals
- **Correlations**: Interactive correlation matrix heatmap

### Key Visualizations
- **KPI Cards**: Real-time metrics with trend indicators
- **Line Charts**: Historical trends over time
- **Area Charts**: Forecasts with confidence intervals
- **Bar Charts**: Comparative metrics analysis
- **Composed Charts**: Multi-metric visualizations
- **Heatmap**: Correlation matrix with interactive hover details

### Technology Stack
- **Next.js 16**: Latest React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS v4**: Modern utility-first styling
- **Recharts**: Data visualization library
- **Axios**: HTTP client for API communication
- **Lucide React**: Icon library

## Project Structure

```
analytics-dashboard/
├── app/
│   ├── globals.css         # Global styles with Tailwind
│   ├── layout.tsx          # Root layout component
│   └── page.tsx            # Main dashboard with tab navigation
├── components/
│   ├── Overview.tsx        # Overview tab with KPIs
│   ├── Economic.tsx        # Economic indicators
│   ├── Banking.tsx         # Banking metrics
│   ├── Forecast.tsx        # Forecasting section
│   └── Correlations.tsx    # Correlation matrix
├── lib/
│   └── api.ts              # API service layer
├── package.json            # Dependencies
├── tsconfig.json           # TypeScript configuration
├── tailwind.config.ts      # Tailwind configuration
└── next.config.ts          # Next.js configuration
```

## API Endpoints

The dashboard connects to a FastAPI backend at `http://localhost:8000` with the following endpoints:

- `GET /api/analytics/overview` - Overview data with KPIs
- `GET /api/analytics/economic-indicators` - Economic indicators
- `GET /api/analytics/banking-metrics` - Banking metrics
- `GET /api/analytics/quarterly` - Quarterly aggregated data
- `GET /api/predictions/simple-forecast` - Forecast predictions
- `GET /api/analytics/correlations` - Correlation matrix

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn
- FastAPI backend running on port 8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The dashboard will be available at `http://localhost:3001`

### Build for Production

```bash
npm run build
npm start
```

## Data Formatting

The application uses Azerbaijani locale (az-AZ) for number formatting:

- **Currency**: AZN (Azerbaijani Manat)
- **Numbers**: Formatted with proper thousands separators
- **Percentages**: Displayed with 1-2 decimal places
- **Compact notation**: Large numbers shown as 1.2M, 3.4K, etc.

## Styling

### Color Scheme
- **Primary**: Blue (#3b82f6)
- **Secondary**: Purple (#8b5cf6)
- **Accent**: Green (#10b981)
- **Background**: Slate gradients
- **Cards**: Translucent with backdrop blur

### Theme
- Dark theme with gradient backgrounds
- Card-based layout with hover effects
- Smooth transitions and animations
- Responsive design for all screen sizes
- Custom scrollbar styling

## Components

### Overview.tsx
- 4 KPI cards (Loan Sales, GDP Growth, NPL Ratio, Customer Count)
- 4 line charts showing trends over time
- Automatic calculation of quarter-over-quarter changes

### Economic.tsx
- GDP Growth & Inflation composed chart
- Unemployment rate area chart
- Oil price trends
- Exchange rate visualization
- Summary statistics cards

### Banking.tsx
- Loan sales bar chart
- NPL ratio and ROA area charts
- Customer count vs deposits comparison
- Loan sales vs deposits side-by-side
- Key metrics summary cards

### Forecast.tsx
- Historical vs predicted values
- Confidence intervals (upper/lower bounds)
- Forecast overview cards
- Detailed forecast table
- Model information and insights

### Correlations.tsx
- Interactive correlation heatmap
- Color-coded correlation strength
- Hover details with correlation coefficients
- Key correlations summary
- Information guide

## Error Handling

- Loading spinners during data fetching
- Error messages for API failures
- Graceful degradation when data is unavailable
- Retry logic in API service

## Performance Optimizations

- Client-side rendering with React hooks
- Efficient data fetching with axios
- Memoized calculations where appropriate
- Lazy loading of chart components
- Optimized re-renders with proper state management

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

### Adding New Tabs

1. Create a new component in `components/`
2. Import and add to the tabs array in `app/page.tsx`
3. Add the component to the switch statement in `renderContent()`

### Adding New API Endpoints

1. Add type definitions in `lib/api.ts`
2. Create a new function in the `analyticsApi` object
3. Use the endpoint in your component with `useEffect`

### Customizing Styles

- Global styles: `app/globals.css`
- Tailwind config: `tailwind.config.ts`
- Component-specific styles: Use Tailwind classes

## License

MIT License - Feel free to use this project for your own purposes.

## Support

For issues or questions, please contact the development team or create an issue in the repository.
