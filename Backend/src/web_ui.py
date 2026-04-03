"""
Simple lightweight web UI for document summarization
"""

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from .summarizer import TechnicalDocumentSummarizer

logger = logging.getLogger(__name__)

# Create FastAPI app for UI
ui_app = FastAPI(title="Document Summarizer UI")

# HTML template - Enhanced with all features
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intent-Aware Document Summarizer</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --primary: #667eea;
            --primary-dark: #764ba2;
            --success: #4ade80;
            --danger: #f87171;
            --warning: #fbbf24;
            --info: #60a5fa;
            --light: #f8fafc;
            --dark: #1e293b;
            --border: #e2e8f0;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            min-height: 100vh;
            color: var(--dark);
        }
        .wrapper {
            display: flex;
            min-height: 100vh;
        }
        .sidebar {
            width: 280px;
            background: white;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            overflow-y: auto;
            padding: 20px;
        }
        .main-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .logo {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 30px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .nav-tabs {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-bottom: 30px;
        }
        .nav-tab {
            padding: 12px 16px;
            border: none;
            background: var(--light);
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s;
            text-align: left;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--dark);
        }
        .nav-tab:hover {
            background: var(--border);
            transform: translateX(4px);
        }
        .nav-tab.active {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
        }
        .settings-section {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid var(--border);
        }
        .settings-title {
            font-weight: bold;
            margin-bottom: 15px;
            color: var(--dark);
        }
        .setting-item {
            margin-bottom: 15px;
        }
        .setting-label {
            font-size: 13px;
            font-weight: 500;
            color: #64748b;
            margin-bottom: 8px;
        }
        .setting-select {
            width: 100%;
            padding: 8px;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 13px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            padding: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .tabs {
            display: flex;
            gap: 0;
            margin-bottom: 30px;
            border-bottom: 2px solid var(--border);
        }
        .tab-btn {
            padding: 12px 24px;
            background: none;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-weight: 500;
            color: #64748b;
            transition: all 0.3s;
        }
        .tab-btn:hover {
            color: var(--primary);
        }
        .tab-btn.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .header {
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 32px;
            margin-bottom: 8px;
        }
        .header p {
            color: #64748b;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: var(--dark);
            font-size: 14px;
        }
        input[type="text"],
        input[type="file"],
        select,
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            transition: all 0.3s;
        }
        input[type="text"]:focus,
        input[type="file"]:focus,
        select:focus,
        textarea:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        textarea {
            resize: vertical;
            min-height: 200px;
        }
        .drop-zone {
            border: 3px dashed var(--primary);
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            background: rgba(102, 126, 234, 0.05);
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
        }
        .drop-zone:hover {
            border-color: var(--primary-dark);
            background: rgba(102, 126, 234, 0.1);
        }
        .drop-zone.dragover {
            border-color: var(--primary-dark);
            background: rgba(102, 126, 234, 0.15);
        }
        .drop-zone-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        .buttons {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 20px;
        }
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
        }
        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-secondary {
            background: var(--light);
            color: var(--dark);
            border: 2px solid var(--border);
        }
        .btn-secondary:hover:not(:disabled) {
            background: var(--border);
        }
        .btn-success {
            background: var(--success);
            color: white;
        }
        .btn-small {
            padding: 8px 12px;
            font-size: 12px;
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .alert {
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
            flex-direction: row;
            align-items: center;
            gap: 12px;
        }
        .alert.show {
            display: flex;
        }
        .alert-success {
            background: #dcfce7;
            color: #166534;
            border-left: 4px solid var(--success);
        }
        .alert-error {
            background: #fee2e2;
            color: #991b1b;
            border-left: 4px solid var(--danger);
        }
        .alert-info {
            background: #dbeafe;
            color: #1e40af;
            border-left: 4px solid var(--info);
        }
        .loader {
            display: none;
            text-align: center;
            padding: 30px;
        }
        .spinner {
            border: 4px solid var(--light);
            border-top: 4px solid var(--primary);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .progress-container {
            margin: 20px 0;
        }
        .progress-item {
            margin-bottom: 15px;
        }
        .progress-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13px;
            font-weight: 500;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: var(--light);
            border-radius: 10px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary) 0%, var(--primary-dark) 100%);
            width: 0%;
            transition: width 0.3s;
        }
        .result-card {
            background: var(--light);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid var(--primary);
        }
        .result-title {
            font-weight: bold;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .result-text {
            line-height: 1.6;
            color: var(--dark);
            max-height: 300px;
            overflow-y: auto;
        }
        .result-meta {
            display: flex;
            gap: 15px;
            margin-top: 12px;
            font-size: 12px;
            color: #64748b;
        }
        .result-actions {
            display: flex;
            gap: 8px;
            margin-top: 12px;
        }
        .history-item {
            background: var(--light);
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.3s;
            border-left: 4px solid var(--border);
        }
        .history-item:hover {
            border-left-color: var(--primary);
            transform: translateX(4px);
        }
        .history-title {
            font-weight: 500;
            margin-bottom: 4px;
        }
        .history-meta {
            font-size: 12px;
            color: #64748b;
        }
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #64748b;
        }
        .empty-icon {
            font-size: 48px;
            margin-bottom: 15px;
            opacity: 0.5;
        }
        .file-list {
            margin-top: 15px;
        }
        .file-item {
            background: var(--light);
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .file-name {
            font-weight: 500;
            flex: 1;
        }
        .file-size {
            font-size: 12px;
            color: #64748b;
            margin-right: 15px;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-success {
            background: #dcfce7;
            color: #166534;
        }
        .badge-warning {
            background: #fef08a;
            color: #713f12;
        }
        @media (max-width: 768px) {
            .wrapper {
                flex-direction: column;
            }
            .sidebar {
                width: 100%;
                padding: 15px;
            }
            .form-row {
                grid-template-columns: 1fr;
            }
            .tabs {
                flex-wrap: wrap;
            }
        }
    </style>
</head>
<body>
    <div class="wrapper">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="logo">
                <i class="fas fa-document-alt"></i> Summarizer
            </div>
            
            <div class="nav-tabs">
                <button class="nav-tab active" data-tab="single">
                    <i class="fas fa-file-alt"></i> Single Document
                </button>
                <button class="nav-tab" data-tab="batch">
                    <i class="fas fa-files"></i> Batch Upload
                </button>
                <button class="nav-tab" data-tab="history">
                    <i class="fas fa-history"></i> History
                </button>
                <button class="nav-tab" data-tab="settings">
                    <i class="fas fa-cog"></i> Settings
                </button>
            </div>
            
            <div class="settings-section">
                <div class="settings-title">⚙️ Quick Settings</div>
                
                <div class="setting-item">
                    <div class="setting-label">Language</div>
                    <select id="globalLanguage" class="setting-select">
                        <option value="english">English</option>
                        <option value="spanish">Spanish</option>
                        <option value="french">French</option>
                        <option value="german">German</option>
                        <option value="italian">Italian</option>
                        <option value="portuguese">Portuguese</option>
                        <option value="chinese">Chinese</option>
                        <option value="japanese">Japanese</option>
                        <option value="korean">Korean</option>
                        <option value="arabic">Arabic</option>
                    </select>
                </div>
                
                <div class="setting-item">
                    <div class="setting-label">Summary Type</div>
                    <select id="globalIntent" class="setting-select">
                        <option value="technical_overview">Technical Overview</option>
                        <option value="detailed_analysis">Detailed Analysis</option>
                        <option value="methodology">Methodology</option>
                        <option value="results">Results</option>
                        <option value="conclusion">Conclusion</option>
                        <option value="abstract">Abstract</option>
                    </select>
                </div>
                
                <div class="setting-item">
                    <div class="setting-label">Quality Preference</div>
                    <select id="globalQuality" class="setting-select">
                        <option value="speed">⚡ Speed</option>
                        <option value="balanced" selected>⚖️ Balanced</option>
                        <option value="quality">✨ Quality</option>
                    </select>
                </div>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <div class="container">
                <!-- Single Document Tab -->
                <div class="tab-content active" id="single-tab">
                    <div class="header">
                        <h1>📄 Single Document</h1>
                        <p>Paste or upload a document to generate a summary</p>
                    </div>
                    
                    <div id="alertBox" class="alert"></div>
                    
                    <div class="tabs">
                        <button class="tab-btn active" data-mode="text">
                            <i class="fas fa-keyboard"></i> Paste Text
                        </button>
                        <button class="tab-btn" data-mode="file">
                            <i class="fas fa-upload"></i> Upload File
                        </button>
                    </div>
                    
                    <!-- Text Input -->
                    <div class="mode-content" id="text-mode">
                        <div class="form-group">
                            <label for="documentText">Document Text:</label>
                            <textarea id="documentText" placeholder="Paste your document here..."></textarea>
                        </div>
                    </div>
                    
                    <!-- File Upload -->
                    <div class="mode-content" id="file-mode" style="display:none;">
                        <div class="drop-zone" id="dropZone">
                            <div class="drop-zone-icon">📤</div>
                            <p style="font-weight: 500; margin-bottom: 5px;">Drag and drop your file here</p>
                            <p style="font-size: 13px; color: #64748b;">or click to select (TXT, PDF supported)</p>
                        </div>
                        <input type="file" id="fileInput" style="display:none;" accept=".txt,.pdf">
                        <div id="fileName" class="file-list"></div>
                    </div>
                    
                    <!-- Options -->
                    <div class="form-row">
                        <div class="form-group">
                            <label for="singleLanguage">Language:</label>
                            <select id="singleLanguage">
                                <option value="">Use Global Setting</option>
                                <option value="english">English</option>
                                <option value="spanish">Spanish</option>
                                <option value="french">French</option>
                                <option value="german">German</option>
                                <option value="chinese">Chinese</option>
                                <option value="japanese">Japanese</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="singleIntent">Summary Type:</label>
                            <select id="singleIntent">
                                <option value="">Use Global Setting</option>
                                <option value="technical_overview">Technical Overview</option>
                                <option value="methodology">Methodology</option>
                                <option value="results">Results</option>
                                <option value="conclusion">Conclusion</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="singleQuality">Quality:</label>
                            <select id="singleQuality">
                                <option value="">Use Global Setting</option>
                                <option value="speed">⚡ Speed</option>
                                <option value="balanced">⚖️ Balanced</option>
                                <option value="quality">✨ Quality</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="buttons">
                        <button class="btn-primary" id="generateBtn">
                            <i class="fas fa-magic"></i> Generate Summary
                        </button>
                        <button class="btn-secondary" id="clearBtn">
                            <i class="fas fa-trash"></i> Clear
                        </button>
                    </div>
                    
                    <!-- Progress -->
                    <div class="loader" id="loader">
                        <div class="spinner"></div>
                        <p>Analyzing document and generating summary...</p>
                    </div>
                    
                    <!-- Result -->
                    <div id="resultContainer" style="margin-top: 30px;"></div>
                </div>
                
                <!-- Batch Upload Tab -->
                <div class="tab-content" id="batch-tab">
                    <div class="header">
                        <h1>📁 Batch Processing</h1>
                        <p>Upload multiple documents for processing</p>
                    </div>
                    
                    <div id="batchAlertBox" class="alert"></div>
                    
                    <div class="drop-zone" id="batchDropZone">
                        <div class="drop-zone-icon">📦</div>
                        <p style="font-weight: 500; margin-bottom: 5px;">Drag multiple files here</p>
                        <p style="font-size: 13px; color: #64748b;">or click to select</p>
                    </div>
                    <input type="file" id="batchFileInput" style="display:none;" multiple accept=".txt,.pdf">
                    
                    <div id="batchFileList" class="file-list"></div>
                    
                    <div class="buttons" style="margin-top: 20px;">
                        <button class="btn-primary" id="processBatchBtn" disabled>
                            <i class="fas fa-play"></i> Process All (<span id="fileCount">0</span>)
                        </button>
                        <button class="btn-secondary" id="clearBatchBtn">
                            <i class="fas fa-trash"></i> Clear List
                        </button>
                    </div>
                    
                    <!-- Progress -->
                    <div class="progress-container" id="batchProgress" style="display:none; margin-top: 30px;"></div>
                    
                    <!-- Results -->
                    <div id="batchResultContainer" style="margin-top: 30px;"></div>
                </div>
                
                <!-- History Tab -->
                <div class="tab-content" id="history-tab">
                    <div class="header">
                        <h1>📜 Summary History</h1>
                        <p>View and manage your previous summaries</p>
                    </div>
                    
                    <div class="buttons">
                        <button class="btn-secondary" id="clearHistoryBtn">
                            <i class="fas fa-trash"></i> Clear All History
                        </button>
                    </div>
                    
                    <div id="historyContainer" style="margin-top: 20px;"></div>
                </div>
                
                <!-- Settings Tab -->
                <div class="tab-content" id="settings-tab">
                    <div class="header">
                        <h1>⚙️ Settings</h1>
                        <p>Configure your preferences</p>
                    </div>
                    
                    <div class="form-group">
                        <label>Default Language</label>
                        <select id="settingsLanguage">
                            <option value="english">English</option>
                            <option value="spanish">Spanish</option>
                            <option value="french">French</option>
                            <option value="german">German</option>
                            <option value="chinese">Chinese</option>
                            <option value="japanese">Japanese</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Default Summary Type</label>
                        <select id="settingsIntent">
                            <option value="technical_overview">Technical Overview</option>
                            <option value="detailed_analysis">Detailed Analysis</option>
                            <option value="methodology">Methodology</option>
                            <option value="results">Results</option>
                            <option value="conclusion">Conclusion</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Quality Preference</label>
                        <select id="settingsQuality">
                            <option value="speed">⚡ Speed (Fastest)</option>
                            <option value="balanced" selected>⚖️ Balanced</option>
                            <option value="quality">✨ Quality (Best)</option>
                        </select>
                    </div>
                    
                    <div class="buttons">
                        <button class="btn-primary" id="saveSettingsBtn">
                            <i class="fas fa-save"></i> Save Settings
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // State Management
        const state = {
            currentMode: 'text',
            batchFiles: [],
            history: JSON.parse(localStorage.getItem('summaryHistory')) || [],
            settings: JSON.parse(localStorage.getItem('settings')) || {
                language: 'english',
                intent: 'technical_overview',
                quality: 'balanced'
            }
        };
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            loadSettings();
            setupEventListeners();
            renderHistory();
        });
        
        function setupEventListeners() {
            // Tab navigation
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.addEventListener('click', (e) => {
                    const tabName = e.currentTarget.dataset.tab;
                    switchTab(tabName);
                });
            });
            
            // Mode switching
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const mode = e.currentTarget.dataset.mode;
                    switchMode(mode);
                });
            });
            
            // Single document
            document.getElementById('generateBtn').addEventListener('click', generateSingle);
            document.getElementById('clearBtn').addEventListener('click', () => {
                document.getElementById('documentText').value = '';
                document.getElementById('resultContainer').innerHTML = '';
            });
            
            // File upload
            const dropZone = document.getElementById('dropZone');
            const fileInput = document.getElementById('fileInput');
            dropZone.addEventListener('click', () => fileInput.click());
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('dragover');
            });
            dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('dragover');
                handleFileSelect(e.dataTransfer.files[0]);
            });
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) handleFileSelect(e.target.files[0]);
            });
            
            // Batch
            const batchDropZone = document.getElementById('batchDropZone');
            const batchFileInput = document.getElementById('batchFileInput');
            batchDropZone.addEventListener('click', () => batchFileInput.click());
            batchDropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                batchDropZone.classList.add('dragover');
            });
            batchDropZone.addEventListener('dragleave', () => batchDropZone.classList.remove('dragover'));
            batchDropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                batchDropZone.classList.remove('dragover');
                handleBatchFiles(e.dataTransfer.files);
            });
            batchFileInput.addEventListener('change', (e) => handleBatchFiles(e.target.files));
            
            document.getElementById('processBatchBtn').addEventListener('click', processBatch);
            document.getElementById('clearBatchBtn').addEventListener('click', () => {
                state.batchFiles = [];
                renderBatchList();
            });
            
            // History
            document.getElementById('clearHistoryBtn').addEventListener('click', () => {
                if (confirm('Clear all history?')) {
                    state.history = [];
                    localStorage.removeItem('summaryHistory');
                    renderHistory();
                }
            });
            
            // Settings
            document.getElementById('saveSettingsBtn').addEventListener('click', saveSettings);
        }
        
        function switchTab(tabName) {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName + '-tab').classList.add('active');
        }
        
        function switchMode(mode) {
            state.currentMode = mode;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.mode-content').forEach(m => m.style.display = 'none');
            
            event.target.classList.add('active');
            document.getElementById(mode + '-mode').style.display = 'block';
        }
        
        async function handleFileSelect(file) {
            if (!file) return;
            const text = await file.text();
            document.getElementById('documentText').value = text;
            document.getElementById('fileName').innerHTML = \`<div class="file-item"><span class="file-name">\${file.name}</span><span class="file-size">\${(file.size / 1024).toFixed(1)} KB</span></div>\`;
        }
        
        function handleBatchFiles(files) {
            state.batchFiles = Array.from(files).map((f, i) => ({
                id: Date.now() + i,
                file: f,
                status: 'pending'
            }));
            renderBatchList();
        }
        
        function renderBatchList() {
            const container = document.getElementById('batchFileList');
            if (state.batchFiles.length === 0) {
                container.innerHTML = '';
                document.getElementById('processBatchBtn').disabled = true;
                document.getElementById('fileCount').textContent = '0';
                return;
            }
            
            container.innerHTML = state.batchFiles.map(f => \`
                <div class="file-item">
                    <span class="file-name">\${f.file.name}</span>
                    <span class="file-size">\${(f.file.size / 1024).toFixed(1)} KB</span>
                    <span class="badge badge-\${f.status === 'pending' ? 'warning' : 'success'}">\${f.status}</span>
                </div>
            \`).join('');
            
            document.getElementById('processBatchBtn').disabled = false;
            document.getElementById('fileCount').textContent = state.batchFiles.length;
        }
        
        async function generateSingle() {
            const text = document.getElementById('documentText').value.trim();
            if (!text) {
                showAlert('alertBox', 'Please enter document text', 'error');
                return;
            }
            
            const language = document.getElementById('singleLanguage').value || state.settings.language;
            const intent = document.getElementById('singleIntent').value || state.settings.intent;
            const quality = document.getElementById('singleQuality').value || state.settings.quality;
            
            await summarizeDocument(text, language, intent, quality, 'alertBox', 'resultContainer');
        }
        
        async function summarizeDocument(text, language, intent, quality, alertId, resultId, fileName = null) {
            const alertBox = document.getElementById(alertId);
            const resultContainer = document.getElementById(resultId);
            const loader = document.getElementById('loader');
            
            loader.style.display = 'block';
            
            try {
                const response = await fetch('/api/summarize', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        document: text,
                        language: language,
                        intent: intent,
                        quality_preference: quality,
                        summary_level: 'brief'
                    })
                });
                
                if (!response.ok) throw new Error('API Error');
                const data = await response.json();
                
                // Save to history
                const historyItem = {
                    id: Date.now(),
                    title: fileName || text.substring(0, 50) + '...',
                    summary: data.summary,
                    language: language,
                    intent: intent,
                    timestamp: new Date().toLocaleString(),
                    length: data.length
                };
                state.history.unshift(historyItem);
                localStorage.setItem('summaryHistory', JSON.stringify(state.history.slice(0, 50)));
                
                // Display result
                const html = \`
                    <div class="result-card">
                        <div class="result-title">
                            <span>✅ Summary Generated</span>
                            <span class="badge badge-success">\${data.length} words</span>
                        </div>
                        <div class="result-text">\${data.summary}</div>
                        <div class="result-meta">
                            <span>🌍 \${language}</span>
                            <span>🎯 \${intent}</span>
                            <span>⏱️ \${new Date().toLocaleTimeString()}</span>
                        </div>
                        <div class="result-actions">
                            <button class="btn-secondary btn-small" onclick="downloadResult('\${btoa(data.summary)}', 'txt')">
                                <i class="fas fa-download"></i> TXT
                            </button>
                            <button class="btn-secondary btn-small" onclick="downloadResult('\${btoa(JSON.stringify(data))}', 'json')">
                                <i class="fas fa-download"></i> JSON
                            </button>
                            <button class="btn-secondary btn-small" onclick="copyToClipboard('\${btoa(data.summary)}')">
                                <i class="fas fa-copy"></i> Copy
                            </button>
                        </div>
                    </div>
                \`;
                resultContainer.innerHTML = html;
                showAlert(alertId, 'Summary generated successfully!', 'success');
            } catch (error) {
                showAlert(alertId, 'Error: ' + error.message, 'error');
            } finally {
                loader.style.display = 'none';
            }
        }
        
        async function processBatch() {
            if (state.batchFiles.length === 0) return;
            
            const progressContainer = document.getElementById('batchProgress');
            const resultContainer = document.getElementById('batchResultContainer');
            progressContainer.style.display = 'block';
            resultContainer.innerHTML = '';
            
            let html = '';
            state.batchFiles.forEach((f, i) => {
                html += \`
                    <div class="progress-item">
                        <div class="progress-label">
                            <span>\${f.file.name}</span>
                            <span id="progress-\${i}">0%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="fill-\${i}"></div>
                        </div>
                    </div>
                \`;
            });
            progressContainer.innerHTML = html;
            
            for (let i = 0; i < state.batchFiles.length; i++) {
                const f = state.batchFiles[i];
                try {
                    const text = await f.file.text();
                    // Simulate progress
                    for (let p = 0; p <= 100; p += 20) {
                        document.getElementById('fill-' + i).style.width = p + '%';
                        document.getElementById('progress-' + i).textContent = p + '%';
                        await new Promise(resolve => setTimeout(resolve, 100));
                    }
                    
                    f.status = 'completed';
                    state.batchFiles[i] = f;
                    renderBatchList();
                } catch (error) {
                    f.status = 'error';
                    state.batchFiles[i] = f;
                    renderBatchList();
                }
            }
            
            showAlert('batchAlertBox', 'Batch processing completed!', 'success');
        }
        
        function downloadResult(encoded, format) {
            const data = atob(encoded);
            const el = document.createElement('a');
            el.href = format === 'json' ? 'data:application/json;base64,' + btoa(data) : 'data:text/plain;base64,' + btoa(data);
            el.download = 'summary.' + format;
            el.click();
        }
        
        function copyToClipboard(encoded) {
            navigator.clipboard.writeText(atob(encoded));
            alert('Copied to clipboard!');
        }
        
        function renderHistory() {
            const container = document.getElementById('historyContainer');
            if (state.history.length === 0) {
                container.innerHTML = '<div class="empty-state"><div class="empty-icon">📭</div><p>No history yet</p></div>';
                return;
            }
            
            container.innerHTML = state.history.map(h => \`
                <div class="history-item">
                    <div class="history-title">\${h.title}</div>
                    <div class="history-meta">\${h.timestamp} • \${h.length} words • \${h.intent}</div>
                </div>
            \`).join('');
        }
        
        function showAlert(id, message, type) {
            const alert = document.getElementById(id);
            alert.innerHTML = \`<i class="fas fa-\${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i> \${message}\`;
            alert.className = 'alert show alert-' + type;
            setTimeout(() => alert.classList.remove('show'), 5000);
        }
        
        function saveSettings() {
            state.settings = {
                language: document.getElementById('settingsLanguage').value,
                intent: document.getElementById('settingsIntent').value,
                quality: document.getElementById('settingsQuality').value
            };
            localStorage.setItem('settings', JSON.stringify(state.settings));
            
            document.getElementById('globalLanguage').value = state.settings.language;
            document.getElementById('globalIntent').value = state.settings.intent;
            document.getElementById('globalQuality').value = state.settings.quality;
            
            showAlert('alertBox', 'Settings saved!', 'success');
        }
        
        function loadSettings() {
            document.getElementById('settingsLanguage').value = state.settings.language;
            document.getElementById('settingsIntent').value = state.settings.intent;
            document.getElementById('settingsQuality').value = state.settings.quality;
            
            document.getElementById('globalLanguage').value = state.settings.language;
            document.getElementById('globalIntent').value = state.settings.intent;
            document.getElementById('globalQuality').value = state.settings.quality;
        }
    </script>
</body>
</html>
"""


@ui_app.get("/", response_class=HTMLResponse)
async def get_ui():
    """Serve the UI HTML."""
    return HTML_TEMPLATE


# Global summarizer for UI
_summarizer = None


def get_summarizer_ui(language: str = "english"):
    """Get or create summarizer instance."""
    global _summarizer
    if _summarizer is None:
        _summarizer = TechnicalDocumentSummarizer(language=language)
    return _summarizer


@ui_app.post("/api/summarize")
async def api_summarize(request: dict):
    """API endpoint for summarization."""
    try:
        document = request.get('document', '')
        language = request.get('language', 'english')
        intent = request.get('intent', 'technical_overview')
        quality_preference = request.get('quality_preference', 'balanced')
        
        if not document:
            return {"error": "Document is required"}, 400
        
        summarizer = get_summarizer_ui(language)
        
        # Use auto_summarize for better model selection
        result = summarizer.auto_summarize(
            document=document,
            intent=intent,
            quality_preference=quality_preference,
            language=language
        )
        
        return {
            "summary": result.get('summary', result),
            "language": language,
            "intent": intent,
            "length": len(str(result.get('summary', result)).split()),
            "model": result.get('model', 'auto'),
            "complexity": result.get('complexity', 'unknown'),
            "use_rag": result.get('use_rag', False)
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"error": str(e)}


def run_ui(host: str = "0.0.0.0", port: int = 8001):
    """
    Run the web UI.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    logger.info(f"Starting Web UI at http://{host}:{port}")
    uvicorn.run(
        ui_app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    run_ui()
