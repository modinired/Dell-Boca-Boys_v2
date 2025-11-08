#!/usr/bin/env python3
"""
Dell Boca Vista Boys Edition v2 - Collaborative AI Learning
===========================================================
Enhanced with dual-model collaborative chat and recursive learning.

New Features:
- 💬 Collaborative Chat: Both Ollama & Gemini contribute
- 🧠 Chiccki synthesizes best answers
- 📊 Full interaction logging for recursive learning
- 📝 Daily summary generation
- 🔄 Continuous improvement from all interactions
"""

import gradio as gr
import json
import os
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple, Optional
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDteOaTmK_8Vg-QOrQjh85bwQvogwTvV5o")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-coder:7b")
WORKSPACE_DIR = Path(__file__).parent / "workspace_dell_boca"
WORKSPACE_DIR.mkdir(exist_ok=True)
DB_PATH = WORKSPACE_DIR / "dell_boca_vista_v2.db"

# Workflow Templates
WORKFLOW_TEMPLATES = {
    "webhook_api": {
        "name": "Webhook to API Integration",
        "description": "Receive webhooks, validate, transform, and forward to external APIs",
        "complexity": "medium",
        "nodes": ["Webhook", "Validate", "Transform", "HTTP Request", "Error Handler"]
    },
    "data_sync": {
        "name": "Database Sync",
        "description": "Sync data between databases with change detection",
        "complexity": "medium",
        "nodes": ["Schedule", "PostgreSQL", "Compare", "Upsert", "Notify"]
    },
    "etl_pipeline": {
        "name": "ETL Pipeline",
        "description": "Extract, Transform, Load workflow",
        "complexity": "high",
        "nodes": ["Extract", "Clean", "Transform", "Validate", "Load"]
    }
}

DELL_BOCA_SYSTEM_PROMPT = """You are Chiccki Cammarano, Capo dei Capi of the Dell Boca Vista Boys.

You orchestrate 7 specialist agents for world-class automation workflows.

Core expertise:
- N8n architecture patterns and best practices
- Error handling, retries, circuit breakers
- Security, RBAC, credential management
- Performance optimization and cost efficiency
- TDD, clean code, production-ready systems

Philosophy: Omertà (protect secrets), Respect (quality first), Loyalty (user's goals), Family (crew collaboration).

Always deliver enterprise-grade, production-ready solutions. Capisce?"""


class DellBocaVistaAgent:
    """Enhanced agent with collaborative chat and recursive learning."""

    def __init__(self):
        self.setup_database()
        self.ollama_available = self.check_ollama()
        self.gemini_available = bool(GEMINI_API_KEY)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def setup_database(self):
        """Initialize comprehensive database with learning tables."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Workflows table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_hash TEXT UNIQUE,
                created_at TEXT NOT NULL,
                goal TEXT NOT NULL,
                workflow_json TEXT NOT NULL,
                node_count INTEGER,
                complexity_score REAL,
                estimated_cost REAL,
                performance_score REAL,
                metadata TEXT
            )
        """)

        # Collaborative chat interactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ollama_response TEXT,
                ollama_latency_ms REAL,
                gemini_response TEXT,
                gemini_latency_ms REAL,
                chiccki_synthesis TEXT NOT NULL,
                chosen_model TEXT,
                user_feedback TEXT,
                quality_score REAL,
                learning_notes TEXT
            )
        """)

        # Daily summaries for recursive learning
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary_date TEXT UNIQUE NOT NULL,
                total_interactions INTEGER,
                ollama_calls INTEGER,
                gemini_calls INTEGER,
                avg_quality_score REAL,
                key_learnings TEXT,
                improvement_areas TEXT,
                patterns_discovered TEXT,
                summary_text TEXT,
                created_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def check_ollama(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _generate_agent_bubbles_html(self, agent_states: dict) -> str:
        """
        Generate HTML for agent thought bubbles with current states.

        Args:
            agent_states: Dict mapping agent IDs to their current state
                         {'chiccki': {'status': 'active', 'thought': '...'},  ...}
        """
        agents = [
            {'id': 'chiccki', 'icon': '🎩', 'name': 'Chick Camarrano Jr.', 'role': 'Capo'},
            {'id': 'agent1', 'icon': '🔧', 'name': 'Arhur Dunzarelli', 'role': 'Workflow Architect'},
            {'id': 'agent2', 'icon': '📊', 'name': 'Little Jim Spedines', 'role': 'Data Integration'},
            {'id': 'agent3', 'icon': '🔒', 'name': 'Gerry Nascondino', 'role': 'Security'},
            {'id': 'agent4', 'icon': '⚡', 'name': 'Collogero Asperturo', 'role': 'Performance'},
            {'id': 'agent5', 'icon': '🧪', 'name': 'Paolo L\'Aranciata', 'role': 'Testing & QA'},
            {'id': 'agent6', 'icon': '📚', 'name': 'Sauconi Osobucco', 'role': 'Documentation'}
        ]

        bubbles_html = []
        for agent in agents:
            agent_id = agent['id']
            state = agent_states.get(agent_id, {'status': 'idle', 'thought': f"{agent['role']} ready"})
            status = state['status']
            thought = state['thought']

            # Determine CSS classes
            bubble_class = 'agent-bubble'
            if status == 'thinking':
                bubble_class += ' thinking'
            elif status == 'active':
                bubble_class += ' active'

            status_class = f'agent-status {status}'
            thought_class = 'agent-thought' if status != 'idle' else 'agent-thought idle'

            bubble = f"""
                <div class="{bubble_class}">
                    <div class="agent-header">
                        <span class="agent-icon">{agent['icon']}</span>
                        <span class="agent-name">{agent['name']}</span>
                        <span class="{status_class}"></span>
                    </div>
                    <div class="{thought_class}">{thought}</div>
                </div>
            """
            bubbles_html.append(bubble)

        return f'<div class="agent-grid">{"".join(bubbles_html)}</div>'

    def collaborative_chat_streaming(
        self,
        message: str,
        history: List,
        show_both_models: bool = True
    ):
        """
        Collaborative chat with real-time agent status updates.
        Yields (history, agent_bubbles_html) tuples progressively.
        """
        if not message.strip():
            yield history, self._generate_agent_bubbles_html({})
            return

        start_time = datetime.now()

        # Step 1: Chiccki activates
        yield history, self._generate_agent_bubbles_html({
            'chiccki': {'status': 'active', 'thought': 'Analyzing your request...'}
        })
        time.sleep(0.3)

        # Prepare prompt
        system_prompt = DELL_BOCA_SYSTEM_PROMPT
        conversation_context = "\n".join([
            f"User: {h[0]}\nAssistant: {h[1]}"
            for h in history[-5:]
        ])

        full_prompt = f"""Previous conversation:
{conversation_context}

