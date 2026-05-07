"""Application configuration"""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Server settings
    host: str = "127.0.0.1"
    port: int = 8000

    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    upload_dir: Path = base_dir / "uploads"
    output_dir: Path = base_dir / "outputs"

    # GLM-OCR settings
    layout_device: str = "cpu"  # Use CPU for layout detection to save GPU for OCR
    ocr_api_host: str = "localhost"
    ocr_api_port: int = 11434  # Ollama default port

    # Session settings
    session_timeout: int = 3600  # 1 hour
    max_file_size: int = 50 * 1024 * 1024  # 50MB

    class Config:
        env_prefix = "PDF2MD_"


settings = Settings()

# Ensure directories exist
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.output_dir.mkdir(parents=True, exist_ok=True)
