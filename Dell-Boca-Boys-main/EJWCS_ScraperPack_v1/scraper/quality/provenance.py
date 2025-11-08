def provenance_score(structured: bool, adapter: str, recency_days: int, redundancy: int) -> float:
    score = 0.5
    if structured: score += 0.2
    if adapter in ("greenhouse","lever","workday"): score += 0.15
    if recency_days <= 7: score += 0.1
    score += min(redundancy * 0.02, 0.1)
    return min(score, 1.0)
