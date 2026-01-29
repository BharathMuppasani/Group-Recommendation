import sys
import json
from pathlib import Path
from rich.console import Console
import argparse

# Add current directory to path so we can import code package
# Add current directory and code directory to path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "code"))

# Keep sys.path hack to ensure 'code' module is found regardless of where python is called from,
# but using relative path '.' if running from root is implicit.
# However, to be safe and strictly follow "run from root", we can rely on python's default behavior 
# if the user runs `python run.py`, the current directory is in path.
# But `sys.path.append` is safer for custom execution. I will ensure it uses relative logic if preferred,
# or just leave it as standard python boilerplate for scripts. 
# User asked "why absolute", I'll switch to relative if possible, but __file__ is standard.
# I will stick to the user's request for data paths being relative arguments.

from code.io import load_researchers, load_proposals
from code.weighting import calculate_rarity_weights
from code.scoring import calculate_seat_cost
from code.greedy import select_team_greedy
from code.metrics import calculate_coverage, get_uncovered_skills

from code.metrics import calculate_coverage, get_uncovered_skills

console = Console()

def update_results_manifest(results_root):
    """
    Scans the results directory for result sets and generates a unified manifest file.
    """
    manifest = {
        "generated_at": None,
        "sets": []
    }
    
    import datetime
    manifest["generated_at"] = datetime.datetime.now().isoformat()
    
    # Scan for subdirectories
    results_path = Path(results_root)
    if not results_path.exists():
        return

    subdirs = sorted([d for d in results_path.iterdir() if d.is_dir()])
    
    for d in subdirs:
        set_name = d.name
        # Look for teams json
        teams_json_path = d / "teams" / f"{set_name}_teams.json"
        
        if teams_json_path.exists():
            try:
                with open(teams_json_path, 'r') as f:
                    data = json.load(f)
                
                # Calculate aggregate metrics
                total = len(data)
                if total == 0:
                    continue
                    
                avg_goodness = sum(item.get("metrics", {}).get("goodness_score", 0) or 0 for item in data) / total
                avg_coverage = sum(item.get("metrics", {}).get("coverage", 0) for item in data) / total
                avg_cost = sum(item.get("metrics", {}).get("seat_cost", 0) for item in data) / total
                
                manifest["sets"].append({
                    "id": set_name,
                    "name": set_name.replace("_", " ").title(),
                    "path": f"{set_name}/teams/{set_name}_teams.json",
                    "stats": {
                        "total_proposals": total,
                        "avg_goodness": avg_goodness,
                        "avg_coverage": avg_coverage,
                        "avg_seat_cost": avg_cost
                    }
                })
            except Exception as e:
                console.print(f"[yellow]Warning: Could not process {teams_json_path}: {e}[/yellow]")

    manifest_path = results_path / "results_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    console.print(f"[green]Updated manifest at {manifest_path}[/green]")

def generate_data_summary(path, researchers, proposals, weights, seat_costs):
    with open(path, "w") as f:
        f.write(f"# Data Summary\n\n")
        f.write(f"- **Researchers**: {len(researchers)}\n")
        f.write(f"- **Proposals**: {len(proposals)}\n\n")
        
        f.write("## Rarest Skills (Top 10)\n")
        sorted_skills = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:10]
        f.write("| Skill | Weight |\n|---|---|\n")
        for s, w in sorted_skills:
            f.write(f"| {s} | {w:.4f} |\n")
        f.write("\n")
        
        f.write("## Seat Costs (Top 10)\n")
        sorted_costs = sorted(seat_costs.items(), key=lambda x: x[1], reverse=True)[:10]
        f.write("| Proposal | Seat Cost |\n|---|---|\n")
        for pid, cost in sorted_costs:
            f.write(f"| {pid} | {cost:.4f} |\n")

def generate_run_report(path, results):
    with open(path, "w") as f:
        f.write("# Run Report\n\n")
        for res in results:
            p = res['proposal']
            team = res['team']
            cov = res['coverage']
            uncovered = res['uncovered']
            cost = res['seat_cost']
            
            f.write(f"## Proposal: {p.name} (ID: {p.id})\n")
            f.write(f"- **Required Skills**: {', '.join(sorted(p.required_skills))}\n")
            f.write(f"- **Seat Cost**: {cost:.4f}\n")
            f.write(f"- **Final Coverage**: {cov:.2%}\n")
            
            goodness = res.get('goodness_score')
            if goodness is not None:
                f.write(f"- **Goodness Score**: {goodness:.4f}\n")
            else:
                f.write(f"- **Goodness Score**: N/A (Missing dependencies)\n")
                
            if uncovered:
                f.write(f"- **Uncovered Skills**: {', '.join(uncovered)}\n")
            else:
                f.write(f"- **Uncovered Skills**: None\n")
            
            f.write("\n### Selected Team\n")
            if not team:
                f.write("No team selected.\n")
            else:
                for i, member in enumerate(team, 1):
                    relevant_skills = [s for s in member.skills if s in p.required_skills]
                    f.write(f"{i}. **{member.name}** (ID: {member.id})\n")
                    f.write(f"   - Covers: {', '.join(relevant_skills)}\n")
            
            f.write("\n---\n\n")

