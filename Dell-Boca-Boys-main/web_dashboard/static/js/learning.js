/**
 * Dell Boca Vista Boys - Learning Analytics JavaScript
 * Comprehensive learning system visualization
 */

class LearningAnalytics {
    constructor() {
        this.apiBase = '';
        this.refreshInterval = null;
        this.init();
    }

    init() {
        console.log('✅ Learning Analytics initialized');
        this.loadLearningData();

        // Auto-refresh every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadLearningData();
        }, 30000);
    }

    async loadLearningData() {
        try {
            const response = await fetch(`${this.apiBase}/api/learning/stats`);
            const data = await response.json();

            this.renderLearningDashboard(data);
            console.log('✅ Learning data loaded');

        } catch (error) {
            console.error('Failed to load learning data:', error);
            this.renderError();
        }
    }

    renderLearningDashboard(data) {
        const container = document.getElementById('learningStats');
        if (!container) return;

        const html = `
            <!-- Summary Cards -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="metric-card">
                        <div class="metric-icon bg-gradient-purple">
                            <i class="fas fa-brain"></i>
                        </div>
                        <div class="metric-info">
                            <h6>Patterns Discovered</h6>
                            <h3>${data.summary.total_patterns}</h3>
                            <small class="text-muted">${(data.summary.avg_pattern_confidence * 100).toFixed(0)}% avg confidence</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card">
                        <div class="metric-icon bg-gradient-blue">
                            <i class="fas fa-layer-group"></i>
                        </div>
                        <div class="metric-info">
                            <h6>Topic Clusters</h6>
                            <h3>${data.summary.total_topics}</h3>
                            <small class="text-muted">Conversation themes</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card">
                        <div class="metric-icon bg-gradient-green">
                            <i class="fas fa-lightbulb"></i>
                        </div>
                        <div class="metric-info">
                            <h6>Active Insights</h6>
                            <h3>${data.summary.active_insights}</h3>
                            <small class="text-muted">AI-generated</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card">
                        <div class="metric-icon bg-gradient-orange">
                            <i class="fas fa-user-cog"></i>
                        </div>
                        <div class="metric-info">
                            <h6>Preferences Learned</h6>
                            <h3>${data.summary.total_preferences}</h3>
                            <small class="text-muted">${(data.summary.avg_preference_confidence * 100).toFixed(0)}% confidence</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Patterns & Topics -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-chart-line"></i> Recent Interaction Patterns</h5>
                        </div>
                        <div class="card-body">
                            ${this.renderPatterns(data.recent_patterns)}
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-tags"></i> Top Conversation Topics</h5>
                        </div>
                        <div class="card-body">
                            ${this.renderTopics(data.top_topics)}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Insights -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-brain"></i> AI-Generated Learning Insights</h5>
                        </div>
                        <div class="card-body">
                            ${this.renderInsights(data.recent_insights)}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Preferences -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-user-check"></i> Learned User Preferences</h5>
                        </div>
                        <div class="card-body">
                            ${this.renderPreferences(data.key_preferences)}
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    renderPatterns(patterns) {
        if (!patterns || patterns.length === 0) {
            return '<p class="text-muted">No patterns discovered yet</p>';
        }

        return `
            <div class="list-group list-group-flush">
                ${patterns.map(pattern => `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="mb-1">${pattern.name}</h6>
                                <small class="text-muted">Observed ${pattern.frequency} times</small>
                            </div>
                            <div class="text-right">
                                <div class="badge badge-success">
                                    ${(pattern.confidence * 100).toFixed(0)}% confidence
                                </div>
                                <br>
                                <small class="text-muted">${this.formatDate(pattern.last_observed)}</small>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderTopics(topics) {
        if (!topics || topics.length === 0) {
            return '<p class="text-muted">No topics identified yet</p>';
        }

        return `
            <div class="list-group list-group-flush">
                ${topics.map(topic => `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <div style="flex: 1;">
                                <h6 class="mb-1">${topic.name}</h6>
                                <div class="progress" style="height: 8px; margin-top: 8px;">
                                    <div class="progress-bar" role="progressbar"
                                         style="width: ${(topic.conversations / 30 * 100)}%; background: linear-gradient(135deg, var(--navy-dark), var(--navy-medium));"
                                         aria-valuenow="${topic.conversations}" aria-valuemin="0" aria-valuemax="30"></div>
                                </div>
                            </div>
                            <div class="text-right ml-3">
                                <strong>${topic.conversations}</strong>
                                <br>
                                <small class="text-muted">conversations</small>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderInsights(insights) {
        if (!insights || insights.length === 0) {
            return '<p class="text-muted">No insights generated yet</p>';
        }

        return `
            <div class="row">
                ${insights.map((insight, index) => `
                    <div class="col-md-6 mb-3">
                        <div class="card h-100" style="border-left: 4px solid ${this.getInsightColor(insight.type)};">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <span class="badge" style="background: ${this.getInsightColor(insight.type)};">
                                        ${insight.type}
                                    </span>
                                    <div class="text-right">
                                        <small class="text-muted">Confidence: ${(insight.confidence * 100).toFixed(0)}%</small>
                                        <br>
                                        <small class="text-muted">Impact: ${(insight.impact * 100).toFixed(0)}%</small>
                                    </div>
                                </div>
                                <h6 class="card-title">${insight.title}</h6>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderPreferences(preferences) {
        if (!preferences || preferences.length === 0) {
            return '<p class="text-muted">No preferences learned yet</p>';
        }

        return `
            <div class="row">
                ${preferences.map(pref => `
                    <div class="col-md-4 mb-3">
                        <div class="card h-100">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <span class="badge badge-primary">${pref.type}</span>
                                    <span class="badge badge-success">${(pref.confidence * 100).toFixed(0)}%</span>
                                </div>
                                <h6 class="card-title mb-2">${this.formatPrefKey(pref.key)}</h6>
                                <p class="card-text text-muted small mb-0">
                                    <strong>${this.formatPrefValue(pref.value)}</strong>
                                </p>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    getInsightColor(type) {
        const colors = {
            'user_preference': '#001f3f',
            'optimization': '#10B981',
            'pattern_discovery': '#3B82F6',
            'behavioral': '#F59E0B',
            'recommendation': '#D4AF37'
        };
        return colors[type] || '#001f3f';
    }

    formatPrefKey(key) {
        return key.replace(/_/g, ' ')
                  .replace(/\b\w/g, l => l.toUpperCase());
    }

    formatPrefValue(value) {
        try {
            const parsed = JSON.parse(value);
            return JSON.stringify(parsed, null, 2);
        } catch {
            return value;
        }
    }

    formatDate(dateStr) {
        if (!dateStr) return 'Unknown';
        try {
            const date = new Date(dateStr);
            const now = new Date();
            const diffMs = now - date;
            const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

            if (diffDays === 0) return 'Today';
            if (diffDays === 1) return 'Yesterday';
            if (diffDays < 7) return `${diffDays} days ago`;
            if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
            return `${Math.floor(diffDays / 30)} months ago`;
        } catch {
            return dateStr;
        }
    }

    renderError() {
        const container = document.getElementById('learningStats');
        if (!container) return;

        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Learning Analytics Unavailable</strong>
                <p>Unable to load learning analytics data. The system is collecting data and will display insights once sufficient information is gathered.</p>
            </div>
        `;
    }

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Initialize when DOM is ready
$(document).ready(() => {
    window.learningAnalytics = new LearningAnalytics();
    console.log('✅ Learning Analytics module loaded');
});
