# PDF to Obsidian Converter

Convert PDFs (articles, scanned documents) to Obsidian-friendly markdown using state-of-the-art GLM-OCR.

## Features

- 🚀 **State-of-the-art OCR** - Uses GLM-OCR (ranks #1 on OmniDocBench)
- 📝 **Live preview** - See results with rendered markdown preview
- ✏️ **Edit before saving** - Fix OCR errors before committing to your vault
- 🖼️ **Image extraction** - Saves images separately with Obsidian `![[image.png]]` links
- 🏠 **100% Local** - Runs on localhost via Ollama, no cloud dependencies

## Quick Start

### 1. Prerequisites

- **Conda** (recommended) - [Install Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- **Ollama** - [Install Ollama](https://ollama.com/)

### 2. Setup (One-time)

```bash
# Pull the GLM-OCR model
ollama pull glm-ocr

# Create conda environment
setup_conda.bat    # Windows CMD
# OR
bash setup_conda.sh    # Git Bash/Linux
```

### 3. Run

```bash
# Start Ollama (in a separate terminal - keep it running)
ollama serve

# Start the app
start_app.bat    # Easy way
# OR
conda activate pdf2md
python -m uvicorn backend.app.main:app --reload
```

### 4. Use

1. Open browser: http://localhost:8000
2. Drag and drop a PDF file
3. Wait for processing (progress shown in real-time)
4. Review and edit the markdown
5. Click "💾 Save to Outputs"
6. Copy from `outputs/` folder to your Obsidian vault

## Project Structure

```
pdf_to_md_obsidian/
├── backend/app/           # FastAPI backend
│   ├── main.py           # Server with WebSocket support
│   ├── processor.py      # GLM-OCR integration
│   ├── config.py         # App configuration
│   └── config.yaml       # GLM-OCR Ollama settings
├── frontend/             # Vanilla JS frontend
│   ├── index.html       # UI
│   ├── styles.css       # Dark theme
│   └── app.js           # Client logic
├── uploads/             # Temporary PDF storage
├── outputs/             # Processed markdown files
├── environment.yml      # Conda environment (recommended)
├── requirements.txt     # Pip dependencies (alternative)
├── setup_conda.bat/.sh  # One-time setup scripts
└── start_app.bat        # Quick start script
```

## Configuration

Edit `backend/app/config.py` to customize:
- Upload/output folder locations
- GLM-OCR settings
- Server host/port
- File size limits

The `backend/app/config.yaml` configures GLM-OCR to use Ollama:
- Disables cloud API (MaaS)
- Points to local Ollama (localhost:11434)
- Uses CPU for layout detection

## Troubleshooting

### "Ollama not running"
- Make sure Ollama is running: `ollama serve`
- Verify glm-ocr model: `ollama list`
- Check Ollama is on port 11434: `curl http://localhost:11434/api/tags`

### "PDF too large"
- Current limit: 50MB
- Try splitting PDF or reducing quality
- Adjust `max_file_size` in `backend/app/config.py`

### "Processing is slow"
- First run loads models (slow)
- Subsequent runs are faster
- Large PDFs take longer
- Layout detection uses CPU (configurable)

### Environment Issues
- **Windows DLL errors**: Use Conda instead of pip
- **Python 3.11+ issues**: Use Python 3.10 (Conda handles this)
- **Import errors**: Run `setup_conda.bat` again

## Alternative Setup (Without Conda)

If you don't have Conda, you can use pip (requires Python 3.10):

```bash
# Create virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
# OR
.venv\Scripts\activate.bat     # Windows CMD

# Install dependencies
pip install -r requirements.txt

# Start Ollama (separate terminal)
ollama serve

# Run app
python -m uvicorn backend.app.main:app --reload
```

**Note**: Pip may have PyTorch DLL issues on Windows. Conda is recommended.

## Development

Based on the architecture documented in `C:\Users\loris\Documents\obisidian\Designing\projects\pdf-to-obsidian\`.

### Tech Stack
- **Backend**: Python 3.10, FastAPI, GLM-OCR SDK
- **Frontend**: HTML/CSS/JavaScript (no build tools)
- **OCR**: GLM-OCR via Ollama
- **UI**: Dark theme, WebSocket real-time updates

### Key Components
- `main.py` - FastAPI routes and WebSocket handling
- `processor.py` - PDF processing with GLM-OCR
- `app.js` - Frontend logic and WebSocket client
- `config.yaml` - GLM-OCR Ollama configuration

## Tips

- Start with small PDFs (1-5 pages) to test
- Review and edit output before saving
- Keep Ollama running for best performance
- First conversion is slower (loads models)
- Images are detected but manual handling needed (future feature)

## License

TBD - Open source

## Acknowledgments

- [GLM-OCR](https://github.com/zai-org/GLM-OCR) - State-of-the-art OCR model
- [Ollama](https://ollama.com/) - Local model deployment
