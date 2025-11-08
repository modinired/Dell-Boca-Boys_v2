"""
Dell Boca Boys V2 - Hybrid LLM Collaboration System
Enables learning collaboration between Gemini (cloud) and Qwen2.5 (local)
"""

import os
import json
import yaml
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

import google.generativeai as genai
from openai import OpenAI  # For vLLM (OpenAI-compatible)
import psycopg
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """LLM provider types"""
    GEMINI = "gemini"
    QWEN_LOCAL = "qwen_local"


class TaskComplexity(Enum):
    """Task complexity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    provider: str
    model: str
    content: str
    tokens_used: int
    response_time_ms: float
    confidence: float
    metadata: Dict[str, Any]


@dataclass
class LearningInteraction:
    """Captured interaction for learning"""
    interaction_id: str
    timestamp: datetime
    provider: str
    model: str
    prompt: str
    response: str
    tokens_used: int
    response_time_ms: float
    user_feedback: Optional[str]
    quality_score: float
    task_type: str
    complexity: str


class HybridLLMManager:
    """Manages collaboration between Gemini and local Qwen2.5"""

    def __init__(self, config_path: str = "llm-config.yml"):
        """Initialize hybrid LLM manager"""

        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Initialize Gemini
        if self.config['llm_architecture']['models']['gemini']['enabled']:
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            self.gemini_model = genai.GenerativeModel(
                self.config['llm_architecture']['models']['gemini']['model']
            )
            logger.info("Gemini model initialized")
        else:
            self.gemini_model = None
            logger.warning("Gemini disabled in configuration")

        # Initialize local Qwen via vLLM
        if self.config['llm_architecture']['models']['qwen_local']['enabled']:
            self.qwen_client = OpenAI(
                base_url=self.config['llm_architecture']['models']['qwen_local']['endpoint'],
                api_key=os.getenv('OPENAI_API_KEY', 'not-used')
            )
            logger.info("Local Qwen model initialized")
        else:
            self.qwen_client = None
            logger.warning("Local Qwen disabled in configuration")

        # Database connection for learning
        self.db_conn = psycopg.connect(
            os.getenv('DATABASE_URL'),
            row_factory=dict_row
        )

        # Initialize learning system
        self._init_learning_system()

        # Performance tracking
        self.stats = {
            'gemini_calls': 0,
            'local_calls': 0,
            'learning_examples_collected': 0,
            'fine_tuning_runs': 0
        }

    def _init_learning_system(self):
        """Initialize learning database tables"""

        with self.db_conn.cursor() as cur:
            # Create learning interactions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS llm_learning_interactions (
                    id SERIAL PRIMARY KEY,
                    interaction_id VARCHAR(255) UNIQUE,
                    timestamp TIMESTAMP NOT NULL,
                    provider VARCHAR(50),
                    model VARCHAR(100),
                    prompt TEXT NOT NULL,
                    response TEXT NOT NULL,
                    tokens_used INTEGER,
                    response_time_ms FLOAT,
                    user_feedback TEXT,
                    quality_score FLOAT,
                    task_type VARCHAR(100),
                    complexity VARCHAR(20),
                    used_for_training BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_interactions_provider
                ON llm_learning_interactions(provider);

                CREATE INDEX IF NOT EXISTS idx_interactions_task_type
                ON llm_learning_interactions(task_type);

                CREATE INDEX IF NOT EXISTS idx_interactions_quality
                ON llm_learning_interactions(quality_score);
            """)

            # Create training examples table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS llm_training_examples (
                    id SERIAL PRIMARY KEY,
                    example_id VARCHAR(255) UNIQUE,
                    source_interaction_id VARCHAR(255) REFERENCES llm_learning_interactions(interaction_id),
                    instruction TEXT NOT NULL,
                    input TEXT,
                    output TEXT NOT NULL,
                    quality_score FLOAT,
                    task_type VARCHAR(100),
                    used_in_training BOOLEAN DEFAULT FALSE,
                    training_run_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Create model performance table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS llm_model_performance (
                    id SERIAL PRIMARY KEY,
                    model_name VARCHAR(100),
                    metric_name VARCHAR(100),
                    metric_value FLOAT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_performance_model
                ON llm_model_performance(model_name, timestamp);
            """)

            self.db_conn.commit()

        logger.info("Learning system initialized")

    async def route_request(
        self,
        prompt: str,
        task_type: str,
        complexity: Optional[TaskComplexity] = None,
        prefer_quality: bool = False
    ) -> LLMResponse:
        """
        Intelligently route request to appropriate LLM

        Args:
            prompt: User prompt
            task_type: Type of task (e.g., "workflow_design", "code_generation")
            complexity: Task complexity (auto-detected if None)
            prefer_quality: Prefer Gemini even for simple tasks

        Returns:
            LLMResponse from the selected model
        """

        # Auto-detect complexity if not provided
        if complexity is None:
            complexity = self._assess_complexity(prompt, task_type)

        # Determine which model to use
        provider = self._select_provider(task_type, complexity, prefer_quality)

        # Execute with selected provider
        if provider == LLMProvider.GEMINI:
            response = await self._call_gemini(prompt, task_type)
        else:
            response = await self._call_local(prompt, task_type)

        # Store interaction for learning
        if self.config['collaborative_learning']['enabled']:
            await self._store_interaction(prompt, response, task_type, complexity.value)

        return response

    async def dual_execute(
        self,
        prompt: str,
        task_type: str
    ) -> Tuple[LLMResponse, LLMResponse, Dict[str, Any]]:
        """
        Execute with both models for comparison and learning

        Returns:
            (gemini_response, local_response, comparison_metrics)
        """

        logger.info(f"Dual execution for task: {task_type}")

        # Execute with both models in parallel
        gemini_task = self._call_gemini(prompt, task_type)
        local_task = self._call_local(prompt, task_type)

        gemini_response, local_response = await asyncio.gather(gemini_task, local_task)

        # Compare responses
        comparison = self._compare_responses(gemini_response, local_response)

        # Learn from differences
        if self.config['collaborative_learning']['enabled']:
            await self._learn_from_comparison(
                prompt, gemini_response, local_response, comparison, task_type
            )

        return gemini_response, local_response, comparison

    async def _call_gemini(self, prompt: str, task_type: str) -> LLMResponse:
        """Call Gemini API"""

        if not self.gemini_model:
            raise ValueError("Gemini is not enabled")

        start_time = datetime.now()

        try:
            # Generate content
            response = await self.gemini_model.generate_content_async(prompt)

            end_time = datetime.now()
            response_time_ms = (end_time - start_time).total_seconds() * 1000

            # Extract content
            content = response.text if hasattr(response, 'text') else str(response)

            # Count tokens (approximate)
            tokens_used = len(prompt.split()) + len(content.split())

            self.stats['gemini_calls'] += 1

            return LLMResponse(
                provider="gemini",
                model=self.config['llm_architecture']['models']['gemini']['model'],
                content=content,
                tokens_used=tokens_used,
                response_time_ms=response_time_ms,
                confidence=0.9,  # Gemini typically high confidence
                metadata={
                    'task_type': task_type,
                    'timestamp': datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            # Fallback to local model
            return await self._call_local(prompt, task_type)

    async def _call_local(self, prompt: str, task_type: str) -> LLMResponse:
        """Call local Qwen model via vLLM"""

        if not self.qwen_client:
            raise ValueError("Local Qwen is not enabled")

        start_time = datetime.now()

        try:
            # Call vLLM with OpenAI-compatible API
            response = self.qwen_client.chat.completions.create(
                model=self.config['llm_architecture']['models']['qwen_local']['model'],
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant specialized in workflow automation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config['llm_architecture']['models']['qwen_local']['max_tokens'],
                temperature=self.config['llm_architecture']['models']['qwen_local']['temperature'],
                top_p=self.config['llm_architecture']['models']['qwen_local']['top_p']
            )

            end_time = datetime.now()
            response_time_ms = (end_time - start_time).total_seconds() * 1000

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            self.stats['local_calls'] += 1

            return LLMResponse(
                provider="qwen_local",
                model=self.config['llm_architecture']['models']['qwen_local']['model'],
                content=content,
                tokens_used=tokens_used,
                response_time_ms=response_time_ms,
                confidence=0.8,  # Local model slightly lower confidence initially
                metadata={
                    'task_type': task_type,
                    'timestamp': datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Local model error: {e}")
            raise

    def _assess_complexity(self, prompt: str, task_type: str) -> TaskComplexity:
        """Assess task complexity from prompt"""

        # Simple heuristics (can be improved with ML)
        prompt_length = len(prompt.split())
        has_complex_keywords = any(
            kw in prompt.lower()
            for kw in ['integrate', 'complex', 'multiple', 'advanced', 'optimize']
        )

        if prompt_length > 200 or has_complex_keywords:
            return TaskComplexity.HIGH
        elif prompt_length > 100:
            return TaskComplexity.MEDIUM
        else:
            return TaskComplexity.LOW

    def _select_provider(
        self,
        task_type: str,
        complexity: TaskComplexity,
        prefer_quality: bool
    ) -> LLMProvider:
        """Select which LLM provider to use"""

        routing_config = self.config['collaborative_learning']['routing']

        # Check Gemini use cases
        for rule in routing_config['use_gemini_for']:
            if task_type == rule.get('task_type'):
                # Check complexity threshold
                if complexity == TaskComplexity.HIGH:
                    logger.info(f"Routing to Gemini: {task_type} (high complexity)")
                    return LLMProvider.GEMINI

        # Check budget constraints
        cost_config = self.config.get('cost_optimization', {})
        if cost_config.get('enabled'):
            if cost_config['routing_strategy']['prefer_local']:
                # Use local by default to save costs
                if not prefer_quality:
                    logger.info(f"Routing to local: {task_type} (cost optimization)")
                    return LLMProvider.QWEN_LOCAL

        # Default to local if available, otherwise Gemini
        if self.qwen_client:
            return LLMProvider.QWEN_LOCAL
        else:
            return LLMProvider.GEMINI

    def _compare_responses(
        self,
        gemini_response: LLMResponse,
        local_response: LLMResponse
    ) -> Dict[str, Any]:
        """Compare two responses"""

        return {
            'gemini_faster': gemini_response.response_time_ms < local_response.response_time_ms,
            'time_difference_ms': abs(gemini_response.response_time_ms - local_response.response_time_ms),
            'gemini_tokens': gemini_response.tokens_used,
            'local_tokens': local_response.tokens_used,
            'content_similarity': self._calculate_similarity(
                gemini_response.content,
                local_response.content
            ),
            'gemini_confidence': gemini_response.confidence,
            'local_confidence': local_response.confidence
        }

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (simple Jaccard similarity)"""

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    async def _store_interaction(
        self,
        prompt: str,
        response: LLMResponse,
        task_type: str,
        complexity: str
    ):
        """Store interaction for future learning"""

        interaction_id = f"{response.provider}_{datetime.now().timestamp()}"

        with self.db_conn.cursor() as cur:
            cur.execute("""
                INSERT INTO llm_learning_interactions (
                    interaction_id, timestamp, provider, model, prompt, response,
                    tokens_used, response_time_ms, quality_score, task_type, complexity
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                interaction_id,
                datetime.now(),
                response.provider,
                response.model,
                prompt,
                response.content,
                response.tokens_used,
                response.response_time_ms,
                response.confidence,  # Use confidence as initial quality score
                task_type,
                complexity
            ))
            self.db_conn.commit()

        self.stats['learning_examples_collected'] += 1
        logger.debug(f"Stored interaction: {interaction_id}")

    async def _learn_from_comparison(
        self,
        prompt: str,
        gemini_response: LLMResponse,
        local_response: LLMResponse,
        comparison: Dict[str, Any],
        task_type: str
    ):
        """Learn from comparing Gemini vs Local responses"""

        feedback = self.config['collaborative_learning']['dual_execution']['feedback']

        # If Gemini performed better, learn from it
        if gemini_response.confidence > local_response.confidence:
            if 'on_gemini_better' in feedback:
                # Create training example from Gemini response
                await self._create_training_example(
                    prompt, gemini_response, task_type, quality_score=gemini_response.confidence
                )
                logger.info("Created training example from Gemini (better performance)")

        # If local performed better, reinforce that pattern
        elif local_response.confidence > gemini_response.confidence:
            if 'on_local_better' in feedback:
                logger.info("Local model performed better - pattern reinforced")
                # Could reduce Gemini usage for this task type

    async def _create_training_example(
        self,
        prompt: str,
        response: LLMResponse,
        task_type: str,
        quality_score: float
    ):
        """Create a training example from an interaction"""

        # Only create examples from high-quality responses
        threshold = self.config['collaborative_learning']['knowledge_transfer']['generate_training_data']['quality_threshold']

        if quality_score < threshold:
            logger.debug(f"Skipping training example (quality {quality_score} < {threshold})")
            return

        example_id = f"example_{datetime.now().timestamp()}"

        # Format as instruction-tuning example
        instruction = f"Task: {task_type}"
        input_text = prompt
        output_text = response.content

        with self.db_conn.cursor() as cur:
            cur.execute("""
                INSERT INTO llm_training_examples (
                    example_id, instruction, input, output, quality_score, task_type
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                example_id, instruction, input_text, output_text, quality_score, task_type
            ))
            self.db_conn.commit()

        logger.info(f"Created training example: {example_id}")

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        return {
            **self.stats,
            'timestamp': datetime.now().isoformat()
        }

    async def trigger_learning_session(self):
        """Manually trigger a learning session"""

        logger.info("Starting learning session...")

        # Get high-quality training examples
        with self.db_conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM llm_training_examples
                WHERE quality_score > 0.8
                AND used_in_training = FALSE
                ORDER BY created_at DESC
                LIMIT 100
            """)
            examples = cur.fetchall()

        if not examples:
            logger.warning("No training examples available")
            return

        logger.info(f"Found {len(examples)} high-quality training examples")

        # Export to JSONL format for fine-tuning
        training_file = f"/tmp/training_data_{datetime.now().timestamp()}.jsonl"
        with open(training_file, 'w') as f:
            for example in examples:
                f.write(json.dumps({
                    "instruction": example['instruction'],
                    "input": example['input'],
                    "output": example['output']
                }) + "\n")

        logger.info(f"Training data exported to: {training_file}")

        # Mark examples as used
        example_ids = [e['example_id'] for e in examples]
        with self.db_conn.cursor() as cur:
            cur.execute("""
                UPDATE llm_training_examples
                SET used_in_training = TRUE,
                    training_run_id = %s
                WHERE example_id = ANY(%s)
            """, (f"run_{datetime.now().timestamp()}", example_ids))
            self.db_conn.commit()

        self.stats['fine_tuning_runs'] += 1

        logger.info("Learning session completed")

        return training_file


# Global instance
llm_manager: Optional[HybridLLMManager] = None


def get_llm_manager() -> HybridLLMManager:
    """Get or create global LLM manager instance"""
    global llm_manager

    if llm_manager is None:
        llm_manager = HybridLLMManager()

    return llm_manager


# Example usage
async def example_usage():
    """Example of how to use the hybrid LLM system"""

    manager = get_llm_manager()

    # Simple request (routes automatically)
    response = await manager.route_request(
        prompt="Create a simple workflow that sends an email",
        task_type="workflow_design",
        complexity=TaskComplexity.LOW
    )
    print(f"Response from {response.provider}: {response.content[:100]}...")

    # Complex request (likely routes to Gemini)
    response = await manager.route_request(
        prompt="Design a complex multi-step workflow that integrates Salesforce, sends Slack notifications, updates a database, and generates a PDF report",
        task_type="complex_workflow_design",
        complexity=TaskComplexity.HIGH,
        prefer_quality=True
    )
    print(f"Response from {response.provider}: {response.content[:100]}...")

    # Dual execution for comparison
    gemini_resp, local_resp, comparison = await manager.dual_execute(
        prompt="Generate a workflow for customer onboarding",
        task_type="workflow_design"
    )
    print(f"Comparison: {comparison}")

    # Get statistics
    stats = manager.get_stats()
    print(f"Stats: {stats}")

    # Trigger learning session
    await manager.trigger_learning_session()


if __name__ == "__main__":
    asyncio.run(example_usage())
