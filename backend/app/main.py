"""Main FastAPI application"""
import asyncio
import json
import logging
import uuid
from pathlib import Path
from typing import Dict
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import aiofiles

from .config import settings
from .processor import processor, ProcessingResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PDF to Obsidian Converter",
    description="Convert PDFs to Obsidian-friendly markdown using GLM-OCR",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage
sessions: Dict[str, dict] = {}

# Mount frontend
frontend_path = settings.base_dir / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize application"""
    logger.info("Starting PDF to Obsidian Converter...")
    try:
        await processor.initialize()
        logger.info("Application started successfully")
    except Exception as e:
        logger.warning(f"Startup initialization failed (Ollama may not be running): {e}")
        logger.warning("Server will start in degraded mode — start Ollama and pull glm-ocr to enable processing")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    await processor.cleanup()


@app.get("/")
async def root():
    """Serve the frontend"""
    frontend_index = frontend_path / "index.html"
    if frontend_index.exists():
        return FileResponse(frontend_index)
    return {"message": "PDF to Obsidian Converter API", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """Check if the service and Ollama are running"""
    ollama_ok = await processor.check_ollama_health()
    return {
        "status": "healthy" if ollama_ok else "degraded",
        "ollama": "running" if ollama_ok else "not running",
        "message": "Service is running" if ollama_ok else "Ollama is not accessible"
    }


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file for processing

    Returns a session_id for tracking progress via WebSocket
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Save uploaded file
        file_path = settings.upload_dir / f"{session_id}.pdf"
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Check file size
        file_size = len(content)
        if file_size > settings.max_file_size:
            file_path.unlink()  # Delete the file
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {file_size / 1024 / 1024:.1f}MB. Maximum: {settings.max_file_size / 1024 / 1024:.0f}MB"
            )

        # Create session
        sessions[session_id] = {
            "filename": file.filename,
            "file_path": str(file_path),
            "status": "uploaded",
            "created_at": datetime.now().isoformat(),
            "result": None
        }

        logger.info(f"File uploaded: {file.filename} -> {session_id}")

        return {
            "session_id": session_id,
            "filename": file.filename,
            "size": file_size
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time processing updates

    Accepts commands:
    - {"action": "start"} - Start processing the PDF
    """
    await websocket.accept()
    logger.info(f"WebSocket connected: {session_id}")

    if session_id not in sessions:
        await websocket.send_json({
            "type": "error",
            "message": "Invalid session ID"
        })
        await websocket.close()
        return

    session = sessions[session_id]

    try:
        # Wait for start command
        while True:
            data = await websocket.receive_json()

            if data.get("action") == "start":
                # Start processing
                session["status"] = "processing"

                async def progress_callback(message: str, percentage: int):
                    """Send progress updates via WebSocket"""
                    await websocket.send_json({
                        "type": "progress",
                        "message": message,
                        "progress": percentage
                    })

                # Process the PDF
                pdf_path = Path(session["file_path"])
                result: ProcessingResult = await processor.process_pdf(
                    pdf_path,
                    progress_callback
                )

                if result.success:
                    # Store result in session
                    session["result"] = {
                        "markdown": result.markdown,
                        "json_result": result.json_result,
                        "images": result.images
                    }
                    session["status"] = "completed"

                    # Send completion message
                    await websocket.send_json({
                        "type": "complete",
                        "markdown": result.markdown,
                        "images": result.images
                    })
                else:
                    session["status"] = "failed"
                    session["error"] = result.error

                    await websocket.send_json({
                        "type": "error",
                        "message": result.error
                    })

                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Processing error: {str(e)}"
            })
        except:
            pass


@app.post("/save/{session_id}")
async def save_result(session_id: str, data: dict):
    """
    Save the edited markdown result to a file

    Body:
    {
        "markdown": "edited markdown content",
        "filename": "output.md"  (optional)
    }
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Processing not completed")

    try:
        # Get edited markdown
        markdown = data.get("markdown")
        if not markdown:
            raise HTTPException(status_code=400, detail="No markdown content provided")

        # Determine output filename
        original_filename = session["filename"]
        base_name = Path(original_filename).stem
        output_filename = data.get("filename", f"{base_name}.md")

        # Ensure .md extension
        if not output_filename.endswith('.md'):
            output_filename += '.md'

        # Save markdown file
        output_path = settings.output_dir / output_filename
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
            await f.write(markdown)

        logger.info(f"Saved markdown: {output_path}")

        # TODO: Handle images if present
        # For now, just note them in the response

        return {
            "success": True,
            "output_path": str(output_path),
            "filename": output_filename
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and cleanup files"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        session = sessions[session_id]

        # Delete uploaded file
        file_path = Path(session["file_path"])
        if file_path.exists():
            file_path.unlink()

        # Remove session
        del sessions[session_id]

        logger.info(f"Session deleted: {session_id}")

        return {"success": True, "message": "Session deleted"}

    except Exception as e:
        logger.error(f"Delete session failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@app.get("/sessions")
async def list_sessions():
    """List all active sessions (for debugging)"""
    return {
        "sessions": [
            {
                "session_id": sid,
                "filename": s["filename"],
                "status": s["status"],
                "created_at": s["created_at"]
            }
            for sid, s in sessions.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
