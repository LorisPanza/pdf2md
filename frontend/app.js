// PDF to Obsidian Converter - Frontend

class PDFConverter {
    constructor() {
        this.sessionId = null;
        this.websocket = null;
        this.markdownContent = '';

        this.init();
    }

    init() {
        this.setupElements();
        this.setupEventListeners();
        this.checkHealth();
    }

    setupElements() {
        // Upload section
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.fileInfo = document.getElementById('file-info');
        this.filename = document.getElementById('filename');
        this.filesize = document.getElementById('filesize');

        // Processing section
        this.processingSection = document.getElementById('processing-section');
        this.progressBar = document.getElementById('progress-bar');
        this.progressMessage = document.getElementById('progress-message');

        // Results section
        this.resultsSection = document.getElementById('results-section');
        this.markdownPreview = document.getElementById('markdown-preview');
        this.markdownEditor = document.getElementById('markdown-editor');
        this.saveBtn = document.getElementById('save-btn');
        this.newBtn = document.getElementById('new-btn');
        this.saveSuccess = document.getElementById('save-success');

        // Error section
        this.errorSection = document.getElementById('error-section');
        this.errorMessage = document.getElementById('error-message');
        this.retryBtn = document.getElementById('retry-btn');

        // Health status
        this.healthStatus = document.getElementById('health-status');
        this.statusIndicator = document.getElementById('status-indicator');
        this.statusText = document.getElementById('status-text');
    }

    setupEventListeners() {
        // Upload area
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && file.type === 'application/pdf') {
                this.uploadFile(file);
            } else {
                this.showError('Please drop a PDF file');
            }
        });

        // Tabs
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Buttons
        this.saveBtn.addEventListener('click', () => this.saveMarkdown());
        this.newBtn.addEventListener('click', () => this.reset());
        this.retryBtn.addEventListener('click', () => this.reset());

        // Sync editor with preview
        this.markdownEditor.addEventListener('input', () => {
            this.markdownContent = this.markdownEditor.value;
            this.renderMarkdown();
        });
    }

    async checkHealth() {
        try {
            const response = await fetch('/health');
            const data = await response.json();

            if (data.ollama === 'running') {
                this.statusIndicator.classList.add('healthy');
                this.statusText.textContent = 'Ready';
            } else {
                this.statusIndicator.classList.add('error');
                this.statusText.textContent = 'Ollama not running';
            }
        } catch (error) {
            this.statusIndicator.classList.add('error');
            this.statusText.textContent = 'Service unavailable';
        }
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.uploadFile(file);
        }
    }

    async uploadFile(file) {
        try {
            // Show file info
            this.filename.textContent = file.name;
            this.filesize.textContent = this.formatFileSize(file.size);
            this.fileInfo.style.display = 'flex';

            // Upload file
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }

            const data = await response.json();
            this.sessionId = data.session_id;

            // Start processing
            this.startProcessing();

        } catch (error) {
            this.showError(error.message);
        }
    }

    startProcessing() {
        // Hide upload, show processing
        document.getElementById('upload-section').style.display = 'none';
        this.processingSection.style.display = 'block';

        // Connect WebSocket
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/${this.sessionId}`;

        this.websocket = new WebSocket(wsUrl);

        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            // Send start command
            this.websocket.send(JSON.stringify({ action: 'start' }));
        };

        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showError('Connection error. Please try again.');
        };

        this.websocket.onclose = () => {
            console.log('WebSocket closed');
        };
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'progress':
                this.updateProgress(data.progress, data.message);
                break;

            case 'complete':
                this.showResults(data.markdown, data.images);
                break;

            case 'error':
                this.showError(data.message);
                break;
        }
    }

    updateProgress(percentage, message) {
        this.progressBar.style.width = `${percentage}%`;
        this.progressMessage.textContent = message;
    }

    showResults(markdown, images) {
        // Close WebSocket
        if (this.websocket) {
            this.websocket.close();
        }

        // Store markdown
        this.markdownContent = markdown;

        // Hide processing, show results
        this.processingSection.style.display = 'none';
        this.resultsSection.style.display = 'block';

        // Populate editor and preview
        this.markdownEditor.value = markdown;
        this.renderMarkdown();

        // Log images for now (TODO: handle properly)
        if (images && images.length > 0) {
            console.log('Images detected:', images);
        }
    }

    renderMarkdown() {
        this.markdownPreview.innerHTML = marked.parse(this.markdownContent);
    }

    switchTab(tabName) {
        // Update buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update panes
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.toggle('active', pane.id === `${tabName}-tab`);
        });
    }

    async saveMarkdown() {
        try {
            const response = await fetch(`/save/${this.sessionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    markdown: this.markdownContent,
                    filename: this.filename.textContent.replace('.pdf', '.md')
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Save failed');
            }

            const data = await response.json();

            // Show success message
            this.saveSuccess.style.display = 'block';
            setTimeout(() => {
                this.saveSuccess.style.display = 'none';
            }, 3000);

            console.log('Saved to:', data.output_path);

        } catch (error) {
            alert('Save failed: ' + error.message);
        }
    }

    showError(message) {
        // Close WebSocket if open
        if (this.websocket) {
            this.websocket.close();
        }

        // Hide other sections
        document.getElementById('upload-section').style.display = 'none';
        this.processingSection.style.display = 'none';
        this.resultsSection.style.display = 'none';

        // Show error
        this.errorSection.style.display = 'block';
        this.errorMessage.textContent = message;
    }

    reset() {
        // Reset state
        this.sessionId = null;
        this.markdownContent = '';

        // Hide all sections except upload
        document.getElementById('upload-section').style.display = 'block';
        this.processingSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.errorSection.style.display = 'none';

        // Reset UI
        this.fileInfo.style.display = 'none';
        this.fileInput.value = '';
        this.progressBar.style.width = '0%';

        // Check health again
        this.checkHealth();
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PDFConverter();
});
