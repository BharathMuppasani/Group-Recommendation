import json
import csv
import ast
import re
from pathlib import Path
from typing import List, Set
from pydantic import BaseModel, Field

class Researcher(BaseModel):
    id: str
    name: str = "Unknown"
    skills: List[str]

class Proposal(BaseModel):
    id: str
    name: str = "Unknown"
    required_skills: List[str]

def _parse_set_string(s: str) -> List[str]:
    """
    Parses a string looking like "{'skill1', 'skill2'}" or similar variants.
    """
    s = s.strip()
    if not s:
        return []
    
    # Try ast.literal_eval first (safer)
    try:
        val = ast.literal_eval(s)
        if isinstance(val, (set, list, tuple)):
            return [str(v).lower().strip() for v in val if v]
    except (ValueError, SyntaxError):
        pass
    
    # Fallback: simple cleanup if AST fails (e.g. strict JSON issues)
    # Remove braces and split
    cleaned = s.replace("{", "").replace("}", "").replace("'", "").replace('"', "")
    # structured skills often use ; or ,
    if ";" in cleaned:
        items = [item.strip().lower() for item in cleaned.split(";") if item.strip()]
    else:
        items = [item.strip().lower() for item in cleaned.split(",") if item.strip()]
    return items

def load_researchers(path: str) -> List[Researcher]:
    path_obj = Path(path)
    if path_obj.suffix.lower() == '.json':
        with open(path, 'r') as f:
            data = json.load(f)
            return [Researcher(**item) for item in data]
    elif path_obj.suffix.lower() == '.csv':
        researchers = []
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            
            for i, row in enumerate(reader):
                rid = str(i)
                
                # Check for Set 1 format (researcher_name, skills)
                if 'researcher_name' in fieldnames:
                    name = row.get('researcher_name', f"Researcher {i}")
                    skills_str = row.get('skills', "")
                    skills = _parse_set_string(skills_str)
                # Check for Set 5 format (Researcher Name, Processed Skills)
                elif 'Researcher Name' in fieldnames:
                    name = row.get('Researcher Name', f"Researcher {i}")
                    skills_str = row.get('Processed Skills', "")
                    skills = _parse_set_string(skills_str)
                # Check for Set 2/3/4 format (names, research)
                elif 'names' in fieldnames:
                    name = row.get('names', f"Researcher {i}")
                    skills_str = row.get('research', "")
                    skills = _parse_set_string(skills_str)
                else:
                    name = f"Researcher {i}"
                    skills = []
                
                researchers.append(Researcher(id=rid, name=name, skills=skills))
        return researchers
    else:
        raise ValueError(f"Unsupported format: {path_obj.suffix}")

def load_proposals(path: str) -> List[Proposal]:
    path_obj = Path(path)
    if path_obj.suffix.lower() == '.json':
        with open(path, 'r') as f:
            data = json.load(f)
            return [Proposal(**item) for item in data]
    elif path_obj.suffix.lower() == '.csv':
        proposals = []
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            
            for i, row in enumerate(reader):
                pid = str(i)
                
                # Set 1/4: nsf_proposal_links_v0, skills
                if 'skills' in fieldnames:
                    name = row.get('nsf_proposal_links_v0') or row.get('nsf_proposal_links_v1') or f"Proposal {i}"
                    skills_str = row.get('skills', "")
                    skills = _parse_set_string(skills_str)
                # Set 5: Proposal Link, Identified Skills
                elif 'Identified Skills' in fieldnames:
                    name = row.get('Proposal Link', f"Proposal {i}")
                    skills_str = row.get('Identified Skills', "")
                    skills = _parse_set_string(skills_str)
                # Set 2/3: nsf_proposal_links_v0/v1, title, synopsis (NO skills)
                elif 'synopsis' in fieldnames or 'title' in fieldnames:
                    name = row.get('title') or row.get('nsf_proposal_links_v0') or row.get('nsf_proposal_links_v1') or f"Proposal {i}"
                    synopsis = row.get('synopsis', "")
                    skills = [] 
                    if synopsis:
                        skills = [s.strip().lower() for s in synopsis.replace(".", ",").split(",") if s.strip()]
                else:
                    name = f"Proposal {i}"
                    skills = []
                    
                proposals.append(Proposal(id=pid, name=name, required_skills=skills))
        return proposals
    else:
        raise ValueError(f"Unsupported format: {path_obj.suffix}")