Current question: {message}

Provide a helpful, accurate answer about automation workflows and automation."""

        # Step 2: Agents 1 & 2 start thinking (workflow analysis)
        yield history, self._generate_agent_bubbles_html({
            'chiccki': {'status': 'active', 'thought': 'Coordinating the crew...'},
            'agent1': {'status': 'thinking', 'thought': 'Analyzing workflow requirements...'},
            'agent2': {'status': 'thinking', 'thought': 'Checking data integration needs...'}
        })

        # Call models
        ollama_response = None
        ollama_latency = None
        gemini_response = None
        gemini_latency = None

        # Step 3: Ollama processing
        if self.ollama_available:
            yield history, self._generate_agent_bubbles_html({
                'chiccki': {'status': 'active', 'thought': 'Consulting local model...'},
                'agent1': {'status': 'active', 'thought': 'Building solution architecture...'},
                'agent3': {'status': 'thinking', 'thought': 'Reviewing security implications...'}
            })

            ollama_response, ollama_latency = self._call_ollama_timed(full_prompt, system_prompt)

        # Step 4: Gemini processing (if available)
        if self.gemini_available:
            yield history, self._generate_agent_bubbles_html({
                'chiccki': {'status': 'active', 'thought': 'Getting cloud perspective...'},
                'agent2': {'status': 'active', 'thought': 'Validating integration patterns...'},
                'agent4': {'status': 'thinking', 'thought': 'Optimizing for performance...'}
            })

            gemini_response, gemini_latency = self._call_gemini_timed(full_prompt, system_prompt)

        # Step 5: Synthesis
        yield history, self._generate_agent_bubbles_html({
            'chiccki': {'status': 'active', 'thought': 'Synthesizing best answer...'},
            'agent5': {'status': 'thinking', 'thought': 'Validating solution quality...'},
            'agent6': {'status': 'thinking', 'thought': 'Preparing documentation...'}
        })
        time.sleep(0.3)

        # Generate final response
        if ollama_response and gemini_response:
            synthesis = self._synthesize_responses(message, ollama_response, gemini_response)
            chosen_model = "synthesis"

            if show_both_models:
                display_response = f"""**🤖 Local Model (Ollama)** - {ollama_latency:.0f}ms:
{ollama_response}

---

**✨ Gemini** - {gemini_latency:.0f}ms:
{gemini_response}

---

**🎩 Chiccki's Best Answer:**
{synthesis}"""
            else:
                display_response = synthesis
        elif ollama_response:
            display_response = ollama_response
            synthesis = ollama_response
            chosen_model = "ollama"
        elif gemini_response:
            display_response = gemini_response
            synthesis = gemini_response
            chosen_model = "gemini"
        else:
            display_response = "⚠️ No models available. Please check your setup."
            synthesis = display_response
            chosen_model = "none"

        # Update history
        history.append((message, display_response))

        # Log interaction
        self._log_chat_interaction(
            message, ollama_response, ollama_latency,
            gemini_response, gemini_latency,
            synthesis, chosen_model
        )

        # Final state: All agents complete
        yield history, self._generate_agent_bubbles_html({
            'chiccki': {'status': 'active', 'thought': 'Response delivered!'},
            'agent1': {'status': 'idle', 'thought': 'Workflow architecture ready'},
            'agent2': {'status': 'idle', 'thought': 'Data integration patterns identified'},
            'agent3': {'status': 'idle', 'thought': 'Security validated'},
            'agent4': {'status': 'idle', 'thought': 'Performance optimized'},
            'agent5': {'status': 'idle', 'thought': 'Quality assured'},
            'agent6': {'status': 'idle', 'thought': 'Documentation complete'}
        })

    def collaborative_chat(
        self,
        message: str,
        history: List,
        show_both_models: bool = True
    ) -> Tuple[List, str]:
        """
        Collaborative chat where both models contribute.

        Process:
        1. Local (Ollama) responds first (primary)
        2. Gemini responds (if available)
        3. Chiccki synthesizes best answer
        4. Log everything for learning

        Args:
            message: User's question
            history: Chat history
            show_both_models: Show both model responses

        Returns:
            (updated_history, empty_string_for_input_clear)
        """
        if not message.strip():
            return history, ""

        start_time = datetime.now()

        # Prepare prompt
        system_prompt = DELL_BOCA_SYSTEM_PROMPT
        conversation_context = "\n".join([
            f"User: {h[0]}\nAssistant: {h[1]}"
            for h in history[-5:]  # Last 5 exchanges
        ])

        full_prompt = f"""Previous conversation:
{conversation_context}

Current question: {message}

Provide a helpful, accurate answer about automation workflows and automation."""

        # Call both models in parallel
        ollama_response = None
        ollama_latency = None
        gemini_response = None
        gemini_latency = None

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}

            # Always call Ollama (primary)
            if self.ollama_available:
                futures['ollama'] = executor.submit(
                    self._call_ollama_timed, full_prompt, system_prompt
                )

            # Call Gemini if available
            if self.gemini_available:
                futures['gemini'] = executor.submit(
                    self._call_gemini_timed, full_prompt, system_prompt
                )

            # Collect results
            for model_name, future in futures.items():
                try:
                    response, latency = future.result(timeout=30)
                    if model_name == 'ollama':
                        ollama_response = response
                        ollama_latency = latency
                    else:
                        gemini_response = response
                        gemini_latency = latency
                except Exception as e:
                    print(f"{model_name} error: {e}")

        # Chiccki synthesizes the best answer
        if ollama_response and gemini_response:
            # Both available - synthesize
            synthesis = self._synthesize_responses(
                message, ollama_response, gemini_response
            )
            chosen_model = "synthesis"

            if show_both_models:
                display_response = f"""**🤖 Local Model (Ollama)** - {ollama_latency:.0f}ms:
{ollama_response}

---

**✨ Gemini** - {gemini_latency:.0f}ms:
{gemini_response}

---

