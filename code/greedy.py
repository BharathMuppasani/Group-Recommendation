from typing import List, Dict, Set
from .io import Proposal, Researcher
from .scoring import calculate_marginal_gain
from .metrics import calculate_coverage # Will implement metrics next, but circular import might be issue if I import.
# Actually, I can implement coverage logic inline or inject dependency?
# Let's import calculate_coverage from metrics, assuming metrics will exist.
# Wait, if I import metrics here and metrics imports io, that is fine.
# But if metrics imports greedy, that is bad. Metrics likely just needs io.
# Let's just implement coverage check inline here or move calculate_coverage to scoring?
# The prompt says metrics.py has calculate_coverage. 
# To avoid import loops if metrics needs scoring (unlikely), I'll just check coverage here 
# or import inside function.
# Let's import inside function for safety or check prompt definition of modules. 
# metrics.py: calculate_coverage. 
# I will use a simple inline check for coverage to break dependency or import inside.
# Actually, I should just implement calculate_coverage in metrics.py and import it.
# Let's assume metrics.py does not import greedy.py.

def select_team_greedy(
    proposal: Proposal, 
    candidates: List[Researcher], 
    weights: Dict[str, float], 
    alpha: float = 0.5, 
    max_size: int = 5, 
    coverage_target: float = 0.9,
    min_gain: float = 0.001
) -> List[Researcher]:
    """
    Greedily add candidates with max marginal gain.
    Stop if constraints met or no gain.
    """
    team: List[Researcher] = []
    available_candidates = candidates[:]
    
    # Pre-calc proposal total weight for coverage calculation
    required = proposal.required_skills
    total_weight = sum(weights.get(s, 0.0) for s in required)
    
    # Helper for coverage
    def current_coverage(t: List[Researcher]) -> float:
        if total_weight == 0: return 1.0
        covered_weight = 0.0
        team_skills = set()
        for m in t:
            team_skills.update(m.skills)
        
        for s in required:
            if s in team_skills:
                covered_weight += weights.get(s, 0.0)
        return covered_weight / total_weight

    while len(team) < max_size:
        # Check current coverage
        cov = current_coverage(team)
        if cov >= coverage_target:
            break
            
        best_cand = None
        best_gain = -1.0
        
        # Find best candidate
        for cand in available_candidates:
            # Skip if already in team (though available_candidates list management should handle this)
            gain = calculate_marginal_gain(cand, team, proposal, weights, alpha)
            if gain > best_gain:
                best_gain = gain
                best_cand = cand
                
        # Check stop conditions
        if best_cand is None or best_gain < min_gain:
            break
            
        # Add to team
        team.append(best_cand)
        available_candidates.remove(best_cand)
        
    return team
