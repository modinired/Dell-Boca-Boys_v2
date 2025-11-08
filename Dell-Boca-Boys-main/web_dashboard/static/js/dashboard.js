/**
 * Dell Boca Vista Boys - Dashboard JavaScript
 * Main UI logic, navigation, and API calls
 */

class DashboardApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.sessionId = this.generateSessionId();
        this.apiBase = '';  // Same origin
        this.init();
    }

    init() {
        console.log('🎩 Dell Boca Vista Boys Dashboard initializing...');

        // Set session ID
        $('#sessionId').text(this.sessionId.substr(0, 8));

        // Bind event listeners
        this.bindNavigationEvents();
        this.bindChatEvents();
        this.bindWorkflowEvents();
        this.bindSidebarToggle();

        // Load initial data
        this.loadDashboardMetrics();
        this.initializeAgentHive();
        this.checkSystemStatus();

        // Start real-time updates
        this.startRealtimeUpdates();

        console.log('✅ Dashboard ready');
    }

    generateSessionId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    bindNavigationEvents() {
        $('.sidebar-nav .nav-link').on('click', (e) => {
            e.preventDefault();
            const page = $(e.currentTarget).data('page');
            this.navigateTo(page);
        });
    }

    navigateTo(pageName) {
        // Update nav active state
        $('.sidebar-nav .nav-link').removeClass('active');
        $(`.sidebar-nav .nav-link[data-page="${pageName}"]`).addClass('active');

        // Hide all pages, show selected
        $('.page-content').removeClass('active');
        $(`#page-${pageName}`).addClass('active');

        // Update page title
        const pageTitle = $(`.sidebar-nav .nav-link[data-page="${pageName}"]`).text().trim();
        $('#pageTitle').text(pageTitle);

        this.currentPage = pageName;

        // Load page-specific data
        if (pageName === 'agents') {
            this.loadFullAgentHive();
        } else if (pageName === 'learning') {
            this.loadLearningStats();
        }
    }

    bindChatEvents() {
        const sendMessage = () => {
            const message = $('#chatInput').val().trim();
            if (!message) return;

            this.sendChatMessage(message);
            $('#chatInput').val('');
        };

        $('#sendButton').on('click', sendMessage);
        $('#chatInput').on('keypress', (e) => {
            if (e.which === 13 && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    async sendChatMessage(message) {
        // Add user message to chat
        this.appendChatMessage('user', message);

        // Show typing indicator
        this.showTypingIndicator();

        // Animate agent collaboration
        this.animateAgentCollaboration();

        try {
            const response = await fetch(`${this.apiBase}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            const data = await response.json();

            // Remove typing indicator
            this.removeTypingIndicator();

            // Add assistant response
            this.appendChatMessage('assistant', data.response);

            // Reset agents after a brief delay
            setTimeout(() => {
                if (window.agentsApp) {
                    window.agentsApp.resetAllAgents();
                }
            }, 1500);

        } catch (error) {
            console.error('Chat error:', error);
            this.removeTypingIndicator();
            this.appendChatMessage('assistant', 'Sorry, I encountered an error. Please try again.');

            // Reset agents on error too
            if (window.agentsApp) {
                window.agentsApp.resetAllAgents();
            }
        }
    }

    animateAgentCollaboration() {
        if (!window.agentsApp) return;

        // Chick (Capo) coordinates immediately
        window.agentsApp.updateAgentStates({
            'chiccki': { status: 'active', thought: 'Coordinating the crew...' }
        });

        // After 300ms - Arhur and Little Jim start analyzing
        setTimeout(() => {
            window.agentsApp.updateAgentStates({
                'agent1': { status: 'thinking', thought: 'Analyzing workflow patterns...' },
                'agent2': { status: 'thinking', thought: 'Processing data integration...' }
            });
        }, 300);

        // After 800ms - Gerry checks security
        setTimeout(() => {
            window.agentsApp.updateAgentStates({
                'agent3': { status: 'active', thought: 'Validating security protocols...' }
            });
        }, 800);

        // After 1200ms - Collogero optimizes
        setTimeout(() => {
            window.agentsApp.updateAgentStates({
                'agent4': { status: 'thinking', thought: 'Optimizing performance...' }
            });
        }, 1200);

        // After 1600ms - Paolo prepares quality check
        setTimeout(() => {
            window.agentsApp.updateAgentStates({
                'agent5': { status: 'active', thought: 'Running quality checks...' }
            });
        }, 1600);

        // After 2000ms - Sauconi documents
        setTimeout(() => {
            window.agentsApp.updateAgentStates({
                'agent6': { status: 'thinking', thought: 'Documenting insights...' }
            });
        }, 2000);

        // After 2400ms - All agents synthesizing
        setTimeout(() => {
            window.agentsApp.updateAgentStates({
                'chiccki': { status: 'thinking', thought: 'Synthesizing crew insights...' },
                'agent1': { status: 'active', thought: 'Finalizing workflow...' },
                'agent2': { status: 'active', thought: 'Data integration complete...' },
                'agent3': { status: 'idle', thought: 'Security validated ✓' },
                'agent4': { status: 'idle', thought: 'Performance optimized ✓' },
                'agent5': { status: 'active', thought: 'QA passed ✓' },
                'agent6': { status: 'active', thought: 'Documentation ready ✓' }
            });
        }, 2400);
    }

    appendChatMessage(role, text) {
        const timestamp = new Date().toLocaleTimeString();
        const avatarIcon = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-hat-cowboy"></i>';

        const messageHtml = `
            <div class="chat-message ${role}">
                <div class="chat-avatar ${role}-avatar">
                    ${avatarIcon}
                </div>
                <div>
                    <div class="chat-bubble">
                        ${this.escapeHtml(text)}
                    </div>
                    <div class="chat-time">${timestamp}</div>
                </div>
            </div>
        `;

        $('#chatMessages').append(messageHtml);
        $('#chatMessages').scrollTop($('#chatMessages')[0].scrollHeight);
    }

    showTypingIndicator() {
        const indicator = `
            <div class="chat-message assistant typing-indicator">
                <div class="chat-avatar assistant-avatar">
                    <i class="fas fa-hat-cowboy"></i>
                </div>
                <div class="chat-bubble">
                    <span class="loading"></span>
                    <span class="loading"></span>
                    <span class="loading"></span>
                </div>
            </div>
        `;
        $('#chatMessages').append(indicator);
        $('#chatMessages').scrollTop($('#chatMessages')[0].scrollHeight);
    }

    removeTypingIndicator() {
        $('.typing-indicator').remove();
    }

    bindWorkflowEvents() {
        // Show/hide custom schedule input
        $('#workflowRecurring').on('change', (e) => {
            if ($(e.target).val() === 'custom') {
                $('#customScheduleDiv').show();
            } else {
                $('#customScheduleDiv').hide();
            }
        });

        // Stage 1: Propose Workflow
        $('#proposeWorkflow').on('click', async () => {
            const goal = $('#workflowGoal').val().trim();
            if (!goal) {
                alert('Please enter a workflow goal');
                return;
            }

            const recurring = $('#workflowRecurring').val();
            const customCron = $('#customCron').val().trim();

            $('#proposeWorkflow').html('<span class="loading"></span> Analyzing...').prop('disabled', true);

            // Animate agents working on proposal
            this.animateAgentCollaboration();

            try {
                const response = await fetch(`${this.apiBase}/api/workflow/propose`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        goal: goal,
                        recurring: recurring,
                        custom_cron: customCron
                    })
                });

                const data = await response.json();

                // Show proposal card with workflow details
                this.renderWorkflowProposal(data);

                // Scroll to proposal
                $('html, body').animate({
                    scrollTop: $('#workflowProposalCard').offset().top - 80
                }, 500);

            } catch (error) {
                console.error('Workflow proposal error:', error);
                alert('Failed to generate proposal. Please try again.');
            } finally {
                $('#proposeWorkflow').html('<i class="fas fa-lightbulb"></i> Propose Workflow').prop('disabled', false);

                // Reset agents
                setTimeout(() => {
                    if (window.agentsApp) {
                        window.agentsApp.resetAllAgents();
                    }
                }, 1500);
            }
        });

        // Stage 2: Approve Workflow
        $('#approveWorkflow').on('click', async () => {
            $('#approveWorkflow').html('<span class="loading"></span> Approving...').prop('disabled', true);

            try {
                // Hide proposal, show building
                $('#workflowProposalCard').fadeOut(300, () => {
                    $('#workflowBuildingCard').fadeIn(300);
                });

                // Start build process
                await this.buildWorkflow();

            } catch (error) {
                console.error('Workflow approval error:', error);
                alert('Failed to build workflow. Please try again.');
                $('#workflowProposalCard').fadeIn(300);
                $('#workflowBuildingCard').fadeOut(300);
            } finally {
                $('#approveWorkflow').html('<i class="fas fa-check-circle"></i> Approve & Build').prop('disabled', false);
            }
        });

        // Reject Workflow
        $('#rejectWorkflow').on('click', () => {
            if (confirm('Are you sure you want to reject this workflow?')) {
                $('#workflowProposalCard').fadeOut(300);
                $('#workflowGoal').val('');
                alert('Workflow rejected. You can request a new one.');
            }
        });

        // Load completed workflows on page load
        this.loadCompletedWorkflows();
    }

    renderWorkflowProposal(data) {
        // Summary
        const summaryHtml = `
            <p><strong>Goal:</strong> ${this.escapeHtml(data.goal)}</p>
            <p><strong>Schedule:</strong> ${this.escapeHtml(data.schedule || 'One-time')}</p>
            <p><strong>Estimated Duration:</strong> ${data.estimated_duration || '2-5 minutes'}</p>
        `;
        $('#proposalSummary').html(summaryHtml);

        // Workflow Steps
        const stepsHtml = (data.steps || []).map((step, index) => `
            <div class="workflow-step" data-step="${index + 1}">
                <div class="workflow-step-title">${this.escapeHtml(step.title)}</div>
                <div class="workflow-step-desc">${this.escapeHtml(step.description)}</div>
                ${step.nodes ? step.nodes.map(node => `
                    <span class="workflow-step-node">
                        <i class="fas fa-${node.icon || 'cube'}"></i>
                        ${this.escapeHtml(node.name)}
                    </span>
                `).join('') : ''}
            </div>
        `).join('');
        $('#proposalSteps').html(stepsHtml || '<p class="text-muted">No detailed steps available.</p>');

        // Credentials
        const credsHtml = (data.credentials || []).map(cred => `
            <div class="credential-card">
                <div class="credential-icon">
                    <i class="fas fa-${cred.icon || 'key'}"></i>
                </div>
                <div class="credential-info">
                    <div class="credential-name">${this.escapeHtml(cred.name)}</div>
                    <div class="credential-status">
                        ${cred.required ? '<span class="badge badge-danger">Required</span>' : '<span class="badge badge-secondary">Optional</span>'}
                    </div>
                </div>
            </div>
        `).join('');
        $('#proposalCredentials').html(credsHtml || '<p class="text-muted">No credentials required.</p>');

        // Resources
        const resourcesHtml = `
            <div class="col-md-4">
                <div class="resource-metric">
                    <div class="resource-metric-value">${data.resources?.nodes || '5-8'}</div>
                    <div class="resource-metric-label">Nodes</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="resource-metric">
                    <div class="resource-metric-value">${data.resources?.connections || '4-7'}</div>
                    <div class="resource-metric-label">Connections</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="resource-metric">
                    <div class="resource-metric-value">${data.resources?.executions || '~10/hr'}</div>
                    <div class="resource-metric-label">Est. Executions</div>
                </div>
            </div>
        `;
        $('#proposalResources').html(resourcesHtml);

        // Store proposal data for building
        this.currentProposal = data;

        // Show proposal card
        $('#workflowProposalCard').fadeIn(400);
    }

    async buildWorkflow() {
        const buildSteps = [
            { icon: 'sitemap', title: 'Analyzing Requirements', desc: 'Understanding workflow goals and constraints' },
            { icon: 'code', title: 'Generating Nodes', desc: 'Creating n8n workflow nodes' },
            { icon: 'plug', title: 'Configuring Connections', desc: 'Linking nodes together' },
            { icon: 'shield-alt', title: 'Setting Up Credentials', desc: 'Configuring authentication' },
            { icon: 'vial', title: 'Testing Workflow', desc: 'Running validation tests' },
            { icon: 'rocket', title: 'Deploying', desc: 'Activating workflow in n8n' }
        ];

        // Render build steps
        const stepsHtml = buildSteps.map((step, index) => `
            <div class="build-step" id="buildStep${index}">
                <div class="build-step-icon pending">
                    <i class="fas fa-${step.icon}"></i>
                </div>
                <div class="build-step-info">
                    <div class="build-step-title">${step.title}</div>
                    <div class="build-step-desc">${step.desc}</div>
                </div>
            </div>
        `).join('');
        $('#buildProgress').html(stepsHtml);

        // Animate agents
        this.renderBuildAgentActivity();

        // Simulate build progress (replace with real API calls)
        for (let i = 0; i < buildSteps.length; i++) {
            await this.sleep(1500);
            $(`#buildStep${i} .build-step-icon`).removeClass('pending active').addClass('active');
            await this.sleep(2000);
            $(`#buildStep${i} .build-step-icon`).removeClass('active').addClass('completed');
            $(`#buildStep${i} .build-step-icon i`).removeClass().addClass('fas fa-check');
        }

        // Build complete
        await this.sleep(500);
        $('#workflowBuildingCard').fadeOut(300, () => {
            // Add to completed workflows
            this.addCompletedWorkflow({
                id: 'wf_' + Date.now(),
                title: this.currentProposal.goal,
                status: 'active',
                created: new Date().toLocaleString(),
                schedule: this.currentProposal.schedule || 'One-time'
            });

            // Reset form
            $('#workflowGoal').val('');
            $('#workflowRecurring').val('once');

            // Show success message
            alert('✅ Workflow built and deployed successfully!');

            // Scroll to completed workflows
            $('html, body').animate({
                scrollTop: $('#workflowCompletedCard').offset().top - 80
            }, 500);
        });
    }

    renderBuildAgentActivity() {
        const activities = [
            { icon: '🎩', agent: 'Chiccki (Capo)', task: 'Coordinating the crew...' },
            { icon: '👨‍💼', agent: 'Arhur', task: 'Analyzing workflow patterns...' },
            { icon: '🧑‍💻', agent: 'Little Jim', task: 'Processing data integration...' },
            { icon: '🛡️', agent: 'Gerry', task: 'Validating security...' },
            { icon: '⚡', agent: 'Collogero', task: 'Optimizing performance...' },
            { icon: '🔬', agent: 'Paolo', task: 'Running QA checks...' },
            { icon: '📝', agent: 'Sauconi', task: 'Documenting workflow...' }
        ];

        const html = activities.map(a => `
            <div class="agent-build-item">
                <div class="agent-build-icon">${a.icon}</div>
                <div class="agent-build-text">
                    <strong>${a.agent}:</strong> ${a.task}
                </div>
            </div>
        `).join('');
        $('#buildAgentActivity').html(html);
    }

    addCompletedWorkflow(workflow) {
        const html = `
            <div class="completed-workflow-item">
                <div class="completed-workflow-header">
                    <div class="completed-workflow-title">${this.escapeHtml(workflow.title)}</div>
                    <span class="completed-workflow-status">${this.escapeHtml(workflow.status)}</span>
                </div>
                <div class="completed-workflow-meta">
                    <div><i class="fas fa-clock"></i> ${workflow.created}</div>
                    <div><i class="fas fa-calendar"></i> ${workflow.schedule}</div>
                </div>
                <div class="completed-workflow-actions">
                    <button class="btn btn-sm btn-outline-primary"><i class="fas fa-eye"></i> View</button>
                    <button class="btn btn-sm btn-outline-secondary"><i class="fas fa-edit"></i> Edit</button>
                    <button class="btn btn-sm btn-outline-danger"><i class="fas fa-stop"></i> Stop</button>
                </div>
            </div>
        `;
        $('#completedWorkflowsList').prepend(html);
    }

    async loadCompletedWorkflows() {
        try {
            const response = await fetch(`${this.apiBase}/api/workflows/completed`);
            const data = await response.json();

            if (data.workflows && data.workflows.length > 0) {
                $('#completedWorkflowsList').html('');
                data.workflows.forEach(wf => this.addCompletedWorkflow(wf));
            } else {
                $('#completedWorkflowsList').html('<p class="text-muted text-center py-4">No completed workflows yet. Create your first one!</p>');
            }
        } catch (error) {
            console.error('Failed to load workflows:', error);
            $('#completedWorkflowsList').html('<p class="text-muted text-center py-4">No completed workflows yet. Create your first one!</p>');
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    bindSidebarToggle() {
        $('#sidebarToggle').on('click', () => {
            $('.sidebar').toggleClass('active');
        });
    }

    async loadDashboardMetrics() {
        try {
            const response = await fetch(`${this.apiBase}/api/metrics`);
            const data = await response.json();

            // Show detailed interaction type breakdown instead of just total
            const types = data.interaction_types || {};
            const breakdown = `
                <div style="font-size: 0.75rem; line-height: 1.4;">
                    <div><i class="fas fa-comment"></i> ${types.gemini_chats || 0} Gemini</div>
                    <div><i class="fas fa-robot"></i> ${types.ollama_chats || 0} Ollama</div>
                    <div><i class="fas fa-users"></i> ${types.collaborative_chats || 0} Collaborative</div>
                    <div><i class="fas fa-project-diagram"></i> ${types.workflow_generations || 0} Workflows</div>
                    <div><i class="fas fa-brain"></i> ${types.learning_events || 0} Learning</div>
                </div>
            `;
            $('#metricTotalChats').html(breakdown);

            $('#metricWorkflows').text(data.total_workflows || 0);
            $('#metricToday').text(data.today_chats || 0);
            $('#metricAvgTime').text(`${data.avg_response_time || 0}ms`);

        } catch (error) {
            console.error('Metrics load error:', error);
        }
    }

    async checkSystemStatus() {
        try {
            const response = await fetch(`${this.apiBase}/api/status`);
            const data = await response.json();

            $('.system-status .status-item').each((i, el) => {
                const $el = $(el);
                const text = $el.text().toLowerCase();

                if (text.includes('ollama') && data.ollama) {
                    $el.find('i').removeClass('text-danger').addClass('text-success');
                } else if (text.includes('gemini') && data.gemini) {
                    $el.find('i').removeClass('text-danger').addClass('text-success');
                } else if (text.includes('database') && data.database) {
                    $el.find('i').removeClass('text-danger').addClass('text-success');
                }
            });

        } catch (error) {
            console.error('Status check error:', error);
        }
    }

    initializeAgentHive() {
        // Will be populated by agents.js
        if (window.agentsApp) {
            window.agentsApp.renderAgentHive('#agentHive');
            window.agentsApp.renderAgentHive('#chatAgentStatus');
        }
    }

    loadFullAgentHive() {
        if (window.agentsApp) {
            window.agentsApp.renderAgentHive('#agentHiveFull');
        }
    }

    async loadLearningStats() {
        try {
            const response = await fetch(`${this.apiBase}/api/learning/stats`);
            const data = await response.json();

            const html = `
                <div class="row">
                    <div class="col-md-4">
                        <div class="metric-card">
                            <div class="metric-icon bg-gradient-purple">
                                <i class="fas fa-book"></i>
                            </div>
                            <div class="metric-info">
                                <h6>Concepts Learned</h6>
                                <h3>${data.concepts_learned || 0}</h3>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="metric-card">
                            <div class="metric-icon bg-gradient-blue">
                                <i class="fas fa-lightbulb"></i>
                            </div>
                            <div class="metric-info">
                                <h6>Reflections</h6>
                                <h3>${data.reflections || 0}</h3>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="metric-card">
                            <div class="metric-icon bg-gradient-green">
                                <i class="fas fa-chart-line"></i>
                            </div>
                            <div class="metric-info">
                                <h6>Improvement Rate</h6>
                                <h3>${data.improvement_rate || 0}%</h3>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            $('#learningStats').html(html);

        } catch (error) {
            console.error('Learning stats error:', error);
        }
    }

    startRealtimeUpdates() {
        // Update metrics every 30 seconds
        setInterval(() => {
            if (this.currentPage === 'dashboard') {
                this.loadDashboardMetrics();
            }
        }, 30000);

        // Update agent statuses every 5 seconds
        setInterval(() => {
            if (window.agentsApp) {
                window.agentsApp.fetchAgentStatuses();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize dashboard when DOM is ready
$(document).ready(() => {
    window.dashboardApp = new DashboardApp();
});
