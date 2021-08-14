from manim import *
from manim.opengl import *
from manim_physics import *

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

config.frame_rate = 30
# config.frame_rate = 15


class AbstractifyTitle(Scene):
    def construct(self):
        self.play(
            Write(Text("Part 1:", font="cmr10", color=YELLOW).shift(LEFT * 4 + UP * 2))
        )
        self.play(Write(Text("Abstractify", font="cmr10").scale(3)))
        self.wait(10)


class Konisberg(Scene):
    def construct(self):
        from PIL import Image

        img = Image.open("some1/konigsberg.png")
        konisberg = ImageMobject(img).scale(1.3)

        coords = [
            UP * 2,
            DOWN * 0.2 + LEFT,
            DOWN * 2 + LEFT * 2,
            RIGHT * 2.5 + DOWN * 0.5,
        ]

        vertices = VGroup(
            *[
                Circle(radius=0.3, color=BLACK).set_fill(RED, 1).shift(coord)
                for coord in coords
            ]
        )

        self.play(FadeIn(konisberg))
        self.wait(10)
        self.play(*[DrawBorderThenFill(vertex) for vertex in vertices])

        curves = [
            [UP * 2, LEFT + UP * 1.1, LEFT + UP * 1.1, DOWN * 0.2 + LEFT],
            [UP * 2, UP * 0.9, UP * 0.9, DOWN * 0.2 + LEFT],
            [
                DOWN * 0.2 + LEFT,
                LEFT + DOWN * 1.3,
                LEFT + DOWN * 1.3,
                DOWN * 2 + LEFT * 2,
            ],
            [DOWN * 0.2 + LEFT, LEFT * 2 + DOWN, LEFT * 2 + DOWN, DOWN * 2 + LEFT * 2],
            [UP * 2, RIGHT * 2.5 + DOWN * 0.5],
            [DOWN * 0.2 + LEFT, RIGHT * 2.5 + DOWN * 0.5],
        ]
        animations = []
        for curve in curves:
            if len(curve) == 4:
                animations.append(Create(bezier := CubicBezier(*curve, stroke_width=10, color=ORANGE)))
                self.bring_to_back(bezier)
                self.bring_to_back(konisberg)
            if len(curve) == 2:
                animations.append(
                    (Create(line := Line(curve[0], curve[1], color=ORANGE, stroke_width=10)))
                )
                self.bring_to_back(line)
                self.bring_to_back(konisberg)
        self.play(*animations)
        self.wait(1)
        self.play(FadeOut(konisberg))
        self.wait(1)


class AbstractifyAnimation(PuzzleScene):
    def construct(self):
        # requires DEV_MODE = False
        marty, rope, nails, nails_group = (puzzle := self.setup_puzzle())

        self.wait(7)

        self.play(
            FadeOut(*[nail.svg for nail in nails]),
            *[ApplyMethod(nail.set_fill, WHITE, 1) for nail in nails],
        )

        self.wait(2)
        self.play(Flash(marty))
        self.wait(4)
        self.play(rope.redrawn_mobjects["curve"].animate.set_stroke(color=YELLOW))
        self.wait(2)
        self.play(rope.redrawn_mobjects["curve"].animate.set_stroke(color=ORANGE))
        self.wait(10)

        self.add(tracker := Dot(color=ORANGE))
        curve = ParametricFunction(
            rope.redrawn_mobjects["curve"].get_function(), color=ORANGE
        )
        self.add_updater(lambda _: tracker.move_to(curve.data["points"][-1]))
        self.play(Create(curve), run_time=3)
        self.play(Flash(marty))

        self.wait(6)

        self.play(
            *[
                nail.animate.set_stroke(WHITE, opacity=1.0).set_fill(BLACK, 1.0)
                for nail in nails
            ]
        )

        self.wait(10)


