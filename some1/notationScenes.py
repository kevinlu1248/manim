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
from rephraseScenes import concat_funcs


class NotationTitle(Scene):
    def construct(self):
        self.play(
            Write(Text("Part 3:", font="cmr10", color=YELLOW).shift(LEFT * 4 + UP * 2), run_time=3)
        )
        self.play(Write(Text("Notation", font="cmr10").scale(3)), run_time=3)
        self.wait(10)


class CubingScene(ThreeDScene):
    def construct(self):
        cube = RubiksCube().scale(0.6).move_to(ORIGIN)

        self.set_camera_orientation(phi=60 * DEGREES, theta=200 * DEGREES)
        self.begin_ambient_camera_rotation(rate=0.02)
        self.renderer.camera.frame_center = cube.get_center()

        self.play(FadeIn(cube))
        self.wait(10)

        algo = ["R'", "F", "R", "F'"]
        algo_display = Text("".join(algo), font="cmr10").scale(1.5)
        self.add_fixed_in_frame_mobjects(algo_display)
        algo_display.shift(UP * 3 + LEFT * 4.5)
        self.play(FadeIn(algo_display))
        self.wait(6)

        indices = [0, 2, 3, 4, 6]

        for i in range(len(algo)):
            self.play(
                algo_display[indices[i] : indices[i + 1]].animate.set_color(YELLOW),
                run_time=0.5,
            )
            self.play(CubeMove(cube, algo[i]))
            self.play(
                algo_display[indices[i] : indices[i + 1]].animate.set_color(WHITE),
                run_time=0.5,
            )
        self.wait(1)