def save_teams_json(path, results):
    output_data = []
    for res in results:
        p = res['proposal']
        team = res['team']
        
        required_skills_set = set(p.required_skills)
        team_data = []
        for m in team:
            # Find intersection of member skills and proposal requirements
            matched = [s for s in m.skills if s in required_skills_set]
            team_data.append({
                "id": m.id,
                "name": m.name,
                "matching_skills": matched
            })
        
        output_data.append({
            "proposal_id": p.id,
            "proposal_name": p.name,
            "required_skills": p.required_skills,
            "recommended_team": team_data,
            "metrics": {
                "coverage": res['coverage'],
                "seat_cost": res['seat_cost'],
                "goodness_score": res.get('goodness_score'),
                "uncovered": res['uncovered']
            }
        })
        
    with open(path, "w") as f:
        json.dump(output_data, f, indent=2)

def calculate_goodness(proposal, team, researchers_map):
    try:
        from code.M1 import apply_ultra_metric
        # Map team objects to IDs as expected by M1?
        # M1: for i in m.team: m.researchers[i] = all_researchers_skills[i]
        # So team should be a list of IDs.
        team_ids = [m.id for m in team]
        
        # M1: apply_ultra_metric(proposal_skills, team, all_researchers_skills)
        # proposal_skills: seems to expect list of strings (metric.demand = proposal_skills)
        score = apply_ultra_metric(proposal.required_skills, team_ids, researchers_map)
        return score
    except (ImportError, ModuleNotFoundError) as e:
        # Dependencies missing
        return None
    except Exception as e:
        console.print(f"[red]Error calculating goodness: {e}[/red]")
        return None

def main():
    parser = argparse.ArgumentParser(description="Run Group Reco Analysis")
    parser.add_argument("--data", default="data/raw", help="Path to input data directory")
    parser.add_argument("--results", default="results", help="Path to output results directory")
    args = parser.parse_args()

    console.print(f"[bold green]Starting Group Reco[/bold green]")
    
    # Use paths relative to current working directory (CWD)
    data_path = Path(args.data)
    results_root = Path(args.results)

    if not data_path.exists():
        console.print(f"[bold red]Data path '{data_path}' does not exist![/bold red]")
        return
        
    results_root.mkdir(parents=True, exist_ok=True)

    # Determine sets to process
    r_files_direct = list(data_path.glob("*_researcher_skills.csv"))
    sets_to_process = []
    
    if r_files_direct:
        sets_to_process.append(data_path)
    else:
        subdirs = sorted([d for d in data_path.iterdir() if d.is_dir()])
        for d in subdirs:
             if list(d.glob("*_researcher_skills.csv")):
                 sets_to_process.append(d)
    
    if not sets_to_process:
        console.print(f"[bold red]No valid datasets found in '{data_path}'[/bold red]")
        return

    for set_dir in sets_to_process:
        set_name = set_dir.name
        console.print(f"\n[bold blue]Processing {set_name}...[/bold blue]")
        
        # Identify files
        r_files = list(set_dir.glob("*_researcher_skills.csv"))
        p_files = list(set_dir.glob("*_proposal_skills.csv"))
        
        if not r_files or not p_files:
            console.print(f"Skipping {set_name}")
            continue
            
        r_csv = r_files[0]
        p_csv = p_files[0]
        
        console.print(f"Loading from {r_csv.name} and {p_csv.name}")
        try:
            researchers = load_researchers(str(r_csv))
            proposals = load_proposals(str(p_csv))
        except Exception as e:
            console.print(f"[red]Error loading data: {e}[/red]")
            continue

        # Prepare map for Goodness Score
        researchers_map = {r.id: r.skills for r in researchers}
        
        # 2. Weighting
        console.print("Calculating weights...")
        weights = calculate_rarity_weights(researchers)
        
        # 3. Process
        alpha = 0.5
        max_team_size = 5
        coverage_target = 0.9
        
        results = []
        seat_costs = {}
        
        with console.status(f"[bold green]Forming teams ({len(proposals)} items)...") as status:
            for p in proposals:
                cost = calculate_seat_cost(p, weights)
                seat_costs[p.id] = cost
                
                # team = select_team_greedy(
                #     proposal=p,
                #     candidates=researchers,
                #     weights=weights,
                #     alpha=alpha,
                #     max_size=max_team_size,
                #     coverage_target=coverage_target
                # )
                from code.greedy import select_team_goodness
                team = select_team_goodness(
                    proposal=p,
                    candidates=researchers,
                    weights=weights,
                    max_size=max_team_size
                )
                
                cov = calculate_coverage(team, p, weights)
                uncovered = get_uncovered_skills(team, p)
                
                # Goodness Score
                goodness = calculate_goodness(p, team, researchers_map)
                
                results.append({
                    "proposal": p,
                    "team": team,
                    "coverage": cov,
                    "uncovered": uncovered,
                    "seat_cost": cost,
                    "goodness_score": goodness
                })

        # 4. Output
        set_out_dir = results_root / set_name
        reports_dir = set_out_dir / "reports"
        teams_dir = set_out_dir / "teams"
        
        reports_dir.mkdir(parents=True, exist_ok=True)
        teams_dir.mkdir(parents=True, exist_ok=True)
        
        console.print(f"Saving results to {set_out_dir}...")
        
        # Human Readable
        generate_data_summary(reports_dir / f"{set_name}_data_summary.md", researchers, proposals, weights, seat_costs)
        generate_run_report(reports_dir / f"{set_name}_run_report.md", results)
        
        # Machine Readable
        save_teams_json(teams_dir / f"{set_name}_teams.json", results)
        
    # Generate Manifest
    console.print("\n[bold blue]Updating Dashboard Manifest...[/bold blue]")
    update_results_manifest(results_root)

    console.print(f"\n[bold green]All Done! Results in '{results_root}'[/bold green]")

if __name__ == "__main__":
    main()
