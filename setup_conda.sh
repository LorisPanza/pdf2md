#!/bin/bash

echo "============================================"
echo "PDF to Obsidian - Conda Setup"
echo "============================================"
echo ""

echo "Removing old environment if exists..."
conda deactivate 2>/dev/null
conda env remove -n pdf2md -y 2>/dev/null

echo ""
echo "Creating new conda environment with Python 3.10..."
conda env create -f environment.yml

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create conda environment"
    exit 1
fi

echo ""
echo "============================================"
echo "Setup complete!"
echo "============================================"
echo ""
echo "To start the application:"
echo "  1. Activate: conda activate pdf2md"
echo "  2. Start Ollama: ollama serve"
echo "  3. Run app: python -m uvicorn backend.app.main:app --reload"
echo ""
