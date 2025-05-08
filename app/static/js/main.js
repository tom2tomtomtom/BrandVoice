// Main JavaScript file for Brand Voice Codifier

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // File upload preview
    const fileInput = document.getElementById('document-upload');
    const fileList = document.getElementById('file-list');
    
    if (fileInput && fileList) {
        fileInput.addEventListener('change', function() {
            fileList.innerHTML = '';
            
            for (let i = 0; i < this.files.length; i++) {
                const file = this.files[i];
                const fileItem = document.createElement('div');
                fileItem.className = 'alert alert-info mb-2';
                
                // Determine file icon based on type
                let fileIcon = 'fa-file';
                if (file.type.includes('pdf')) {
                    fileIcon = 'fa-file-pdf';
                } else if (file.type.includes('text')) {
                    fileIcon = 'fa-file-alt';
                }
                
                fileItem.innerHTML = `
                    <i class="fas ${fileIcon} me-2"></i>
                    <strong>${file.name}</strong> (${formatFileSize(file.size)})
                `;
                
                fileList.appendChild(fileItem);
            }
        });
    }
    
    // Handle form submissions with loading state
    const forms = document.querySelectorAll('form.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            } else {
                // Show loading state
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Processing...';
                    
                    // Store original text for restoration after form submission
                    submitBtn.dataset.originalText = originalText;
                }
            }
            
            form.classList.add('was-validated');
        });
    });
    
    // Interview navigation
    const prevBtn = document.getElementById('prev-section');
    const nextBtn = document.getElementById('next-section');
    const sectionTabs = document.querySelectorAll('.interview-tab');
    
    if (prevBtn && nextBtn && sectionTabs.length > 0) {
        let currentSection = 0;
        
        // Initialize tabs
        showSection(currentSection);
        
        prevBtn.addEventListener('click', function() {
            if (currentSection > 0) {
                currentSection--;
                showSection(currentSection);
            }
        });
        
        nextBtn.addEventListener('click', function() {
            if (currentSection < sectionTabs.length - 1) {
                // Validate current section before proceeding
                const currentForm = sectionTabs[currentSection].querySelector('form');
                if (currentForm && !validateForm(currentForm)) {
                    return;
                }
                
                currentSection++;
                showSection(currentSection);
            }
        });
        
        function showSection(index) {
            // Hide all sections
            sectionTabs.forEach(tab => tab.classList.add('d-none'));
            
            // Show current section
            sectionTabs[index].classList.remove('d-none');
            
            // Update button states
            prevBtn.disabled = index === 0;
            
            if (index === sectionTabs.length - 1) {
                nextBtn.textContent = 'Complete Interview';
                nextBtn.classList.remove('btn-primary');
                nextBtn.classList.add('btn-success');
            } else {
                nextBtn.textContent = 'Next Section';
                nextBtn.classList.remove('btn-success');
                nextBtn.classList.add('btn-primary');
            }
            
            // Update progress indicator
            const progressBar = document.getElementById('interview-progress');
            if (progressBar) {
                const progress = ((index + 1) / sectionTabs.length) * 100;
                progressBar.style.width = progress + '%';
                progressBar.setAttribute('aria-valuenow', progress);
            }
        }
        
        function validateForm(form) {
            // Basic validation
            let isValid = true;
            
            const requiredFields = form.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                if (!field.value) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            return isValid;
        }
    }
    
    // Web scraper URL validation
    const urlInput = document.getElementById('website-url');
    const scrapeBtn = document.getElementById('scrape-button');
    
    if (urlInput && scrapeBtn) {
        urlInput.addEventListener('input', function() {
            const url = this.value.trim();
            const isValid = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/.test(url);
            
            if (isValid) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                scrapeBtn.disabled = false;
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
                scrapeBtn.disabled = true;
            }
        });
    }
});

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
