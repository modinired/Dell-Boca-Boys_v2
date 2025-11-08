"""
Unit tests for the new workflow engine and library.
These tests validate the basic functionality of the workflow
library and composition engine without requiring network access
or external language models.
"""

from core.workflow_library import WorkflowLibrary
from core.workflow_engine import WorkflowEngine


def test_workflow_library_add_and_list():
    lib = WorkflowLibrary(db_path=':memory:')
    lib.add_template('test_template', 'A test template', '{"nodes":[]}', 'test_source')
    templates = lib.list_templates()
    names = [t['name'] for t in templates]
    assert 'test_template' in names


def test_workflow_library_duplicate_add():
    lib = WorkflowLibrary(db_path=':memory:')
    lib.add_template('dup', 'desc', '{"nodes":[]}', 'source1')
    # duplicate insert should not raise and should keep original
    lib.add_template('dup', 'desc2', '{"nodes":[1]}', 'source2')
    tpl = lib.get_template('dup')
    assert tpl['description'] == 'desc'


def test_workflow_engine_compose_error_on_missing_template():
    engine = WorkflowEngine()
    draft = {'status': 'ok', 'draft': {'name': 'MyDraft'}}
    result = engine.compose_workflow(draft, template_name='nonexistent')
    assert result['status'] == 'error'
    assert 'not found' in result['detail']


def test_workflow_engine_compose_with_skills():
    # Use engine with in‑memory library and managers
    engine = WorkflowEngine()
    draft = {'status': 'ok', 'draft': {'name': 'DraftWithProviders', 'providers': []}}
    # Compose without requested skills should succeed
    result = engine.compose_workflow(draft)
    assert result['status'] == 'ok'
