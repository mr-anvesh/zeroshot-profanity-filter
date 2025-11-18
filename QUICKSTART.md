# Quick Start Guide

## 🎯 Your Python Version Issue

You're using Python 3.14, which is very new and doesn't have pre-built wheels for many packages (like pyarrow, which Streamlit needs). 

## ✅ Solution: Deploy Directly to Streamlit Cloud

The good news: **You don't need to install Streamlit locally!** You can deploy directly to Streamlit Cloud, which will use Python 3.11 (specified in `runtime.txt`).

## 🚀 Deploy to Streamlit Cloud (Recommended)

### Step 1: Push to GitHub

```bash
cd /Users/anveshmishra/Developer/mDeBERTa-v3-base-mnli-xnli

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Add AI profanity filter with Streamlit frontend"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

**Important for large model files (>100MB):**
```bash
# Install Git LFS (one time setup)
brew install git-lfs  # macOS
git lfs install

# Track large files
git lfs track "*.safetensors"
git lfs track "*.onnx"
git add .gitattributes
git commit -m "Add Git LFS tracking"
git push
```

### Step 2: Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in:
   - **Repository:** Your GitHub repository
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **"Deploy!"**

That's it! Streamlit Cloud will:
- Use Python 3.11 (from `runtime.txt`)
- Install all dependencies
- Load your model
- Give you a public URL

## 💻 Test Locally (Optional)

If you want to test locally, you have two options:

### Option 1: Use Python 3.11 (Recommended)

```bash
# Install Python 3.11 using pyenv
brew install pyenv
pyenv install 3.11
pyenv local 3.11

# Create new virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Option 2: Install cmake for Python 3.14

```bash
# Install cmake
brew install cmake

# Try installing again
source .venv/bin/activate
pip install streamlit

# Run the app
streamlit run app.py
```

## 📁 Files Created

- ✅ `app.py` - Streamlit web interface
- ✅ `profanity_filter.py` - Backend filter
- ✅ `requirements.txt` - Dependencies
- ✅ `runtime.txt` - Python version for Streamlit Cloud
- ✅ `.python-version` - Python version specification
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `packages.txt` - System dependencies
- ✅ `.gitattributes` - Git LFS configuration
- ✅ `DEPLOYMENT.md` - Detailed deployment guide
- ✅ `example_usage.py` - Example usage

## 🎨 Features

Your Streamlit app includes:
- 🛡️ Real-time profanity detection
- 📊 Statistics dashboard
- 🎚️ Adjustable sensitivity slider
- 🔄 Multiple filtering modes
- 📝 Example texts
- 📈 Confidence scores
- 🌐 Works with 100+ languages

## 🆘 Troubleshooting

### Git LFS Issues
If your model files are >100MB and git push fails:
```bash
git lfs migrate import --include="*.safetensors,*.onnx"
git push
```

### Streamlit Cloud Memory Issues
If deployment fails due to memory limits, the app uses `@st.cache_resource` to optimize memory usage. You can also consider:
- Using the ONNX quantized model (smaller)
- Loading model from Hugging Face Hub instead

### Model Loading from Hugging Face (Alternative)
If you don't want to commit the model files:

Edit `profanity_filter.py`:
```python
# Change line 29 from:
model=model_path,
# To:
model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
```

## 📚 Next Steps

1. **Deploy to Streamlit Cloud** (easiest, no local setup needed)
2. Share your public URL with others
3. Monitor usage in Streamlit Cloud dashboard
4. Customize the UI in `app.py` if desired

## 🔗 Useful Links

- [Streamlit Cloud](https://share.streamlit.io)
- [Git LFS](https://git-lfs.github.com/)
- [Model on Hugging Face](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli)
- [Streamlit Documentation](https://docs.streamlit.io)

---

**Pro Tip:** Streamlit Cloud is perfect for this project because it handles all the Python version and dependency issues automatically!
