// sleek-background.js - Minimalist, professional background with sticky progress bar
window.onload = function() {
    setTimeout(createSleekBackground, 300);
};

function createSleekBackground() {
    console.log("Creating sleek background...");
    
    // Create main background container
    const bgContainer = document.createElement('div');
    bgContainer.className = 'sleek-background';
    document.body.insertBefore(bgContainer, document.body.firstChild);
    
    // Add gradient accents
    const gradientAccent = document.createElement('div');
    gradientAccent.className = 'gradient-accent';
    bgContainer.appendChild(gradientAccent);
    
    const gradientAccent2 = document.createElement('div');
    gradientAccent2.className = 'gradient-accent-2';
    bgContainer.appendChild(gradientAccent2);
    
    // Add subtle lines
    createSleekLines(bgContainer);
    
    // Add floating dots
    createFloatingDots(bgContainer);
    
    console.log("Sleek background created");
}

function createSleekLines(container) {
    // Create a few subtle lines
    const lineCount = 5;
    
    for (let i = 0; i < lineCount; i++) {
        const line = document.createElement('div');
        line.className = 'sleek-line';
        
        // Randomly position the line
        const isHorizontal = Math.random() > 0.5;
        const width = isHorizontal ? Math.random() * 300 + 100 : 1;
        const height = isHorizontal ? 1 : Math.random() * 300 + 100;
        
        // Position randomly but more toward the edges
        let posX, posY;
        
        if (Math.random() > 0.5) {
            // Position near left or right edge
            posX = Math.random() > 0.5 ? 
                Math.random() * 200 : 
                window.innerWidth - (Math.random() * 200) - width;
        } else {
            // Position anywhere
            posX = Math.random() * (window.innerWidth - width);
        }
        
        if (Math.random() > 0.5) {
            // Position near top or bottom edge
            posY = Math.random() > 0.5 ? 
                Math.random() * 200 : 
                window.innerHeight - (Math.random() * 200) - height;
        } else {
            // Position anywhere
            posY = Math.random() * (window.innerHeight - height);
        }
        
        line.style.width = `${width}px`;
        line.style.height = `${height}px`;
        line.style.left = `${posX}px`;
        line.style.top = `${posY}px`;
        
        // Add subtle blur
        line.style.filter = "blur(1px)";
        
        container.appendChild(line);
    }
}

function createFloatingDots(container) {
    // Create floating dots
    const dotCount = 20;
    
    for (let i = 0; i < dotCount; i++) {
        const dot = document.createElement('div');
        dot.className = 'sleek-dot';
        
        // Random position
        const posX = Math.random() * window.innerWidth;
        const posY = Math.random() * window.innerHeight;
        
        dot.style.left = `${posX}px`;
        dot.style.top = `${posY}px`;
        
        // Random size (small)
        const size = Math.random() * 3 + 2;
        dot.style.width = `${size}px`;
        dot.style.height = `${size}px`;
        
        // Random opacity
        dot.style.opacity = Math.random() * 0.2 + 0.1;
        
        // Random animation delay
        dot.style.animationDelay = `${Math.random() * 5}s`;
        dot.style.animationDuration = `${Math.random() * 15 + 15}s`;
        
        container.appendChild(dot);
    }
}

// Initialize sticky progress bar - to be called from DOMContentLoaded
function initStickyProgressBar() {
    const progressBar = document.getElementById('progressBar');
    if (!progressBar) return;
    
    // Create a wrapper div to maintain layout space when bar becomes fixed
    const wrapper = document.createElement('div');
    wrapper.className = 'sticky-progress-container';
    progressBar.parentNode.insertBefore(wrapper, progressBar);
    wrapper.appendChild(progressBar);
    
    // Clone the progress bar for the sticky version
    const stickyBar = progressBar.cloneNode(true);
    stickyBar.id = 'stickyProgressBar';
    stickyBar.classList.add('sticky');
    document.body.appendChild(stickyBar);
    
    // Sync the active states between the two progress bars
    function syncProgressBars() {
        const activeStep = progressBar.querySelector('.progress-step.active');
        const completedSteps = progressBar.querySelectorAll('.progress-step.completed');
        
        if (activeStep) {
            const activeIndex = activeStep.dataset.step;
            const stickyActiveStep = stickyBar.querySelector(`.progress-step[data-step="${activeIndex}"]`);
            stickyBar.querySelectorAll('.progress-step').forEach(step => step.classList.remove('active', 'completed'));
            
            if (stickyActiveStep) {
                stickyActiveStep.classList.add('active');
                
                // Add completed class to previous steps
                stickyBar.querySelectorAll('.progress-step').forEach(step => {
                    if (parseInt(step.dataset.step) < parseInt(activeIndex)) {
                        step.classList.add('completed');
                    }
                });
            }
            
            // Set progress width
            const progressWidth = ((parseInt(activeIndex) - 1) / (progressBar.querySelectorAll('.progress-step').length - 1)) * 100;
            stickyBar.style.setProperty('--progress-width', progressWidth + '%');
        }
    }
    
    // Check scroll position and show/hide sticky bar
    function checkScrollPosition() {
        const wrapperRect = wrapper.getBoundingClientRect();
        const isOffScreen = wrapperRect.bottom < 0;
        
        if (isOffScreen) {
            stickyBar.classList.add('visible');
        } else {
            stickyBar.classList.remove('visible');
        }
    }
    
    // Initialize and add event listeners
    window.addEventListener('scroll', checkScrollPosition);
    
    // Watch for changes to the original progress bar
    const observer = new MutationObserver(syncProgressBars);
    observer.observe(progressBar, { attributes: true, childList: true, subtree: true });
    
    // Initial sync
    syncProgressBars();
}
function copyTableData() {
    // Create a hidden text area
    const textarea = document.createElement('textarea');
    
    // Get all tables
    const tables = document.querySelectorAll('table');
    let allData = '';
    
    // Process each table
    tables.forEach(table => {
        // Find table heading if available
        let heading = '';
        const parentEl = table.parentElement;
        if (parentEl && parentEl.querySelector('h2')) {
            heading = parentEl.querySelector('h2').textContent + '\n';
        }
        
        allData += heading;
        
        // Process rows
        const rows = table.querySelectorAll('tr');
        rows.forEach(row => {
            const cells = row.querySelectorAll('td, th');
            let rowData = '';
            
            cells.forEach((cell, i) => {
                rowData += cell.textContent.trim();
                if (i < cells.length - 1) {
                    rowData += '\t';
                }
            });
            
            allData += rowData + '\n';
        });
        
        allData += '\n\n';
    });
    
    // Set textarea value
    textarea.value = allData;
    
    // Add to body
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    
    // Select and copy
    textarea.select();
    document.execCommand('copy');
    
    // Clean up
    document.body.removeChild(textarea);
    
    // Show feedback
    const btn = document.getElementById('copy-all-btn');
    const originalText = btn.textContent;
    btn.textContent = 'Copied!';
    
    setTimeout(function() {
        btn.textContent = originalText;
    }, 2000);
}
