# Degeneracy Mitigations for LLM-Based Preference Ranking

This repository investigates techniques for reducing **degenerate preference rankings** produced by LLM-simulated voter personas. It is a focused fork of a larger generative social choice experiment repository.

## Problem

When LLMs simulate voter personas ranking 100 policy statements, they frequently produce **degenerate rankings** -- sequential `[0, 1, 2, ..., 99]` or reverse `[99, 98, ..., 0]` orderings that mirror the presentation order rather than reflecting genuine preferences. In baseline experiments, the degeneracy rate was **81%**.

This repo tests three approaches to mitigate this problem, each evaluated at multiple reasoning effort levels.

## Approaches

### Approach A -- Iterative Top-K / Bottom-K Ranking

Instead of asking the LLM to rank all 100 statements at once, the ranking is built iteratively over 5 rounds. Each round, the LLM selects the 10 most-preferred and 10 least-preferred statements from the remaining pool (100 -> 80 -> 60 -> 40 -> 20). Invalid or degenerate round outputs are retried up to 3 times.

### Approach A\* -- Reversed Bottom-K Variant

Same as Approach A, but the bottom-K prompt asks for statements ordered "least preferred first" instead of "least preferred last." The hypothesis is that outputting the worst statement first is cognitively easier for the model than reserving it for the end of the list.

### Approach B -- Scoring-Based Ranking

Each voter assigns a score (0--99) to every statement in a single call. The ranking is derived by sorting statements by score. Duplicate scores are resolved through up to 3 deduplication rounds where the LLM re-scores only the tied statements.

### Reasoning Effort Levels

Each approach is tested at three reasoning effort levels using `gpt-5-mini`: **minimal**, **low**, and **medium**.

## Project Structure

```
src/degeneracy_mitigation/     # Experiment source code
  run_test.py                  #   CLI entry point (run approaches A, A*, B)
  analyze_results.py           #   Degeneracy stats, Spearman correlations
  ideology_histogram.py        #   Ideology ranking histogram plots
  iterative_ranking.py         #   Approach A implementation
  iterative_ranking_star.py    #   Approach A* implementation
  scoring_ranking.py           #   Approach B implementation
  config.py                    #   Shared configuration
  degeneracy_detector.py       #   Degeneracy detection utilities
  generate_voter_files.py      #   Voter file generation
  hash_identifiers.py          #   Deterministic hash ID generation

outputs/degeneracy_mitigation/ # Raw results (rankings, scores, stats)
  approach_a/{minimal,low,medium}/
  approach_a_star/{minimal,low,medium}/
  approach_b/{minimal,low,medium}/

plots/degeneracy_mitigation/   # Ideology ranking histograms
  approach_a/                  #   9 plots (3 approaches x 3 reasoning levels)
  approach_a_star/
  approach_b/

data/                          # Input data (personas, statements, ideology clusters)
reports/                       # Generated analysis reports
```

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for package management.

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync
```

## Setup

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Run the experiment

```bash
# Run all approaches at all reasoning levels
uv run python -m src.degeneracy_mitigation.run_test --approach all --reasoning-effort all

# Run a specific approach
uv run python -m src.degeneracy_mitigation.run_test --approach ranking       # Approach A
uv run python -m src.degeneracy_mitigation.run_test --approach ranking_star  # Approach A*
uv run python -m src.degeneracy_mitigation.run_test --approach scoring       # Approach B

# Run at a specific reasoning level
uv run python -m src.degeneracy_mitigation.run_test --approach all --reasoning-effort low
```

### Analyze results

```bash
# Print degeneracy rates, unique rankings, and cross-approach correlations
uv run python -m src.degeneracy_mitigation.analyze_results

# Save analysis to comparison.json
uv run python -m src.degeneracy_mitigation.analyze_results --save
```

### Generate ideology histograms

```bash
# Generate all histogram plots and a markdown report
uv run python -m src.degeneracy_mitigation.ideology_histogram --all

# Generate for a single condition
uv run python -m src.degeneracy_mitigation.ideology_histogram \
    --approach approach_a --reasoning low
```

## Origin

This repository is a focused fork of a larger single-winner generative social choice experiment. Most files from the parent repo have been removed; the remaining code in `src/` outside of `degeneracy_mitigation/` is retained as supporting infrastructure.
