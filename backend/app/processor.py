"""PDF processing using GLM-OCR"""
import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass

from glmocr import GlmOcr, parse
from .config import settings

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of PDF processing"""
    success: bool
    markdown: Optional[str] = None
    json_result: Optional[dict] = None
    error: Optional[str] = None
    images: list[str] = None

    def __post_init__(self):
        if self.images is None:
            self.images = []


# How long Ollama should keep the OCR model resident in memory between requests,
# so each page doesn't pay the cold-load cost again.
OLLAMA_KEEP_ALIVE = "30m"


class PDFProcessor:
    """Handles PDF processing with GLM-OCR"""

    def __init__(self):
        self.parser = None
        self.ocr_model = self._load_model_name()

    def _load_model_name(self) -> str:
        """Read the configured OCR model name from config.yaml (no network needed)"""
        from glmocr.config import load_config
        config_path = Path(__file__).parent / "config.yaml"
        config = load_config(str(config_path))
        return config.pipeline.ocr_api.model

    async def _prewarm_model(self):
        """
        Force Ollama to load the model weights into memory before the pipeline's
        own warm-up call. A cold model load can take longer than the pipeline's
        connect_timeout, causing initialization to fail with a spurious timeout.
        """
        import httpx
        url = f"http://{settings.ocr_api_host}:{settings.ocr_api_port}/api/generate"
        async with httpx.AsyncClient() as client:
            await client.post(
                url,
                json={"model": self.ocr_model, "keep_alive": OLLAMA_KEEP_ALIVE},
                timeout=150.0
            )

    async def initialize(self):
        """Initialize the GLM-OCR parser"""
        try:
            # Get config path
            config_path = Path(__file__).parent / "config.yaml"

            # Load config for verification
            from glmocr.config import load_config
            config = load_config(str(config_path))

            # Debug logging
            logger.info(f"Loading config from: {config_path}")
            logger.info(f"MaaS enabled: {config.pipeline.maas.enabled}")
            logger.info(f"OCR API host: {config.pipeline.ocr_api.api_host}")
            logger.info(f"OCR API port: {config.pipeline.ocr_api.api_port}")
            logger.info(f"OCR API path: {config.pipeline.ocr_api.api_path}")
            logger.info(f"OCR API mode: {config.pipeline.ocr_api.api_mode}")
            logger.info(f"OCR model: {config.pipeline.ocr_api.model}")

            # Preload the model into Ollama's memory so the pipeline's warm-up
            # call below doesn't race a cold model load against its own timeout
            logger.info(f"Pre-warming Ollama model '{self.ocr_model}'...")
            await self._prewarm_model()
            logger.info("Model pre-warmed successfully")

            # Initialize parser with config_path parameter
            self.parser = GlmOcr(
                config_path=str(config_path),
                layout_device=settings.layout_device
            )

            # Start the pipeline (important: keeps it alive for all requests)
            self.parser.__enter__()
            logger.info("GLM-OCR parser initialized and pipeline started successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GLM-OCR parser: {e}")
            raise

    async def check_ollama_health(self) -> bool:
        """Check if Ollama is running and the configured OCR model is pulled"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://{settings.ocr_api_host}:{settings.ocr_api_port}/api/tags",
                    timeout=5.0
                )
                if response.status_code != 200:
                    return False
                models = response.json().get("models", [])
                # Ollama tags include the version, e.g. "glm-ocr:latest"
                model_names = {m.get("name", "").split(":")[0] for m in models}
                return self.ocr_model.split(":")[0] in model_names
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False

    async def process_pdf(
        self,
        pdf_path: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> ProcessingResult:
        """
        Process a PDF file and return markdown result

        Args:
            pdf_path: Path to the PDF file
            progress_callback: Optional callback for progress updates (message, percentage)

        Returns:
            ProcessingResult with markdown and metadata
        """
        try:
            # Check Ollama health first
            if progress_callback:
                await progress_callback("Checking Ollama service...", 5)

            if not await self.check_ollama_health():
                return ProcessingResult(
                    success=False,
                    error=f"Ollama is not running or model '{self.ocr_model}' is not pulled. "
                          f"Run 'ollama serve' and 'ollama pull {self.ocr_model}'"
                )

            if self.parser is None:
                return ProcessingResult(
                    success=False,
                    error="OCR parser failed to initialize. Check server logs and restart the server."
                )

            # Validate file exists
            if not pdf_path.exists():
                return ProcessingResult(
                    success=False,
                    error=f"PDF file not found: {pdf_path}"
                )

            # Check file size
            file_size = pdf_path.stat().st_size
            if file_size > settings.max_file_size:
                return ProcessingResult(
                    success=False,
                    error=f"PDF file too large: {file_size / 1024 / 1024:.1f}MB. Maximum: {settings.max_file_size / 1024 / 1024:.0f}MB"
                )

            if progress_callback:
                await progress_callback("Loading PDF...", 10)

            # Process with GLM-OCR
            # Note: This is synchronous, so we run it in a thread pool
            if progress_callback:
                await progress_callback("Analyzing layout...", 30)

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._process_sync,
                str(pdf_path)
            )

            if progress_callback:
                await progress_callback("OCR processing...", 60)

            # Extract markdown and metadata
            markdown = result.markdown_result
            json_data = result.json_result

            if progress_callback:
                await progress_callback("Finalizing...", 90)

            # Extract image information from JSON if available
            images = []
            if json_data and "layout" in json_data:
                for item in json_data.get("layout", []):
                    if item.get("type") == "figure":
                        images.append(item.get("content", ""))

            if progress_callback:
                await progress_callback("Complete!", 100)

            return ProcessingResult(
                success=True,
                markdown=markdown,
                json_result=json_data,
                images=images
            )

        except Exception as e:
            logger.error(f"Error processing PDF: {e}", exc_info=True)
            return ProcessingResult(
                success=False,
                error=f"Processing failed: {str(e)}"
            )

    def _process_sync(self, pdf_path: str):
        """Synchronous processing wrapper for GLM-OCR"""
        # Pipeline is already started in initialize(), just call parse
        return self.parser.parse(pdf_path)

    async def cleanup(self):
        """Cleanup resources"""
        if self.parser:
            try:
                # Stop the pipeline on shutdown
                self.parser.__exit__(None, None, None)
                logger.info("GLM-OCR pipeline stopped")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")


# Global processor instance
processor = PDFProcessor()
