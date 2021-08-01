import functools

from manim import *
from manim_physics import *
import pymunk

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

class AbstractifyTitle(Scene):
    def construct(self):
        self.play(Write(Text("Step 1:", font="cmr10", color=YELLOW).shift(LEFT * 4 + UP * 2)))
        self.play(Write(Text("Abstractify", font="cmr10").scale(3)))

class Konisberg(Scene):
    def construct(self):
        from PIL import Image
        img = Image.open("some1/konigsberg.png")
        konisberg = ImageMobject(img).scale(1.3)

        coords = [UP * 2, DOWN * 0.2 + LEFT, DOWN * 2 + LEFT * 2, RIGHT * 2.5 + DOWN * 0.5]

        vertices = VGroup(*[Circle(radius=0.3, color=BLACK).set_fill(YELLOW, 1).shift(coord) for coord in coords])
        
        self.add(konisberg)
        self.play(*[DrawBorderThenFill(vertex) for vertex in vertices])

        curves = [[UP * 2, LEFT + UP, DOWN * 0.2 + LEFT]]
        for curve in curves:
            # self.play(Create(CubicBezier(*curve)))
            self.play(Create(ParametricFunction(*get_interpolator([(point[0], point[1]) for point in curve]))))
        self.wait(1)