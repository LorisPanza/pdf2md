# PDF to Obsidian - Project Overview

## Quick Links

- **Main Documentation**: [README.md](README.md)
- **Design Docs**: `C:\Users\loris\Documents\obisidian\Designing\projects\pdf-to-obsidian\`

## Project Files

### Setup & Run
- `setup_conda.bat` / `setup_conda.sh` - One-time environment setup
- `start_app.bat` - Quick start script (checks Ollama, activates env, starts server)
- `environment.yml` - Conda environment specification (recommended)
- `requirements.txt` - Pip dependencies (alternative to conda)

### Source Code
- `backend/app/main.py` - FastAPI server with WebSocket
- `backend/app/processor.py` - GLM-OCR PDF processing
- `backend/app/config.py` - Application settings
- `backend/app/config.yaml` - GLM-OCR Ollama configuration
- `frontend/index.html` - Web UI
- `frontend/app.js` - Client-side JavaScript
- `frontend/styles.css` - Dark theme styling

### Data Folders
- `uploads/` - Temporary PDF storage (gitignored)
- `outputs/` - Processed markdown files (gitignored)

### Configuration
- `.gitignore` - Git ignore rules
- `README.md` - Main documentation

## Workflow

1. **Setup** (once): Run `setup_conda.bat` → Creates `pdf2md` environment
2. **Start Ollama**: `ollama serve` → Keep running in separate terminal
3. **Run App**: `start_app.bat` → Opens http://localhost:8000
4. **Process PDFs**: Upload → Review → Edit → Save to `outputs/`
5. **Copy to Obsidian**: Move `.md` files from `outputs/` to your vault

## Architecture

```
User Browser (http://localhost:8000)
    ↓
Frontend (HTML/CSS/JS + WebSocket)
    ↓
FastAPI Backend (Python)
    ↓
GLM-OCR SDK (Python)
    ↓
Ollama (localhost:11434)
    ↓
glm-ocr model (local inference)
```

## Key Design Decisions

- **Local-first**: No cloud dependencies, runs on localhost
- **Conda over pip**: Avoids PyTorch DLL issues on Windows
- **WebSocket**: Real-time progress updates
- **No build tools**: Vanilla HTML/CSS/JS for simplicity
- **Ollama**: Simplest way to run GLM-OCR locally
- **CPU layout detection**: Saves GPU for OCR tasks

## Common Tasks

### Update Dependencies
```bash
conda env update -f environment.yml
```

### Clear Uploads/Outputs
```bash
rm -rf uploads/* outputs/*
```

### Check Ollama Models
```bash
ollama list
```

### View Logs
```bash
# Logs are printed to console where uvicorn runs
# Look for: "OCR API host: localhost" and "OCR API port: 11434"
```

### Debug Config
```python
from glmocr.config import load_config
config = load_config("backend/app/config.yaml")
print(f"MaaS: {config.pipeline.maas.enabled}")  # Should be False
print(f"Port: {config.pipeline.ocr_api.api_port}")  # Should be 11434
```

## Development Status

- ✅ MVP Complete (v0.1)
- ✅ Conda environment working
- ✅ Ollama integration fixed
- ✅ WebSocket real-time updates
- ✅ Edit before save
- ⏳ Image handling (detected but not saved separately)
- ⏳ Batch processing
- ⏳ Obsidian frontmatter

See design docs for full roadmap.
