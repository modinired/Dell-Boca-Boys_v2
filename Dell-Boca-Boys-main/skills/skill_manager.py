#!/usr/bin/env python3
"""
Enterprise Skills Manager for Dell-Boca-Boys
Manages 83+ enterprise skills across 20+ domains
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

class SkillManager:
    """Manages enterprise skill discovery, validation, and execution."""
    
    def __init__(self, registry_path: str = "./skills/registry"):
        self.registry_path = Path(registry_path)
        self.logger = logging.getLogger("skill_manager")
        self.skills_cache = {}
        self._load_all_skills()
    
    def _load_all_skills(self):
        """Load all skill definitions from registry."""
        for skill_file in self.registry_path.glob("*.json"):
            domain = skill_file.stem
            try:
                with open(skill_file) as f:
                    skills = json.load(f)
                    self.skills_cache[domain] = skills
                    self.logger.info(f"Loaded {len(skills)} skills from {domain}")
            except Exception as e:
                self.logger.error(f"Failed to load {skill_file}: {e}")
    
    def list_domains(self) -> List[str]:
        """List all available skill domains."""
        return list(self.skills_cache.keys())
    
    def list_skills(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """List skills, optionally filtered by domain."""
        if domain:
            return self.skills_cache.get(domain, [])
        all_skills = []
        for skills in self.skills_cache.values():
            all_skills.extend(skills)
        return all_skills
    
    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific skill by ID."""
        for skills in self.skills_cache.values():
            for skill in skills:
                if skill.get("skill_id") == skill_id:
                    return skill
        return None
    
    def search_skills(self, query: str) -> List[Dict[str, Any]]:
        """Search skills by keyword."""
        results = []
        query_lower = query.lower()
        for skills in self.skills_cache.values():
            for skill in skills:
                if (query_lower in skill.get("skill_name", "").lower() or 
                    query_lower in skill.get("description", "").lower()):
                    results.append(skill)
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get skill registry statistics."""
        total_skills = sum(len(skills) for skills in self.skills_cache.values())
        return {
            "total_domains": len(self.skills_cache),
            "total_skills": total_skills,
            "domains": {domain: len(skills) for domain, skills in self.skills_cache.items()}
        }

def create_skill_manager() -> SkillManager:
    """Factory function for skill manager."""
    return SkillManager()
