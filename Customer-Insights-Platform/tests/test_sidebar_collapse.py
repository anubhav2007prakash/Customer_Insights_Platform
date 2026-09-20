from components.layouts.app_shell import get_sidebar_layout


def test_sidebar_layout_uses_narrower_width_when_collapsed() -> None:
    assert get_sidebar_layout(False) == (0.17, 0.83)
    assert get_sidebar_layout(True) == (0.07, 0.93)
