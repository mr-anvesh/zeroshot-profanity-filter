// API Base URL
const API_BASE = '';

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.getAttribute('data-tab');
        
        // Update buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');
        
        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        // Hide error message
        hideError();
    });
});

// Threshold slider update
const filterThreshold = document.getElementById('filter-threshold');
const filterThresholdValue = document.getElementById('filter-threshold-value');

filterThreshold.addEventListener('input', (e) => {
    filterThresholdValue.textContent = e.target.value;
});

// Filter text functionality
const filterButton = document.getElementById('filter-button');
const filterInput = document.getElementById('filter-input');
const filterMode = document.getElementById('filter-mode');

filterButton.addEventListener('click', async () => {
    const text = filterInput.value.trim();
    
    if (!text) {
        showError('Please enter some text to filter.');
        return;
    }
    
    setLoading(filterButton, true);
    hideError();
    hideResult('filter-result');
    
    try {
        const response = await fetch(`${API_BASE}/api/filter`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                mode: filterMode.value,
                threshold: parseFloat(filterThreshold.value)
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to filter text');
        }
        
        displayFilterResult(data);
    } catch (error) {
        showError(`Error: ${error.message}`);
    } finally {
        setLoading(filterButton, false);
    }
});

// Check text functionality
const checkButton = document.getElementById('check-button');
const checkInput = document.getElementById('check-input');

