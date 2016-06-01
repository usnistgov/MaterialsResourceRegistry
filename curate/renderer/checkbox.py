"""
"""
import logging
from curate.renderer.list import ListRenderer

logger = logging.getLogger(__name__)


class CheckboxRenderer(ListRenderer):
    """
    """

    def _render_input(self, element):
        """

        :param element
        :return:
        """

        data = {
            'id': element.pk,
            'value': element.value,
        }

        return self._load_template('checkbox', data)

    def render_module(self, element):
        return ''