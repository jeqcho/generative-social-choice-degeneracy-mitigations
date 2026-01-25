"""
Generate ideology ranking histograms for Phase 2 sample-alt-voters experiment data.

Shows how voter ideology groups rank statements from different author ideology groups,
with programmatic mean/median statistics output.

Usage:
    # Single condition
    uv run python -m src.sample_alt_voters.ideology_histogram \
        --topic abortion --voter-dist uniform --alt-dist persona_no_context --rep 0

    # All conditions
    uv run python -m src.sample_alt_voters.ideology_histogram --all
"""

import argparse
import json
import logging
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from .config import (
    PHASE2_DATA_DIR,
    DATA_DIR,
    TOPICS,
    TOPIC_SHORT_NAMES,
    ALT_DISTRIBUTIONS,
    N_REPS_UNIFORM,
    N_REPS_CLUSTERED,
)

logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

VOTER_DISTRIBUTIONS = ["uniform", "clustered"]

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
PLOTS_DIR = Path(__file__).parent.parent.parent / "plots" / "phase2_ideology"
REPORTS_DIR = Path(__file__).parent.parent.parent / "reports"


# =============================================================================
# Data Loading Functions
# =============================================================================

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


def load_voter_ids(rep_dir: Path) -> List[int]:
    """Load voter_indices from voters.json."""
    voters_path = rep_dir / "voters.json"
    with open(voters_path) as f:
        return json.load(f)["voter_indices"]


def get_statement_author_ids(topic: str, rep_id: int) -> List[int]:
    """Load context_persona_ids from context file."""
    context_path = DATA_DIR / "sample-alt-voters" / "sampled-context" / topic / f"rep{rep_id}.json"
    with open(context_path) as f:
        return [int(pid) for pid in json.load(f)["context_persona_ids"]]


def load_rankings_from_preferences(rep_dir: Path) -> Optional[List[List[int]]]:
    """
    Load preferences.json and convert to rankings format.

    Input format: preferences[rank][voter] = stmt_idx (as string)
    Output format: rankings[voter][rank] = stmt_idx (as int)
    """
    pref_path = rep_dir / "preferences.json"
    if not pref_path.exists():
        logger.warning(f"Preferences file not found: {pref_path}")
        return None

    with open(pref_path) as f:
        preferences = json.load(f)  # [rank][voter] = "stmt_idx"

    n_voters = len(preferences[0])
    n_ranks = len(preferences)

    # Transpose and convert to int
    rankings = []
    for voter in range(n_voters):
        voter_ranking = [int(preferences[rank][voter]) for rank in range(n_ranks)]
        rankings.append(voter_ranking)

    return rankings