class PaperAnalogy(Scene):
    def construct(self):
        # TODO
        # render mode must be opengl
        GRAPHITE_COLOR = "#251607"
        self.camera.set_euler_angles(phi=60 * DEGREES, theta=-45 * DEGREES)
        self.add_updater(
            lambda _: self.camera.set_theta(
                theta=self.camera.data["euler_angles"][0] - 0.1 * DEGREES
            )
        )

        self.play(
            GrowFromCenter(
                paper := OpenGLSurface(
                    lambda u, v: np.array([u, v, 0]),
                    u_range=[-5, 5],
                    v_range=[-5, 5],
                    color="#f2eecb",
                )
            ),
            run_time=3,
        )
        self.wait(1)
        self.play(
            GrowFromCenter(
                hole1 := Circle(0.5, color=WHITE)
                .set_fill(BLACK, 1)
                .shift(LEFT * 2 + UP)
            ),
            GrowFromCenter(
                hole2 := Circle(0.5, color=WHITE)
                .set_fill(BLACK, 1)
                .shift(LEFT * 2 + DOWN)
            ),
            run_time=3,
        )
        marty = Dot(color=YELLOW)
        marty.set_fill(GRAPHITE_COLOR, 1)
        self.play(Create(marty))
        curve = ParametricFunction(
            *PuzzleScene.get_curve("BT"), use_smoothing=False, color=GRAPHITE_COLOR
        )

        pencil_radius = 0.15
        pencil_tip_length = 0.5
        pencil_body_height = 3
        pencil_base = OpenGLSurface(
            Cylinder(pencil_radius, height=1, add_bases=True, checkerboard_color=YELLOW)
            .shift([0, 0, 1])
            .func,
            u_range=(0, pencil_body_height),
            v_range=(0, 2 * PI),
            color=YELLOW,
        ).shift([0, 0, pencil_tip_length])
        pencil_tip = OpenGLSurface(
            Cone(pencil_radius, pencil_tip_length, direction=[0, 0, -1]).func,
            u_range=(-(pencil_tip_length + 0.05), 0),
            v_range=(0, 2 * PI),
            color="#caa472",
        )
        pencil_cap = OpenGLSurface(
            lambda u, v: [
                v * np.cos(u),
                v * np.sin(u),
                pencil_body_height + pencil_tip_length,
            ],
            u_range=(0, 2 * PI),
            v_range=(0, pencil_radius),
            color=YELLOW,
        )

        pencil = Group(pencil_base, pencil_tip, pencil_cap)

        self.play(FadeIn(pencil))
        pencil.add_updater(
            lambda _: pencil.move_to(
                curve.data["points"][-1]
                + np.array([0, 0, (pencil_tip_length + pencil_body_height) / 2])
            )
        )
        self.play(Create(curve, lag_ratio=0), run_time=7)
        self.wait(2)

        # TODO: tilt pencil

        plane = Group(hole1, hole2, paper)
        self.play(FadeOut(pencil, curve, marty))
        self.play(ApplyMethod(plane.scale, 0.01))
        self.remove(plane)


class SameLoopsQuestion(Scene):
    def construct(self):
        self.play(
            Write(
                Text("How do we know if two loops are the same?", font="cmr10").scale(
                    0.8
                )
            ),
            run_time=2,
        )
        self.wait(3)


class SameLoopsL(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(*PuzzleScene.get_curve("T"))
        )

        marty.set_moment((0.3, 0))
        self.wait(5)
        nails[0].disappear()
        marty.set_moment((0.5, 0))
        self.wait(4)
        self.reset_puzzle(*puzzle)


class SameLoopsR(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                *get_interpolator([(0, 0), (-1, 2), (-3, 3), (-4, 2), (-1, 0)])
            )
        )

        marty.set_moment((0.3, 0))
        self.wait(5)
        nails[0].disappear()
        marty.set_moment((0.5, 0))
        self.wait(4)
        self.reset_puzzle(*puzzle)


class EquivalentLoops_1(PuzzleScene):
    def construct(self):
        #     self.play(FadeIn(question_mark := Text("?", font="cmr10").scale(5)))
        #     self.wait(3)
        #     self.play(FadeOut(question_mark))
        # TODO: add split screen scene

        puzzles = [self.setup_puzzle(do_add=False) for _ in range(2)]
        puzzles_vgroups = [(marty, rope, *nails) for marty, rope, nails in range(2)]
        self.add(puzzles_vgroup)
        # print(puzzles)
        # puzzles_vgroup = VGroup(*[marty for marty, rope, nails, nails_group in puzzles])
        # puzzles_vgroup.set_x(0).arrange(buff=7.0)
        # self.add(puzzles_vgroup)
        self.wait(1)


class HomotopyAnimation(Animation):
    def __init__(self, curve, other_curve, **kwargs):
        if not isinstance(curve, ParametricFunction) or not isinstance(
            other_curve, ParametricFunction
        ):
            raise TypeError("Curves must be parametric functions")
        self.og_func = curve.get_function()
        self.other_curve_func = other_curve.get_function()
        super().__init__(curve, **kwargs)

    def interpolate_mobject(self, alpha):
        self.mobject.function = lambda t: alpha * self.other_curve_func(t) + (
            1 - alpha
        ) * self.og_func(t)

        if "points" not in self.mobject.data:
            return
        n = len(self.mobject.data["points"])
        self.mobject.data["points"] = [self.mobject.function(0)] * n
        self.mobject.init_points()
        self.mobject.data["points"] = self.mobject.data["points"][n:]