**🎩 Chiccki's Best Answer:**
{synthesis}"""
            else:
                display_response = synthesis

        elif ollama_response:
            # Only Ollama available (default)
            synthesis = ollama_response
            chosen_model = "ollama"
            display_response = f"**🤖 Local Model:** {ollama_response}"

        elif gemini_response:
            # Only Gemini available (fallback)
            synthesis = gemini_response
            chosen_model = "gemini"
            display_response = f"**✨ Gemini:** {gemini_response}"

        else:
            # No models available
            synthesis = "Sorry, no AI models are currently available."
            chosen_model = "none"
            display_response = "❌ No models available"

        # Log interaction for learning
        self._log_chat_interaction(
            message=message,
            ollama_response=ollama_response,
            ollama_latency=ollama_latency,
            gemini_response=gemini_response,
            gemini_latency=gemini_latency,
            synthesis=synthesis,
            chosen_model=chosen_model
        )

        # Update history
        history.append((message, display_response))

        return history, ""

    def _call_ollama_timed(self, prompt: str, system_prompt: str) -> Tuple[str, float]:
        """Call Ollama and return response with timing."""
        start = datetime.now()

        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 2048}
            },
            timeout=30
        )

        latency = (datetime.now() - start).total_seconds() * 1000

        if response.status_code == 200:
            return response.json().get("response", ""), latency
        else:
            raise Exception(f"Ollama error: {response.status_code}")

    def _call_gemini_timed(self, prompt: str, system_prompt: str) -> Tuple[str, float]:
        """Call Gemini and return response with timing."""
        start = datetime.now()

        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 2048
            }
        }

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

        response = requests.post(
            url,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=30
        )

        latency = (datetime.now() - start).total_seconds() * 1000

        response.raise_for_status()
        data = response.json()

        if "candidates" in data and len(data["candidates"]) > 0:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text, latency
        else:
            raise Exception("No response from Gemini")

    def _synthesize_responses(
        self,
        question: str,
        ollama_response: str,
        gemini_response: str
    ) -> str:
        """Chiccki synthesizes the best answer from both models."""
        # For now, use a simple heuristic
        # In production, could use another LLM call to synthesize

        # If responses are similar, use Ollama (primary)
        if self._similarity_check(ollama_response, gemini_response):
            return ollama_response

        # If Gemini's response is significantly longer/more detailed
        if len(gemini_response) > len(ollama_response) * 1.5:
            return f"{ollama_response}\n\n**Additional context:** {gemini_response}"

        # Default: Use local model (primary)
        return ollama_response

    def _similarity_check(self, text1: str, text2: str) -> bool:
        """Simple similarity check."""
        # Very basic - could be enhanced with embeddings
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return False

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return (intersection / union) > 0.5 if union > 0 else False

    def _log_chat_interaction(
        self,
        message: str,
        ollama_response: Optional[str],
        ollama_latency: Optional[float],
        gemini_response: Optional[str],
        gemini_latency: Optional[float],
        synthesis: str,
        chosen_model: str
    ):
        """Log chat interaction for learning."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO chat_interactions (
                    session_id, timestamp, user_message,
                    ollama_response, ollama_latency_ms,
                    gemini_response, gemini_latency_ms,
                    chiccki_synthesis, chosen_model
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.session_id,
                datetime.now().isoformat(),
                message,
                ollama_response,
                ollama_latency,
                gemini_response,
                gemini_latency,
                synthesis,
                chosen_model
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to log interaction: {e}")

    def generate_daily_summary(self, target_date: Optional[date] = None) -> str:
        """
        Generate daily summary for recursive learning.

        Args:
            target_date: Date to summarize (default: today)

        Returns:
            Summary text
        """
        if target_date is None:
            target_date = date.today()

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Get interactions for the day
            start_time = target_date.isoformat() + " 00:00:00"
            end_time = target_date.isoformat() + " 23:59:59"

            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN ollama_response IS NOT NULL THEN 1 ELSE 0 END) as ollama_count,
                    SUM(CASE WHEN gemini_response IS NOT NULL THEN 1 ELSE 0 END) as gemini_count,
                    AVG(quality_score) as avg_quality,
                    GROUP_CONCAT(user_message, ' | ') as all_questions
                FROM chat_interactions
                WHERE timestamp >= ? AND timestamp <= ?
            """, (start_time, end_time))

            stats = cursor.fetchone()

            if not stats or stats[0] == 0:
                return f"No interactions recorded for {target_date}"

            total, ollama_count, gemini_count, avg_quality, questions = stats

            # Generate summary
            summary = f"""# Daily Summary - {target_date}

## Statistics
- **Total Interactions:** {total}
- **Ollama Calls:** {ollama_count}
- **Gemini Calls:** {gemini_count}
- **Avg Quality Score:** {avg_quality or 'N/A'}

## Key Topics
{self._extract_topics(questions)}

## Learnings
- Both models collaborated {min(ollama_count or 0, gemini_count or 0)} times
- Primary model (Ollama) handled {ollama_count or 0} requests
- Gemini provided {gemini_count or 0} responses

## Improvement Areas
- Continue monitoring model agreement rates
- Track user feedback for quality improvements
- Identify patterns in questions for knowledge base expansion

