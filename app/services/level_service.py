LEVEL_THRESHOLDS = [
    (1, 0),
    (2, 3),
    (3, 10),
    (4, 25),
    (5, 50),
    (6, 100),
    (7, 200),
    (8, 350),
    (9, 500),
    (10, 750),
]


def calculate_level(total_tasks: int) -> int:
    """
    Determine user level based on total tasks completed.
    Level 1: 0-2, Level 2: 3-9, Level 3: 10-24, Level 4: 25-49,
    Level 5: 50-99, Level 6: 100-199, Level 7: 200-349,
    Level 8: 350-499, Level 9: 500-749, Level 10: 750+
    """
    level = 1
    for lvl, threshold in LEVEL_THRESHOLDS:
        if total_tasks >= threshold:
            level = lvl
        else:
            break
    return level
