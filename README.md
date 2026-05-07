# PDF to Obsidian Converter

Convert PDFs (articles, scanned documents) to Obsidian-friendly markdown using state-of-the-art GLM-OCR.

## Features

- 🚀 **State-of-the-art OCR** - Uses GLM-OCR (ranks #1 on OmniDocBench)
- 📝 **Live preview** - See results with rendered markdown preview
- ✏️ **Edit before saving** - Fix OCR errors before committing to your vault
- 🖼️ **Image extraction** - Saves images separately with Obsidian `![[image.png]]` links
- 🏠 **100% Local** - Runs on localhost via Ollama, no cloud dependencies

## Prerequisites

1. **Python 3.10+**
2. **Ollama** - [Install Ollama](https://ollama.com/)
3. **GLM-OCR Model**:
   ```bash
   ollama pull glm-ocr
   ```

## Installation

1. Clone or download this repository

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install GLM-OCR SDK:
   ```bash
   pip install "glmocr[selfhosted]"
   ```

## Usage

1. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ```

2. **Start the application**:
   ```bash
   python -m uvicorn backend.app.main:app --reload
   ```

3. **Open your browser**:
   Navigate to http://localhost:8000

4. **Convert a PDF**:
   - Drag and drop a PDF file
   - Wait for processing (progress shown)
   - Review and edit the markdown
   - Click "Save" to export

## Project Structure

```
pdf_to_md_obsidian/
├── backend/
│   └── app/
│       ├── main.py           # FastAPI server
│       ├── config.py         # Configuration
│       └── processor.py      # GLM-OCR integration
├── frontend/
│   ├── index.html           # UI
│   ├── styles.css           # Styling
│   └── app.js               # Client logic
├── uploads/                 # Temporary PDF storage
├── outputs/                 # Processed outputs
└── requirements.txt         # Python dependencies
```

## Configuration

Edit `backend/app/config.py` to customize:
- Upload folder location
- Output folder location
- GLM-OCR settings (layout device, etc.)
- Server host/port

## Troubleshooting

**"Ollama not running"**
- Make sure Ollama is installed and running: `ollama serve`
- Verify the glm-ocr model is installed: `ollama list`

**"PDF too large"**
- GLM-OCR has size limits for processing
- Try splitting the PDF or reducing quality

**Processing takes a long time**
- First run loads the model (slow)
- Subsequent runs are faster
- Consider running layout detection on CPU: see config options

## Development

Based on the architecture documented in the [project wiki](../../obisidian/Designing/projects/pdf-to-obsidian/).

## License

TBD - Open source

## Acknowledgments

- [GLM-OCR](https://github.com/zai-org/GLM-OCR) - State-of-the-art OCR model
- [Ollama](https://ollama.com/) - Local model deployment
