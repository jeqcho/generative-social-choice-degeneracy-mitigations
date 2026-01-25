"""
Generate ideology ranking histograms for degeneracy mitigation experiment data.

Shows how voter ideology groups rank statements from different author ideology groups,
with programmatic mean/median statistics output.

Usage:
    # Single approach/reasoning
    uv run python -m src.degeneracy_mitigation.ideology_histogram \
        --approach approach_a --reasoning low

    # All approaches and reasoning levels
    uv run python -m src.degeneracy_mitigation.ideology_histogram --all
"""

import argparse
import json
import logging
import random
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from .config import (
    OUTPUT_DIR,
    DATA_DIR,
    N_VOTERS,
    N_STATEMENTS,
    TEST_REP,
    TEST_TOPIC,
)

logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

APPROACHES = ["approach_a", "approach_a_star", "approach_b"]
REASONING_LEVELS = ["minimal", "low", "medium"]

APPROACH_LABELS = {
    "approach_a": "Approach A (Iterative Ranking)",
    "approach_a_star": "Approach A* (Iterative Top-K/Bottom-K)",
    "approach_b": "Approach B (Scoring)",
}

IDEOLOGY_COLORS = {
    "progressive_liberal": "blue",
    "conservative_traditional": "red",
    "other": "gray",
}

IDEOLOGY_LABELS = {
    "progressive_liberal": "Progressive",
    "conservative_traditional": "Conservative",
    "other": "Other",
}

# Output directories
PLOTS_DIR = Path(__file__).parent.parent.parent / "plots" / "degeneracy_mitigation"
REPORTS_DIR = Path(__file__).parent.parent.parent / "reports"


# =============================================================================
# Data Loading Functions
# =============================================================================

def get_voter_global_ids(rep: int = 0, n_voters: int = 100, n_personas: int = 815) -> List[int]:
    """
    Reconstruct which global persona IDs were sampled as voters.

    Must match the sampling logic in run_test.py:load_voters_for_rep()
    """
    rng = random.Random(42 + rep)
    return rng.sample(range(n_personas), n_voters)


def get_statement_author_ids(topic: str = "abortion", rep: int = 0) -> List[int]:
    """
    Load context_persona_ids from context file.

    Returns list of global persona IDs, one per statement.
    """
    context_path = DATA_DIR / "sample-alt-voters" / "sampled-context" / topic / f"rep{rep}.json"
    with open(context_path) as f:
        data = json.load(f)
    return [int(pid) for pid in data["context_persona_ids"]]


def load_ideology_clusters() -> Dict[str, List[int]]:
    """Load ideology cluster assignments."""
    clusters_path = DATA_DIR / "sample-alt-voters" / "ideology_clusters.json"
    with open(clusters_path) as f:
        return json.load(f)


def build_ideology_lookup(clusters: Dict[str, List[int]]) -> Dict[int, str]:
    """Create reverse lookup: persona_id -> ideology."""
    lookup = {}
    for ideology, ids in clusters.items():
        for pid in ids:
            lookup[pid] = ideology
    return lookup


def load_rankings(approach: str, reasoning: str) -> Optional[List[List[int]]]:
    """
    Load rankings.json for an approach/reasoning combo.

    Returns rankings[voter_idx][rank] = stmt_idx, or None if file doesn't exist.
    """
    path = OUTPUT_DIR / approach / reasoning / "rankings.json"
    if not path.exists():
        logger.warning(f"Rankings file not found: {path}")
        return None

    with open(path) as f:
        return json.load(f)


# =============================================================================
# Analysis Functions
# =============================================================================

def collect_rank_distributions(
    rankings: List[List[int]],
    voter_ids: List[int],
    author_ids: List[int],
    ideology_lookup: Dict[int, str]
) -> Dict[Tuple[str, str], List[int]]:
    """
    Collect ranks grouped by (voter_ideology, author_ideology).

    For each voter-statement pair, records the 1-indexed rank (1=most preferred, 100=least).

    Returns:
        Dict mapping (voter_ideology, author_ideology) -> list of ranks
    """
    distributions = defaultdict(list)

    for voter_pos, voter_ranking in enumerate(rankings):
        voter_id = voter_ids[voter_pos]
        voter_ideology = ideology_lookup.get(voter_id, "other")

        for rank_0indexed, stmt_idx in enumerate(voter_ranking):
            author_id = author_ids[stmt_idx]
            author_ideology = ideology_lookup.get(author_id, "other")
            rank_1indexed = rank_0indexed + 1

            distributions[(voter_ideology, author_ideology)].append(rank_1indexed)

    return distributions


