def dynamic_threshold(default_rate: float) -> tuple:
    """
    Adjusts approval/review/rejection thresholds based on recent portfolio performance.
    Example: If default rate rises, tighten approval limits.
    """
    base_approve = 0.4
    base_review = 0.7

    if default_rate > 0.2:
        base_approve -= 0.05
        base_review -= 0.1

    return base_approve, base_review