class NotationIntro(PuzzleScene):
    def construct(self):
        marty, _unused_rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                nail_positions=[UP * 1.5, DOWN * 1.5],
                nail_radius=1.5,
                do_add=False,
            )
        )
        [nail.set_stroke(WHITE, opacity=1.0) for nail in nails]
        self.play(FadeIn(marty, *nails))
        self.wait(4)

        curve_notations = [
            (
                lambda t: DOWN * 1.5
                + 1.5
                * np.array(
                    [np.cos((-t + 1 / 4) * PI * 2), np.sin((-t + 1 / 4) * PI * 2), 0]
                ),
                Text("B", font="cmr10"),
            ),
            (
                lambda t: UP * 1.5
                + 1.5
                * np.array(
                    [np.cos((-t - 1 / 4) * PI * 2), np.sin((-t - 1 / 4) * PI * 2), 0]
                ),
                Text("T", font="cmr10"),
            ),
            (
                lambda t: DOWN * 1.5
                + 1.5
                * np.array(
                    [np.cos((t + 1 / 4) * PI * 2), np.sin((t + 1 / 4) * PI * 2), 0]
                ),
                MathTex(r"\overline{\text{B}}"),
            ),
            (
                lambda t: UP * 1.5
                + 1.5
                * np.array(
                    [np.cos((t - 1 / 4) * PI * 2), np.sin((t - 1 / 4) * PI * 2), 0]
                ),
                MathTex(r"\overline{\text{T}}"),
            ),
        ]

        for func, char in curve_notations:
            self.play(
                Create(
                    curve := ParametricFunction(
                        func,
                        color=ORANGE,
                    )
                ),
                Write(text := char.scale(3).shift(LEFT * 4)),
                run_time=1.5
            )
            self.play(FadeOut(curve, text))

        self.wait(2)

        self.play(
            FadeOut(marty, *nails),
            FadeIn(
                equals := Text(":", font="cmr10").shift(LEFT * 3),
                plus_1 := Text("→", font="cmr10"),
                plus_2 := Text("→", font="cmr10").shift(RIGHT * 3),
                curve := ParametricFunction(
                    *get_interpolator(
                        [
                            (0, 0),
                            (1.8, -1.8),
                            (0, -3.6),
                            (-1.8, -1.8),
                            (-0.5, 0),
                            (0, 0),
                            (-0.5, 0),
                            (-1.8, 1.8),
                            (0, 3.6),
                            (1.8, 1.8),
                            (0, 0),
                            (-2, 2),
                            (0, 3.8),
                            (2, 2),
                        ]
                    ),
                    color=ORANGE,
                )
                .scale(0.3)
                .move_to(LEFT * 4.5),
                b_curve := ParametricFunction(
                    *get_interpolator(
                        [
                            (0, 0),
                            (1.8, -1.8),
                            (0, -3.6),
                            (-1.8, -1.8),
                        ]
                    ),
                    color=BLUE,
                )
                .scale(0.3)
                .move_to(LEFT * 1.5),
                t_curve_1 := ParametricFunction(
                    *get_interpolator(
                        [
                            (0, 0),
                            (-1.8, 1.8),
                            (0, 3.6),
                            (1.8, 1.8),
                        ]
                    ),
                    color=GREEN,
                )
                .scale(0.3)
                .move_to(RIGHT * 1.5),
                t_curve_2 := ParametricFunction(
                    *get_interpolator(
                        [
                            (0, 0),
                            (-2, 2),
                            (0, 3.8),
                            (2, 2),
                        ]
                    ),
                    color=RED,
                )
                .scale(0.3)
                .move_to(RIGHT * 4.5),
            ),
        )

        self.wait(1)

        self.play(
            FadeOut(b_curve, t_curve_1, t_curve_2),
            FadeIn(
                b_text := Text("B", font="cmr10").move_to(LEFT * 1.5),
                t_text_1 := Text("T", font="cmr10").move_to(RIGHT * 1.5),
                t_text_2 := Text("T", font="cmr10").move_to(RIGHT * 4.5),
            ),
        )

        self.play(
            FadeOut(plus_1, plus_2),
            curve.animate.move_to(LEFT * 3),
            equals.animate.move_to(LEFT * 1.5),
            b_text.animate.move_to(ORIGIN),
            t_text_1.animate.move_to(RIGHT * 1.5),
            t_text_2.animate.move_to(RIGHT * 3),
        )
        
        self.wait(3)

        self.play(
            FadeOut(curve, b_text, equals, t_text_1, t_text_2), FadeIn(marty, *nails)
        )

        self.wait(3)

        self.play(
            marty.animate.move_to(ORIGIN),
            nails[0].animate.move_to(LEFT * 2 + UP).scale(1 / 3),
            nails[1].animate.move_to(LEFT * 2 + DOWN).scale(1 / 3),
        )

        self.play(
            Create(ParametricFunction(*PuzzleScene.get_curve("BTT"), color=ORANGE)),
            Write(Text("BTT", font="cmr10").shift(RIGHT * 3).scale(2)),
            run_time=2,
        )

        self.wait(16)


class NonCommutativity(PuzzleScene):
    def construct(self):
        marty1, _unused_rope1, nails1, nails_group1 = (
            puzzle := self.setup_puzzle(
                do_add=False,
            )
        )
        [nail.set_stroke(WHITE, opacity=1.0) for nail in nails1]
        [mobject.shift(LEFT * 2) for mobject in (marty1, *nails1)]

        marty2, _unused_rope2, nails2, nails_group2 = (
            puzzle := self.setup_puzzle(
                do_add=False,
            )
        )
        [nail.set_stroke(WHITE, opacity=1.0) for nail in nails2]
        [mobject.shift(RIGHT * 4) for mobject in (marty2, *nails2)]
        self.play(FadeIn(marty1, marty2, *nails1, *nails2))

        self.play(
            Create(
                ParametricFunction(*PuzzleScene.get_curve("TB"), color=ORANGE).shift(
                    LEFT * 2
                )
            ),
            Create(
                ParametricFunction(*PuzzleScene.get_curve("BT"), color=ORANGE).shift(
                    RIGHT * 4
                )
            ),
            Write(
                Text("TB", font="cmr10").scale(1.5).shift(LEFT * 2 + UP * 2.5)
            ),
            Write(
                Text("BT", font="cmr10").scale(1.5).shift(RIGHT * 4 + UP * 2.5)
            ),
            run_time=3,
        )

        self.wait(15)
        # self.play(FadeOut(*self.mobjects))


