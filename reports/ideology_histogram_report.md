# Ideology Histogram Analysis Report

> Generated: 2026-01-25 04:43
> Data source: Degeneracy mitigation experiment (abortion topic, rep 0)

## Summary

Analysis of how voter ideology groups rank statements from different author ideology groups across 3 approaches (A, A*, B) and 3 reasoning levels (minimal, low, medium).

**Methodology:**
- 100 voters sampled from 815 personas
- 100 statements with known author ideologies
- Each voter ranks all 100 statements (rank 1 = most preferred)
- Results grouped by (voter ideology, author ideology) pairs

## Approach A (Iterative Ranking)

### Minimal Reasoning

| Voter Ideology | Author Ideology | Mean Rank | Median Rank | Count |
|----------------|-----------------|-----------|-------------|-------|
| Progressive | Progressive | 37.1 | 36.0 | 2617 |
| Progressive | Conservative | 78.9 | 84.0 | 1256 |
| Progressive | Other | 50.2 | 54.0 | 733 |
| Conservative | Progressive | 62.3 | 63.0 | 2064 |
| Conservative | Conservative | 25.5 | 18.0 | 994 |
| Conservative | Other | 47.5 | 41.0 | 578 |
| Other | Progressive | 46.9 | 46.0 | 969 |
| Other | Conservative | 58.6 | 74.0 | 459 |
| Other | Other | 49.2 | 49.0 | 269 |

### Low Reasoning

| Voter Ideology | Author Ideology | Mean Rank | Median Rank | Count |
|----------------|-----------------|-----------|-------------|-------|
| Progressive | Progressive | 35.3 | 35.0 | 2623 |
| Progressive | Conservative | 81.7 | 86.0 | 1243 |
| Progressive | Other | 51.9 | 59.0 | 736 |
| Conservative | Progressive | 62.7 | 63.0 | 2109 |
| Conservative | Conservative | 27.2 | 16.0 | 999 |
| Conservative | Other | 46.2 | 39.0 | 592 |
| Other | Progressive | 46.1 | 46.0 | 969 |
| Other | Conservative | 60.3 | 77.0 | 459 |
| Other | Other | 49.5 | 49.5 | 272 |

### Medium Reasoning

| Voter Ideology | Author Ideology | Mean Rank | Median Rank | Count |
|----------------|-----------------|-----------|-------------|-------|
| Progressive | Progressive | 35.1 | 35.0 | 2622 |
| Progressive | Conservative | 82.1 | 87.0 | 1242 |
| Progressive | Other | 52.0 | 60.5 | 736 |
| Conservative | Progressive | 63.1 | 63.0 | 2109 |
| Conservative | Conservative | 27.1 | 16.0 | 999 |
| Conservative | Other | 45.3 | 38.0 | 592 |
| Other | Progressive | 45.6 | 46.0 | 969 |
| Other | Conservative | 62.1 | 79.0 | 459 |
| Other | Other | 48.3 | 50.5 | 272 |

## Approach A* (Iterative Top-K/Bottom-K)

### Minimal Reasoning

| Voter Ideology | Author Ideology | Mean Rank | Median Rank | Count |
|----------------|-----------------|-----------|-------------|-------|
| Progressive | Progressive | 39.1 | 36.0 | 2622 |
| Progressive | Conservative | 72.1 | 75.0 | 1244 |
| Progressive | Other | 54.8 | 54.0 | 737 |
| Conservative | Progressive | 62.7 | 63.0 | 2106 |
| Conservative | Conservative | 24.4 | 17.0 | 999 |
| Conservative | Other | 50.7 | 43.0 | 589 |
| Other | Progressive | 49.3 | 48.0 | 970 |
| Other | Conservative | 51.4 | 64.0 | 460 |
| Other | Other | 53.5 | 54.0 | 272 |

### Low Reasoning

| Voter Ideology | Author Ideology | Mean Rank | Median Rank | Count |
|----------------|-----------------|-----------|-------------|-------|
| Progressive | Progressive | 38.2 | 35.0 | 2622 |
| Progressive | Conservative | 71.5 | 73.0 | 1242 |
| Progressive | Other | 58.9 | 60.0 | 737 |
| Conservative | Progressive | 63.6 | 63.0 | 2109 |
| Conservative | Conservative | 24.6 | 16.0 | 999 |
| Conservative | Other | 47.5 | 38.0 | 592 |
| Other | Progressive | 49.6 | 47.0 | 969 |
| Other | Conservative | 50.0 | 64.0 | 460 |
| Other | Other | 54.6 | 54.0 | 272 |