def compute_statistics(
    rank_distributions: Dict[Tuple[str, str], List[int]]
) -> Dict[Tuple[str, str], Dict[str, float]]:
    """Compute mean, median, and count for each (voter, author) ideology pair."""
    stats = {}
    for key, ranks in rank_distributions.items():
        if ranks:
            stats[key] = {
                "mean": float(np.mean(ranks)),
                "median": float(np.median(ranks)),
                "count": len(ranks)
            }
        else:
            stats[key] = {"mean": 0.0, "median": 0.0, "count": 0}
    return stats


def print_statistics(stats: Dict[Tuple[str, str], Dict[str, float]], label: str) -> None:
    """Print statistics to console in a formatted way."""
    print(f"\n=== {label} ===")

    # Group by author ideology
    for author_ideology in ["progressive_liberal", "conservative_traditional", "other"]:
        author_label = IDEOLOGY_LABELS.get(author_ideology, author_ideology)
        print(f"\nRankings of {author_label}-Authored Statements:")

        for voter_ideology in ["progressive_liberal", "conservative_traditional", "other"]:
            key = (voter_ideology, author_ideology)
            if key in stats:
                s = stats[key]
                voter_label = IDEOLOGY_LABELS.get(voter_ideology, voter_ideology)
                print(f"  {voter_label} voters: mean={s['mean']:.1f}, median={s['median']:.1f}, n={s['count']}")


# =============================================================================
# Plotting Functions
# =============================================================================