checkButton.addEventListener('click', async () => {
    const text = checkInput.value.trim();
    
    if (!text) {
        showError('Please enter some text to check.');
        return;
    }
    
    setLoading(checkButton, true);
    hideError();
    hideResult('check-result');
    
    try {
        const response = await fetch(`${API_BASE}/api/check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to check text');
        }
        
        displayCheckResult(data);
    } catch (error) {
        showError(`Error: ${error.message}`);
    } finally {
        setLoading(checkButton, false);
    }
});

// Display filter results
function displayFilterResult(data) {
    document.getElementById('filter-original').textContent = data.original;
    document.getElementById('filter-filtered').textContent = data.filtered;
    document.getElementById('filter-confidence').textContent = 
        `Profane: ${(data.profane_probability * 100).toFixed(1)}% | Non-Profane: ${(data.non_profane_probability * 100).toFixed(1)}%`;
    document.getElementById('filter-label').textContent = data.label;
    
    const profaneBadge = document.getElementById('filter-profane-badge');
    const profaneText = document.getElementById('filter-profane');
    
    if (data.is_profane) {
        profaneText.textContent = '⚠️ Profane';
        profaneBadge.classList.add('profane');
        profaneBadge.classList.remove('clean');
    } else {
        profaneText.textContent = '✓ Clean';
        profaneBadge.classList.add('clean');
        profaneBadge.classList.remove('profane');
    }
    
    showResult('filter-result');
}

// Display check results
function displayCheckResult(data) {
    document.getElementById('check-text').textContent = data.text;
    document.getElementById('check-confidence').textContent = 
        `Profane: ${(data.profane_probability * 100).toFixed(1)}% | Non-Profane: ${(data.non_profane_probability * 100).toFixed(1)}%`;
    document.getElementById('check-label').textContent = data.label;
    
    const profaneBadge = document.getElementById('check-profane-badge');
    const profaneText = document.getElementById('check-profane');
    
    if (data.is_profane) {
        profaneText.textContent = '⚠️ Profane';
        profaneBadge.classList.add('profane');
        profaneBadge.classList.remove('clean');
    } else {
        profaneText.textContent = '✓ Clean';
        profaneBadge.classList.add('clean');
        profaneBadge.classList.remove('profane');
    }
    
    showResult('check-result');
}

// Helper functions
function setLoading(button, isLoading) {
    const spinner = button.querySelector('.spinner');
    const text = button.querySelector('.button-text');
    
    if (isLoading) {
        button.disabled = true;
        spinner.classList.remove('hidden');
        text.textContent = 'Processing...';
    } else {
        button.disabled = false;
        spinner.classList.add('hidden');
        text.textContent = button.id === 'filter-button' ? 'Filter Text' : 'Check Text';
    }
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function hideError() {
    const errorDiv = document.getElementById('error-message');
    errorDiv.classList.add('hidden');
}

function showResult(elementId) {
    document.getElementById(elementId).classList.remove('hidden');
}

function hideResult(elementId) {
    document.getElementById(elementId).classList.add('hidden');
}

// Enter key support for textareas
filterInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        filterButton.click();
    }
});

checkInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        checkButton.click();
    }
});

// Image upload functionality
const imageInput = document.getElementById('image-input');
const imageButton = document.getElementById('image-button');
const imageUploadArea = document.getElementById('image-upload-area');
const uploadPlaceholder = document.getElementById('upload-placeholder');
const imagePreview = document.getElementById('image-preview');
const previewImg = document.getElementById('preview-img');
const removeImageBtn = document.getElementById('remove-image');
let selectedFile = null;

// Click to upload
imageUploadArea.addEventListener('click', (e) => {
    if (!e.target.closest('.remove-image')) {
        imageInput.click();
    }
});

// Drag and drop
imageUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    imageUploadArea.classList.add('drag-over');
});

imageUploadArea.addEventListener('dragleave', () => {
    imageUploadArea.classList.remove('drag-over');
});

imageUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    imageUploadArea.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleImageFile(files[0]);
    }
});

// File input change
imageInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleImageFile(e.target.files[0]);
    }
});

// Handle image file
function handleImageFile(file) {
    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        showError('Invalid file type. Please upload an image file (PNG, JPG, JPEG, GIF, BMP, WEBP).');
        return;
    }
    
    // Validate file size (16MB max)
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('File size too large. Maximum size is 16MB.');
        return;
    }
    
    selectedFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        uploadPlaceholder.style.display = 'none';
        imagePreview.style.display = 'block';
        imageButton.disabled = false;
    };
    reader.readAsDataURL(file);
    
    hideError();
    hideResult('image-result');
}

// Remove image
removeImageBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    selectedFile = null;
    imageInput.value = '';
    uploadPlaceholder.style.display = 'flex';
    imagePreview.style.display = 'none';
    imageButton.disabled = true;
    hideResult('image-result');
});

// Check image functionality
imageButton.addEventListener('click', async () => {
    if (!selectedFile) {
        showError('Please select an image to check.');
        return;
    }
    
    setLoading(imageButton, true);
    hideError();
    hideResult('image-result');
    
    try {
        const formData = new FormData();
        formData.append('image', selectedFile);
        
        const response = await fetch(`${API_BASE}/api/check-image`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to check image');
        }
        
        displayImageResult(data);
    } catch (error) {
        showError(`Error: ${error.message}`);
    } finally {
        setLoading(imageButton, false);
    }
});

// Display image results
function displayImageResult(data) {
    const confidence = (data.confidence * 100).toFixed(1);
    document.getElementById('image-confidence').textContent = `${confidence}%`;
    document.getElementById('image-label').textContent = data.label.toUpperCase();
    
    const profaneBadge = document.getElementById('image-profane-badge');
    const profaneText = document.getElementById('image-profane');
    
    if (data.is_profane) {
        profaneText.textContent = '⚠️ NSFW/Profane';
        profaneBadge.classList.add('profane');
        profaneBadge.classList.remove('clean');
    } else {
        profaneText.textContent = '✓ Safe';
        profaneBadge.classList.add('clean');
        profaneBadge.classList.remove('profane');
    }
    
    // Display all scores
    const scoresList = document.getElementById('image-scores-list');
    scoresList.innerHTML = '';
    
    if (data.all_scores) {
        Object.entries(data.all_scores).forEach(([label, score]) => {
            const scoreItem = document.createElement('div');
            scoreItem.className = 'score-item';
            scoreItem.innerHTML = `
                <span class="score-label">${label}:</span>
                <span class="score-value">${(score * 100).toFixed(1)}%</span>
            `;
            scoresList.appendChild(scoreItem);
        });
    }
    
    showResult('image-result');
}

// Update setLoading to handle image button text
const originalSetLoading = setLoading;
function setLoading(button, isLoading) {
    const spinner = button.querySelector('.spinner');
    const text = button.querySelector('.button-text');
    
    if (isLoading) {
        button.disabled = true;
        spinner.classList.remove('hidden');
        text.textContent = 'Processing...';
    } else {
        if (button.id === 'image-button' && !selectedFile) {
            button.disabled = true;
        } else {
            button.disabled = false;
        }
        spinner.classList.add('hidden');
        
        if (button.id === 'filter-button') {
            text.textContent = 'Filter Text';
        } else if (button.id === 'check-button') {
            text.textContent = 'Check Text';
        } else if (button.id === 'image-button') {
            text.textContent = 'Check Image';
        }
    }
}
