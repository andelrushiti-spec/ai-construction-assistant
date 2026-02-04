// Construction Legal Assistant - Frontend JavaScript

const API_BASE = '/api';

// Utility Functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => alertDiv.remove(), 5000);
}

function showSpinner(element) {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    element.appendChild(spinner);
    return spinner;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Authentication Functions
async function register(username, email, password) {
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            showAlert('Registration successful! Please login.', 'success');
            setTimeout(() => showLoginForm(), 1500);
        } else {
            showAlert(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showAlert('Network error: ' + error.message, 'error');
    }
}

async function login(username, password) {
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            showAlert('Login successful!', 'success');
            setTimeout(() => window.location.href = '/dashboard', 1000);
        } else {
            showAlert(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showAlert('Network error: ' + error.message, 'error');
    }
}

async function logout() {
    try {
        const response = await fetch(`${API_BASE}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });

        if (response.ok) {
            window.location.href = '/';
        }
    } catch (error) {
        showAlert('Logout failed', 'error');
    }
}

async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE}/auth/check`, {
            credentials: 'include'
        });

        const data = await response.json();
        return data.authenticated;
    } catch (error) {
        return false;
    }
}

// Project Functions
async function getProjects() {
    try {
        const response = await fetch(`${API_BASE}/projects/`, {
            credentials: 'include'
        });

        if (response.status === 401) {
            window.location.href = '/';
            return;
        }

        const data = await response.json();
        return data.projects;
    } catch (error) {
        showAlert('Failed to load projects', 'error');
        return [];
    }
}

async function createProject(name, description) {
    try {
        const response = await fetch(`${API_BASE}/projects/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ name, description })
        });

        const data = await response.json();

        if (response.ok) {
            showAlert('Project created successfully!', 'success');
            return data.project;
        } else {
            showAlert(data.error || 'Failed to create project', 'error');
            return null;
        }
    } catch (error) {
        showAlert('Network error: ' + error.message, 'error');
        return null;
    }
}

async function getProjectDetails(projectId) {
    try {
        const response = await fetch(`${API_BASE}/projects/${projectId}`, {
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();
            return data.project;
        } else {
            showAlert('Failed to load project details', 'error');
            return null;
        }
    } catch (error) {
        showAlert('Network error: ' + error.message, 'error');
        return null;
    }
}

async function deleteProject(projectId) {
    if (!confirm('Are you sure you want to delete this project? All contracts, laws, and queries will be permanently deleted.')) {
        return false;
    }

    try {
        const response = await fetch(`${API_BASE}/projects/${projectId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (response.ok) {
            showAlert('Project deleted successfully', 'success');
            return true;
        } else {
            showAlert('Failed to delete project', 'error');
            return false;
        }
    } catch (error) {
        showAlert('Network error: ' + error.message, 'error');
        return false;
    }
}

// Contract Upload Functions
async function uploadContract(projectId, file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const xhr = new XMLHttpRequest();

        return new Promise((resolve, reject) => {
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable && onProgress) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    onProgress(percentComplete);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 201) {
                    const data = JSON.parse(xhr.responseText);
                    showAlert('Contract uploaded! Processing in background...', 'success');
                    resolve(data.contract);
                } else {
                    const data = JSON.parse(xhr.responseText);
                    showAlert(data.error || 'Upload failed', 'error');
                    reject(new Error(data.error));
                }
            });

            xhr.addEventListener('error', () => {
                showAlert('Upload failed', 'error');
                reject(new Error('Upload failed'));
            });

            xhr.open('POST', `${API_BASE}/upload/contract/${projectId}`);
            xhr.withCredentials = true;
            xhr.send(formData);
        });
    } catch (error) {
        showAlert('Network error: ' + error.message, 'error');
        throw error;
    }
}

async function getContractStatus(contractId) {
    try {
        const response = await fetch(`${API_BASE}/upload/contract/${contractId}/status`, {
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();
            return data.contract;
        }
        return null;
    } catch (error) {
        return null;
    }
}

// Law Upload Functions
async function uploadLaw(projectId, file, metadata, onProgress) {
    const formData = new FormData();
    formData.append('file', file);

    if (metadata.law_number) formData.append('law_number', metadata.law_number);
    if (metadata.law_title) formData.append('law_title', metadata.law_title);
    if (metadata.year) formData.append('year', metadata.year);
    if (metadata.update_version) formData.append('update_version', metadata.update_version);

    try {
        const xhr = new XMLHttpRequest();

        return new Promise((resolve, reject) => {
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable && onProgress) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    onProgress(percentComplete);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 201) {
                    const data = JSON.parse(xhr.responseText);
                    showAlert('Law uploaded! Processing in background...', 'success');
                    resolve(data.law);
                } else {
                    const data = JSON.parse(xhr.responseText);
                    showAlert(data.error || 'Upload failed', 'error');
                    reject(new Error(data.error));
                }
            });

            xhr.addEventListener('error', () => {
                showAlert('Upload failed', 'error');
                reject(new Error('Upload failed'));
            });

            xhr.open('POST', `${API_BASE}/upload/law/${projectId}`);
            xhr.withCredentials = true;
            xhr.send(formData);
        });
    } catch (error) {
        showAlert('Network error: ' + error.message, 'error');
        throw error;
    }
}

// Query Functions
async function askQuestion(projectId, question) {
    try {
        const response = await fetch(`${API_BASE}/query/${projectId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ question })
        });

        if (response.ok) {
            const data = await response.json();
            return data;
        } else {
            const data = await response.json();
            showAlert(data.error || 'Failed to get answer', 'error');
            return null;
        }
    } catch (error) {
        showAlert('Network error: ' + error.message, 'error');
        return null;
    }
}

async function getQueryHistory(projectId) {
    try {
        const response = await fetch(`${API_BASE}/query/history/${projectId}`, {
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();
            return data.history;
        }
        return [];
    } catch (error) {
        return [];
    }
}

// File Upload Drag & Drop
function setupFileUpload(dropZoneId, fileInputId, onFileSelected) {
    const dropZone = document.getElementById(dropZoneId);
    const fileInput = document.getElementById(fileInputId);

    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            onFileSelected(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            onFileSelected(e.target.files[0]);
        }
    });
}

// Progress Bar
function updateProgressBar(progressBarId, percentage) {
    const progressBar = document.getElementById(progressBarId);
    if (progressBar) {
        const fill = progressBar.querySelector('.progress-fill');
        if (fill) {
            fill.style.width = `${percentage}%`;
            fill.textContent = `${Math.round(percentage)}%`;
        }
    }
}

// Export functions for use in HTML
window.appFunctions = {
    register,
    login,
    logout,
    checkAuth,
    getProjects,
    createProject,
    getProjectDetails,
    deleteProject,
    uploadContract,
    getContractStatus,
    uploadLaw,
    askQuestion,
    getQueryHistory,
    setupFileUpload,
    updateProgressBar,
    showAlert,
    showSpinner,
    formatDate
};
