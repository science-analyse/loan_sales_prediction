# 🚀 Render Deployment Instructions

## Current Issue
Render is using Python 3.13, but our dependencies require Python 3.11

## Solution

### In Render Dashboard:

1. **Go to your service settings**
2. **Environment** tab
3. **Add environment variable**:
   - Key: `PYTHON_VERSION`
   - Value: `3.11.10`

4. **Build & Deploy** tab
5. **Set Build Command**:
   ```bash
   ./render-build.sh
   ```

6. **Set Start Command**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

7. **Click "Manual Deploy"** → **"Deploy latest commit"**

## Files Already Created

✅ `runtime.txt` - Specifies Python 3.11.10
✅ `render-build.sh` - Build script
✅ `render.yaml` - Configuration file
✅ `requirements.txt` - Updated with compatible versions
✅ `.gitignore` - Allows models and data to be committed

## What Gets Deployed

✅ **18 REAL trained models** (all .pkl files in notebooks/prediction/models/)
✅ **Real data CSVs** (ml_ready_data.csv, pca_features.csv)
✅ **Model registry** (model_registry.json)
✅ **Full web app** (FastAPI + Jinja2 frontend)

## After Successful Deploy

Your app will be live at:
```
https://loan-sales-prediction.onrender.com
```

## To Verify Models Are Real

Once deployed, test the API:
```bash
curl https://loan-sales-prediction.onrender.com/api/health
```

Should return:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "total_models": 18
}
```

---

**NOTE**: All 18 models are REAL, trained models - no mock/fake data!
