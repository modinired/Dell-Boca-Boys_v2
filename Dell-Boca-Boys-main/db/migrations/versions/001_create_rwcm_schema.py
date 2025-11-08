"""Create RWCM Schema with 17 tables for enterprise workflow orchestration

Revision ID: 001_rwcm_schema
Revises:
Create Date: 2025-11-07 12:00:00

This migration creates the complete SRC-RWCM (Symbiotic Recursive Cognition -
Role Workflow Capability Mapping) database schema with support for:
- Roles and hierarchical organization
- Skills and capability mapping
- Workflows with trigger definitions
- Step-based action orchestration
- Agent assignment and execution
- Reflection and learning loops
- Publication queue for governance
- Policy enforcement
- Ontology and knowledge graphs
- Event bus for asynchronous messaging
- Schema registry for data validation
- RLM embeddings for semantic search (pgvector)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001_rwcm_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all RWCM tables."""

    # Enable pgvector extension for RLM embeddings
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # 1. ROLES - Hierarchical organizational structure
    op.create_table(
        'role',
        sa.Column('role_id', sa.String(32), primary_key=True),
        sa.Column('role_title', sa.String(128), nullable=False),
        sa.Column('department', sa.String(64), nullable=False),
        sa.Column('hierarchy_level', sa.String(8), nullable=False),
        sa.Column('supervises_role_id', sa.String(32), nullable=True),
        sa.Column('role_type', sa.String(16), nullable=False, server_default='human'),
        sa.Column('capability_vector', sa.LargeBinary, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(64), nullable=False, server_default='system'),
        sa.Column('updated_by', sa.String(64), nullable=False, server_default='system'),
        sa.ForeignKeyConstraint(['supervises_role_id'], ['role.role_id'], name='fk_role_supervises'),
    )
    op.create_index('ix_role_dept', 'role', ['department'])

    # 2. SKILLS - Executable capabilities and skill nodes
    op.create_table(
        'skill_node',
        sa.Column('skill_id', sa.String(32), primary_key=True),
        sa.Column('skill_name', sa.String(128), nullable=False),
        sa.Column('category', sa.String(64), nullable=False),
        sa.Column('signature', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('runtime_binding', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('version', sa.String(24), nullable=False),
        sa.Column('stability_tier', sa.String(16), nullable=False, server_default='ga'),
        sa.Column('owner_role_id', sa.String(32), nullable=False),
        sa.Column('is_generator', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(64), nullable=False),
        sa.Column('updated_by', sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(['owner_role_id'], ['role.role_id'], name='fk_skill_owner_role'),
    )
    op.create_index('ux_skill_name_version', 'skill_node', ['skill_name', 'version'], unique=True)

    # 3. ROLE-SKILL MAPPING - Many-to-many relationship with permissions
    op.create_table(
        'role_skill_map',
        sa.Column('role_id', sa.String(32), nullable=False),
        sa.Column('skill_id', sa.String(32), nullable=False),
        sa.Column('permission', sa.String(16), nullable=False, server_default='use'),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(64), nullable=False, server_default='system'),
        sa.Column('updated_by', sa.String(64), nullable=False, server_default='system'),
        sa.PrimaryKeyConstraint('role_id', 'skill_id'),
        sa.ForeignKeyConstraint(['role_id'], ['role.role_id'], name='fk_rsm_role'),
        sa.ForeignKeyConstraint(['skill_id'], ['skill_node.skill_id'], name='fk_rsm_skill'),
    )

    # 4. WORKFLOWS - Versioned workflow definitions with genome
    op.create_table(
        'workflow',
        sa.Column('workflow_id', sa.String(32), primary_key=True),
        sa.Column('workflow_name', sa.String(128), nullable=False),
        sa.Column('objective', sa.Text, nullable=False),
        sa.Column('constraints', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('responsible_role_id', sa.String(32), nullable=False),
        sa.Column('genome', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(16), nullable=False, server_default='active'),
        sa.Column('version', sa.String(24), nullable=False),
        sa.Column('lineage', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(64), nullable=False),
        sa.Column('updated_by', sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(['responsible_role_id'], ['role.role_id'], name='fk_wf_role'),
    )
    op.create_index('ux_workflow_name_version', 'workflow', ['workflow_name', 'version'], unique=True)

    # 5. TRIGGER DEFINITIONS - Workflow activation triggers
    op.create_table(
        'trigger_def',
        sa.Column('trigger_id', sa.String(32), primary_key=True),
        sa.Column('workflow_id', sa.String(32), nullable=False),
        sa.Column('trigger_type', sa.String(24), nullable=False),
        sa.Column('selector', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(64), nullable=False, server_default='system'),
        sa.Column('updated_by', sa.String(64), nullable=False, server_default='system'),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflow.workflow_id'], name='fk_trig_wf'),
    )

    # 6. STEP ACTIONS - Workflow step definitions
    op.create_table(
        'step_action',
        sa.Column('step_id', sa.String(32), primary_key=True),
        sa.Column('workflow_id', sa.String(32), nullable=False),
        sa.Column('sequence', sa.Integer, nullable=False),
        sa.Column('action_type', sa.String(24), nullable=False),
        sa.Column('skill_id', sa.String(32), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('next_step_logic', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('timeout_ms', sa.Integer, nullable=False, server_default='300000'),
        sa.Column('retries', sa.Integer, nullable=False, server_default='2'),
        sa.Column('idempotency_key', sa.String(64), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(64), nullable=False),
        sa.Column('updated_by', sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflow.workflow_id'], name='fk_step_wf'),
        sa.ForeignKeyConstraint(['skill_id'], ['skill_node.skill_id'], name='fk_step_skill'),
    )
    op.create_index('ix_step_wf_sequence', 'step_action', ['workflow_id', 'sequence'])

    # 7. AGENTS - Execution agents with policy profiles
    op.create_table(
        'agent',
        sa.Column('agent_id', sa.String(32), primary_key=True),
        sa.Column('agent_name', sa.String(128), nullable=False),
        sa.Column('agent_type', sa.String(24), nullable=False),
        sa.Column('role_id', sa.String(32), nullable=False),
        sa.Column('policy_profile', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('embedding', sa.LargeBinary, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(64), nullable=False),
        sa.Column('updated_by', sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['role.role_id'], name='fk_agent_role'),
    )

    # 8. RUN EPISODES - Workflow execution instances
    op.create_table(
        'run_episode',
        sa.Column('episode_id', sa.String(36), primary_key=True),
        sa.Column('workflow_id', sa.String(32), nullable=False),
        sa.Column('trigger_id', sa.String(32), nullable=True),
        sa.Column('initiator_id', sa.String(32), nullable=True),
        sa.Column('started_at', sa.TIMESTAMP, nullable=False),
        sa.Column('ended_at', sa.TIMESTAMP, nullable=True),
        sa.Column('outcome', sa.String(24), nullable=False, server_default='running'),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('context_hash', sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflow.workflow_id'], name='fk_episode_wf'),
    )
    op.create_index('ix_episode_wf_time', 'run_episode', ['workflow_id', sa.text('started_at DESC')])

    # 9. STEP RUNS - Individual step execution records
    op.create_table(
        'step_run',
        sa.Column('step_run_id', sa.String(36), primary_key=True),
        sa.Column('episode_id', sa.String(36), nullable=False),
        sa.Column('step_id', sa.String(32), nullable=False),
        sa.Column('agent_id', sa.String(32), nullable=False),
        sa.Column('started_at', sa.TIMESTAMP, nullable=False),
        sa.Column('ended_at', sa.TIMESTAMP, nullable=True),
        sa.Column('status', sa.String(24), nullable=False),
        sa.Column('input', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('output', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('telemetry', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(['episode_id'], ['run_episode.episode_id'], name='fk_sr_episode'),
        sa.ForeignKeyConstraint(['step_id'], ['step_action.step_id'], name='fk_sr_step'),
        sa.ForeignKeyConstraint(['agent_id'], ['agent.agent_id'], name='fk_sr_agent'),
    )

    # 10. REFLECTION LOG - Learning and improvement insights
    op.create_table(
        'reflection_log',
        sa.Column('reflection_id', sa.String(36), primary_key=True),
        sa.Column('source_type', sa.String(24), nullable=False),
        sa.Column('source_id', sa.String(36), nullable=False),
        sa.Column('insight_type', sa.String(32), nullable=False),
        sa.Column('insight', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('learning_signal', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('proposed_actions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('reviewer_role_id', sa.String(32), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('approved_at', sa.TIMESTAMP, nullable=True),
        sa.Column('status', sa.String(16), nullable=False, server_default='recorded'),
    )
    op.create_index('ix_reflection_status', 'reflection_log', [sa.text('status'), sa.text('created_at DESC')])

    # 11. PUBLICATION QUEUE - Governance and approval workflow
    op.create_table(
        'publication_queue',
        sa.Column('publication_id', sa.String(36), primary_key=True),
        sa.Column('proposal_type', sa.String(24), nullable=False),
        sa.Column('proposal_body', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('provenance', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('risk_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('policy_checks', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('decision', sa.String(16), nullable=False, server_default='pending'),
        sa.Column('decided_by', sa.String(64), nullable=True),
        sa.Column('decided_at', sa.TIMESTAMP, nullable=True),
        sa.Column('published_object_id', sa.String(32), nullable=True),
    )

    # 12. POLICY - Declarative policy definitions
    op.create_table(
        'policy',
        sa.Column('policy_id', sa.String(32), primary_key=True),
        sa.Column('policy_name', sa.String(128), nullable=False),
        sa.Column('scope', sa.String(24), nullable=False),
        sa.Column('spec', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('owner_role_id', sa.String(32), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(64), nullable=False, server_default='system'),
        sa.Column('updated_by', sa.String(64), nullable=False, server_default='system'),
        sa.ForeignKeyConstraint(['owner_role_id'], ['role.role_id'], name='fk_policy_owner_role'),
    )

    # 13. ONTOLOGY NODE - Knowledge graph and taxonomy
    op.create_table(
        'ontology_node',
        sa.Column('node_id', sa.String(32), primary_key=True),
        sa.Column('node_type', sa.String(24), nullable=False),
        sa.Column('label', sa.String(128), nullable=False),
        sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('parent_id', sa.String(32), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(64), nullable=False, server_default='system'),
        sa.Column('updated_by', sa.String(64), nullable=False, server_default='system'),
    )

    # 14. EVENT BUS - Asynchronous event messaging
    op.create_table(
        'event_bus',
        sa.Column('event_id', sa.String(36), primary_key=True),
        sa.Column('topic', sa.String(128), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('produced_at', sa.TIMESTAMP, nullable=False),
        sa.Column('producer_id', sa.String(64), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(64), nullable=False, server_default='system'),
    )
    op.create_index('ix_event_topic_time', 'event_bus', ['topic', sa.text('produced_at DESC')])

    # 15. SCHEMA REGISTRY - Data validation schemas
    op.create_table(
        'schema_registry',
        sa.Column('subject', sa.String(128), primary_key=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('format', sa.String(16), nullable=False),
        sa.Column('schema', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('compatibility', sa.String(16), nullable=False, server_default='backward'),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("format IN ('json','avro')", name='ck_schema_format'),
    )

    # 16. RLM EMBEDDINGS - Semantic embeddings with pgvector
    op.execute("""
        CREATE TABLE rlm_embedding (
            emb_id VARCHAR(36) PRIMARY KEY,
            source_type VARCHAR(24) NOT NULL,
            source_id VARCHAR(36) NOT NULL,
            vector VECTOR(1024) NOT NULL,
            metadata JSONB NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.create_index('ix_rlm_stype', 'rlm_embedding', ['source_type'])


def downgrade() -> None:
    """Drop all RWCM tables in reverse order."""
    op.drop_table('rlm_embedding')
    op.drop_table('schema_registry')
    op.drop_table('event_bus')
    op.drop_table('ontology_node')
    op.drop_table('policy')
    op.drop_table('publication_queue')
    op.drop_table('reflection_log')
    op.drop_table('step_run')
    op.drop_table('run_episode')
    op.drop_table('agent')
    op.drop_table('step_action')
    op.drop_table('trigger_def')
    op.drop_table('workflow')
    op.drop_table('role_skill_map')
    op.drop_table('skill_node')
    op.drop_table('role')

    op.execute('DROP EXTENSION IF EXISTS vector')
