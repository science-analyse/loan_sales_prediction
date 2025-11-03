# Quick Start Guide

## Prerequisites

1. **Backend API**: Ensure your FastAPI backend is running on `http://localhost:8000`
2. **Node.js**: Version 18 or higher
3. **npm**: Comes with Node.js

## Installation & Running

### Step 1: Install Dependencies
```bash
cd /Users/ismatsamadov/loan_sales_prediction/analytics-dashboard
npm install
```

### Step 2: Start Development Server
```bash
npm run dev
```

The dashboard will be available at: **http://localhost:3001**

### Step 3: Verify Connection
- Check the green "API Connected" indicator in the header
- If you see errors, ensure the FastAPI backend is running on port 8000

## Available Scripts

```bash
npm run dev      # Start development server on port 3001
npm run build    # Build for production
npm start        # Start production server
npm run lint     # Run ESLint
```

## Testing the Dashboard

### 1. Overview Tab
- Should display 4 KPI cards
- Should show 4 trend charts
- Verify quarter-over-quarter changes

### 2. Economic Tab
- GDP Growth & Inflation combined chart
- Unemployment, Oil Price, and Exchange Rate charts
- Summary statistics at the bottom

### 3. Banking Tab
- Loan sales bar chart
- NPL Ratio and ROA area charts
- Customer vs Deposits comparison
- Key metrics summary

### 4. Forecast Tab
- Historical and predicted values
- Confidence intervals (shaded area)
- Detailed forecast table
- Model information

### 5. Correlations Tab
- Interactive heatmap
- Hover over cells for details
- Key correlations summary

## Troubleshooting

### API Connection Issues
**Problem**: Red error message "Failed to fetch data"
**Solution**:
- Verify FastAPI backend is running: `curl http://localhost:8000/api/analytics/overview`
- Check CORS settings in FastAPI backend
- Ensure all required endpoints are available

### TypeScript Errors
**Problem**: Type errors in development
**Solution**:
```bash
npx tsc --noEmit
```

### Build Errors
**Problem**: Build fails
**Solution**:
```bash
rm -rf .next
rm -rf node_modules
npm install
npm run build
```

### Port Already in Use
**Problem**: Port 3001 is already in use
**Solution**:
```bash
# Change port in package.json or kill existing process
lsof -ti:3001 | xargs kill
```

## Backend API Requirements

Ensure your FastAPI backend has these endpoints:

```python
GET /api/analytics/overview
GET /api/analytics/economic-indicators
GET /api/analytics/banking-metrics
GET /api/analytics/quarterly
GET /api/predictions/simple-forecast
GET /api/analytics/correlations
```

### Sample Response Formats

**Overview/Quarterly:**
```json
[
  {
    "quarter": "2023-Q1",
    "loan_sales": 1500000,
    "gdp_growth": 3.5,
    "inflation": 8.2,
    "npl_ratio": 5.4,
    "roa": 2.1,
    "customer_count": 150000
  }
]
```

**Economic Indicators:**
```json
[
  {
    "quarter": "2023-Q1",
    "gdp_growth": 3.5,
    "inflation": 8.2,
    "unemployment": 6.5,
    "oil_price": 85.50,
    "exchange_rate": 1.70
  }
]
```

**Banking Metrics:**
```json
[
  {
    "quarter": "2023-Q1",
    "loan_sales": 1500000,
    "npl_ratio": 5.4,
    "roa": 2.1,
    "customer_count": 150000,
    "deposits": 2500000
  }
]
```

**Forecast:**
```json
{
  "historical": [
    {
      "quarter": "2023-Q1",
      "actual": 1500000,
      "predicted": null
    }
  ],
  "forecast": [
    {
      "quarter": "2024-Q1",
      "predicted": 1650000,
      "lower_bound": 1550000,
      "upper_bound": 1750000
    }
  ]
}
```

**Correlations:**
```json
{
  "variables": ["loan_sales", "gdp_growth", "inflation", "npl_ratio"],
  "matrix": [
    [1.0, 0.85, -0.42, -0.67],
    [0.85, 1.0, -0.38, -0.55],
    [-0.42, -0.38, 1.0, 0.45],
    [-0.67, -0.55, 0.45, 1.0]
  ]
}
```

## Production Deployment

### Build for Production
```bash
npm run build
```

### Start Production Server
```bash
npm start
```

### Environment Variables (Optional)
Create a `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Then update `lib/api.ts`:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

## Features Overview

### Responsive Design
- Mobile-friendly layout
- Tablet optimized
- Desktop full-width

### Dark Theme
- Modern dark color scheme
- Gradient backgrounds
- Translucent cards with backdrop blur

### Interactive Charts
- Hover tooltips
- Legend toggle
- Responsive sizing
- Smooth animations

### Data Formatting
- Azerbaijani locale (az-AZ)
- Currency: AZN
- Compact notation for large numbers
- Percentage formatting

## Next Steps

1. Customize colors in `app/globals.css` and `tailwind.config.ts`
2. Add new tabs by creating components and updating `app/page.tsx`
3. Extend API endpoints in `lib/api.ts`
4. Add authentication if needed
5. Deploy to Vercel, Netlify, or your preferred platform

## Support

For issues or questions:
- Check the main README.md
- Review the code comments
- Verify API endpoint responses
- Check browser console for errors

---

**Enjoy your analytics dashboard!**
