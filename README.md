<div align="center">

# 📄✨ PDF to Obsidian

**Transform your PDFs into beautiful Obsidian notes with AI-powered OCR**

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Powered by Ollama](https://img.shields.io/badge/Powered%20by-Ollama-000000?style=for-the-badge)](https://ollama.com)
[![GLM-OCR](https://img.shields.io/badge/GLM--OCR-Rank%20%231-FF6B6B?style=for-the-badge)](https://github.com/zai-org/GLM-OCR)

*Stop retyping. Start researching.*

</div>

---

## 🎯 What is This?

A **localhost web app** that converts PDFs (papers, articles, scanned docs) into **clean Obsidian markdown** using state-of-the-art AI OCR.

- 🚀 **Best-in-class OCR** - GLM-OCR ranks #1 on OmniDocBench
- 🏠 **100% Local** - No cloud, no API keys, runs on your machine
- ⚡ **Live Preview** - See markdown as it processes, edit before saving
- 🎨 **Dark Theme** - Beautiful interface with real-time progress

## 🚀 Quick Start

### Prerequisites

1. **[Ollama](https://ollama.com)** - Download and install
2. **[Conda](https://docs.conda.io/en/latest/miniconda.html)** - Recommended for Windows

### Setup

```bash
# 1. Pull the GLM-OCR model
ollama pull glm-ocr

# 2. Create conda environment
conda env create -f environment.yml
```

### Run

```bash
# Terminal 1: Start Ollama (keep running)
ollama serve

# Terminal 2: Start the app
conda activate pdf2md
python -m uvicorn backend.app.main:app --reload

# Or use the launcher (Windows)
start_app.bat
```

**Open browser:** http://localhost:8000

## 🎬 How It Works

1. **Drop your PDF** into the web interface
2. **Watch live progress** as GLM-OCR processes each page
3. **Review the markdown** in the preview tab
4. **Edit if needed** to fix any OCR errors
5. **Save to outputs/** folder
6. **Copy to your Obsidian vault** - done!

## 📁 Project Structure

```
pdf_to_md_obsidian/
├── backend/app/           # FastAPI server
│   ├── main.py           # Routes + WebSocket
│   ├── processor.py      # GLM-OCR integration
│   ├── config.py         # App settings
│   └── config.yaml       # Ollama configuration
├── frontend/             # Vanilla JS UI
│   ├── index.html       # Dark theme interface
│   ├── app.js           # WebSocket client
│   └── styles.css       # Styling
├── uploads/             # Temporary PDFs
├── outputs/             # Your markdown files
├── environment.yml      # Conda environment
└── start_app.bat        # Quick launcher (Windows)
```

## 🔧 Configuration

### App Settings (`backend/app/config.py`)

```python
max_file_size = 50 * 1024 * 1024  # 50MB limit
upload_dir = "uploads"
output_dir = "outputs"
```

### GLM-OCR Settings (`backend/app/config.yaml`)

```yaml
pipeline:
  maas:
    enabled: false  # Use local Ollama
  ocr_api:
    api_host: localhost
    api_port: 11434
    api_mode: openai  # OpenAI-compatible endpoint
    model: glm-ocr
  layout:
    device: cpu  # or cuda if you have GPU
```

## 🔧 Troubleshooting

<details>
<summary><b>🔴 "Ollama not running"</b></summary>

```bash
# Start Ollama
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags

# Check model is installed
ollama list
```
</details>

<details>
<summary><b>🟡 "Processing failed"</b></summary>

Restart the app - the pipeline needs to start fresh:
```bash
# Press Ctrl+C, then restart
python -m uvicorn backend.app.main:app --reload
```
</details>

<details>
<summary><b>🔵 Windows PyTorch DLL errors</b></summary>

**Solution:** Use Conda (not pip)
```bash
conda env create -f environment.yml
```
Conda handles PyTorch dependencies correctly on Windows.
</details>

<details>
<summary><b>🟢 Slow processing</b></summary>

- **First run**: Model loading is slow (~30 seconds)
- **Subsequent runs**: Much faster
- **GPU**: Change `device: cuda` in `config.yaml`
</details>

## 💡 Tips

- Start with small PDFs (1-5 pages) to test
- Always review before saving - OCR isn't perfect
- Keep Ollama running for best performance
- First conversion is slower (loads models)

## 🛠️ Alternative Setup (pip)

Without Conda? Use pip (requires Python 3.10):

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload
```

⚠️ May have PyTorch DLL issues on Windows - Conda recommended.

## 📊 Tech Stack

- **Backend:** Python 3.10, FastAPI, WebSockets
- **OCR:** GLM-OCR via Ollama
- **Frontend:** Vanilla HTML/CSS/JS
- **Layout Detection:** PaddleOCR PP-DocLayout V3

## 🙏 Acknowledgments

- [GLM-OCR](https://github.com/zai-org/GLM-OCR) - State-of-the-art OCR
- [Ollama](https://ollama.com/) - Local LLM deployment
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Obsidian](https://obsidian.md/) - Note-taking app

---

<div align="center">

**Made with ❤️ for the Obsidian community**

</div>
