# Quick Start Guide

## Prerequisites Check

Before starting, ensure you have:
- [ ] Python 3.10 or higher installed
- [ ] Ollama installed ([ollama.com](https://ollama.com))
- [ ] GLM-OCR model pulled: `ollama pull glm-ocr`

## Setup (5 minutes)

1. **Install dependencies:**
   ```bash
   cd D:\projects\pdf_to_md_obsidian
   pip install -r requirements.txt
   pip install "glmocr[selfhosted]"
   ```

2. **Verify Ollama is running:**
   ```bash
   ollama serve
   ```
   Leave this running in a terminal.

3. **Start the application:**
   Open a new terminal:
   ```bash
   cd D:\projects\pdf_to_md_obsidian
   python -m uvicorn backend.app.main:app --reload
   ```

4. **Open in browser:**
   Navigate to http://localhost:8000

## First Conversion

1. Drag and drop a PDF file (or click to browse)
2. Wait for processing (progress shown in real-time)
3. Review the markdown preview
4. Switch to "Edit Markdown" tab to make corrections
5. Click "💾 Save to Outputs"
6. Find your file in `outputs/` folder

## Copy to Obsidian

The output markdown file is in `D:\projects\pdf_to_md_obsidian\outputs\`.

Simply copy the `.md` file to your Obsidian vault!

## Troubleshooting

**"Ollama not running"**
- Run `ollama serve` in a terminal
- Check if it's listening on port 11434

**"PDF too large"**
- Current limit is 50MB
- Try reducing PDF quality or splitting it

**Processing is slow**
- First run is slow (loads model)
- Subsequent runs are faster
- Large PDFs take longer

## Tips

- Start with a small test PDF (1-5 pages)
- Review and edit output before saving
- Images are extracted but need manual handling (future feature)
- Keep Ollama running for best performance
