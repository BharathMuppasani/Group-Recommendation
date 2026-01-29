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

def select_team_goodness(
    proposal: Proposal,
    candidates: List[Researcher],
    weights: Dict[str, float],
    alpha: float = 0.5,  # Unused in goodness metric directly but kept for signature compatibility if needed
    max_size: int = 5
) -> List[Researcher]:
    """
    Selects a team that maximizes the Goodness Measure from metrics_scorer.py.
    The Goodness Measure is non-monotonic with respect to team size (due to setsize penalty and k-robustness bonus).
    Therefore, we search for the best team of size k for k in range 1..max_size.
    """
    # Import here to avoid circular dependencies if metrics imports greedy (though it shouldn't)
    from .metrics_scorer import MetricScorer

    best_overall_team = []
    best_overall_score = -float('inf')

    # Optimization: Pre-compute researcher map for MetricScorer
    # MetricScorer needs researchers in a dict format: {id: [skills]}
    # candidates is a list of Researcher objects.
    all_researchers_skills = {r.id: r.skills for r in candidates}
    
    # We will try to find the best team for each target size
    for target_size in range(1, max_size + 1):
        # For a fixed size, we can try a greedy approach to build the team
        # However, "Goodness" is complex. A simple greedy might get stuck.
        # But since we want to align with the "Goodness" definition which heavily weights coverage,
        # we can start with the most relevant people.
        
        # Let's try a Beam Search or simple Greedy wrapper around Goodness.
        # Simple Greedy: Start empty, add the person who increases Goodness the most, until size k.
        
        current_team_ids = []
        
        scorer = MetricScorer()
        scorer.demand = proposal.required_skills
        # Default weights from M1.py: [-1, -1, 1, 1] 
        # (Redundancy, Setsize, Coverage, kRobustness)
        scorer.set_new_weights([-1, -1, 1, 1])
        
        # Available candidates to pick from
        available = [r.id for r in candidates]
        
        for _ in range(target_size):
            best_candidate = None
            best_score_at_step = -float('inf')
            
            # Try adding each available candidate
            for cand_id in available:
                temp_team = current_team_ids + [cand_id]
                
                # Setup scorer
                scorer.reset()
                scorer.demand = proposal.required_skills
                scorer.team = temp_team
                scorer.researchers = all_researchers_skills # Pass the full dictionary
                scorer.set_new_weights([-1, -1, 1, 1])
                
                # Run metrics
                scorer.run_metrics()
                score = scorer.goodness
                
                if score > best_score_at_step:
                    best_score_at_step = score
                    best_candidate = cand_id
            
            if best_candidate:
                current_team_ids.append(best_candidate)
                available.remove(best_candidate)
            else:
                break
        
        # Evaluate final team of this size
        # (It should match best_score_at_step, but let's be safe)
        scorer.reset()
        scorer.demand = proposal.required_skills
        scorer.team = current_team_ids
        scorer.researchers = all_researchers_skills
        scorer.set_new_weights([-1, -1, 1, 1])
        scorer.run_metrics()
        final_score = scorer.goodness
        
        if final_score > best_overall_score:
            best_overall_score = final_score
            # Map back to Researcher objects
            best_overall_team = [r for r in candidates if r.id in current_team_ids]

    return best_overall_team