def get_rep_dirs(topic: str, voter_dist: str, alt_dist: str) -> List[Tuple[Path, int]]:
    """
    Get all rep directories for a given condition.

    Returns list of (rep_dir, rep_id) tuples.
    """
    topic_short = TOPIC_SHORT_NAMES.get(topic, topic)
    base_dir = PHASE2_DATA_DIR / topic_short / voter_dist / alt_dist

    if not base_dir.exists():
        logger.warning(f"Directory not found: {base_dir}")
        return []

    rep_dirs = []

    if voter_dist == "uniform":
        # uniform has rep0, rep1, ..., rep9
        for rep_id in range(N_REPS_UNIFORM):
            rep_dir = base_dir / f"rep{rep_id}"
            if rep_dir.exists():
                rep_dirs.append((rep_dir, rep_id))
    else:
        # clustered has rep0_progressive_liberal, rep1_conservative_traditional
        for item in sorted(base_dir.iterdir()):
            if item.is_dir() and item.name.startswith("rep"):
                # Extract rep_id from name like "rep0_progressive_liberal"
                match = re.match(r"rep(\d+)", item.name)
                if match:
                    rep_id = int(match.group(1))
                    rep_dirs.append((item, rep_id))

    return rep_dirs


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
    """Generate 2-panel histogram plot."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    bins = np.arange(0, 101, 10)

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
        "# Phase 2 Ideology Histogram Analysis Report",
        "",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "> Data source: Phase 2 sample-alt-voters experiment (A* with low reasoning)",
        "",
        "## Summary",
        "",
        "Analysis of how voter ideology groups rank statements from different author ideology groups",
        "across 2 topics, 2 voter distributions, 4 alt distributions, and multiple replications.",
        "",
        "**Methodology:**",
        "- 100 voters per replication",
        "- 100 statements with known author ideologies",
        "- Each voter ranks all 100 statements (rank 1 = most preferred)",
        "- Results grouped by (voter ideology, author ideology) pairs",
        "",
    ]

    # Group by topic
    current_topic = None
    current_voter_dist = None
    current_alt_dist = None

    for key in sorted(all_stats.keys()):
        parts = key.split("/")
        if len(parts) < 4:
            continue

        topic, voter_dist, alt_dist, rep = parts[0], parts[1], parts[2], parts[3]

        # Topic header
        if topic != current_topic:
            lines.append(f"## {topic.title()}")
            lines.append("")
            current_topic = topic
            current_voter_dist = None
            current_alt_dist = None

        # Voter dist header
        if voter_dist != current_voter_dist:
            lines.append(f"### {voter_dist.title()} Voter Distribution")
            lines.append("")
            current_voter_dist = voter_dist
            current_alt_dist = None

        # Alt dist header
        if alt_dist != current_alt_dist:
            lines.append(f"#### {alt_dist}")
            lines.append("")
            lines.append("| Rep | Progressive→Progressive | Conservative→Conservative | Progressive→Conservative | Conservative→Progressive |")
            lines.append("|-----|------------------------|--------------------------|-------------------------|-------------------------|")
            current_alt_dist = alt_dist

        # Stats row
        stats = all_stats[key]

        def fmt(voter_ideo, author_ideo):
            k = (voter_ideo, author_ideo)
            if k in stats:
                return f"{stats[k]['mean']:.1f}"
            return "-"

        pp = fmt("progressive_liberal", "progressive_liberal")
        cc = fmt("conservative_traditional", "conservative_traditional")
        pc = fmt("progressive_liberal", "conservative_traditional")
        cp = fmt("conservative_traditional", "progressive_liberal")

        lines.append(f"| {rep} | {pp} | {cc} | {pc} | {cp} |")

    lines.append("")
    lines.append("## Key Findings")
    lines.append("")
    lines.append("### Ideological Sorting Interpretation")
    lines.append("")
    lines.append("- **Strong sorting**: Progressive→Progressive mean < 40, Conservative→Conservative mean < 40")
    lines.append("- **Cross-ideology rejection**: Progressive→Conservative mean > 60, Conservative→Progressive mean > 60")
    lines.append("- **No sorting**: All means close to 50 (random ranking)")
    lines.append("")
    lines.append("### Expected Patterns")
    lines.append("")
    lines.append("If LLM personas exhibit genuine ideological preferences:")
    lines.append("- Progressive voters should prefer Progressive-authored statements (lower rank)")
    lines.append("- Conservative voters should prefer Conservative-authored statements (lower rank)")
    lines.append("- Cross-ideology rankings should be higher (less preferred)")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    logger.info(f"Saved markdown report to {output_path}")


# =============================================================================
# Main Processing Functions
# =============================================================================

def process_single_condition(
    topic: str,
    voter_dist: str,
    alt_dist: str,
    rep_dir: Path,
    rep_id: int,
    ideology_lookup: Dict[int, str],
    output_dir: Path
) -> Optional[Dict[Tuple[str, str], Dict[str, float]]]:
    """Process a single replication condition."""
    topic_short = TOPIC_SHORT_NAMES.get(topic, topic)
    label = f"{topic_short}/{voter_dist}/{alt_dist}/rep{rep_id}"
    logger.info(f"Processing {label}...")

    # Load rankings
    rankings = load_rankings_from_preferences(rep_dir)
    if rankings is None:
        return None

    # Load voter IDs
    voter_ids = load_voter_ids(rep_dir)

    # Load author IDs
    author_ids = get_statement_author_ids(topic_short, rep_id)

    # Collect distributions
    distributions = collect_rank_distributions(
        rankings, voter_ids, author_ids, ideology_lookup
    )

    # Compute statistics
    stats = compute_statistics(distributions)

    # Print to console
    print_statistics(stats, label)

    # Generate histogram
    plot_path = output_dir / topic_short / voter_dist / alt_dist / f"rep{rep_id}_ideology_rankings.png"
    plot_title = f"Ideology Rankings: {topic_short}/{voter_dist}/{alt_dist}/rep{rep_id}"
    plot_ideology_histograms(distributions, plot_path, plot_title)

    return stats


def run_all_conditions(
    topics: Optional[List[str]] = None,
    voter_dists: Optional[List[str]] = None,
    alt_dists: Optional[List[str]] = None,
    output_dir: Optional[Path] = None,
    report_dir: Optional[Path] = None
) -> None:
    """Run histogram generation for all specified conditions."""
    if output_dir is None:
        output_dir = PLOTS_DIR
    if report_dir is None:
        report_dir = REPORTS_DIR
    if topics is None:
        topics = list(TOPICS)
    if voter_dists is None:
        voter_dists = VOTER_DISTRIBUTIONS
    if alt_dists is None:
        alt_dists = ALT_DISTRIBUTIONS

    # Load ideology data
    logger.info("Loading ideology clusters...")
    clusters = load_ideology_clusters()
    ideology_lookup = build_ideology_lookup(clusters)

    # Process all conditions
    all_stats = {}
    total_processed = 0

    for topic in topics:
        topic_short = TOPIC_SHORT_NAMES.get(topic, topic)

        for voter_dist in voter_dists:
            for alt_dist in alt_dists:
                rep_dirs = get_rep_dirs(topic, voter_dist, alt_dist)

                for rep_dir, rep_id in rep_dirs:
                    stats = process_single_condition(
                        topic, voter_dist, alt_dist,
                        rep_dir, rep_id,
                        ideology_lookup, output_dir
                    )
                    if stats is not None:
                        key = f"{topic_short}/{voter_dist}/{alt_dist}/rep{rep_id}"
                        all_stats[key] = stats
                        total_processed += 1

    # Generate markdown report
    report_path = report_dir / "phase2_ideology_histogram_report.md"
    generate_markdown_report(all_stats, report_path)

    # Save JSON summary
    json_path = output_dir / "summary_statistics.json"
    json_stats = {
        k: {f"{v[0]},{v[1]}": s for v, s in stats.items()}
        for k, stats in all_stats.items()
    }
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, 'w') as f:
        json.dump(json_stats, f, indent=2)
    logger.info(f"Saved JSON statistics to {json_path}")

    print(f"\n=== Done ===")
    print(f"Processed {total_processed} conditions")
    print(f"Histogram plots saved to {output_dir}")
    print(f"Markdown report saved to {report_path}")


def main():
    """CLI entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(
        description="Generate ideology ranking histograms for Phase 2 data"
    )
    parser.add_argument("--topic", choices=["abortion", "electoral"])
    parser.add_argument("--voter-dist", choices=VOTER_DISTRIBUTIONS)
    parser.add_argument("--alt-dist", choices=ALT_DISTRIBUTIONS)
    parser.add_argument("--rep", type=int)
    parser.add_argument("--all", action="store_true", help="Process all conditions")
    parser.add_argument("--output-dir", type=str)
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else PLOTS_DIR

    if args.all:
        topics = [args.topic] if args.topic else None
        voter_dists = [args.voter_dist] if args.voter_dist else None
        alt_dists = [args.alt_dist] if args.alt_dist else None
        run_all_conditions(
            topics=topics,
            voter_dists=voter_dists,
            alt_dists=alt_dists,
            output_dir=output_dir
        )
    elif args.topic and args.voter_dist and args.alt_dist and args.rep is not None:
        # Single condition
        clusters = load_ideology_clusters()
        ideology_lookup = build_ideology_lookup(clusters)

        topic_short = TOPIC_SHORT_NAMES.get(args.topic, args.topic)
        rep_dir = PHASE2_DATA_DIR / topic_short / args.voter_dist / args.alt_dist / f"rep{args.rep}"

        if not rep_dir.exists():
            print(f"Error: Directory not found: {rep_dir}")
            return

        process_single_condition(
            args.topic, args.voter_dist, args.alt_dist,
            rep_dir, args.rep,
            ideology_lookup, output_dir
        )
    else:
        print("Please specify either --all or all of --topic, --voter-dist, --alt-dist, --rep")
        parser.print_help()


if __name__ == "__main__":
    main()
