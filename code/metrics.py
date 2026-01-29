from typing import List, Dict, Set
from .io import Proposal, Researcher

def calculate_coverage(team: List[Researcher], proposal: Proposal, weights: Dict[str, float]) -> float:
    """Weighted coverage percentage"""
    required = proposal.required_skills
    if not required:
        return 1.0
        
    total_weight = sum(weights.get(s, 0.0) for s in required)
    if total_weight == 0.0:
        return 1.0
        
    team_skills = set()
    for m in team:
        team_skills.update(m.skills)
        
    covered_weight = 0.0
    for s in required:
        if s in team_skills:
            covered_weight += weights.get(s, 0.0)
            
    return covered_weight / total_weight

def get_uncovered_skills(team: List[Researcher], proposal: Proposal) -> List[str]:
    required = set(proposal.required_skills)
    team_skills = set()
    for m in team:
        team_skills.update(m.skills)
        
    uncovered = [s for s in required if s not in team_skills]
    return sorted(uncovered)
