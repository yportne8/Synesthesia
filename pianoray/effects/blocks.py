"""
Blocks effect.
"""

import numpy as np

from ..cpp import Types
from .effect import Effect


class Blocks(Effect):
    """
    The blocks that fall down.
    """

    def render(self, props, img: np.ndarray, frame: int):
        """
        Render the blocks.
        :param notes: MIDI notes from parse_midi.
        """
        self.libs["blocks"].render_blocks(
            img, img.shape[1], img.shape[0],
            frame, self.notes_str,
        )
