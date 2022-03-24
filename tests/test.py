#
#  PianoRay
#  Video rendering pipeline with piano visualization.
#  Copyright  PianoRay Authors  2022
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import numpy as np
from pianoray import BasePipeline


class Pipeline(BasePipeline):
    meta = {
        "start": 0,
        "end": 30,
        "res": (1920, 1080),
        "fps": 30,
    }

    def render_frame(self, frame):
        if frame == 0:
            # Testing stuff
            print(self.kernels.jtest(None))
            print(self.kernels.pytest(None))
            print(self.kernels.ctest(None))

        res = self.meta["res"]

        img = np.zeros((res[1], res[0], 3), dtype=np.uint8)
        img[..., 0] = 255

        return img