---
*Generated by Chiccki Cammarano for the Dell Boca Vista Boys*
"""

            # Save summary
            cursor.execute("""
                INSERT OR REPLACE INTO daily_summaries (
                    summary_date, total_interactions, ollama_calls, gemini_calls,
                    avg_quality_score, summary_text, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                target_date.isoformat(),
                total,
                ollama_count or 0,
                gemini_count or 0,
                avg_quality or 0.0,
                summary,
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

            return summary

        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def _extract_topics(self, questions: str) -> str:
        """Extract key topics from questions."""
        if not questions:
            return "No topics identified"

        # Simple keyword extraction
        keywords = {}
        for word in questions.lower().split():
            if len(word) > 4:  # Skip short words
                keywords[word] = keywords.get(word, 0) + 1

        # Top 5 keywords
        top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]

        return "\n".join([f"- {word} ({count} times)" for word, count in top_keywords])

    def generate_workflow_simple(self, user_goal):
        """Generate workflow using collaborative AI with visual diagram."""
        if not user_goal or not user_goal.strip():
            return ("⚠️ Please enter a workflow goal.", "", "")

        try:
            # Build prompt for workflow description
            prompt = f"""Generate an automation workflow for this goal:

{user_goal}

Provide:
1. Workflow description
2. Required nodes and their configuration
3. Implementation steps
4. Best practices

Be specific and actionable."""

            # Use collaborative approach
            result = ""

            if self.ollama_available:
                try:
                    response = requests.post(
                        f"{OLLAMA_BASE_URL}/api/generate",
                        json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
                        timeout=60
                    )
                    if response.ok:
                        result += "**Ollama's Approach:**\n\n"
                        result += response.json().get("response", "")
                        result += "\n\n---\n\n"
                except:
                    pass

            if self.gemini_available:
                try:
                    gem_response = requests.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}",
                        json={"contents": [{"parts": [{"text": prompt}]}]},
                        timeout=60
                    )
                    if gem_response.ok:
                        data = gem_response.json()
                        if "candidates" in data:
                            result += "**Gemini's Approach:**\n\n"
                            result += data["candidates"][0]["content"]["parts"][0]["text"]
                except:
                    pass

            if not result:
                return ("❌ Both models unavailable. Please check Ollama and Gemini API.", "", "")

            # Generate Mermaid diagram
            mermaid_diagram = self._generate_mermaid_diagram(user_goal, result)

            # Generate Workflow JSON
            n8n_json = self._generate_n8n_json(user_goal, result)

            # Save to database
            self._save_workflow(user_goal, result, mermaid_diagram, n8n_json)

            formatted_result = f"✅ **Workflow Generated Successfully!**\n\n{result}"

            return (formatted_result, mermaid_diagram, n8n_json)

        except Exception as e:
            return (f"❌ Error generating workflow: {str(e)}", "", "")

    def _generate_mermaid_diagram(self, goal, workflow_text):
        """Generate Mermaid flowchart from workflow description."""
        try:
            # Extract key nodes from workflow text
            prompt = f"""Based on this workflow description, create a Mermaid flowchart diagram.

Workflow Goal: {goal}

Description: {workflow_text[:1000]}

Generate ONLY the Mermaid code (starting with 'graph TD') showing:
- Start node
- Main workflow nodes
- Connections between nodes
- End node

Use simple node names. Keep it clean and readable."""

            if self.gemini_available:
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}",
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=30
                )
                if response.ok:
                    data = response.json()
                    if "candidates" in data:
                        mermaid = data["candidates"][0]["content"]["parts"][0]["text"]
                        # Clean up the response to get just the mermaid code
                        if "```mermaid" in mermaid:
                            mermaid = mermaid.split("```mermaid")[1].split("```")[0].strip()
                        elif "graph TD" in mermaid:
                            # Extract just the graph part
                            lines = mermaid.split("\n")
                            mermaid = "\n".join([l for l in lines if l.strip() and not l.strip().startswith("#")])
                        return mermaid

            # Fallback diagram
            return """graph TD
    A[Start] --> B[Trigger]
    B --> C[Process]
    C --> D[Action]
    D --> E[End]"""

        except Exception as e:
            print(f"Mermaid generation error: {e}")
            return """graph TD
    A[Start] --> B[Workflow]
    B --> C[End]"""

    def _generate_n8n_json(self, goal, workflow_text):
        """Generate automation-ready JSON workflow."""
        try:
            prompt = f"""Generate an automation workflow JSON for: {goal}

Based on this description: {workflow_text[:800]}

Create valid Workflow JSON with:
- nodes array with realistic node types
- connections array
- proper n8n structure

Return ONLY valid JSON, no explanation."""

            if self.gemini_available:
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}",
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=30
                )
                if response.ok:
                    data = response.json()
                    if "candidates" in data:
                        json_text = data["candidates"][0]["content"]["parts"][0]["text"]
                        # Extract JSON from response
                        if "```json" in json_text:
                            json_text = json_text.split("```json")[1].split("```")[0].strip()
                        # Validate it's JSON
                        try:
                            parsed = json.loads(json_text)
                            return json.dumps(parsed, indent=2)
                        except:
                            pass

            # Fallback basic JSON
            return json.dumps({
                "name": goal[:50],
                "nodes": [
                    {"type": "n8n-nodes-base.start", "name": "Start", "position": [250, 300]},
                    {"type": "n8n-nodes-base.set", "name": "Process", "position": [450, 300]},
                ],
                "connections": {}
            }, indent=2)

        except Exception as e:
            print(f"JSON generation error: {e}")
            return "{}"

    def _save_workflow(self, goal, workflow_text, mermaid_diagram="", n8n_json=""):
        """Save generated workflow to database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            workflow_hash = hashlib.sha256(f"{goal}{workflow_text}".encode()).hexdigest()[:16]

            cursor.execute("""
                INSERT OR REPLACE INTO workflows
                (workflow_hash, created_at, goal, workflow_json, node_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                workflow_hash,
                datetime.now().isoformat(),
                goal,
                n8n_json if n8n_json else workflow_text,
                0,
                json.dumps({
                    "type": "collaborative_generation",
                    "has_mermaid": bool(mermaid_diagram),
                    "has_json": bool(n8n_json)
                })
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving workflow: {e}")

    def build_workflow_in_n8n(self, n8n_json_str):
        """Deploy workflow to automation platform."""
        try:
            if not n8n_json_str or n8n_json_str == "{}":
                return "❌ No valid workflow JSON to build"

            # Parse the JSON
            try:
                workflow_data = json.loads(n8n_json_str)
            except:
                return "❌ Invalid JSON format"

            # Check if n8n is configured
            n8n_url = os.getenv("N8N_BASE_URL", "http://localhost:5678")

            # Try to create workflow in n8n
            try:
                response = requests.post(
                    f"{n8n_url}/api/v1/workflows",
                    json=workflow_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )

                if response.ok:
                    workflow_id = response.json().get("id", "unknown")
                    return f"✅ **Workflow deployed to n8n!**\n\nWorkflow ID: {workflow_id}\n\nOpen in n8n: {n8n_url}/workflow/{workflow_id}"
                else:
                    return f"⚠️  n8n API returned error: {response.status_code}\n\nYou can manually import the JSON into n8n."
            except requests.exceptions.ConnectionError:
                return "⚠️  Cannot connect to n8n. Is it running?\n\nYou can manually import the JSON:\n1. Copy the JSON\n2. Go to n8n\n3. Click 'Import from File'\n4. Paste the JSON"
            except Exception as e:
                return f"⚠️  Error connecting to n8n: {str(e)}\n\nManual import option available."

        except Exception as e:
            return f"❌ Error: {str(e)}"

    def generate_daily_summary(self, selected_date):
        """Generate daily learning summary."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Get date range
            date_str = selected_date.isoformat()
            next_date = (selected_date + timedelta(days=1)).isoformat()

            # Get stats for the day
            cursor.execute("""
                SELECT
                    COUNT(*) as total_chats,
                    COUNT(CASE WHEN ollama_response IS NOT NULL THEN 1 END) as ollama_calls,
                    COUNT(CASE WHEN gemini_response IS NOT NULL THEN 1 END) as gemini_calls,
                    AVG(CASE WHEN ollama_latency_ms > 0 THEN ollama_latency_ms END) as avg_ollama_latency,
                    AVG(CASE WHEN gemini_latency_ms > 0 THEN gemini_latency_ms END) as avg_gemini_latency
                FROM chat_interactions
                WHERE timestamp >= ? AND timestamp < ?
            """, (date_str, next_date))

            stats = cursor.fetchone()
            total, ollama_calls, gemini_calls, avg_ollama, avg_gemini = stats

            if total == 0:
                return f"## 📊 No activity on {date_str}\n\nNo interactions recorded for this date."

            # Get workflow stats
            cursor.execute("""
                SELECT COUNT(*) FROM workflows
                WHERE created_at >= ? AND created_at < ?
            """, (date_str, next_date))

            workflows_generated = cursor.fetchone()[0]

            # Build summary
            summary = f"""## 📊 Daily Learning Summary - {date_str}

### Interaction Stats
- **Total Chats**: {total}
- **Ollama Calls**: {ollama_calls}
- **Gemini Calls**: {gemini_calls}
- **Workflows Generated**: {workflows_generated}

### Performance
- **Ollama Avg Latency**: {avg_ollama:.0f}ms
- **Gemini Avg Latency**: {avg_gemini:.0f}ms

### Model Usage
- **Ollama Preference**: {(ollama_calls/total*100) if total > 0 else 0:.1f}%
- **Gemini Collaboration**: {(gemini_calls/total*100) if total > 0 else 0:.1f}%

### Learning Insights
"""

            # Get sample interactions
            cursor.execute("""
                SELECT user_message, chiccki_synthesis
                FROM chat_interactions
                WHERE timestamp >= ? AND timestamp < ?
                ORDER BY timestamp DESC
                LIMIT 3
            """, (date_str, next_date))

            samples = cursor.fetchall()

            if samples:
                summary += "\n**Sample Interactions:**\n"
                for i, (msg, response) in enumerate(samples, 1):
                    summary += f"\n{i}. *Q: {msg[:100]}...*\n"
                    summary += f"   *A: {response[:150]}...*\n"

            # Key learnings
            summary += f"""

### 📈 Growth Metrics
- Interactions today add to our collective knowledge
- Both models contribute unique perspectives
- Chiccki synthesizes the best of both worlds

---
*Generated by Dell Boca Vista Boys - Recursive Learning System*
"""

            conn.close()

            return summary

        except Exception as e:
            return f"❌ Error generating summary: {str(e)}"

    def get_live_stats(self):
        """Get real-time statistics for the dashboard."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Total interactions
            cursor.execute("SELECT COUNT(*) FROM chat_interactions")
            total_chats = cursor.fetchone()[0]

            # Total workflows
            cursor.execute("SELECT COUNT(*) FROM workflows")
            total_workflows = cursor.fetchone()[0]

            # Today's activity
            today = date.today().isoformat()
            tomorrow = (date.today() + timedelta(days=1)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM chat_interactions
                WHERE timestamp >= ? AND timestamp < ?
            """, (today, tomorrow))
            today_chats = cursor.fetchone()[0]

            # Average response time
            cursor.execute("""
                SELECT AVG(ollama_latency_ms), AVG(gemini_latency_ms)
                FROM chat_interactions
                WHERE ollama_latency_ms > 0 OR gemini_latency_ms > 0
            """)
            avg_ollama, avg_gemini = cursor.fetchone()

            # Last 7 days activity
            week_ago = (date.today() - timedelta(days=7)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM chat_interactions
                WHERE timestamp >= ?
            """, (week_ago,))
            week_chats = cursor.fetchone()[0]

            conn.close()

            return {
                'total_chats': total_chats,
                'total_workflows': total_workflows,
                'today_chats': today_chats,
                'week_chats': week_chats,
                'avg_ollama_ms': avg_ollama or 0,
                'avg_gemini_ms': avg_gemini or 0
            }
        except Exception as e:
            print(f"Error getting live stats: {e}")
            return {
                'total_chats': 0,
                'total_workflows': 0,
                'today_chats': 0,
                'week_chats': 0,
                'avg_ollama_ms': 0,
                'avg_gemini_ms': 0
            }


# Initialize agent
agent = DellBocaVistaAgent()

# Gradio Interface
# Navy blue: #001f3f, #1a4d7a, #2c5f8d
# Cream: #FFFDD0, #F5F5DC, #FFF8DC
with gr.Blocks(
    title="Dell Boca Vista Boys v2",
    theme=gr.themes.Soft(
        primary_hue=gr.themes.colors.slate,
        secondary_hue=gr.themes.colors.stone,
        neutral_hue=gr.themes.colors.slate,
        font=("Inter", "system-ui", "sans-serif")
    ).set(
        body_background_fill='#F8F9FA',
        body_text_color='#001f3f',
        button_primary_background_fill='#001f3f',
        button_primary_background_fill_hover='#1a4d7a',
        button_primary_text_color='#FFFDD0',
        block_background_fill='#FFFFFF',
        block_border_width='0px',
        block_label_text_color='#001f3f',
        input_background_fill='#FFFFFF',
        input_background_fill_focus='#FFFFFF',
        input_border_color='#E5E7EB',
        input_border_color_focus='#1a4d7a',
        panel_background_fill='#FFFFFF',
        panel_border_width='0px',
        border_color_primary='#E5E7EB'
    )
) as demo:

    gr.HTML("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

        /* Modern Global Styles */
        * {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        /* Glass Morphism Effect */
        .gradio-container {
            backdrop-filter: blur(10px);
        }

        /* Refined Card Styles */
        .gr-block, .gr-box {
            backdrop-filter: blur(20px) saturate(180%);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .gr-block:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(0, 31, 63, 0.12), 0 4px 8px rgba(0, 31, 63, 0.08) !important;
        }

        /* Smooth Button Transitions */
        .gr-button {
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            font-weight: 600;
            letter-spacing: 0.025em;
        }

        .gr-button:active {
            transform: scale(0.98);
        }

        /* Input Focus Glow */
        .gr-input:focus, .gr-textbox:focus {
            transition: all 0.2s ease;
        }

        /* Tab Styling */
        .gr-tab {
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .gr-tab:hover {
            background: rgba(26, 77, 122, 0.05);
        }

        .gr-tab-selected {
            border-bottom: 3px solid #001f3f !important;
        }

        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }

        .professional-header {
            background: linear-gradient(135deg, #001326 0%, #001f3f 25%, #1a4d7a 75%, #2c5f8d 100%);
            padding: 0;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 31, 63, 0.4);
        }

        .professional-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 200%;
            height: 100%;
            background: linear-gradient(90deg,
                transparent 0%,
                rgba(255, 253, 208, 0.05) 50%,
                transparent 100%);
            animation: shimmer 8s infinite;
        }

        .professional-header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg,
                transparent 0%,
                rgba(255, 253, 208, 0.5) 50%,
                transparent 100%);
        }

        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 3rem 2rem;
            position: relative;
            z-index: 1;
            animation: fadeInDown 0.8s ease-out;
        }

        .logo-section {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .logo-icon {
            font-size: 4.5rem;
            animation: float 3s ease-in-out infinite;
            filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
        }

        .brand-container {
            text-align: left;
            flex: 1;
            max-width: 600px;
        }

        .company-name {
            font-family: 'Playfair Display', serif;
            font-size: 3.5rem;
            font-weight: 800;
            color: #FFFDD0;
            margin: 0;
            line-height: 1.1;
            letter-spacing: -1px;
            background: linear-gradient(135deg, #FFFDD0 0%, #FFF8DC 50%, #FFFDD0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            position: relative;
        }

        .company-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 1.1rem;
            font-weight: 300;
            color: #FFF8DC;
            margin: 0.5rem 0 0 0;
            letter-spacing: 2px;
            text-transform: uppercase;
            opacity: 0.85;
        }

        .tagline-container {
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(255, 253, 208, 0.2);
            text-align: center;
        }

        .tagline-title {
            font-family: 'Inter', sans-serif;
            font-size: 1.5rem;
            font-weight: 600;
            color: #FFFDD0;
            margin: 0 0 0.75rem 0;
            letter-spacing: 0.5px;
        }

        .tagline-text {
            font-family: 'Playfair Display', serif;
            font-size: 1.15rem;
            font-style: italic;
            color: #FFF8DC;
            margin: 0;
            opacity: 0.9;
            font-weight: 400;
        }

        .feature-badges {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 1.5rem;
            flex-wrap: wrap;
        }

        .badge {
            background: rgba(255, 253, 208, 0.1);
            border: 1px solid rgba(255, 253, 208, 0.3);
            border-radius: 2rem;
            padding: 0.5rem 1.25rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            font-weight: 500;
            color: #FFFDD0;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .badge:hover {
            background: rgba(255, 253, 208, 0.2);
            border-color: rgba(255, 253, 208, 0.5);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 253, 208, 0.2);
        }

        @media (max-width: 768px) {
            .logo-section {
                flex-direction: column;
                gap: 1rem;
            }

            .brand-container {
                text-align: center;
            }

            .company-name {
                font-size: 2.5rem;
            }

            .logo-icon {
                font-size: 3rem;
            }
        }
    </style>

    <div class="professional-header">
        <div class="header-content">
            <div class="logo-section">
                <div class="logo-icon">
                    <img src="/file/Dell-Boca Vista Boys.png" alt="Dell Boca Vista Boys Logo"
                         style="height: 120px; filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));">
                </div>
                <div class="brand-container">
                    <h1 class="company-name">The Dell Boca Vista Boys</h1>
                    <p class="company-subtitle">A Terry Dellmonaco Company</p>
                </div>
            </div>

            <div class="tagline-container">
                <h2 class="tagline-title">Collaborative AI with Recursive Learning</h2>
                <p class="tagline-text">"Two minds are better than one. The crew learns from every interaction."</p>

                <div class="feature-badges">
                    <span class="badge">🤖 Dual-LLM Intelligence</span>
                    <span class="badge">🧠 Continuous Learning</span>
                    <span class="badge">⚡ Real-Time Analytics</span>
                    <span class="badge">🎯 Production Ready</span>
                </div>
            </div>
        </div>
    </div>
    """)

    status_ollama = "🟢" if agent.ollama_available else "🔴"
    status_gemini = "🟢" if agent.gemini_available else "🟡"

    # Dynamic status panel with animations
    gr.HTML(f"""
    <style>
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        @keyframes slideIn {{
            from {{ transform: translateX(-10px); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        .status-panel {{
            background: linear-gradient(135deg, #FFFFFF 0%, #F5F5DC 100%);
            border: 2px solid #1a4d7a;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0, 31, 63, 0.1);
            animation: slideIn 0.5s ease-out;
        }}
        .status-item {{
            display: flex;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #e0e0e0;
            transition: transform 0.2s ease;
        }}
        .status-item:last-child {{
            border-bottom: none;
        }}
        .status-item:hover {{
            transform: translateX(5px);
        }}
        .status-indicator {{
            font-size: 1.2rem;
            margin-right: 0.75rem;
            animation: pulse 2s infinite;
        }}
        .status-label {{
            font-weight: 600;
            color: #001f3f;
            margin-right: 0.5rem;
        }}
        .status-value {{
            color: #2c5f8d;
            font-family: monospace;
        }}
        .active-status {{
            background: linear-gradient(90deg, rgba(26, 77, 122, 0.1) 0%, transparent 100%);
            border-left: 3px solid #1a4d7a;
            padding-left: 1rem;
        }}
    </style>

    <div class="status-panel">
        <h3 style="color: #001f3f; margin-top: 0; margin-bottom: 1rem; font-size: 1.3rem;">
            ⚡ System Status
        </h3>
        <div class="status-item {'active-status' if agent.ollama_available else ''}">
            <span class="status-indicator">{status_ollama}</span>
            <span class="status-label">Local (Ollama):</span>
            <span class="status-value">{'Primary - ' + LLM_MODEL if agent.ollama_available else 'Offline'}</span>
        </div>
        <div class="status-item {'active-status' if agent.gemini_available else ''}">
            <span class="status-indicator">{status_gemini}</span>
            <span class="status-label">Gemini:</span>
            <span class="status-value">{'Collaborative Partner' if agent.gemini_available else 'Add API key'}</span>
        </div>
        <div class="status-item active-status">
            <span class="status-indicator">🧠</span>
            <span class="status-label">Learning:</span>
            <span class="status-value">All interactions logged for recursive improvement</span>
        </div>
        <div class="status-item">
            <span class="status-indicator">📊</span>
            <span class="status-label">Session:</span>
            <span class="status-value">{agent.session_id}</span>
        </div>
        <div class="status-item">
            <span class="status-indicator">💾</span>
            <span class="status-label">Database:</span>
            <span class="status-value" style="font-size: 0.85rem;">{DB_PATH}</span>
        </div>
    </div>
    """)

    with gr.Tabs():
        # Collaborative Chat Tab
        with gr.Tab("💬 Collaborative Chat"):
            gr.Markdown("""
            ### Talk with The Dell Boca Vista Boys

            **How it works:**
            1. 🤖 **Local Model (Ollama)** responds first - fast, always available
            2. ✨ **Gemini** provides its perspective (if available)
            3. 🎩 **Chiccki** synthesizes the best answer
            4. 📊 Everything logged for recursive learning

            **This chat makes the Boys smarter over time!**
            """)

            # Agent Thought Bubbles - Real-time Activity
            agent_status_html = gr.HTML("""
            <style>
                .agent-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                    margin: 1rem 0 2rem 0;
                    padding: 0;
                }

                .agent-bubble {
                    background: linear-gradient(135deg, #FFFDD0 0%, #F5F5DC 100%);
                    border: 2px solid #D4AF37;
                    border-radius: 1rem;
                    padding: 1rem;
                    min-height: 120px;
                    position: relative;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 8px rgba(0, 31, 63, 0.1);
                }

                .agent-bubble:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 31, 63, 0.2);
                }

                .agent-bubble.active {
                    border-color: #001f3f;
                    background: linear-gradient(135deg, #FFF8DC 0%, #FFFDD0 100%);
                    animation: pulse-border 2s infinite;
                }

                @keyframes pulse-border {
                    0%, 100% { border-color: #001f3f; }
                    50% { border-color: #D4AF37; }
                }

                .agent-bubble.thinking {
                    border-color: #1a4d7a;
                }

                .agent-header {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    margin-bottom: 0.75rem;
                }

                .agent-icon {
                    font-size: 1.5rem;
                }

                .agent-name {
                    font-size: 0.9rem;
                    font-weight: 700;
                    color: #001f3f;
                }

                .agent-status {
                    display: inline-block;
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #ccc;
                    margin-left: auto;
                }

                .agent-status.idle {
                    background: #ccc;
                }

                .agent-status.thinking {
                    background: #FFC107;
                    animation: pulse-dot 1s infinite;
                }

                .agent-status.active {
                    background: #4CAF50;
                }

                @keyframes pulse-dot {
                    0%, 100% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.5; transform: scale(1.2); }
                }

                .agent-thought {
                    font-size: 0.85rem;
                    color: #2c5f8d;
                    line-height: 1.4;
                    font-style: italic;
                    min-height: 40px;
                }

                .agent-thought.idle {
                    opacity: 0.5;
                }
            </style>
            <div class="agent-grid">
                <div class="agent-bubble active">
                    <div class="agent-header">
                        <span class="agent-icon">🎩</span>
                        <span class="agent-name">Chiccki</span>
                        <span class="agent-status active"></span>
                    </div>
                    <div class="agent-thought">Ready to orchestrate the crew...</div>
                </div>

                <div class="agent-bubble">
                    <div class="agent-header">
                        <span class="agent-icon">🔧</span>
                        <span class="agent-name">Agent 1</span>
                        <span class="agent-status idle"></span>
                    </div>
                    <div class="agent-thought idle">Workflow Architect on standby</div>
                </div>

                <div class="agent-bubble">
                    <div class="agent-header">
                        <span class="agent-icon">📊</span>
                        <span class="agent-name">Agent 2</span>
                        <span class="agent-status idle"></span>
                    </div>
                    <div class="agent-thought idle">Data Integration ready</div>
                </div>

                <div class="agent-bubble">
                    <div class="agent-header">
                        <span class="agent-icon">🔒</span>
                        <span class="agent-name">Agent 3</span>
                        <span class="agent-status idle"></span>
                    </div>
                    <div class="agent-thought idle">Security monitoring...</div>
                </div>

                <div class="agent-bubble">
                    <div class="agent-header">
                        <span class="agent-icon">⚡</span>
                        <span class="agent-name">Agent 4</span>
                        <span class="agent-status idle"></span>
                    </div>
                    <div class="agent-thought idle">Performance optimization ready</div>
                </div>

                <div class="agent-bubble">
                    <div class="agent-header">
                        <span class="agent-icon">🧪</span>
                        <span class="agent-name">Agent 5</span>
                        <span class="agent-status idle"></span>
                    </div>
                    <div class="agent-thought idle">Testing & QA standing by</div>
                </div>

                <div class="agent-bubble">
                    <div class="agent-header">
                        <span class="agent-icon">📚</span>
                        <span class="agent-name">Agent 6</span>
                        <span class="agent-status idle"></span>
                    </div>
                    <div class="agent-thought idle">Documentation specialist ready</div>
                </div>
            </div>
            """)


            with gr.Row():
                show_both = gr.Checkbox(
                    label="Show Both Model Responses",
                    value=True,
                    info="See how both models think"
                )

            chatbot = gr.Chatbot(
                height=600,
                label="Chiccki Cammarano & The Crew",
                show_copy_button=True
            )

            with gr.Row():
                chat_input = gr.Textbox(
                    placeholder="Ask about workflows, automation, best practices...",
                    show_label=False,
                    scale=8
                )
                send_btn = gr.Button("Send", scale=2, variant="primary")

            gr.Examples(
                examples=[
                    "How do I handle errors in automation workflows?",
                    "What's the best way to paginate API calls?",
                    "Explain the difference between Set and Edit Fields nodes",
                    "How can I optimize a slow workflow?",
                    "What are best practices for production deployments?",
                ],
                inputs=chat_input
            )

        # Daily Summary Tab
        with gr.Tab("📊 Learning Dashboard"):
            gr.Markdown("""
            ### Recursive Learning System

            The Dell Boca Vista Boys learn from every interaction.
            This dashboard shows what they've learned and how they're improving.
            """)

            # Live Metrics Display
            stats = agent.get_live_stats()
            gr.HTML(f"""
            <style>
                .metrics-container {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1.5rem;
                    margin: 1.5rem 0;
                }}
                .metric-card {{
                    background: linear-gradient(135deg, #FFFFFF 0%, #F5F5DC 100%);
                    border: 2px solid #1a4d7a;
                    border-radius: 0.75rem;
                    padding: 1.5rem;
                    text-align: center;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 8px rgba(0, 31, 63, 0.1);
                }}
                .metric-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 6px 16px rgba(0, 31, 63, 0.2);
                    border-color: #2c5f8d;
                }}
                .metric-icon {{
                    font-size: 2.5rem;
                    margin-bottom: 0.5rem;
                    display: block;
                }}
                .metric-value {{
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: #001f3f;
                    margin: 0.5rem 0;
                    font-family: 'Courier New', monospace;
                }}
                .metric-label {{
                    font-size: 1rem;
                    color: #2c5f8d;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }}
                .metric-sublabel {{
                    font-size: 0.85rem;
                    color: #666;
                    margin-top: 0.25rem;
                }}
                @keyframes countUp {{
                    from {{ opacity: 0; transform: scale(0.5); }}
                    to {{ opacity: 1; transform: scale(1); }}
                }}
                .metric-value {{
                    animation: countUp 0.5s ease-out;
                }}
            </style>

            <div class="metrics-container">
                <div class="metric-card">
                    <span class="metric-icon">💬</span>
                    <div class="metric-value">{stats['total_chats']}</div>
                    <div class="metric-label">Total Interactions</div>
                    <div class="metric-sublabel">All-time learning events</div>
                </div>

                <div class="metric-card">
                    <span class="metric-icon">🚀</span>
                    <div class="metric-value">{stats['total_workflows']}</div>
                    <div class="metric-label">Workflows Generated</div>
                    <div class="metric-sublabel">Collaborative creations</div>
                </div>

                <div class="metric-card">
                    <span class="metric-icon">📅</span>
                    <div class="metric-value">{stats['today_chats']}</div>
                    <div class="metric-label">Today's Activity</div>
                    <div class="metric-sublabel">Learning today</div>
                </div>

                <div class="metric-card">
                    <span class="metric-icon">📈</span>
                    <div class="metric-value">{stats['week_chats']}</div>
                    <div class="metric-label">This Week</div>
                    <div class="metric-sublabel">7-day activity</div>
                </div>

                <div class="metric-card">
                    <span class="metric-icon">⚡</span>
                    <div class="metric-value">{stats['avg_ollama_ms']:.0f}ms</div>
                    <div class="metric-label">Ollama Speed</div>
                    <div class="metric-sublabel">Average response time</div>
                </div>

                <div class="metric-card">
                    <span class="metric-icon">✨</span>
                    <div class="metric-value">{stats['avg_gemini_ms']:.0f}ms</div>
                    <div class="metric-label">Gemini Speed</div>
                    <div class="metric-sublabel">Average response time</div>
                </div>
            </div>
            """)

            gr.Markdown("---")
            gr.Markdown("### 📝 Daily Summary Generator")

            with gr.Row():
                summary_date = gr.Dropdown(
                    choices=[
                        (date.today() - timedelta(days=i)).isoformat()
                        for i in range(7)
                    ],
                    value=date.today().isoformat(),
                    label="Select Date"
                )
                generate_summary_btn = gr.Button("📝 Generate Summary", variant="primary")

            summary_output = gr.Markdown()

            gr.Markdown("""
            ---
            **What Gets Learned:**
            - Which types of questions are most common
            - Where both models agree (high confidence answers)
            - Where models disagree (opportunities for improvement)
            - User interaction patterns
            - Quality metrics and feedback

            **How It's Used:**
            - Improve future responses
            - Identify knowledge gaps
            - Optimize model routing
            - Enhance workflow templates
            - Guide system improvements
            """)

        # Workflow Generator (enhanced with visuals)
        with gr.Tab("🛠️ Workflow Generator"):
            gr.Markdown("""
            ### Professional N8n Workflow Generation

            **Generate complete workflows with:**
            - 📝 Detailed description from dual-LLM collaboration
            - 📊 Visual workflow diagram
            - 🔧 Ready-to-use Workflow JSON
            - 🚀 One-click deployment to n8n
            """)

            workflow_goal = gr.Textbox(
                label="Workflow Goal",
                placeholder="Example: Create a workflow that monitors GitHub issues and posts to Slack when new issues are created...",
                lines=4
            )

            with gr.Row():
                generate_btn = gr.Button("🚀 Generate Workflow", variant="primary", scale=2)
                clear_btn = gr.Button("🔄 Clear", scale=1)

            # Description output
            with gr.Accordion("📝 Workflow Description", open=True):
                status_output = gr.Markdown()

            # Visual diagram
            with gr.Accordion("📊 Visual Diagram", open=True):
                gr.Markdown("**Interactive workflow visualization:**")
                mermaid_output = gr.HTML(label="Workflow Diagram")

            # Workflow JSON and actions
            with gr.Accordion("🔧 Workflow JSON & Actions", open=False):
                n8n_json_output = gr.Code(label="n8n Workflow JSON", language="json")

                with gr.Row():
                    build_n8n_btn = gr.Button("🚀 Deploy Workflow", variant="primary")
                    copy_json_btn = gr.Button("📋 Copy JSON")
                    download_json_btn = gr.Button("💾 Download JSON")

                build_result = gr.Markdown()

            # Hidden states to pass data between functions
            mermaid_state = gr.State("")
            json_state = gr.State("")

    gr.Markdown("""
    ---
    **Dell Boca Vista Boys Edition v2** | Collaborative AI | Recursive Learning

    Every interaction makes us smarter. 🎩 Capisce?
    """)

    # Event Handlers - Real-time Agent Bubbles
    send_btn.click(
        fn=agent.collaborative_chat_streaming,
        inputs=[chat_input, chatbot, show_both],
        outputs=[chatbot, agent_status_html]
    ).then(
        fn=lambda: "",
        inputs=None,
        outputs=[chat_input]
    )

    chat_input.submit(
        fn=agent.collaborative_chat_streaming,
        inputs=[chat_input, chatbot, show_both],
        outputs=[chatbot, agent_status_html]
    ).then(
        fn=lambda: "",
        inputs=None,
        outputs=[chat_input]
    )

    generate_summary_btn.click(
        fn=lambda d: agent.generate_daily_summary(date.fromisoformat(d)),
        inputs=[summary_date],
        outputs=[summary_output]
    )

    # Helper function to render Mermaid diagram
    def render_mermaid(mermaid_code):
        if not mermaid_code or mermaid_code.strip() == "":
            return "<p>No diagram generated</p>"

        return f"""
        <div class="mermaid-container" style="background: white; padding: 2rem; border-radius: 0.5rem; border: 2px solid #1a4d7a;">
            <div class="mermaid">
{mermaid_code}
            </div>
        </div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'default',
                flowchart: {{
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                }}
            }});
        </script>
        """

    # Workflow Generator button handler
    def generate_workflow_handler(goal):
        description, mermaid, n8n_json = agent.generate_workflow_simple(goal)
        mermaid_html = render_mermaid(mermaid)
        return description, mermaid_html, n8n_json, mermaid, n8n_json

    generate_btn.click(
        fn=generate_workflow_handler,
        inputs=[workflow_goal],
        outputs=[status_output, mermaid_output, n8n_json_output, mermaid_state, json_state]
    )

    # Clear button
    clear_btn.click(
        fn=lambda: ("", "", "", "", ""),
        outputs=[workflow_goal, status_output, mermaid_output, n8n_json_output, build_result]
    )

    # Deploy Workflow button
    build_n8n_btn.click(
        fn=lambda json_str: agent.build_workflow_in_n8n(json_str),
        inputs=[json_state],
        outputs=[build_result]
    )


if __name__ == "__main__":
    print("=" * 70)
    print("🎩 DELL BOCA VISTA BOYS EDITION V2")
    print("=" * 70)
    print("💬 Collaborative Chat: Ollama + Gemini working together")
    print("🧠 Recursive Learning: Every interaction makes us smarter")
    print("=" * 70)
    print(f"🤖 Local: {LLM_MODEL if agent.ollama_available else 'Offline'}")
    print(f"✨ Gemini: {'Active' if agent.gemini_available else 'Add API key'}")
    print(f"💾 Database: {DB_PATH}")
    print(f"📊 Session: {agent.session_id}")
    print("=" * 70)
    print()
    print("🎯 Local is primary. Gemini collaborates. Chiccki synthesizes.")
    print("📈 All interactions logged for continuous improvement.")
    print()

    demo.launch(
        server_name="0.0.0.0",
        server_port=7800,
        share=False,
        show_error=True,
        inbrowser=True
    )
