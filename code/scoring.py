from typing import List, Dict, Set
from .io import Proposal, Researcher

def calculate_seat_cost(proposal: Proposal, weights: Dict[str, float]) -> float:
    """avg(weights[s] for s in proposal.required_skills)"""
    required = proposal.required_skills
    if not required:
        return 0.0
    
    total_w = sum(weights.get(s, 0.0) for s in required)
    return total_w / len(required)

def calculate_team_score(team: List[Researcher], proposal: Proposal, weights: Dict[str, float], alpha: float = 0.5) -> float:
    """Sum of w(s) * (1 - alpha^count(s)) for required skills"""
    required = set(proposal.required_skills)
    skill_counts: Dict[str, int] = {s: 0 for s in required}
    
    # Count coverage by team
    for member in team:
        # Optimization: only checking required skills
        member_skills = set(member.skills)
        for s in required:
            if s in member_skills:
                skill_counts[s] += 1
                
    score = 0.0
    for s in required:
        w = weights.get(s, 0.0)
        c = skill_counts[s]
        # Gain g(c) = 1 - alpha^c
        g_c = 1.0 - (alpha ** c)
        score += w * g_c
        
    return score

def calculate_marginal_gain(candidate: Researcher, current_team: List[Researcher], proposal: Proposal, weights: Dict[str, float], alpha: float = 0.5) -> float:
    """F(T + {c}, p) - F(T, p)"""
    current_score = calculate_team_score(current_team, proposal, weights, alpha)
    new_team = current_team + [candidate]
    new_score = calculate_team_score(new_team, proposal, weights, alpha)
    return new_score - current_score