def to_latex(*simplified_notations):
    ans = [
        simplified_notation.replace("T'", r"\overline{\text{T}}")
        .replace("B'", r"\overline{\text{B}}")
        .replace("T", r"\text{T}}")
        .replace("B", r"\text{B}")
        for simplified_notation in simplified_notations
    ]
    if len(ans) == 1:
        return ans[0]
    else:
        return ans


class Inversibility(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                concat_funcs(
                    PuzzleScene.get_curve("B")[0], PuzzleScene.get_curve("B'")[0]
                ),
                t_range=[0, 1],
                use_circle_nails=True,
            )
        )
        marty.set_moment((0.5, 0))
        self.wait(2)
        self.play(
            Write(
                notation := MathTex(r"\text{B}\overline{\text{B}}")
                .scale(2)
                .shift(UP * 2.5)
            )
        )
        self.wait(1)
        marty.set_moment((1.5, 0))
        self.wait(1)

        self.play(FadeOut(rope.redrawn_mobjects["curve"], *nails))

        self.play(
            notation.animate.move_to(LEFT * 3.3 + UP * 0.2),
            Write(Tex(" = U (the unloop)", color=YELLOW).scale(2).shift(RIGHT * 1.5)),
        )

        self.wait(2)

        for simplified_notation in ("TT'", "B'B", "T'T"):
            self.play(
                FadeOut(notation),
                Write(
                    notation := MathTex(to_latex(simplified_notation))
                    .scale(2)
                    .next_to(notation, ORIGIN)
                ),
            )
            self.wait(1)
            if simplified_notation == "TT'":
                self.wait(2)
        
        self.wait(2)


class InversibilityInside(PuzzleScene):
    def construct(self):

        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                concat_funcs(
                    PuzzleScene.get_curve("BT")[0],
                    PuzzleScene.get_curve("T'", radius=0.9)[0],
                ),
                [0, 1],
                use_circle_nails=True,
                rope_config={
                    "k": 18,
                },
            )
        )
        self.wait(7)
        marty.set_moment((0.5, 0))
        self.play(Write(notation := MathTex(to_latex("BTT'")).scale(2).shift(UP * 2.5)))
        self.play(
            self.camera.animate.shift(RIGHT * 2), notation.animate.shift(RIGHT * 2)
        )
        self.wait(3)

        # TODO: fix
        self.play(
            FadeOut(notation),
            Write(notation := Text("B", font="cmr10").scale(2).move_to(notation)),
        )

        self.remove(marty)
        self.play(
            FadeOut(rope.redrawn_mobjects["curve"], *nails, notation, marty.image), Flash(marty)
        )


class InversibilityText(Scene):
    def construct(self):
        current_string = [r"\text{U} = " + to_latex("TT'")]
        self.play(Write(eq := MathTex(*current_string).scale(2)))
        possibilities = ("TT'", "T'T", "B'B", "BB'")
        for _ in range(5):
            current_string.append(to_latex(random.choice(possibilities)))
            new_eq = MathTex(*current_string).scale(2)
            self.play(eq.animate.move_to(new_eq[:-1]), Write(new_eq[-1]))
            self.add(new_eq)
            self.remove(eq)
            eq = new_eq
        self.wait(8)


class FurtherNonCommutativity(PuzzleScene):
    def construct(self):
        # TBT' != TTB
        self.play(Write(unequal := MathTex(to_latex("BTT' = B")).scale(2)))
        self.wait(1)
        self.play(unequal.animate.shift(UP * 2), Write(MathTex(r"\text{but}").scale(2)))
        self.wait(1)
        self.play(Write(MathTex(to_latex(r"TBT' \not= B")).scale(2).shift(DOWN * 2)))
        self.wait(5)
        # self.play(FadeOut(*self.mobjects))


# class FurtherNonCommutativity(PuzzleScene):
#     def construct(self):


