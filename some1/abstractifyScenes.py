import functools

from manim import *
from manim.opengl import *
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

config.frame_rate = 15


class AbstractifyTitle(Scene):
    def construct(self):
        self.play(
            Write(Text("Step 1:", font="cmr10", color=YELLOW).shift(LEFT * 4 + UP * 2))
        )
        self.play(Write(Text("Abstractify", font="cmr10").scale(3)))


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
                Circle(radius=0.3, color=BLACK).set_fill(BLUE, 1).shift(coord)
                for coord in coords
            ]
        )

        self.add(konisberg)
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
                animations.append(Create(bezier := CubicBezier(*curve, color=BLUE_E)))
                self.bring_to_back(bezier)
                self.bring_to_back(konisberg)
            if len(curve) == 2:
                animations.append(
                    (Create(line := Line(curve[0], curve[1], color=BLUE_E)))
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

        self.play(
            FadeOut(*[nail.svg for nail in nails]),
            *[ApplyMethod(nail.set_fill, WHITE, 1) for nail in nails],
        )

        self.wait(1)

        self.play(
            *[
                nail.animate.set_stroke(WHITE, opacity=1.0).set_fill(BLACK, 1.0)
                for nail in nails
            ]
        )

        self.wait(1)


class PaperAnalogy(Scene):
    def construct(self):
        # TODO
        # render mode must be opengl
        GRAPHITE_COLOR = "#251607"
        self.camera.set_euler_angles(phi=60 * DEGREES, theta=-45 * DEGREES)
        self.add_updater(
            lambda _: self.camera.set_theta(
                theta=self.camera.data["euler_angles"][0] - 0.3 * DEGREES
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
            )
        )
        # self.wait(1)
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
        self.play(Create(curve, lag_ratio=0), run_time=5)
        self.wait(1)

        # TODO: tilt pencil

        plane = Group(hole1, hole2, paper)
        self.play(FadeOut(pencil, curve, marty))
        self.play(ApplyMethod(plane.scale, 0.01))
        self.remove(plane)

        self.interactive_embed()
        self.wait()


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
        if not isinstance(curve, ParametricFunction) or not isinstance(other_curve, ParametricFunction):
            raise TypeError("Curves must be parametric functions")
        self.og_func = curve.get_function()
        self.other_curve_func = other_curve.get_function()
        super().__init__(curve, **kwargs)

    def interpolate_mobject(self, alpha):
        self.mobject.function = (
            lambda t:
                alpha * self.other_curve_func(t) \
                + (1 - alpha) * self.og_func(t)
                if alpha 
                else self.og_func(t)
        )

        n = len(self.mobject.data["points"])
        self.mobject.data["points"] = [self.mobject.function(0)] * n
        self.mobject.init_points()
        self.mobject.data["points"] = self.mobject.data["points"][n:]

    def interpolate_mobject(self, alpha):
        self.mobject.function = (
            lambda t:
                alpha * self.other_curve_func(t) \
                + (1 - alpha) * self.og_func(t)
                if alpha 
                else self.og_func(t)
        )

        n = len(self.mobject.data["points"])
        self.mobject.data["points"] = [self.mobject.function(0)] * n
        self.mobject.init_points()
        self.mobject.data["points"] = self.mobject.data["points"][n:]


class EquivalentLoopsHomotopy(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(*get_interpolator([(0, 0), (2, 1), (1, 2)]), use_circle_nails=True)
        )

        other_curve_func, other_t_range = get_interpolator([(0, 0), (1, -2), (3, -2)])
        self.play(
            Create(
                curve := ParametricFunction(other_curve_func, other_t_range, color=BLUE)
            )
        )

        curve_func, t_range = rope.redrawn_mobjects["curve"].get_function(), [0, 1]

        """
        animation_length = 3
        tracker = ValueTracker(0)
        in_between_curve_func = lambda time: (
            lambda t: (
                time * other_curve_func(t) + (1 - time) * curve_func(t)
                if time
                else curve_func(t)
            )
        )
        self.add_updater(lambda dt: tracker.increment_value(dt))
        self.add(
            always_redraw(
                lambda: ParametricFunction(
                    in_between_curve_func(
                        rate_functions.ease_in_out_cubic(
                            tracker.get_value() / animation_length
                        )
                    ),
                    color=ORANGE,
                )
            )
        )
        self.remove(rope.redrawn_mobjects["curve"])
        """

        self.play(HomotopyAnimation(curve, rope.redrawn_mobjects["curve"]))

        self.wait(4)