### Medium Reasoning

| Voter Ideology | Author Ideology | Mean Rank | Median Rank | Count |
|----------------|-----------------|-----------|-------------|-------|
| Progressive | Progressive | 38.4 | 35.0 | 2622 |
| Progressive | Conservative | 70.2 | 72.0 | 1242 |
| Progressive | Other | 60.3 | 67.5 | 736 |
| Conservative | Progressive | 63.5 | 63.0 | 2109 |
| Conservative | Conservative | 25.8 | 16.0 | 999 |
| Conservative | Other | 45.7 | 38.0 | 592 |
| Other | Progressive | 49.3 | 47.0 | 969 |
| Other | Conservative | 52.9 | 66.0 | 459 |
| Other | Other | 50.6 | 46.0 | 272 |

## Approach B (Scoring)

### Minimal Reasoning

| Voter Ideology | Author Ideology | Mean Rank | Median Rank | Count |
|----------------|-----------------|-----------|-------------|-------|
| Progressive | Progressive | 37.6 | 36.0 | 2622 |
| Progressive | Conservative | 77.8 | 85.0 | 1242 |
| Progressive | Other | 50.5 | 53.0 | 736 |
| Conservative | Progressive | 61.5 | 63.0 | 2086 |
| Conservative | Conservative | 28.1 | 18.0 | 986 |
| Conservative | Other | 47.0 | 42.0 | 586 |
| Other | Progressive | 45.6 | 44.0 | 969 |
| Other | Conservative | 61.3 | 74.0 | 459 |
| Other | Other | 49.8 | 49.5 | 272 |

### Low Reasoning

| Voter Ideology | Author Ideology | Mean Rank | Median Rank | Count |
|----------------|-----------------|-----------|-------------|-------|
| Progressive | Progressive | 51.0 | 51.0 | 2622 |
| Progressive | Conservative | 48.6 | 48.0 | 1242 |
| Progressive | Other | 51.9 | 53.5 | 736 |
| Conservative | Progressive | 50.6 | 51.0 | 2109 |
| Conservative | Conservative | 50.2 | 50.0 | 999 |
| Conservative | Other | 50.5 | 50.0 | 592 |
| Other | Progressive | 50.0 | 49.0 | 969 |
| Other | Conservative | 51.1 | 51.0 | 459 |
| Other | Other | 51.3 | 56.0 | 272 |

### Medium Reasoning

| Voter Ideology | Author Ideology | Mean Rank | Median Rank | Count |
|----------------|-----------------|-----------|-------------|-------|
| Progressive | Progressive | 50.5 | 50.0 | 2605 |
| Progressive | Conservative | 48.9 | 48.0 | 1233 |
| Progressive | Other | 51.6 | 53.0 | 731 |
| Conservative | Progressive | 51.4 | 52.0 | 2104 |
| Conservative | Conservative | 48.6 | 48.0 | 999 |
| Conservative | Other | 50.0 | 50.0 | 592 |
| Other | Progressive | 50.0 | 49.0 | 969 |
| Other | Conservative | 51.0 | 52.0 | 459 |
| Other | Other | 51.4 | 56.0 | 272 |

## Key Findings

### Ideological Sorting

Look for patterns where:
- Progressive voters rank Progressive-authored statements higher (lower rank number)
- Conservative voters rank Conservative-authored statements higher
- If mean ranks are ~50 for all combinations, there is minimal ideological sorting

### Effect of Reasoning Level

Compare across minimal, low, medium reasoning levels to see if higher reasoning effort produces different ranking patterns.

### Approach Comparison

- **Approach A** (iterative ranking): Expected to produce valid rankings
- **Approach A*** (iterative top-K/bottom-K): Expected to produce valid rankings
- **Approach B** (scoring): Known to produce degenerate rankings at low/medium reasoning - rankings may reflect presentation order rather than genuine preferences
