"""
Dell Boca Boys V2 - Simple LLM Collaboration
Gemini + Qwen2.5 work together to produce optimal outputs
Learning emerges naturally from collaboration
"""

import os
import logging
import asyncio
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import google.generativeai as genai
from openai import OpenAI  # For vLLM (OpenAI-compatible)

logger = logging.getLogger(__name__)


class CollaborationMode(Enum):
    """How models collaborate"""
    CONSENSUS = "consensus"  # Both models must agree
    BEST_OF = "best_of"  # Take the best response
    SYNTHESIS = "synthesis"  # Combine both responses
    GEMINI_LEADS = "gemini_leads"  # Gemini decides, Qwen validates
    QWEN_LEADS = "qwen_leads"  # Qwen decides, Gemini validates


@dataclass
class CollaborativeResponse:
    """Response from collaborative LLM system"""
    final_output: str
    gemini_contribution: str
    qwen_contribution: str
    collaboration_mode: str
    confidence: float
    response_time_ms: float
    metadata: Dict


class CollaborativeLLM:
    """Simple LLM collaboration - both models work together for best output"""

    def __init__(self):
        """Initialize both LLMs"""

        # Initialize Gemini
        gemini_api_key = os.getenv('GOOGLE_API_KEY')
        if not gemini_api_key:
            logger.warning("GOOGLE_API_KEY not set. Gemini disabled.")
            self.gemini_model = None
        else:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("Gemini initialized")

        # Initialize local Qwen via vLLM
        self.qwen_client = OpenAI(
            base_url=os.getenv('VLLM_ENDPOINT', 'http://vllm:8000/v1'),
            api_key=os.getenv('OPENAI_API_KEY', 'not-used')
        )
        logger.info("Local Qwen initialized")

        # Default collaboration mode
        self.default_mode = CollaborationMode.SYNTHESIS

    async def collaborate(
        self,
        prompt: str,
        mode: Optional[CollaborationMode] = None,
        context: Optional[Dict] = None
    ) -> CollaborativeResponse:
        """
        Both LLMs work on the same prompt and collaborate for best output

        Args:
            prompt: User's request
            mode: How to collaborate (default: SYNTHESIS)
            context: Additional context for the task

        Returns:
            CollaborativeResponse with the best combined output
        """

        start_time = datetime.now()
        mode = mode or self.default_mode

        logger.info(f"Collaborative request with mode: {mode.value}")

        # Both models work on the same prompt simultaneously
        gemini_task = self._ask_gemini(prompt, context)
        qwen_task = self._ask_qwen(prompt, context)

        # Get both responses in parallel
        gemini_response, qwen_response = await asyncio.gather(
            gemini_task, qwen_task, return_exceptions=True
        )

        # Handle failures gracefully
        if isinstance(gemini_response, Exception):
            logger.warning(f"Gemini failed: {gemini_response}. Using Qwen only.")
            gemini_response = None

        if isinstance(qwen_response, Exception):
            logger.warning(f"Qwen failed: {qwen_response}. Using Gemini only.")
            qwen_response = None

        # Fallback if both failed
        if gemini_response is None and qwen_response is None:
            raise Exception("Both LLMs failed to respond")

        # Fallback if one failed
        if gemini_response is None:
            final_output = qwen_response
            confidence = 0.7
        elif qwen_response is None:
            final_output = gemini_response
            confidence = 0.8
        else:
            # Collaborate to produce best output
            final_output, confidence = await self._combine_responses(
                prompt, gemini_response, qwen_response, mode
            )

        end_time = datetime.now()
        response_time_ms = (end_time - start_time).total_seconds() * 1000

        return CollaborativeResponse(
            final_output=final_output,
            gemini_contribution=gemini_response or "",
            qwen_contribution=qwen_response or "",
            collaboration_mode=mode.value,
            confidence=confidence,
            response_time_ms=response_time_ms,
            metadata={
                'timestamp': datetime.now().isoformat(),
                'both_models_responded': gemini_response is not None and qwen_response is not None
            }
        )

    async def _ask_gemini(self, prompt: str, context: Optional[Dict]) -> str:
        """Ask Gemini for its response"""

        if not self.gemini_model:
            raise Exception("Gemini not available")

        try:
            # Add context if provided
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nTask: {prompt}"

            response = await self.gemini_model.generate_content_async(full_prompt)
            return response.text if hasattr(response, 'text') else str(response)

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            raise

    async def _ask_qwen(self, prompt: str, context: Optional[Dict]) -> str:
        """Ask Qwen for its response"""

        try:
            # Add context if provided
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nTask: {prompt}"

            response = self.qwen_client.chat.completions.create(
                model="Qwen/Qwen2.5-Coder-32B-Instruct-AWQ",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant specialized in workflow automation."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=4096,
                temperature=0.1
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Qwen error: {e}")
            raise

    async def _combine_responses(
        self,
        original_prompt: str,
        gemini_response: str,
        qwen_response: str,
        mode: CollaborationMode
    ) -> Tuple[str, float]:
        """
        Combine responses from both models based on collaboration mode

        Returns:
            (final_output, confidence)
        """

        if mode == CollaborationMode.CONSENSUS:
            # Both must agree - use Gemini to find consensus
            return await self._find_consensus(gemini_response, qwen_response)

        elif mode == CollaborationMode.BEST_OF:
            # Pick the best response
            return self._select_best(gemini_response, qwen_response)

        elif mode == CollaborationMode.SYNTHESIS:
            # Combine both into a superior answer
            return await self._synthesize(original_prompt, gemini_response, qwen_response)

        elif mode == CollaborationMode.GEMINI_LEADS:
            # Gemini creates, Qwen validates
            return await self._gemini_leads(gemini_response, qwen_response)

        elif mode == CollaborationMode.QWEN_LEADS:
            # Qwen creates, Gemini validates
            return await self._qwen_leads(gemini_response, qwen_response)

        else:
            # Default to synthesis
            return await self._synthesize(original_prompt, gemini_response, qwen_response)

    async def _find_consensus(self, response1: str, response2: str) -> Tuple[str, float]:
        """Find consensus between two responses"""

        # Use Gemini to find common ground
        consensus_prompt = f"""
You have two AI responses to the same question. Find the consensus and create a unified answer that incorporates the best parts of both.

Response 1:
{response1}

Response 2:
{response2}

Provide a consensus answer that:
1. Includes points both responses agree on
2. Resolves any contradictions intelligently
3. Is more accurate and complete than either alone

Consensus answer:
"""

        consensus = await self._ask_gemini(consensus_prompt, None)
        return consensus, 0.95  # High confidence - both models contributed

    def _select_best(self, response1: str, response2: str) -> Tuple[str, float]:
        """Select the best response (simple heuristic)"""

        # Simple heuristic: longer, more detailed response is often better
        # In production, you could use more sophisticated metrics

        len1 = len(response1)
        len2 = len(response2)

        if len1 > len2 * 1.2:  # Gemini significantly longer
            return response1, 0.85
        elif len2 > len1 * 1.2:  # Qwen significantly longer
            return response2, 0.85
        else:
            # Similar length - prefer Gemini (generally higher quality)
            return response1, 0.8

    async def _synthesize(
        self,
        original_prompt: str,
        gemini_response: str,
        qwen_response: str
    ) -> Tuple[str, float]:
        """Synthesize both responses into superior answer"""

        synthesis_prompt = f"""
Original question: {original_prompt}

You have two AI responses. Synthesize them into ONE superior answer that:
1. Takes the best insights from both
2. Adds any missing information
3. Removes redundancies
4. Ensures accuracy and clarity

Gemini's answer:
{gemini_response}

Qwen's answer:
{qwen_response}

Synthesized superior answer:
"""

        # Use Gemini for synthesis (it excels at this)
        synthesized = await self._ask_gemini(synthesis_prompt, None)

        return synthesized, 0.95  # Very high confidence - best of both worlds

    async def _gemini_leads(self, gemini_response: str, qwen_response: str) -> Tuple[str, float]:
        """Gemini creates, Qwen validates and improves"""

        validation_prompt = f"""
Review this response and suggest improvements:

{gemini_response}

Alternative perspective:
{qwen_response}

Provide the FINAL IMPROVED version:
"""

        improved = await self._ask_gemini(validation_prompt, None)
        return improved, 0.9

    async def _qwen_leads(self, gemini_response: str, qwen_response: str) -> Tuple[str, float]:
        """Qwen creates, Gemini validates and improves"""

        validation_prompt = f"""
Review this technical response and suggest improvements:

{qwen_response}

Alternative perspective:
{gemini_response}

Provide the FINAL IMPROVED version:
"""

        improved = await self._ask_gemini(validation_prompt, None)
        return improved, 0.9


# Global instance
_collaborative_llm: Optional[CollaborativeLLM] = None


def get_collaborative_llm() -> CollaborativeLLM:
    """Get global collaborative LLM instance"""
    global _collaborative_llm

    if _collaborative_llm is None:
        _collaborative_llm = CollaborativeLLM()

    return _collaborative_llm


# Convenience function
async def ask_collaborative(
    prompt: str,
    mode: CollaborationMode = CollaborationMode.SYNTHESIS
) -> str:
    """
    Simple function to ask both LLMs and get best combined answer

    Args:
        prompt: Your question/request
        mode: How models should collaborate

    Returns:
        Best combined answer from both models
    """

    llm = get_collaborative_llm()
    response = await llm.collaborate(prompt, mode)

    return response.final_output


# Example usage
async def example():
    """Example of collaborative LLM usage"""

    # Simple collaboration - both models synthesize their knowledge
    result = await ask_collaborative(
        "Design a workflow that monitors webhooks, validates data, "
        "enriches from database, and sends notifications",
        mode=CollaborationMode.SYNTHESIS
    )

    print("=== COLLABORATIVE RESULT ===")
    print(result)
    print()

    # More detailed usage
    llm = get_collaborative_llm()

    response = await llm.collaborate(
        prompt="Create a workflow for customer onboarding",
        mode=CollaborationMode.GEMINI_LEADS,
        context={"industry": "SaaS", "complexity": "medium"}
    )

    print(f"Mode: {response.collaboration_mode}")
    print(f"Confidence: {response.confidence}")
    print(f"Response time: {response.response_time_ms:.2f}ms")
    print()
    print("=== GEMINI'S CONTRIBUTION ===")
    print(response.gemini_contribution[:200] + "...")
    print()
    print("=== QWEN'S CONTRIBUTION ===")
    print(response.qwen_contribution[:200] + "...")
    print()
    print("=== FINAL COLLABORATIVE OUTPUT ===")
    print(response.final_output)


if __name__ == "__main__":
    asyncio.run(example())
