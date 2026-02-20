// ================================
// SalonPro - Main JavaScript
// ================================

// Login Form Handler
function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    // Simple validation
    if (email && password) {
        // Simulate login delay
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Signing in...';
        submitBtn.disabled = true;
        
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
    }
}

// Initialize Chart.js when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize chart if canvas exists
    const chartCanvas = document.getElementById('salesChart');
    if (chartCanvas) {
        initializeSalesChart();
    }
    
    // Add click listeners to all interactive elements
    initializeInteractivity();
});

// Sales Chart Initialization
function initializeSalesChart() {
    const ctx = document.getElementById('salesChart');
    if (!ctx) return;
    
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(232, 150, 143, 0.3)');
    gradient.addColorStop(1, 'rgba(232, 150, 143, 0.05)');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Revenue',
                data: [3200, 1800, 4100, 4300, 5800, 4900, 3200],
                borderColor: '#E8968F',
                backgroundColor: gradient,
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 5,
                pointBackgroundColor: '#E8968F',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 7,
                pointHoverBackgroundColor: '#E8968F',
                pointHoverBorderColor: '#fff',
                pointHoverBorderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#2C2C2C',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                    borderRadius: 8,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return '$' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#F3F4F6',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#9CA3AF',
                        font: {
                            family: 'Lexend',
                            size: 12
                        },
                        callback: function(value) {
                            return '$' + (value / 1000) + 'k';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        color: '#6B7280',
                        font: {
                            family: 'Lexend',
                            size: 12,
                            weight: '500'
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Initialize all interactive elements
function initializeInteractivity() {
    // Sidebar toggle
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            const sidebar = document.querySelector('.sidebar');
            sidebar.classList.toggle('collapsed');
        });
    }
    
    // Chart tabs
    const chartTabs = document.querySelectorAll('.chart-tab');
    chartTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            chartTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            // Here you would update the chart data
        });
    });
    
    // Filter buttons
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            // Here you would filter the data
        });
    });
    
    // Status filters
    const statusFilters = document.querySelectorAll('.status-filter');
    statusFilters.forEach(filter => {
        filter.addEventListener('click', function() {
            statusFilters.forEach(f => f.classList.remove('active'));
            this.classList.add('active');
            // Here you would filter visits by status
        });
    });
    
    // View toggle buttons
    const viewBtns = document.querySelectorAll('.view-btn');
    viewBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            viewBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            // Here you would change calendar view
        });
    });
    
    // Calendar day click
    const calendarDays = document.querySelectorAll('.calendar-day:not(.other-month)');
    calendarDays.forEach(day => {
        day.addEventListener('click', function() {
            calendarDays.forEach(d => d.classList.remove('selected'));
            this.classList.add('selected');
            // Here you would load visits for selected day
        });
    });
    
    // Table select all checkbox
    const selectAll = document.getElementById('select-all');
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.clients-table tbody input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
    
    // Add hover effects to stat cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements that should animate
    const animateElements = document.querySelectorAll('.stat-card, .chart-section, .client-item');
    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(el);
    });
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Utility function to format date
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    }).format(new Date(date));
}

// Simulate real-time updates (for demo purposes)
function simulateRealTimeUpdates() {
    setInterval(() => {
        // Update notification badge
        const badge = document.querySelector('.notification-badge');
        if (badge && Math.random() > 0.7) {
            const count = parseInt(badge.textContent);
            badge.textContent = count + 1;
            
            // Add pulse animation
            badge.style.animation = 'pulse 0.5s ease-in-out';
            setTimeout(() => {
                badge.style.animation = '';
            }, 500);
        }
    }, 30000); // Every 30 seconds
}

// Add CSS for pulse animation dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.2); }
    }
    
    .sidebar.collapsed {
        width: 80px;
    }
    
    .sidebar.collapsed .logo span,
    .sidebar.collapsed .nav-item span,
    .sidebar.collapsed .help-section {
        display: none;
    }
    
    .calendar-day.selected {
        background: #F4B5AF !important;
        border: 2px solid #E8968F;
    }
`;
document.head.appendChild(style);

// Initialize real-time updates
simulateRealTimeUpdates();

// Export functions for global use
window.handleLogin = handleLogin;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;