# Deploying to Streamlit Cloud

This guide will help you deploy the Profanity Filter app to Streamlit Cloud for free.

## Prerequisites

1. A GitHub account
2. Git installed on your local machine
3. This project pushed to a GitHub repository

## Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure your repository includes these files:
- ✅ `app.py` - Main Streamlit application
- ✅ `profanity_filter.py` - Backend profanity filter
- ✅ `requirements.txt` - Python dependencies
- ✅ `packages.txt` - System dependencies (optional)
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ All model files (config.json, model.safetensors, tokenizer files, etc.)

### 2. Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Profanity filter with Streamlit"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

**Important:** If your model files are large (>100MB), you'll need to use Git LFS:

```bash
# Install Git LFS
git lfs install

# Track large files (already configured in .gitattributes)
git lfs track "*.safetensors"
git lfs track "*.onnx"
git lfs track "*.model"

# Add and commit
git add .gitattributes
git commit -m "Add Git LFS tracking"
git push
```

### 3. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Fill in the deployment details:
   - **Repository:** Select your GitHub repository
   - **Branch:** `main` (or your default branch)
   - **Main file path:** `app.py`
5. Click "Deploy!"

### 4. Wait for Deployment

- First deployment may take 5-10 minutes
- Streamlit Cloud will:
  - Clone your repository
  - Install dependencies from `requirements.txt`
  - Load your model files
  - Start the app

### 5. Access Your App

Once deployed, you'll get a URL like:
```
https://YOUR_USERNAME-YOUR_REPO_NAME-RANDOM_ID.streamlit.app
```

## Configuration Options

### Memory and Resources

Streamlit Cloud free tier provides:
- 1 GB RAM
- 1 CPU core
- 50 GB bandwidth per month

If you encounter memory issues, consider:
1. Using quantized models (ONNX version)
2. Reducing model precision
3. Implementing lazy loading

### Custom Domain

To use a custom domain:
1. Go to your app settings on Streamlit Cloud
2. Navigate to "General" > "Custom subdomain"
3. Enter your desired subdomain

### Environment Variables

If you need environment variables:
1. Go to app settings
2. Click "Secrets"
3. Add your secrets in TOML format

## Troubleshooting

### Model Loading Issues

If the model fails to load:
1. Check that all model files are committed
2. Verify Git LFS is working for large files
3. Check Streamlit Cloud logs for errors

### Memory Errors

If you get out-of-memory errors:
```python
# In app.py, modify the model loading to use less memory
pf = ProfanityFilter(model_path="./", threshold=threshold)
```

Consider using the quantized ONNX model instead:
```python
# Use ONNX runtime for better performance
from optimum.onnxruntime import ORTModelForSequenceClassification
```

### Slow First Load

The first time someone visits your app:
- Model loads into memory (30-60 seconds)
- Subsequent visits are faster (model is cached)
- Add a loading spinner for better UX

### Repository Size Limits

GitHub has a 100 MB file size limit. For large models:
1. Use Git LFS (configured in `.gitattributes`)
2. Or host model files externally (Hugging Face Hub)

To load from Hugging Face Hub instead:
```python
# In profanity_filter.py, change model_path to:
model_path = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
```

## Monitoring

### View Logs

1. Go to your app on Streamlit Cloud
2. Click "Manage app"
3. View logs in the console

### Analytics

Streamlit Cloud provides basic analytics:
- Number of visitors
- App status
- Resource usage

## Updating Your App

To update the deployed app:

```bash
# Make your changes
git add .
git commit -m "Update: description of changes"
git push
```

Streamlit Cloud will automatically detect changes and redeploy.

## Cost and Limits

### Free Tier Includes:
- ✅ Unlimited public apps
- ✅ 1 private app
- ✅ Community support
- ✅ GitHub authentication

### Limitations:
- 1 GB RAM per app
- Apps sleep after inactivity (wake on visit)
- 50 GB bandwidth/month

### Upgrading

If you need more resources, consider:
- Streamlit Cloud Teams/Enterprise
- Self-hosting on AWS/GCP/Azure
- Using Docker containers

## Alternative Deployment Options

If Streamlit Cloud doesn't work for you:

### 1. Hugging Face Spaces
```bash
# Push to Hugging Face Spaces
# Create a space at huggingface.co/spaces
# Add app.py and requirements.txt
```

### 2. Docker
```dockerfile
# Create Dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py"]
```

### 3. Heroku
```bash
# Create Procfile
web: streamlit run app.py --server.port=$PORT
```

## Support

- [Streamlit Documentation](https://docs.streamlit.io)
- [Streamlit Community Forum](https://discuss.streamlit.io)
- [GitHub Issues](https://github.com/streamlit/streamlit/issues)

## Security Notes

1. Don't commit secrets or API keys
2. Use Streamlit Secrets for sensitive data
3. Enable XSRF protection (already configured)
4. Keep dependencies updated

## Performance Tips

1. Use `@st.cache_resource` for model loading (already implemented)
2. Minimize unnecessary reruns
3. Use session state for persistence
4. Implement pagination for large datasets

---

Good luck with your deployment! 🚀
