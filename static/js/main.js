// Main JavaScript file for Brand Voice Codifier

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Initialize tabs
    var tabElList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tab"]'));
    tabElList.forEach(function(tabEl) {
        tabEl.addEventListener('click', function(event) {
            event.preventDefault();
            var tab = new bootstrap.Tab(tabEl);
            tab.show();
        });
    });

    // Add loading state to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Processing...';

                // Store original text for restoration after form submission
                submitButton.dataset.originalText = originalText;
            }
        });
    });

    // Add gauge chart functionality
    if (typeof Chart !== 'undefined') {
        // Register gauge chart type
        Chart.defaults.gauge = Chart.defaults.doughnut;

        const gaugeChartType = {
            id: 'gauge',
            beforeDraw: function(chart) {
                const width = chart.width;
                const height = chart.height;
                const ctx = chart.ctx;
                const dataset = chart.data.datasets[0];
                const options = chart.options;

                // Draw background
                ctx.save();
                ctx.beginPath();
                ctx.arc(width / 2, height / 2, height * 0.4, Math.PI, 0, false);
                ctx.fillStyle = '#f5f5f5';
                ctx.fill();
                ctx.restore();

                // Draw needle
                const value = dataset.value;
                const min = dataset.minValue || 0;
                const max = dataset.maxValue || 10;
                const angle = Math.PI * (1 - (value - min) / (max - min));

                const needleLength = height * 0.35;
                const needleWidth = width * 0.03;
                const needleColor = options.needle && options.needle.color || 'rgba(0, 0, 0, 0.8)';

                ctx.save();
                ctx.translate(width / 2, height / 2);
                ctx.rotate(angle);

                // Draw needle
                ctx.beginPath();
                ctx.moveTo(0, -5);
                ctx.lineTo(needleLength, 0);
                ctx.lineTo(0, 5);
                ctx.fillStyle = needleColor;
                ctx.fill();

                // Draw needle center
                ctx.beginPath();
                ctx.arc(0, 0, 10, 0, Math.PI * 2);
                ctx.fillStyle = needleColor;
                ctx.fill();

                ctx.restore();

                // Draw value label
                if (options.valueLabel && options.valueLabel.display) {
                    const fontSize = height / 10;
                    ctx.font = fontSize + 'px Arial';
                    ctx.textBaseline = 'middle';
                    ctx.textAlign = 'center';

                    let valueText = value.toString();
                    if (options.valueLabel.formatter) {
                        valueText = options.valueLabel.formatter(value);
                    }

                    const labelColor = options.valueLabel.color || '#000';
                    const labelBgColor = options.valueLabel.backgroundColor || 'rgba(255, 255, 255, 0.8)';
                    const labelPadding = options.valueLabel.padding || { top: 5, bottom: 5 };

                    const textWidth = ctx.measureText(valueText).width;
                    const bgWidth = textWidth + 20;
                    const bgHeight = fontSize + labelPadding.top + labelPadding.bottom;

                    ctx.fillStyle = labelBgColor;
                    ctx.fillRect(width / 2 - bgWidth / 2, height * 0.7 - bgHeight / 2, bgWidth, bgHeight);

                    ctx.fillStyle = labelColor;
                    ctx.fillText(valueText, width / 2, height * 0.7);
                }
            }
        };

        Chart.register(gaugeChartType);
    }

    // Handle file uploads
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const filePreview = document.getElementById('file-preview');
            if (!filePreview) return;

            if (this.files.length > 0) {
                const file = this.files[0];
                const fileName = document.getElementById('file-name');
                const fileSize = document.getElementById('file-size');

                if (fileName && fileSize) {
                    fileName.textContent = file.name;
                    fileSize.textContent = formatFileSize(file.size);
                    filePreview.classList.remove('d-none');
                }
            } else {
                filePreview.classList.add('d-none');
            }
        });
    });

    // URL validation for web scraper
    const urlInput = document.getElementById('url');
    if (urlInput) {
        urlInput.addEventListener('input', function() {
            const analyzeButton = document.getElementById('analyze-button');
            if (!analyzeButton) return;

            const url = this.value.trim();
            const isValid = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/.test(url);

            if (isValid) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                analyzeButton.disabled = false;
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
                analyzeButton.disabled = true;
            }
        });
    }

    // Handle restart button
    const restartButton = document.getElementById('confirm-restart');
    if (restartButton) {
        restartButton.addEventListener('click', function() {
            // Show loading state
            this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Restarting...';
            this.disabled = true;

            // Submit the restart form
            document.getElementById('restart-form').submit();
        });
    }
});

// Utility function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