class FillingHole(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                *PuzzleScene.get_curve("TBT'"),
                use_circle_nails=True,
                rope_config={
                    "k": 18,
                    "rope_creation_speed": 3,
                    "animations_at_creation": Write(
                        notation := MathTex(*to_latex("T", "B", "T'"))
                        .scale(2)
                        .shift(UP * 2.5)
                    ),
                },
            )
        )
        marty.set_moment((0.5, 0))
        self.play(
            self.camera.animate.shift(RIGHT * 2), notation.animate.shift(RIGHT * 2)
        )
        self.wait(7)
        nails[0].disappear()
        self.wait(3)
        self.play(
            FadeOut(notation[0], notation[2]),
        )
        self.wait(3)
        self.remove(marty)
        self.play(
            FadeOut(
                rope.redrawn_mobjects["curve"],
                *[nail for nail in nails if nail in self.mobjects],
                notation[1],
                marty.image,
            ),
            Flash(marty),
        )
        self.wait(5)


class NotationSummary(Scene):
    def construct(self):
        # text = r"""
        # \begin{flushleft}
        # Filling the holes with the new notation:\\ 
        # - Top hole = removing all occurences of B, $\overline{\text{B}}$\\ 
        # - Bottom hole = removing all occurences of T, $\overline{\text{T}}$
        # \end{flushleft}
        # """.strip().replace(
        #     " " * 8, ""
        # )

        # lines = text.split("\n")

        # par = Tex(text, line_spacing=2)  # TODO: adjust line spacing

        # self.play(Write(par))
        # self.wait(3)

        # self.play(FadeOut(par))

        hint = r"""
        \begin{flushleft}
        Rephrased puzzle: \\ 
        Is there a sequence composed of B, B', T, and T' (not equal to U), \\ 
        such that removing all occurences of B and B', or T and T' \\ 
        will result in the remaining terms cancelling out to form U?
        \end{flushleft}
        """.replace(
            "B'", r"$\overline{\text{B}}$"
        ).replace(
            "T'", r"$\overline{\text{T}}$"
        )
        self.play(FadeIn(Tex(hint, font="cmr10").scale(0.85)), run_time=1)
        self.wait(18)


class CloseToAnswer(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                *PuzzleScene.get_curve("TBT'"),
                use_circle_nails=True,
                rope_config={
                    "k": 18,
                    "rope_creation_speed": 3,
                    "animations_at_creation": Write(
                        notation := MathTex(*to_latex("T", "B", "T'"))
                        .scale(2)
                        .shift(UP * 2.5)
                    ),
                },
            )
        )
        marty.set_moment((0.5, 0))
        self.wait(6)
        nails[1].disappear()
        new_notation = MathTex(*to_latex("T", "T'")).scale(2).shift(UP * 2.5)
        self.wait(1)
        self.play(
            FadeOut(notation[1]),
            notation[0].animate.move_to(new_notation[0]),
            notation[2].animate.move_to(new_notation[1]),
        )
        self.remove(notation)
        self.add(new_notation)
        notation = new_notation
        self.wait(1)
        self.play(
            FadeOut(notation),
            Write(notation := MathTex(r"\text{U}").scale(2).move_to(notation)),
        )
        self.wait(3)
        self.play(
            FadeOut(
                rope.redrawn_mobjects["curve"],
                *[nail for nail in nails if nail in self.mobjects],
                notation,
            )
        )

class CloseToAnswerText(Scene):
    def construct(self):
        self.play(Write(initial_text := MathTex(*to_latex("T", "B", "T'")).scale(2)))
        self.wait(5)
        to_text = MathTex(*to_latex("T", "B", "T'", "B'")).scale(2)
        self.play(initial_text.animate.move_to(to_text[:-1]), Write(to_text[-1]))
        self.wait(10)


