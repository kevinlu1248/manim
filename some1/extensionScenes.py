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


class ExtensionTitle(Scene):
    def construct(self):
        self.play(
            Write(Text("Part 4:", font="cmr10", color=YELLOW).shift(LEFT * 4 + UP * 2))
        )
        self.play(Write(Text("Extension", font="cmr10").scale(3)))


class ThreeStakes(PuzzleScene):
    def construct(self):
        marty, _unused_rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                nail_positions=[LEFT * 2 + UP * 1.5, LEFT * 2, LEFT * 2 + DOWN * 1.5],
                do_add=False,
            )
        )
        self.play(FadeIn(marty, *nails, *[nail.svg for nail in nails]))

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

        self.play(Write(r_text := Text("R", font="cmr10").next_to(nails[1], RIGHT * 2)))

        self.wait(1)

        # TODO: use homotopy

        self.play(
            FadeOut(*nails, r_text),
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

        self.wait(1)


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

        self.play(FadeOut(par))
