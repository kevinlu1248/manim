import random

from manim import *
from manim.opengl import *
from manim_physics import *
from manim_rubikscube import *

from physicsUtils import (
    EPS,
    to_3D,
    get_interpolator,
    ModifiedSpaceScene,
    SpaceSceneWithRopes,
    get_teardrop_curve,
    get_smoother,
)
from puzzleScenes import PuzzleScene
from abstractifyScenes import HomotopyAnimation


class NotationTitle(Scene):
    def construct(self):
        self.play(
            Write(Text("Step 3:", font="cmr10", color=YELLOW).shift(LEFT * 4 + UP * 2))
        )
        self.play(Write(Text("Notation", font="cmr10").scale(3)))

class CubingScene(Scene):
    def construct(self):
         # After creating the RubiksCube, it may be necessary to scale it to
         # comfortably see the cube in the camera's frame
         cube = RubiksCube().scale(0.6)

         # Setup where the camera looks
         self.set_camera_orientation(phi=50*DEGREES, theta=160*DEGREES)
         self.renderer.camera.frame_center = cube.get_center()

         # At this point, you have created a RubiksCube object.
         # All that's left is to add it to the scene.

         # A RubiksCube acts as any other Mobject. It can be added with
         # self.add() or any Manim creation animation
         self.play(
             FadeIn(cube)
         )

         # Rotate the camera around the RubiksCube for 8 seconds
         self.begin_ambient_camera_rotation(rate=0.5)
         self.wait(8)

