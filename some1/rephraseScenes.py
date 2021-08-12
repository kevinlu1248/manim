import random

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
from abstractifyScenes import HomotopyAnimation


class RephraseTitle(Scene):
    def construct(self):
        self.play(
            Write(Text("Part 2:", font="cmr10", color=YELLOW).shift(LEFT * 4 + UP * 2)),
            run_time=3
        )
        self.play(Write(Text("Rephrase", font="cmr10").scale(3)),
            run_time=3
        )
        self.wait(12)

class HintRecall(Scene):
    def construct(self):
        hint = "Recall hint:\nSuppose you found the answer. How would \nyou describe your answer to someone \nwithout drawing it for them?"
        self.play(
            Write(
                Paragraph(
                    *hint.split("\n"), line_spacing=2, font="cmr10", align="center"
                ).scale(0.8)
            ),
            run_time = 3
        )
        self.wait(5)

class Unloop(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                *get_interpolator([(0, 0), (2, 2), (2, -2)]), use_circle_nails=True
            )
        )

        self.wait(7)

        self.play(Write(text := Text("Unloop").shift(DOWN * 3)))
        self.wait(2)
        self.play(FadeOut(text))

        self.reset_puzzle(*puzzle)


def concat_funcs(*funcs, splits=None):
    """Assume all are in range [0, 1] for simplicity."""
    assert len(funcs) >= 2
    for i in range(len(funcs) - 1):
        print(funcs[i](1), funcs[i + 1](0))
        assert np.linalg.norm(funcs[i](1) - funcs[i + 1](0)) < 1e-2
    n = len(funcs)
    if splits == None:
        splits = [i / n for i in range(1, n)]
    splits.append(1)
    assert len(splits) == n

    def concatenated_func(t):
        if t == 0:
            return funcs[0](0)
        if t == 1:
            return funcs[-1](1)
        for nth, split in enumerate(splits):
            if t <= split:
                break
        func = funcs[nth]
        if nth == 0:
            return func(t / splits[0])
        else:
            return func((t - splits[nth - 1]) / (splits[nth] - splits[nth - 1]))

    return concatenated_func


