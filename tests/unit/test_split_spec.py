from __future__ import annotations

import pytest

from core.models.split_spec import SplitSpec


def test_split_spec_builds_groups_from_multiple_breaks() -> None:
    spec = SplitSpec(start_indexes=(2, 5))

    groups = spec.build_groups(7)

    assert groups == [[0, 1], [2, 3, 4], [5, 6]]


def test_split_spec_always_includes_first_page_as_a_start() -> None:
    spec = SplitSpec(start_indexes=(3,))

    starts = spec.normalized_starts(6)

    assert starts == [0, 3]


def test_split_spec_ignores_duplicate_and_zero_indexes() -> None:
    spec = SplitSpec(start_indexes=(0, 4, 4, 2))

    starts = spec.normalized_starts(6)

    assert starts == [0, 2, 4]


def test_split_spec_returns_single_group_without_extra_breaks() -> None:
    spec = SplitSpec()

    groups = spec.build_groups(5)

    assert groups == [[0, 1, 2, 3, 4]]


def test_split_spec_describes_group_ranges() -> None:
    spec = SplitSpec(start_indexes=(2, 5))

    descriptions = spec.describe_groups(7)

    assert descriptions == [
        "1. pages 1-2 (2 pages)",
        "2. pages 3-5 (3 pages)",
        "3. pages 6-7 (2 pages)",
    ]


def test_split_spec_rejects_out_of_range_start() -> None:
    spec = SplitSpec(start_indexes=(5,))

    with pytest.raises(ValueError):
        spec.build_groups(5)