def plot_ideology_histograms(
    rank_distributions: Dict[Tuple[str, str], List[int]],
    output_path: Path,
    title: str
) -> None:
    """
    Generate 2-panel histogram plot.

    Left: Rankings of Progressive-authored statements
    Right: Rankings of Conservative-authored statements
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    bins = np.arange(0, 101, 10)  # 0-10, 10-20, ..., 90-100

    # Left: Progressive-authored statements
    for voter_ideology in ["progressive_liberal", "conservative_traditional", "other"]:
        key = (voter_ideology, "progressive_liberal")
        if key in rank_distributions and rank_distributions[key]:
            ranks = rank_distributions[key]
            voter_label = IDEOLOGY_LABELS.get(voter_ideology, voter_ideology)
            color = IDEOLOGY_COLORS.get(voter_ideology, "gray")
            ax1.hist(
                ranks, bins=bins, alpha=0.5,
                color=color,
                label=f"{voter_label} voters (n={len(ranks)})",
                edgecolor='black', linewidth=0.5
            )

    ax1.set_xlabel("Rank (1=most preferred, 100=least preferred)")
    ax1.set_ylabel("Frequency")
    ax1.set_title("Rankings of Progressive-Authored Statements")
    ax1.legend(loc='upper right')
    ax1.set_xlim(0, 100)

    # Right: Conservative-authored statements
    for voter_ideology in ["progressive_liberal", "conservative_traditional", "other"]:
        key = (voter_ideology, "conservative_traditional")
        if key in rank_distributions and rank_distributions[key]:
            ranks = rank_distributions[key]
            voter_label = IDEOLOGY_LABELS.get(voter_ideology, voter_ideology)
            color = IDEOLOGY_COLORS.get(voter_ideology, "gray")
            ax2.hist(
                ranks, bins=bins, alpha=0.5,
                color=color,
                label=f"{voter_label} voters (n={len(ranks)})",
                edgecolor='black', linewidth=0.5
            )

    ax2.set_xlabel("Rank (1=most preferred, 100=least preferred)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Rankings of Conservative-Authored Statements")
    ax2.legend(loc='upper right')
    ax2.set_xlim(0, 100)

    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    logger.info(f"Saved histogram to {output_path}")


# =============================================================================
# Report Generation
# =============================================================================

def generate_markdown_report(
    all_stats: Dict[str, Dict[Tuple[str, str], Dict[str, float]]],
    output_path: Path
) -> None:
    """Generate comprehensive markdown report with all statistics."""

    lines = [
        "# Ideology Histogram Analysis Report",
        "",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> Data source: Degeneracy mitigation experiment (abortion topic, rep 0)",
        "",
        "## Summary",
        "",
        "Analysis of how voter ideology groups rank statements from different author ideology groups across 3 approaches (A, A*, B) and 3 reasoning levels (minimal, low, medium).",
        "",
        "**Methodology:**",
        "- 100 voters sampled from 815 personas",
        "- 100 statements with known author ideologies",
        "- Each voter ranks all 100 statements (rank 1 = most preferred)",
        "- Results grouped by (voter ideology, author ideology) pairs",
        "",
    ]

    # Results by approach
    for approach in APPROACHES:
        approach_label = APPROACH_LABELS.get(approach, approach)
        lines.append(f"## {approach_label}")
        lines.append("")

        for reasoning in REASONING_LEVELS:
            key = f"{approach}/{reasoning}"
            if key not in all_stats:
                lines.append(f"### {reasoning.title()} Reasoning")
                lines.append("")
                lines.append("*No data available*")
                lines.append("")
                continue

            stats = all_stats[key]
            lines.append(f"### {reasoning.title()} Reasoning")
            lines.append("")
            lines.append("| Voter Ideology | Author Ideology | Mean Rank | Median Rank | Count |")
            lines.append("|----------------|-----------------|-----------|-------------|-------|")

            for voter_ideology in ["progressive_liberal", "conservative_traditional", "other"]:
                for author_ideology in ["progressive_liberal", "conservative_traditional", "other"]:
                    stat_key = (voter_ideology, author_ideology)
                    if stat_key in stats:
                        s = stats[stat_key]
                        v_label = IDEOLOGY_LABELS.get(voter_ideology, voter_ideology)
                        a_label = IDEOLOGY_LABELS.get(author_ideology, author_ideology)
                        lines.append(f"| {v_label} | {a_label} | {s['mean']:.1f} | {s['median']:.1f} | {s['count']} |")

            lines.append("")

    # Key Findings section
    lines.append("## Key Findings")
    lines.append("")
    lines.append("### Ideological Sorting")
    lines.append("")
    lines.append("Look for patterns where:")
    lines.append("- Progressive voters rank Progressive-authored statements higher (lower rank number)")
    lines.append("- Conservative voters rank Conservative-authored statements higher")
    lines.append("- If mean ranks are ~50 for all combinations, there is minimal ideological sorting")
    lines.append("")
    lines.append("### Effect of Reasoning Level")
    lines.append("")
    lines.append("Compare across minimal, low, medium reasoning levels to see if higher reasoning effort produces different ranking patterns.")
    lines.append("")
    lines.append("### Approach Comparison")
    lines.append("")
    lines.append("- **Approach A** (iterative ranking): Expected to produce valid rankings")
    lines.append("- **Approach A*** (iterative top-K/bottom-K): Expected to produce valid rankings")
    lines.append("- **Approach B** (scoring): Known to produce degenerate rankings at low/medium reasoning - rankings may reflect presentation order rather than genuine preferences")
    lines.append("")

    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    logger.info(f"Saved markdown report to {output_path}")


# =============================================================================
# Main Processing Functions
# =============================================================================

def process_single_condition(
    approach: str,
    reasoning: str,
    voter_ids: List[int],
    author_ids: List[int],
    ideology_lookup: Dict[int, str],
    output_dir: Path
) -> Optional[Dict[Tuple[str, str], Dict[str, float]]]:
    """
    Process a single (approach, reasoning) condition.

    Returns statistics dict or None if cannot process.
    """
    logger.info(f"Processing {approach}/{reasoning}...")

    rankings = load_rankings(approach, reasoning)
    if rankings is None:
        return None

    # Collect rank distributions
    distributions = collect_rank_distributions(
        rankings, voter_ids, author_ids, ideology_lookup
    )

    # Compute statistics
    stats = compute_statistics(distributions)

    # Print to console
    approach_label = APPROACH_LABELS.get(approach, approach)
    print_statistics(stats, f"{approach_label}, {reasoning.title()} Reasoning")

    # Generate histogram
    plot_path = output_dir / approach / f"{reasoning}_ideology_rankings.png"
    plot_title = f"How Different Voter Groups Rank Statements by Author Ideology\n({approach_label}, {reasoning.title()} Reasoning)"
    plot_ideology_histograms(distributions, plot_path, plot_title)

    return stats


def run_all_conditions(output_dir: Path = None, report_dir: Path = None) -> None:
    """Run histogram generation for all approaches and reasoning levels."""
    if output_dir is None:
        output_dir = PLOTS_DIR
    if report_dir is None:
        report_dir = REPORTS_DIR

    # Load shared data
    logger.info("Loading ideology clusters...")
    clusters = load_ideology_clusters()
    ideology_lookup = build_ideology_lookup(clusters)

    logger.info("Reconstructing voter IDs...")
    voter_ids = get_voter_global_ids(rep=TEST_REP, n_voters=N_VOTERS)

    logger.info("Loading statement author IDs...")
    author_ids = get_statement_author_ids(topic=TEST_TOPIC, rep=TEST_REP)

    # Log ideology distribution
    voter_ideologies = [ideology_lookup.get(vid, "other") for vid in voter_ids]
    author_ideologies = [ideology_lookup.get(aid, "other") for aid in author_ids]

    print("\n=== Ideology Distribution ===")
    print(f"Voters: {sum(1 for i in voter_ideologies if i == 'progressive_liberal')} progressive, "
          f"{sum(1 for i in voter_ideologies if i == 'conservative_traditional')} conservative, "
          f"{sum(1 for i in voter_ideologies if i == 'other')} other")
    print(f"Authors: {sum(1 for i in author_ideologies if i == 'progressive_liberal')} progressive, "
          f"{sum(1 for i in author_ideologies if i == 'conservative_traditional')} conservative, "
          f"{sum(1 for i in author_ideologies if i == 'other')} other")

    # Process all conditions
    all_stats = {}
    for approach in APPROACHES:
        for reasoning in REASONING_LEVELS:
            stats = process_single_condition(
                approach, reasoning,
                voter_ids, author_ids, ideology_lookup,
                output_dir
            )
            if stats is not None:
                key = f"{approach}/{reasoning}"
                all_stats[key] = stats

    # Generate markdown report
    report_path = report_dir / "ideology_histogram_report.md"
    generate_markdown_report(all_stats, report_path)

    # Save JSON summary
    json_path = output_dir / "summary_statistics.json"
    json_stats = {
        k: {f"{v[0]},{v[1]}": s for v, s in stats.items()}
        for k, stats in all_stats.items()
    }
    with open(json_path, 'w') as f:
        json.dump(json_stats, f, indent=2)
    logger.info(f"Saved JSON statistics to {json_path}")

    print(f"\n=== Done ===")
    print(f"Generated {len(all_stats)} histogram plots in {output_dir}")
    print(f"Markdown report saved to {report_path}")


def main():
    """CLI entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(
        description="Generate ideology ranking histograms for degeneracy mitigation data"
    )
    parser.add_argument(
        "--approach",
        choices=APPROACHES,
        help="Specific approach to analyze"
    )
    parser.add_argument(
        "--reasoning",
        choices=REASONING_LEVELS,
        help="Specific reasoning level to analyze"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all approaches and reasoning levels"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for plots"
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else PLOTS_DIR

    if args.all:
        run_all_conditions(output_dir=output_dir)
    elif args.approach and args.reasoning:
        # Load shared data
        clusters = load_ideology_clusters()
        ideology_lookup = build_ideology_lookup(clusters)
        voter_ids = get_voter_global_ids(rep=TEST_REP, n_voters=N_VOTERS)
        author_ids = get_statement_author_ids(topic=TEST_TOPIC, rep=TEST_REP)

        process_single_condition(
            args.approach, args.reasoning,
            voter_ids, author_ids, ideology_lookup,
            output_dir
        )
    else:
        print("Please specify either --all or both --approach and --reasoning")
        parser.print_help()


if __name__ == "__main__":
    main()