class BreakingDownLoops(PuzzleScene):
    def construct(self):
        marty, _unused_rope, nails, nails_group = (
            puzzle := self.setup_puzzle(do_add=False)
        )

        self.play(
            *[nail.animate.set_stroke(WHITE, opacity=1) for nail in nails],
            FadeIn(marty),
        )

        self.play(
            Create(
                btt_curve := ParametricFunction(
                    *PuzzleScene.get_curve("BTT"), color=ORANGE
                )
            ),
            run_time=2,
        )

        self.wait(4)

        self.play(
            FadeOut(btt_curve),
            Create(
                bt_curve := ParametricFunction(*PuzzleScene.get_curve("BT"), color=BLUE)
            ),
            run_time=2,
        )

        self.play(
            Create(
                t_curve := ParametricFunction(*PuzzleScene.get_curve("T"), color=GREEN)
            ),
            run_time=2,
        )

        self.play(FadeIn(btt_curve), FadeOut(bt_curve, t_curve))

        self.play(
            HomotopyAnimation(
                btt_curve,
                ParametricFunction(
                    concat_funcs(
                        PuzzleScene.get_curve("BT")[0],
                        PuzzleScene.get_curve("T")[0],
                        splits=[0.6],
                    )
                ),
            ),
            run_time=3,
        )

        btt_new = ParametricFunction(*PuzzleScene.get_curve("BTT"), color=ORANGE)

        self.wait(3)
        self.play(FadeOut(btt_curve), FadeIn(btt_new, bt_curve, t_curve))
        btt_curve = btt_new

        self.wait(1)

        btt_copy, bt_copy, t_copy = (
            mobject.copy() for mobject in (btt_curve, bt_curve, t_curve)
        )
        equals_1, plus_1 = Text(":").shift(RIGHT * 1.75 + UP * 2.5), Text("→").shift(
            RIGHT * 4.25 + UP * 2.5
        )
        self.add(btt_copy, bt_copy, t_copy)
        self.play(
            *[
                mobject.animate.shift(LEFT * 2)
                for mobject in (marty, *nails, btt_curve, bt_curve, t_curve)
            ],
            btt_copy.animate.scale(0.5).move_to(RIGHT * 0.5 + UP * 2.5),
            bt_copy.animate.scale(0.5).move_to(RIGHT * 3 + UP * 2.5),
            t_copy.animate.scale(0.5).move_to(RIGHT * 5.5 + UP * 2.5),
            FadeIn(equals_1, plus_1),
        )

        self.wait(8)
        self.play(FadeOut(btt_curve, t_curve))
        self.wait(2)

        self.play(
            FadeOut(bt_curve),
            Create(
                b_curve := ParametricFunction(
                    *PuzzleScene.get_curve("B"), color=RED
                ).shift(LEFT * 2)
            ),
            run_time=2,
        )
        self.play(
            Create(
                t_curve_2 := ParametricFunction(
                    *PuzzleScene.get_curve("T"), color=PURPLE
                ).shift(LEFT * 2)
            ),
            run_time=2,
        )
        self.play(
            FadeIn(bt_curve), 
            FadeOut(b_curve, t_curve_2)
        )

        bt_func, b_t_func = bt_curve.get_function(), concat_funcs(
            PuzzleScene.get_curve("B")[0], PuzzleScene.get_curve("T")[0]
        )
        bt_shifted, b_t_shifted = (
            lambda t: bt_func(t) + LEFT * 2,
            lambda t: b_t_func(t) + LEFT * 2,
        )
        # self.play(
        #     HomotopyAnimation(
        #         bt_curve := ParametricFunction(bt_shifted, color=BLUE),
        #         ParametricFunction(b_t_shifted),
        #         run_time=3,
        #     )
        # )

        self.play(
            FadeOut(bt_curve),
            FadeIn(
                b_curve,
                t_curve_2,
                bt_new := ParametricFunction(
                    *PuzzleScene.get_curve("BT"), color=BLUE
                ).shift(LEFT * 2),
            ),
        )

        # bt_new = ParametricFunction(
        #     *PuzzleScene.get_curve("BT"), color=BLUE
        # ).shift(LEFT * 2)

        bt_curve = bt_new
        bt_copy_2, b_copy, t_copy_2 = (
            mobject.copy() for mobject in (bt_curve, b_curve, t_curve_2)
        )
        equals_2, plus_2 = Text(":").shift(RIGHT * 1.75), Text("→").shift(RIGHT * 4.25)

        self.play(
            bt_copy_2.animate.scale(0.5).move_to(RIGHT * 0.5),
            b_copy.animate.scale(0.5).move_to(RIGHT * 3),
            t_copy_2.animate.scale(0.5).move_to(RIGHT * 5.5),
            FadeIn(equals_2, plus_2),
        )

        self.wait(2)

        btt_f, equals_f, b_f, plus_f_1, t_f_2, plus_f_2, t_f_1 = (
            mobject.copy()
            for mobject in (
                btt_copy,
                equals_1,
                b_copy,
                plus_1,
                t_copy_2,
                plus_2,
                t_copy,
            )
        )
        self.add(btt_f, equals_f, b_f, plus_f_1, t_f_1, plus_f_2, t_f_2)
        self.play(
            btt_f.animate.shift(DOWN * 5 + LEFT * 2),
            equals_f.animate.shift(DOWN * 5 + LEFT * 2),
            b_f.animate.shift(DOWN * 2.5 + LEFT * 2),
            plus_f_1.animate.shift(DOWN * 5 + LEFT * 2),
            t_f_2.animate.shift(DOWN * 2.5 + LEFT * 2),
            plus_f_2.animate.shift(DOWN * 2.5),
            t_f_1.animate.shift(DOWN * 5),
        )
        self.wait(10)


class RandomMotion(Animation):
    def __init__(self, *args, movement_size=0.3, n=5, **kwargs):
        super().__init__(*args, **kwargs)

        points = [self.mobject.get_center()[:2]]
        for _ in range(n):
            theta = random.uniform(0, 2 * PI)
            vec = movement_size * np.array([np.cos(theta), np.sin(theta)])
            points.append(vec + points[-1])
        self.path_to_travel, _unused_range = get_interpolator(points, do_loop=False)

    def interpolate_mobject(self, alpha):
        self.mobject.move_to(to_3D(self.path_to_travel(alpha)))


class MoveAroundScene(PuzzleScene):
    def construct(self):
        # USE CAIRO
        marty, _unused_rope, nails, nails_group = (
            puzzle := self.setup_puzzle(do_add=False)
        )

        self.play(
            *[nail.animate.set_stroke(WHITE, opacity=1) for nail in nails],
            FadeIn(marty),
        )

        random.seed(42)

        self.play(
            *[RandomMotion(mobject) for mobject in nails + [marty]], run_time=1
        )  # set runtime to 5 at least for prod

        self.play(
            ApplyMethod(marty.move_to, ORIGIN),
            nails[0].animate.move_to(UP * 1.5).scale(3),
            nails[1].animate.move_to(DOWN * 1.5).scale(3),
        )

        self.play(
            Create(
                curve := ParametricFunction(
                    *get_interpolator(
                        [(0, 0), (1, 0), (3, 1), (2, 4), (-2, 2), (-0.5, 0)]
                    ),
                    color=ORANGE,
                )
            )
        )
        self.play(
            FadeOut(curve),
            Create(rect := RoundedRectangle(width=13, height=7, z_index=-1)),
        )
        self.play(rect.animate.stretch_to_fit_width(6))
        self.play(rect.animate.stretch_to_fit_width(10))
        self.play(rect.animate.stretch_to_fit_width(4))

        # boundary

        for nail in nails:
            nail.set_fill(BLACK, opacity=1)
        rect.data["z_index"] = -1
        rect.shift([0, 0, -1])
        self.play(rect.animate.scale(0))


