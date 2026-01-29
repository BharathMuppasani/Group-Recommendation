import csv
import random
import ast
from faker import Faker

fake = Faker()
random.seed(42)

# Parameters
NUM_RESEARCHERS = 2000
NUM_PROPOSALS = 500
MIN_SKILLS_RESEARCHER = 3
MAX_SKILLS_RESEARCHER = 10
MIN_SKILLS_PROPOSAL = 2
MAX_SKILLS_PROPOSAL = 8

# Common research skills pool (derived from sample data context)
SKILL_POOL = [
    "machine learning", "artificial intelligence", "deep learning", "data science", "statistics",
    "python", "biology", "chemistry", "biophysics", "genetics", "bioinformatics",
    "chemical engineering", "material science", "nanotechnology", "polymers", "ceramics",
    "physics", "quantum computing", "thermodynamics", "fluid dynamics", "mechanics",
    "civil engineering", "structural health monitoring", "geotechnical engineering",
    "electrical engineering", "embedded systems", "iot", "wireless communication", "robotics",
    "computer vision", "natural language processing", "system security", "cybersecurity",
    "blockchain", "cloud computing", "high performance computing", "software engineering",
    "education", "engineering education", "pedagogy", "curriculum development",
    "economics", "business", "project management", "logistics", "supply chain",
    "psychology", "neuroscience", "cognitive science", "human computer interaction",
    "environmental science", "sustainability", "ecology", "climate change", "renewable energy",
    "solar energy", "battery technology", "fuel cells", "nuclear engineering",
    "mathematics", "applied mathematics", "graph theory", "optimization"
]

def generate_skills(min_k, max_k):
    k = random.randint(min_k, max_k)
    return set(random.sample(SKILL_POOL, k))

def generate_researchers():
    researchers = []
    for i in range(NUM_RESEARCHERS):
        name = fake.name()
        skills = generate_skills(MIN_SKILLS_RESEARCHER, MAX_SKILLS_RESEARCHER)
        # Format as string representation of set, mimicking input data
        # e.g., "{'skill1', 'skill2'}"
        skills_str = f"{{{', '.join([repr(s) for s in skills])}}}"
        researchers.append({"researcher_name": name, "skills": skills_str})
    return researchers

def generate_proposals():
    proposals = []
    for i in range(NUM_PROPOSALS):
        link = f"https://www.nsf.gov/pubs/2026/nsf26{i:03d}/nsf26{i:03d}.htm"
        skills = generate_skills(MIN_SKILLS_PROPOSAL, MAX_SKILLS_PROPOSAL)
        skills_str = f"{{{', '.join([repr(s) for s in skills])}}}"
        proposals.append({"nsf_proposal_links_v0": link, "skills": skills_str})
    return proposals

def main():
    print(f"Generating {NUM_RESEARCHERS} researchers and {NUM_PROPOSALS} proposals...")
    
    # Save Researchers
    with open("data/raw/set-4/large_researcher_skills.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["", "researcher_name", "skills"])
        writer.writeheader()
        for i, r in enumerate(generate_researchers()):
            row = {"": i, **r}
            writer.writerow(row)
    
    # Save Proposals
    with open("data/raw/set-4/large_proposal_skills.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["", "nsf_proposal_links_v0", "skills"])
        writer.writeheader()
        for i, p in enumerate(generate_proposals()):
            row = {"": i, **p}
            writer.writerow(row)

    print("Done! Saved to data/raw/set-4/")

if __name__ == "__main__":
    main()
