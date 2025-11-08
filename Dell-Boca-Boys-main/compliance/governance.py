#!/usr/bin/env python3
"""
Enterprise Governance Framework for Dell-Boca-Boys
Implements publication queue, reflection loops, and policy enforcement for RWCM workflows.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ProposalType(Enum):
    """Types of proposals requiring governance review."""
    WORKFLOW_CREATION = "workflow_creation"
    WORKFLOW_MODIFICATION = "workflow_modification"
    SKILL_DEPLOYMENT = "skill_deployment"
    POLICY_CHANGE = "policy_change"
    ROLE_MODIFICATION = "role_modification"
    AGENT_DEPLOYMENT = "agent_deployment"


class DecisionStatus(Enum):
    """Governance decision statuses."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"


@dataclass
class GovernancePolicy:
    """Defines a governance policy."""
    policy_id: str
    name: str
    scope: str
    auto_approve_threshold: float
    require_review_threshold: float
    auto_reject_threshold: float
    reviewer_roles: List[str]


class GovernanceFramework:
    """Enterprise governance framework for workflow management."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("governance")
        self.policies = self._load_policies()

    def _load_policies(self) -> Dict[str, GovernancePolicy]:
        """Load governance policies from configuration."""
        return {
            "workflow": GovernancePolicy(
                policy_id="workflow_gov",
                name="Workflow Governance",
                scope="workflow",
                auto_approve_threshold=0.9,
                require_review_threshold=0.7,
                auto_reject_threshold=0.3,
                reviewer_roles=["workflow_admin", "compliance_officer"]
            ),
            "skill": GovernancePolicy(
                policy_id="skill_gov",
                name="Skill Deployment Governance",
                scope="skill",
                auto_approve_threshold=0.95,
                require_review_threshold=0.8,
                auto_reject_threshold=0.5,
                reviewer_roles=["skill_admin", "security_officer"]
            ),
            "policy": GovernancePolicy(
                policy_id="policy_gov",
                name="Policy Change Governance",
                scope="policy",
                auto_approve_threshold=1.0,  # Always require review
                require_review_threshold=0.0,
                auto_reject_threshold=-1.0,
                reviewer_roles=["compliance_officer", "ciso"]
            )
        }

    def evaluate_proposal(self, proposal_type: ProposalType, proposal_body: Dict[str, Any],
                         provenance: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a proposal for governance approval."""
        risk_score = self._calculate_risk_score(proposal_type, proposal_body, provenance)
        
        policy_checks = self._run_policy_checks(proposal_type, proposal_body)
        
        policy_key = self._get_policy_key(proposal_type)
        policy = self.policies.get(policy_key)
        
        if not policy:
            return {
                "decision": DecisionStatus.REQUIRES_REVIEW.value,
                "risk_score": risk_score,
                "reason": f"No policy found for {proposal_type.value}",
                "policy_checks": policy_checks
            }
        
        # Decision logic
        if risk_score <= policy.auto_approve_threshold and all(policy_checks.values()):
            decision = DecisionStatus.APPROVED.value
            reason = "Auto-approved: low risk and passed all checks"
        elif risk_score <= policy.require_review_threshold:
            decision = DecisionStatus.REQUIRES_REVIEW.value
            reason = "Requires manual review: moderate risk"
        else:
            decision = DecisionStatus.REJECTED.value
            reason = "Auto-rejected: high risk score"
        
        return {
            "decision": decision,
            "risk_score": risk_score,
            "reason": reason,
            "policy_checks": policy_checks,
            "reviewers_required": policy.reviewer_roles if decision == DecisionStatus.REQUIRES_REVIEW.value else []
        }

    def _calculate_risk_score(self, proposal_type: ProposalType, proposal_body: Dict[str, Any],
                             provenance: Dict[str, Any]) -> float:
        """Calculate risk score (0.0 = highest risk, 1.0 = lowest risk)."""
        base_risk = 0.5
        
        # Adjust based on proposal type
        type_risks = {
            ProposalType.POLICY_CHANGE: -0.3,
            ProposalType.WORKFLOW_MODIFICATION: -0.1,
            ProposalType.SKILL_DEPLOYMENT: -0.1,
            ProposalType.AGENT_DEPLOYMENT: -0.2,
        }
        base_risk += type_risks.get(proposal_type, 0)
        
        # Adjust based on provenance
        if provenance.get("source") == "trusted_system":
            base_risk += 0.2
        if provenance.get("reviewed_by"):
            base_risk += 0.1
        if provenance.get("test_coverage", 0) > 0.8:
            base_risk += 0.1
        
        return max(0.0, min(1.0, base_risk))

    def _run_policy_checks(self, proposal_type: ProposalType, proposal_body: Dict[str, Any]) -> Dict[str, bool]:
        """Run automated policy checks."""
        checks = {
            "has_documentation": bool(proposal_body.get("description")),
            "has_owner": bool(proposal_body.get("owner_role_id")),
            "has_version": bool(proposal_body.get("version")),
            "valid_schema": self._validate_schema(proposal_body),
        }
        
        if proposal_type == ProposalType.WORKFLOW_CREATION:
            checks["has_objective"] = bool(proposal_body.get("objective"))
            checks["has_steps"] = len(proposal_body.get("steps", [])) > 0
        
        return checks

    def _validate_schema(self, proposal_body: Dict[str, Any]) -> bool:
        """Validate proposal schema."""
        required_fields = ["created_by"]
        return all(field in proposal_body for field in required_fields)

    def _get_policy_key(self, proposal_type: ProposalType) -> str:
        """Map proposal type to policy key."""
        mapping = {
            ProposalType.WORKFLOW_CREATION: "workflow",
            ProposalType.WORKFLOW_MODIFICATION: "workflow",
            ProposalType.SKILL_DEPLOYMENT: "skill",
            ProposalType.POLICY_CHANGE: "policy",
            ProposalType.ROLE_MODIFICATION: "policy",
            ProposalType.AGENT_DEPLOYMENT: "skill",
        }
        return mapping.get(proposal_type, "workflow")

    def record_decision(self, publication_id: str, decision: str, decided_by: str) -> Dict[str, Any]:
        """Record a governance decision."""
        return {
            "publication_id": publication_id,
            "decision": decision,
            "decided_by": decided_by,
            "decided_at": datetime.now().isoformat(),
            "recorded": True
        }

    def get_pending_reviews(self, reviewer_role: str) -> List[Dict[str, Any]]:
        """Get pending governance reviews for a role."""
        # In production, query publication_queue table
        return []


def create_governance_framework(config: Optional[Dict[str, Any]] = None) -> GovernanceFramework:
    """Create governance framework with configuration."""
    return GovernanceFramework(config or {})