class MoveAroundScene_2(PuzzleScene):
    def construct(self):
        marty, _unused_rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                nail_positions=[UP * 1.5, DOWN * 1.5],
                nail_radius=1.5,
                do_add=False,
            )
        )
        [nail.set_stroke(WHITE, opacity=1.0) for nail in nails]
        self.add(marty, *nails)

        pointer = Dot(color=ORANGE)
        compressed_curve = ParametricFunction(
            concat_funcs(
                lambda t: DOWN * 1.5
                + 1.5
                * np.array(
                    [np.cos((-t + 1 / 4) * PI * 2), np.sin((-t + 1 / 4) * PI * 2), 0]
                ),
                lambda t: UP * 1.5
                + 1.5
                * np.array(
                    [np.cos((-t + 3 / 4) * PI * 2), np.sin((-t + 3 / 4) * PI * 2), 0]
                ),
                lambda t: UP * 1.5
                + 1.5
                * np.array(
                    [np.cos((-t + 3 / 4) * PI * 2), np.sin((-t + 3 / 4) * PI * 2), 0]
                ),
            ),
            color=ORANGE,
        )

        self.add(pointer)
        self.add_updater(
            updater := lambda _: pointer.move_to(compressed_curve.data["points"][-1])
        )

        self.play(Create(compressed_curve), run_time=3)  # use 7 for prod
        self.remove_updater(updater)
        pointer.move_to(ORIGIN)
        self.play(FadeOut(pointer))

        new_curve = ParametricFunction(
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
            )
        )

        self.play(HomotopyAnimation(compressed_curve, new_curve))
        self.play(FadeOut(compressed_curve))

        self.play(
            Create(
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
            )
        )

        self.play(
            Create(
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
            )
        )

        self.play(
            Create(
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
            )
        )

        self.play(
            FadeOut(marty, *nails),
            compressed_curve.animate.move_to(LEFT * 4.5).scale(0.3),
            b_curve.animate.move_to(LEFT * 1.5).scale(0.3),
            t_curve_1.animate.move_to(RIGHT * 1.5).scale(0.3),
            t_curve_2.animate.move_to(RIGHT * 4.5).scale(0.3),
            FadeIn(
                equals := Text(":", font="cmr10").shift(LEFT * 3),
                plus_1 := Text("→", font="cmr10"),
                plus_2 := Text("→", font="cmr10").shift(RIGHT * 3),
            ),
        )

        self.wait(3)

        self.play(
            FadeOut(
                compressed_curve, b_curve, t_curve_1, t_curve_2, equals, plus_1, plus_2
            )
        )


class ElementaryLoops(PuzzleScene):
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
        self.wait(1)

        bug = Dot(color=ORANGE)
        curve = ParametricFunction(
            lambda t: UP * 1.5
            + 1.5
            * np.array(
                [
                    np.cos(-t * PI * 2 / 3 + 3 * PI / 2),
                    np.sin(-t * PI * 2 / 3 + 3 * PI / 2),
                    0,
                ]
            ),
            color=ORANGE,
        )

        self.play(FadeIn(bug))
        self.add_updater(updater := lambda _: bug.move_to(curve.data["points"][-1]))

        self.play(Create(curve), run_time=3)  # use 7 for prod

        self.play(
            FadeIn(
                bug_marker := Text("Bug →").scale(0.5).next_to(bug, LEFT * 2),
                curve_marker := Text("Loop →").scale(0.5).next_to(curve, LEFT * 2),
            )
        )
        self.wait(1)
        self.play(FadeOut(bug_marker, curve_marker))
        self.add(
            unloop_dir := Arrow(
                start=bug.get_center() + LEFT / 2,
                end=bug.get_center() + LEFT * 1.5 + DOWN,
            ),
            t_dir := Arrow(
                start=bug.get_center() + UP / 2, end=bug.get_center() + RIGHT + UP * 1.5
            ),
            unloop_text := Text("Unloop")
            .scale(0.5)
            .next_to(unloop_dir, (UP + LEFT) * 0.01)
            .rotate(PI / 4),
            t_text := Text("Loop")
            .scale(0.5)
            .next_to(t_dir, (UP + LEFT) * 0.01)
            .rotate(PI / 4),
        )
        self.wait(3)
