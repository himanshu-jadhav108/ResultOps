"""
ResultOps - Rank Calculator
Proper tie-aware ranking: same SGPA + same total marks → same rank,
next distinct student gets rank = position (e.g. 1, 2, 2, 4).
"""


class RankCalculator:
    """
    Calculates academic ranks with correct tie-handling.

    Sorting priority:
      1. SGPA descending (higher is better)
      2. Total marks descending (tie-breaker)

    Tie rule (standard competition ranking / 1224 style):
      Two students with identical SGPA AND identical total marks share the
      same rank. The next student gets rank = their position in the sorted list.
      Example: scores [9.0, 9.0, 8.5, 8.0] → ranks [1, 1, 3, 4]
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate(self, records: list[dict]) -> list[dict]:
        """
        Assign ranks to a list of student result dicts.

        Each dict should have at least:
          - 'sgpa'         : float | None
          - 'total_marks'  : int | float | None  (optional, used as tie-breaker)

        Returns the same list (new dicts) with an added 'Rank' key.
        """
        if not records:
            return []

        enriched = [
            {
                **r,
                "_sgpa_key": r.get("sgpa") or 0,
                "_marks_key": self._total_marks(r),
            }
            for r in records
        ]

        # Sort: SGPA desc, then total marks desc
        enriched.sort(key=lambda x: (x["_sgpa_key"], x["_marks_key"]), reverse=True)

        # Assign ranks with tie-handling
        ranked = []
        position = 0
        prev_sgpa = None
        prev_marks = None
        shared_rank = 0

        for rec in enriched:
            position += 1
            cur_sgpa = rec["_sgpa_key"]
            cur_marks = rec["_marks_key"]

            if cur_sgpa == prev_sgpa and cur_marks == prev_marks:
                # Tie: share previous rank
                rank = shared_rank
            else:
                rank = position
                shared_rank = position

            prev_sgpa = cur_sgpa
            prev_marks = cur_marks

            # Build clean output dict (drop internal keys)
            out = {k: v for k, v in rec.items() if not k.startswith("_")}
            out["Rank"] = rank
            ranked.append(out)

        return ranked

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _total_marks(record: dict) -> float:
        """
        Derive total marks from a result record.
        Tries 'total_marks' → sum of subject totals → 0.
        """
        if record.get("total_marks") is not None:
            return float(record["total_marks"])

        subjects = record.get("subjects", [])
        if subjects:
            marks = [
                s.get("total") or 0 for s in subjects if s.get("total") is not None
            ]
            return float(sum(marks))

        return 0.0


# ── Module-level convenience function ────────────────────────────────────────


def calculate_ranks(records: list[dict]) -> list[dict]:
    """Convenience wrapper around RankCalculator.calculate()."""
    return RankCalculator().calculate(records)
