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


def test_split_spec_builds_selected_mode_group() -> None:
    spec = SplitSpec(mode="selected")

    groups = spec.build_output_groups(
        page_count=6,
        current_page_index=2,
        selected_indexes=[0, 3, 4],
    )

    assert groups == [[0, 3, 4]]


def test_split_spec_builds_single_page_groups_when_multiple_output_enabled() -> None:
    spec = SplitSpec(mode="selected", create_multiple_files=True)

    groups = spec.build_output_groups(
        page_count=6,
        current_page_index=2,
        selected_indexes=[0, 3, 4],
    )

    assert groups == [[0], [3], [4]]


def test_split_spec_builds_current_page_group() -> None:
    spec = SplitSpec(mode="current")

    groups = spec.build_output_groups(page_count=8, current_page_index=5)

    assert groups == [[5]]


def test_split_spec_builds_odd_and_even_groups() -> None:
    odd_spec = SplitSpec(mode="odd")
    even_spec = SplitSpec(mode="even")

    odd_groups = odd_spec.build_output_groups(page_count=6)
    even_groups = even_spec.build_output_groups(page_count=6)

    assert odd_groups == [[0, 2, 4]]
    assert even_groups == [[1, 3, 5]]


def test_split_spec_builds_custom_ranges_group() -> None:
    spec = SplitSpec(mode="custom", custom_ranges="1, 3-4, 6")

    groups = spec.build_output_groups(page_count=6)

    assert groups == [[0, 2, 3, 5]]


def test_split_spec_rejects_invalid_custom_ranges() -> None:
    spec = SplitSpec(mode="custom", custom_ranges="2-a")

    with pytest.raises(ValueError):
        spec.build_output_groups(page_count=6)
