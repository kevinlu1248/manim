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
from rephraseScenes import concat_funcs
from notationScenes import to_latex

import pymunk


class ExtensionTitle(Scene):
    def construct(self):
        self.play(
            Write(Text("Part 4:", font="cmr10", color=YELLOW).shift(LEFT * 4 + UP * 2), run_time=3)
        )
        self.play(Write(Text("Extension", font="cmr10").scale(3)), run_time=3)
        self.wait(20)


class ThreeStakes(PuzzleScene):
    def construct(self):
        marty, _unused_rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                nail_positions=[LEFT * 2 + UP * 1.5, LEFT * 2, LEFT * 2 + DOWN * 1.5],
                do_add=False,
            )
        )
        self.play(FadeIn(marty, *nails, *[nail.svg for nail in nails], marty.image))
        self.wait(10)

        self.play(
            FadeOut(*[nail.svg for nail in nails]),
            *[nail.animate.set_stroke(WHITE, opacity=1.0) for nail in nails],
        )

        self.wait(1)

        self.play(
            nails[0].animate.move_to(
                2 * np.array([np.cos(2 * PI / 3), np.sin(2 * PI / 3), 0])
            ),
            nails[2].animate.move_to(
                2 * np.array([np.cos(4 * PI / 3), np.sin(4 * PI / 3), 0])
            ),
            nails[1].animate.move_to(2 * RIGHT),
        )


        self.wait(3)

        # TODO: use homotopy

        self.play(
            FadeOut(*nails),
            FadeIn(
                ParametricFunction(
                    lambda t: 3
                    * np.array(
                        [np.cos(3 * t) * np.cos(t), np.cos(3 * t) * np.sin(t), 0]
                    ),
                    t_range=[0, 2 * PI],
                )
            ),
        )
        
        self.wait(2)

        self.play(Write(r_text := Text("R", font="cmr10").next_to(nails[1], RIGHT * 4)))

        self.wait(2)


class ExtensionStakes(Scene):
    def construct(self):
        text = f"""
        Possible extensions:
        1. 3 stakes?
        2. 3 stakes, but pulling 2 is required?
        3. n stakes?
        4. n stakes, but pulling k is required?
        """.strip().replace(
            " " * 8, ""
        )

        lines = text.split("\n")

        par = Paragraph(
            *text.split("\n"), line_spacing=1.5, font="cmr10", disable_ligatures=True
        ).scale(0.8)

        highlight_texts = [
            [],
            ["3"],
            ["3", "2 "],
            ["n"],
            ["n", "k "],
        ]

        for i in range(len(par)):
            for text in highlight_texts[i]:
                par[i][lines[i].find(text) : lines[i].find(text) + len(text)].set_color(
                    YELLOW
                )
            self.play(Write(par[i]))
            if i >= 1:
                self.wait(2)

        self.wait(20)
        # self.play(FadeOut(par))

class PictureHanging_1(SpaceSceneWithRopes):
    def construct(self):
        self.space.space.gravity = 0, 0
        self.space.space.damping = 0.3
        self.play(
            Create(nail1 := Circle(radius=.5).shift(LEFT * 2 + UP * 2).set_stroke(WHITE)),
            Create(nail2 := Circle(radius=.5).shift(RIGHT * 2 + UP * 2).set_stroke(WHITE))
        )
        self.make_static_body(nail1, nail2)
        default_rope_config = {
            "k": 22,
            "do_loop": True,
            "color": ORANGE,
            # "offset": 0
            "rope_creation_speed": 3
        }
        rope = self.make_rope(
            *get_interpolator([
                (0, -2), 
                (-3, 2),
                (-2, 3),
                (0, 3),
                (2, 1),
                (3, 2),
                (2, 3),
                (0, 3),
                (-2, 3),
                (-3, 2),
                (-2, 1),
                (0, 2),
                (2, 3),
                (3, 2),
                (1, -1.5)
            ], offset=0),
            **default_rope_config
        )
        self.space.space.gravity = 0, -10
        self.wait(2)
        nail2.shape.filter = pymunk.ShapeFilter(group=PuzzleScene.num_of_chains)
        self.play(FadeOut(nail2))
        self.wait(4)
        self.play(FadeOut(nail1))


class PictureHanging_2(SpaceSceneWithRopes):
    def construct(self):
        self.space.space.gravity = 0, 0
        self.space.space.damping = 0.3
        self.play(
            Create(nail1 := Circle(radius=.5).shift(LEFT * 2 + UP * 2).set_stroke(WHITE)),
            Create(nail2 := Circle(radius=.5).shift(RIGHT * 2 + UP * 2).set_stroke(WHITE))
        )
        self.make_static_body(nail1, nail2)
        default_rope_config = {
            "k": 22,
            "do_loop": True,
            "color": ORANGE,
            # "offset": 0
            "rope_creation_speed": 3
        }
        rope = self.make_rope(
            *get_interpolator([
                (0, -2), 
                (-3, 2),
                (-2, 3),
                (0, 3),
                (2, 1),
                (3, 2),
                (2, 3),
                (0, 3),
                (-2, 3),
                (-3, 2),
                (-2, 1),
                (0, 2),
                (2, 3),
                (3, 2),
                (1, -1.5)
            ], offset=0),
            **default_rope_config
        )
        self.space.space.gravity = 0, -10
        self.wait(2)
        nail1.shape.filter = pymunk.ShapeFilter(group=PuzzleScene.num_of_chains)
        self.play(FadeOut(nail1))
        self.wait(4)
        self.play(FadeOut(nail2))

class FurtherTitle(Scene):
    def construct(self):
        self.play(
            Write(Text("Part 5:", font="cmr10", color=YELLOW).shift(LEFT * 4 + UP * 2))
        )
        self.play(Write(Text("Further", font="cmr10").scale(3)))
        self.wait(18)

class FurtherTopics(Scene):
    def construct(self):
        hint = """
        Related or used topics:
        - Homotopy = equivalences via a continuous motion
        - Fundamental groups =  loops in some space under homotopy
        - Free groups = sequences of letters and their inverses
        - Knot theory = study of knots
        """.strip().replace(" " * 8, "")
        self.play(
            FadeIn(
                Paragraph(
                    *hint.split("\n"), line_spacing=2, font="cmr10", align="center"
                ).scale(0.6)
            )
        )
        self.wait(5)