class FinalAnswer_1(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                *PuzzleScene.get_curve("TBT'B'"),
                use_circle_nails=True,
                rope_config={
                    "k": 18,
                    "rope_creation_speed": 3,
                    "animations_at_creation": Write(
                        notation := MathTex(*to_latex("T", "B", "T'", "B'"))
                        .scale(2)
                        .shift(UP * 2.5)
                    ),
                },
            )
        )
        marty.set_moment((0.5, 0))
        self.wait(8)
        nails[1].disappear()
        new_notation = MathTex(*to_latex("T", "T'")).scale(2).shift(UP * 2.5)
        self.wait(1)
        self.play(
            FadeOut(notation[1], notation[3]),
            notation[0].animate.move_to(new_notation[0]),
            notation[2].animate.move_to(new_notation[1]),
        )
        self.remove(notation)
        self.add(notation := new_notation)
        self.wait(1)
        self.play(
            FadeOut(notation),
            Write(notation := MathTex(r"\text{U}").scale(2).move_to(notation)),
        )
        self.wait(3)
        self.play(
            FadeOut(
                rope.redrawn_mobjects["curve"],
                *[nail for nail in nails if nail in self.mobjects],
                notation,
            )
        )


class FinalAnswer_2(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                *PuzzleScene.get_curve("TBT'B'"),
                use_circle_nails=True,
                rope_config={
                    "k": 18,
                    "rope_creation_speed": 3,
                    "animations_at_creation": Write(
                        notation := MathTex(*to_latex("T", "B", "T'", "B'"))
                        .scale(2)
                        .shift(UP * 2.5)
                    ),
                },
            )
        )
        marty.set_moment((0.5, 0))
        self.wait(8)
        nails[0].disappear()
        new_notation = MathTex(*to_latex("B", "B'")).scale(2).shift(UP * 2.5)
        self.wait(1)
        self.play(
            FadeOut(notation[0], notation[2]),
            notation[1].animate.move_to(new_notation[0]),
            notation[3].animate.move_to(new_notation[1]),
        )
        self.remove(notation)
        self.add(notation := new_notation)
        self.wait(1)
        self.play(
            FadeOut(notation),
            Write(notation := MathTex(r"\text{U}").scale(2).move_to(notation)),
        )
        self.wait(3)
        self.play(
            FadeOut(
                rope.redrawn_mobjects["curve"],
                *[nail for nail in nails if nail in self.mobjects],
                notation,
            )
        )


class NotationAnswer(Scene):
    def construct(self):
        self.play(
            Write(eq := Tex("U ", "$=$ ").scale(2).shift(LEFT * 2.7 + DOWN * 0.1)),
            Write(
                src := MathTex(*to_latex("T", "T'", "B", "B'")).scale(2),
            ),
        )
        self.wait(10)
        self.play(
            FadeOut(eq[1]),
            FadeIn(Tex(r"$\not=$ ").scale(2).move_to(eq[1])),
            TransformMatchingShapes(
                src[1:-1],
                MathTex(*to_latex("T", "B", "T'", "B'")).scale(2)[1:-1],
                path_arc=PI / 2,
            ),
        )
        self.wait(5)


class SolutionSummary(Scene):
    def construct(self):
        text = f"""
        Summary of Solution:
        1. Abstractify to loops on a 2D plane with two holes, 
        with a definition of equivalence.
        2. Simplify the space from a plane to a figure eight.
        3. Use a notation to describe the loops, and rephrase 
        the puzzle to a question about sequences of letters.
        """.strip().replace(
            " " * 8, ""
        )

        lines = text.split("\n")

        par = Paragraph(
            *text.split("\n"), line_spacing=1.5, font="cmr10", disable_ligatures=True
        ).scale(0.8)

        highlight_texts = [
            [],
            ["Abstractify", "2D plane with two holes"],
            ["equivalence"],
            ["Simplify", "figure eight"],
            ["notation", "rephrase"],
            ["sequences of letters"],
        ]

        for i in range(len(par)):
            for text in highlight_texts[i]:
                par[i][lines[i].find(text) : lines[i].find(text) + len(text)].set_color(
                    YELLOW
                )
            self.play(Write(par[i]))
            if i in (2, 3, 5):
                self.wait(2)

        self.play(FadeOut(par))
