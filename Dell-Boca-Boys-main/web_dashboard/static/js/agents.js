/**
 * Dell Boca Vista Boys - Agents JavaScript
 * Real-time agent status and thought bubbles
 */

class AgentsApp {
    constructor() {
        this.agents = [
            {
                id: 'chiccki',
                icon: '🎩',
                name: 'Chick Camarrano Jr.',
                role: 'Capo',
                status: 'idle',
                thought: 'Ready to orchestrate the crew'
            },
            {
                id: 'agent1',
                icon: '🔧',
                name: 'Arhur Dunzarelli',
                role: 'Workflow Architect',
                status: 'idle',
                thought: 'Workflow architecture ready'
            },
            {
                id: 'agent2',
                icon: '📊',
                name: 'Little Jim Spedines',
                role: 'Data Integration',
                status: 'idle',
                thought: 'Data integration patterns loaded'
            },
            {
                id: 'agent3',
                icon: '🔒',
                name: 'Gerry Nascondino',
                role: 'Security',
                status: 'idle',
                thought: 'Security protocols active'
            },
            {
                id: 'agent4',
                icon: '⚡',
                name: 'Collogero Asperturo',
                role: 'Performance',
                status: 'idle',
                thought: 'Performance optimization standby'
            },
            {
                id: 'agent5',
                icon: '🧪',
                name: 'Paolo L\'Aranciata',
                role: 'Testing & QA',
                status: 'idle',
                thought: 'Quality assurance ready'
            },
            {
                id: 'agent6',
                icon: '📚',
                name: 'Sauconi Osobucco',
                role: 'Documentation',
                status: 'idle',
                thought: 'Documentation systems ready'
            }
        ];

        this.apiBase = '';
        this.updateInterval = null;
    }

    renderAgentHive(targetSelector) {
        const container = $(targetSelector);
        if (!container.length) return;

        container.empty();

        this.agents.forEach(agent => {
            const bubbleHtml = this.createAgentBubble(agent);
            container.append(bubbleHtml);
        });
    }

    createAgentBubble(agent) {
        const statusClass = agent.status === 'idle' ? 'idle' :
                           agent.status === 'thinking' ? 'thinking' : 'active';

        return `
            <div class="agent-bubble ${agent.status}" data-agent-id="${agent.id}">
                <div class="agent-header">
                    <span class="agent-icon">${agent.icon}</span>
                    <span class="agent-name">${agent.name}</span>
                    <span class="agent-status ${statusClass}"></span>
                </div>
                <div class="agent-role">${agent.role}</div>
                <div class="agent-thought ${statusClass}">
                    ${agent.thought}
                </div>
            </div>
        `;
    }

    updateAgentStates(states) {
        // states is an object like:
        // { 'chiccki': { status: 'active', thought: '...' }, ... }

        Object.keys(states).forEach(agentId => {
            const state = states[agentId];
            const agent = this.agents.find(a => a.id === agentId);

            if (agent) {
                agent.status = state.status;
                agent.thought = state.thought;
            }

            // Update UI
            this.updateAgentBubbleUI(agentId, state);
        });
    }

    updateAgentBubbleUI(agentId, state) {
        const bubble = $(`.agent-bubble[data-agent-id="${agentId}"]`);
        if (!bubble.length) return;

        // Update status class on bubble
        bubble.removeClass('idle thinking active').addClass(state.status);

        // Update status indicator
        const statusIndicator = bubble.find('.agent-status');
        statusIndicator.removeClass('idle thinking active').addClass(state.status);

        // Update thought
        const thoughtEl = bubble.find('.agent-thought');
        thoughtEl.removeClass('idle thinking active').addClass(state.status);
        thoughtEl.text(state.thought);
    }

    async fetchAgentStatuses() {
        try {
            const response = await fetch(`${this.apiBase}/api/agents/status`);
            const data = await response.json();

            if (data.agent_states) {
                this.updateAgentStates(data.agent_states);
            }
        } catch (error) {
            console.error('Failed to fetch agent statuses:', error);
        }
    }

    simulateAgentActivity(agentId, duration = 3000) {
        const agent = this.agents.find(a => a.id === agentId);
        if (!agent) return;

        // Set to thinking
        agent.status = 'thinking';
        agent.thought = 'Processing...';
        this.updateAgentBubbleUI(agentId, agent);

        // After duration/2, set to active
        setTimeout(() => {
            agent.status = 'active';
            agent.thought = 'Working on it...';
            this.updateAgentBubbleUI(agentId, agent);
        }, duration / 2);

        // After duration, back to idle
        setTimeout(() => {
            agent.status = 'idle';
            agent.thought = `${agent.role} complete`;
            this.updateAgentBubbleUI(agentId, agent);
        }, duration);
    }

    startRealtimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        this.updateInterval = setInterval(() => {
            this.fetchAgentStatuses();
        }, 3000);
    }

    stopRealtimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    getAgentById(id) {
        return this.agents.find(a => a.id === id);
    }

    getAllAgents() {
        return this.agents;
    }

    resetAllAgents() {
        this.agents.forEach(agent => {
            agent.status = 'idle';
            agent.thought = `${agent.role} ready`;
            this.updateAgentBubbleUI(agent.id, agent);
        });
    }
}

// Initialize agents app when DOM is ready
$(document).ready(() => {
    window.agentsApp = new AgentsApp();

    // Render initial agent hive
    window.agentsApp.renderAgentHive('#agentHive');
    window.agentsApp.renderAgentHive('#chatAgentStatus');
    window.agentsApp.renderAgentHive('#agentHiveFull');

    // Start real-time updates
    // window.agentsApp.startRealtimeUpdates();

    console.log('✅ Agents app initialized');
});