class HomotopyWithColorChange(HomotopyAnimation):
    def interpolate_mobject(self, alpha):
        """Extremely artificial and not generalizable"""
        super().interpolate_mobject(alpha)
        for point in self.mobject.data["points"]:
            if (
                np.linalg.norm(point - (LEFT * 2 + UP)) <= 0.5
                or np.linalg.norm(point - (LEFT * 2 + UP)) <= 0.5
            ):
                self.mobject.set_stroke(RED)
                break
        else:
            self.mobject.set_stroke(GREEN)


class EquivalentLoopsHomotopy(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                *get_interpolator([(0, 0), (2, 1), (1, 2)]), use_circle_nails=True
            )
        )

        other_curve_func, other_t_range = get_interpolator([(0, 0), (1, -2), (3, -2)])
        # self.wait(1)
        # self.play(
        #     Create(
        #         curve := ParametricFunction(other_curve_func, other_t_range, color=BLUE)
        #     ),
        # )
        # self.wait(1)

        # self.play(
        #     HomotopyAnimation(
        #         curve,
        #         rope.redrawn_mobjects["curve"],
        #         rate_func=rate_functions.ease_in_out_cubic,
        #     ),
        #     run_time=5,
        # )
        # self.play(FadeOut(curve))
        # self.wait(1)

        func, range = PuzzleScene.get_curve("T")
        curve = ParametricFunction(lambda t: func(1 - t), color=GREEN)

        # not_allowed_func = lambda t: 0.15 * rope.redrawn_mobjects[
        #     "curve"
        # ].get_function()(t) + (1 - 0.15) * func(1 - t)

        not_allowed_func, _ = get_interpolator([
            (0, 0),
            (-2, 0),
            (-3, 1),
            (-2, 2)
        ])

        self.play(Create(curve))
        self.play(
            Homotopy(
                curve,
                ParametricFunction(not_allowed_func),
                rate_func=rate_functions.ease_in_out_cubic,
            ),
            run_time=2,
        )
        self.play(
            HomotopyWithColorChange(
                curve,
                ParametricFunction(lambda t: func(1 - t)),
                rate_func=rate_functions.ease_in_out_cubic,
            ),
            run_time=2,
        )

        self.wait(7)

        self.play(ApplyMethod(nails[0].set_fill, WHITE, 1))
        self.play(FadeOut(nails[0]))

        self.play(
            HomotopyAnimation(
                curve,
                rope.redrawn_mobjects["curve"],
                rate_func=rate_functions.ease_in_out_cubic,
            ),
            run_time=3,
        )

        self.wait(5)


class AbstractifiedQuestionSummary(Scene):
    def construct(self):
        text = """
        New question:
        How do we construct a loop not equivalent
        to a loop going around neither holes, 
        unless a hole is filled in?
        """.strip().replace(
            " " * 8, ""
        )
        lines = text.split("\n")
        par = Paragraph(
            *text.split("\n"), line_spacing=2, font="cmr10", disable_ligatures=True
        )
        highlight_texts = [
            [],
            ["not equivalent"],
            ["loop going around neither holes"],
            ["unless"],
        ]

        for i in range(len(par)):
            for text in highlight_texts[i]:
                par[i][lines[i].find(text) : lines[i].find(text) + len(text)].set_color(
                    YELLOW
                )
            self.play(Write(par[i]))
            if i == 0:
                self.wait(3)
        self.wait(9)


class AbstractifySummarySlide(Scene):
    def construct(self):
        # TODO: make better timings
        text = f"""
        Summary of Section:
        1. We simplified this puzzle down to 
          - A 2D plane with two holes
          - Marty (a point)
          - The leash (a loop confined within the plane)
        2. Leash must follow the following constraints:
          - Within the plane
          - Two loops are equivalent if they can move between
            each other through a motion confined within the plane
        """.strip().replace(
            " " * 8, ""
        )

        lines = text.split("\n")

        par = Paragraph(
            *text.split("\n"), line_spacing=2, font="cmr10", disable_ligatures=True
        ).scale(0.5)

        highlight_texts = [
            [],
            [],
            ["2D plane", "two holes"],
            ["point"],
            ["loop"],
            [],
            ["Within"],
            ["equivalent", "motion confined within the plane"],
            [],
        ]

        for i in range(len(par)):
            for text in highlight_texts[i]:
                par[i][lines[i].find(text) : lines[i].find(text) + len(text)].set_color(
                    YELLOW
                )
            self.play(Write(par[i]))
            self.wait(1)
        self.wait(3)
        self.play(FadeOut(par))

        self.wait(1)
