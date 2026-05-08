"""PDF processing using GLM-OCR"""
import asyncio
import logging
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


class PDFProcessor:
    """Handles PDF processing with GLM-OCR"""

    def __init__(self):
        self.parser = None

    async def initialize(self):
        """Initialize the GLM-OCR parser"""
        try:
            # Load config from YAML file to use local Ollama instead of MaaS
            from glmocr.config import load_config

            config_path = Path(__file__).parent / "config.yaml"
            config = load_config(str(config_path))

            logger.info(f"Loaded config from {config_path}, MaaS enabled: {config.pipeline.maas.enabled}")

            # Initialize parser with selfhosted mode explicitly
            # This prevents MaaS client initialization
            self.parser = GlmOcr(
                mode="selfhosted",  # Explicitly use selfhosted mode
                layout_device=settings.layout_device,
                config_model=config
            )
            logger.info("GLM-OCR parser initialized successfully with local Ollama (selfhosted mode)")
        except Exception as e:
            logger.error(f"Failed to initialize GLM-OCR parser: {e}")
            raise

    async def check_ollama_health(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://{settings.ocr_api_host}:{settings.ocr_api_port}/api/tags",
                    timeout=5.0
                )
                return response.status_code == 200
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
                    error="Ollama service is not running. Please start Ollama with 'ollama serve'"
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
        with self.parser:
            return self.parser.parse(pdf_path)

    async def cleanup(self):
        """Cleanup resources"""
        if self.parser:
            # GLM-OCR cleanup if needed
            pass


# Global processor instance
processor = PDFProcessor()
