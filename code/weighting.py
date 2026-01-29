from typing import List, Dict
import math
from .io import Researcher
import numpy as np

def calculate_rarity_weights(researchers: List[Researcher]) -> Dict[str, float]:
    """
    Compute skill weights: w(s) = log( (N+1) / (df(s)+1) )
    """
    N = len(researchers)
    skill_counts: Dict[str, int] = {}
    
    # 1. Count df(s)
    for r in researchers:
        # distinct skills per researcher to avoid double counting if duplicate skills present
        unique_skills = set(r.skills)
        for s in unique_skills:
            skill_counts[s] = skill_counts.get(s, 0) + 1
            
    # 2. Compute weights
    weights: Dict[str, float] = {}
    for s, count in skill_counts.items():
        # log base e (natural log) is standard for IDF, but standard doesn't specify base. 
        # prompt implies natural log by default notation \log.
        weights[s] = math.log((N + 1) / (count + 1))
        
    return weights
