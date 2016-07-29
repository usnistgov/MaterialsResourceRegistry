from django.test import TestCase
from utils.XSDParser.parser import _fmt_tooltip


class TestFormatTooltip(TestCase):
    """
    """
    def setUp(self):
        pass

    def test_empty(self):
        tooltip = ""
        result = _fmt_tooltip(tooltip)
        self.assertEquals(tooltip, result)

    def test_same_length(self):
        tooltip = "aaaaaaaaaa"
        width = 10
        result = _fmt_tooltip(tooltip, width)
        self.assertEquals(tooltip, result)

    def test_inferior_length(self):
        tooltip = "aaaaaa"
        width = 10
        result = _fmt_tooltip(tooltip, width)
        lines = result.split('\n')
        for line in lines:
            self.assertTrue(len(line) <= width)

    def test_wrap_half(self):
        tooltip = "aaaaaaaaaa"
        width = 5
        result = _fmt_tooltip(tooltip, width)
        lines = result.split('\n')
        for line in lines:
            self.assertTrue(len(line) <= width)

    def test_wrap_half_space(self):
        tooltip = "aaaa aaaaaa"
        width = 5
        result = _fmt_tooltip(tooltip, width)
        lines = result.split('\n')
        for line in lines:
            self.assertTrue(len(line) <= width)

    def test_wrap_half_2_lines(self):
        tooltip = "aaaa\naaaaaa"
        width = 5
        result = _fmt_tooltip(tooltip, width)
        lines = result.split('\n')
        for line in lines:
            self.assertTrue(len(line) <= width)

    def test_wrap_half_2_lines_middle(self):
        tooltip = "aaaaa\naaaaa"
        width = 5
        result = _fmt_tooltip(tooltip, width)
        lines = result.split('\n')
        for line in lines:
            self.assertTrue(len(line) <= width)