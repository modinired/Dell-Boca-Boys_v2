/**
 * Dell Boca Vista Boys - Charts JavaScript
 * Performance visualization using Chart.js
 */

class ChartsApp {
    constructor() {
        this.performanceChart = null;
        this.agentActivityChart = null;
        this.apiBase = '';
        this.init();
    }

    init() {
        // Wait for DOM and Chart.js to be ready
        if (typeof Chart === 'undefined') {
            setTimeout(() => this.init(), 100);
            return;
        }

        this.initializeCharts();
        this.loadChartData();

        console.log('✅ Charts initialized');
    }

    initializeCharts() {
        this.createPerformanceChart();
        this.createAgentActivityChart();
    }

    createPerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;

        this.performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [
                    {
                        label: 'Total Interactions',
                        data: [65, 78, 90, 81, 96, 105, 134, 142, 158, 170, 185, 200],
                        borderColor: '#001f3f',
                        backgroundColor: 'rgba(0, 31, 63, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Workflows Generated',
                        data: [28, 35, 42, 38, 45, 52, 61, 68, 75, 82, 89, 95],
                        borderColor: '#1a4d7a',
                        backgroundColor: 'rgba(26, 77, 122, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Learning Events',
                        data: [45, 52, 61, 70, 75, 85, 95, 102, 118, 125, 140, 155],
                        borderColor: '#10B981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 31, 63, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    createAgentActivityChart() {
        const ctx = document.getElementById('agentActivityChart');
        if (!ctx) return;

        this.agentActivityChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [
                    'Chick Camarrano Jr.',
                    'Arhur Dunzarelli',
                    'Little Jim Spedines',
                    'Gerry Nascondino',
                    'Collogero Asperturo',
                    'Paolo L\'Aranciata',
                    'Sauconi Osobucco'
                ],
                datasets: [{
                    data: [250, 180, 195, 160, 170, 145, 155],
                    backgroundColor: [
                        '#001f3f',
                        '#1a4d7a',
                        '#2c5f8d',
                        '#4a7ba7',
                        '#D4AF37',
                        '#10B981',
                        '#3B82F6'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            padding: 12,
                            usePointStyle: true,
                            font: {
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += context.parsed + ' tasks';
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }

    async loadChartData() {
        try {
            const response = await fetch(`${this.apiBase}/api/charts/performance`);
            const data = await response.json();

            if (data.performance && this.performanceChart) {
                this.updatePerformanceChart(data.performance);
            }

            if (data.agent_activity && this.agentActivityChart) {
                this.updateAgentActivityChart(data.agent_activity);
            }

        } catch (error) {
            console.log('Using demo chart data (API not available yet)');
        }
    }

    updatePerformanceChart(data) {
        if (!this.performanceChart) return;

        this.performanceChart.data.labels = data.labels || this.performanceChart.data.labels;
        this.performanceChart.data.datasets[0].data = data.interactions || this.performanceChart.data.datasets[0].data;
        this.performanceChart.data.datasets[1].data = data.workflows || this.performanceChart.data.datasets[1].data;
        this.performanceChart.data.datasets[2].data = data.learning || this.performanceChart.data.datasets[2].data;

        this.performanceChart.update();
    }

    updateAgentActivityChart(data) {
        if (!this.agentActivityChart) return;

        this.agentActivityChart.data.datasets[0].data = data.values || this.agentActivityChart.data.datasets[0].data;
        this.agentActivityChart.update();
    }

    destroy() {
        if (this.performanceChart) {
            this.performanceChart.destroy();
        }
        if (this.agentActivityChart) {
            this.agentActivityChart.destroy();
        }
    }
}

// Initialize charts when DOM is ready
$(document).ready(() => {
    window.chartsApp = new ChartsApp();
});
