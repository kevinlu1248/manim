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

DEV_MODE = False
DEV_MODE = True
config.frame_rate = 15 if DEV_MODE else 60


class PuzzleScene(SpaceSceneWithRopes):
    def setup_puzzle(
        self,
        curve_function=None,
        t_range=None,
        nail_positions=[LEFT * 2 + UP, LEFT * 2 + DOWN],
        nail_radius=0.5,
        do_add=True,
        use_circle_nails=False,
    ):
        from PIL import Image

        self.space.space.gravity = 0, 0
        self.space.space.damping = 0.3

        nails = []
        animations = []

        for position in nail_positions:
            nails.append(
                Circle(nail_radius)
                .set_fill(WHITE, 0)
                .set_stroke(WHITE, opacity=0 if not use_circle_nails else 1)
                .shift(position)
            )
            animations.append(FadeIn(nails[-1]))
            nails[-1].svg = (
                SVGMobject("some1/nail.svg")
                .scale(0.4)
                .rotate(-PI / 12)
                .next_to(nails[-1], ORIGIN)
            )
            if not use_circle_nails:
                animations.append(FadeIn(nails[-1].svg))

        nails_group = VGroup(*nails)
        if do_add:
            self.make_static_body(nails_group)

        marty = Dot(color=YELLOW)
        # self.play(FadeIn(marty))

        if not DEV_MODE:
            img = Image.open("some1/dog_emoji.png")
            marty.image = ImageMobject(img).scale(0.3)
            animations.append(FadeIn(marty.image))
            marty.image.add_updater(
                lambda im: im.next_to(marty, np.array([0.0, -0.5, 0.0]))
            )

        animations.append(FadeIn(marty))

        if curve_function == None:
            # curve_function, t_range = get_teardrop_curve(LEFT * 3, ORIGIN, 2)
            curve_function, t_range = PuzzleScene.get_curve("BT")

        if do_add:
            self.play(*animations)

        if do_add:
            # self.bring_to_front(marty)
            self.make_rigid_body(marty)

        if do_add:
            rope = self.make_rope(
                curve_function,
                t_range,
                k=12,
                do_loop=True,
                pendant=marty,
                color=ORANGE,
                # do_smooth=False
                # do_add_dots=True
            )
        else:
            rope = None

        def set_force(_self, force):
            if hasattr(_self, "force_setter"):
                _self.remove_updater(_self.force_setter)

            def force_setter(_self):
                _self.body.force = force

            _self.add_updater(force_setter)
            _self.force_setter = force_setter

        def set_moment(_self, force):
            if hasattr(_self, "moment_setter"):
                _self.remove_updater(_self.moment_setter)

            def moment_setter(_self):
                _self.body.force = force

            _self.add_updater(moment_setter)
            _self.moment_setter = moment_setter

        marty.set_force = functools.partial(set_force, marty)
        marty.set_moment = functools.partial(set_moment, marty)

        def disappear(_self):
            _self.shape.filter = pymunk.ShapeFilter(group=PuzzleScene.num_of_chains)
            self.play(FadeOut(_self), FadeOut(_self.svg, shift=np.array(UP)))

        for nail in nails:
            nail.disappear = functools.partial(disappear, nail)

        def disappears(_self):
            for item in _self:
                item.shape.filter = pymunk.ShapeFilter(group=PuzzleScene.num_of_chains)
            self.play(
                FadeOut(*_self),
                FadeOut(*[item.svg for item in _self], shift=np.array(UP)),
            )

        nails_group.disappears = functools.partial(disappears, nails)

        return marty, rope, nails, nails_group

    @staticmethod
    def notation_to_points(
        s: str, centers=[(-2, 1), (-2, -1)], radius=0.7, r_increment=0.1, raw=False
    ):
        # TODO: add center
        assert set(s).issubset({"T", "B", "'"})
        result = [(0, 0)]
        tokens = s.replace("T", " T").replace("B", " B").split()
        t_radius = radius
        b_radius = radius

        t_center, b_center = centers
        t_type = lambda r: [
            (-2, 0),
            (-2 - r, 0.5 + r),
            (-2, 0.5 + r * 2),
            (-2 + r, 0.5 + r),
        ]
        tb_type = lambda r: [
            (-2, 0),
            (-2 + r, 0.5 + r),
            (-2, 0.5 + r * 2),
            (-2 - r, 0.5 + r),
        ]
        b_type = lambda r: [
            (-2, 0),
            (-2 + r, -0.5 + -r),
            (-2, -0.5 + -r * 2),
            (-2 - r, -0.5 + -r),
        ]
        bb_type = lambda r: [
            (-2, 0),
            (-2 - r, -0.5 + -r),
            (-2, -0.5 + -r * 2),
            (-2 + r, -0.5 + -r),
        ]
        prev_token = None
        for token in tokens:
            if token == "T":
                if prev_token == "B":
                    result.extend(t_type(t_radius)[1:])
                else:
                    result.extend(t_type(t_radius))
                t_radius += r_increment
            elif token == "T'":
                if prev_token == "B'":
                    result.extend(tb_type(t_radius)[1:])
                else:
                    result.extend(tb_type(t_radius))
                t_radius += r_increment
            elif token == "B":
                if prev_token == "T'":
                    result.extend(b_type(b_radius)[1:])
                else:
                    result.extend(b_type(b_radius))
                b_radius += r_increment
            elif token == "B'":
                if prev_token == "T'":
                    result.extend(bb_type(b_radius)[1:])
                else:
                    result.extend(bb_type(b_radius))
                b_radius += r_increment
            else:
                raise TypeError("Token needs to be T T' B or B'")
            prev_token = token
        if s[0] == "T'" or s[0] == "B":
            result[1] = (-1, 0.2)
        if s[-1] == "T'" or s[-1] == "B":
            result.append((-2, -0.3))
            result.append((-1, -0.2))
        return result

    @staticmethod
    def parse_points(curve_points_raw):
        return [
            [float(line[0]), float(line[1])]
            for line in map(lambda s: s.split(), curve_points_raw.strip().split("\n"))
        ]

    @staticmethod
    def get_points_from_file(file_name):
        with open(file_name, "r") as file:
            return PuzzleScene.parse_points(file.read())

    @staticmethod
    def get_points(notation=None, file_name=None, raw_points=None, points=None):
        if (
            notation is None
            and file_name is None
            and raw_points is None
            and points is None
        ):
            raise TypeError("Need file_name or curve_points or points")
        if notation is not None:
            return PuzzleScene.notation_to_points(notation)
        if file_name is not None:
            return PuzzleScene.get_points_from_file(file_name)
        elif raw_points is not None:
            return PuzzleScene.parse_points(raw_points)
        else:
            return points

    def get_curve(notation=None, file_name=None, raw_points=None, points=None):
        return get_interpolator(
            PuzzleScene.get_points(notation, file_name, raw_points, points)
        )

    def draw_curve_through_given_points(
        self,
        notation=None,
        file_name=None,
        raw_points=None,
        points=None,
        do_animate=True,
        do_plot_points=True,
    ):
        dots = []
        curve_points = PuzzleScene.get_points(notation, file_name, raw_points, points)
        if do_plot_points:
            for point in curve_points:
                dots.append(Dot(to_3D(point), color=BLUE))
                self.add(dots[-1])
        else:
            dots = None
        curve = ParametricFunction(*get_interpolator(curve_points))
        if do_animate:
            self.play(Create(curve))
        else:
            self.add(curve)
        return curve, dots

    def reset_puzzle(self, marty, rope, nails, nails_group):
        # # TODO
        marty.set_force((0, 0))
        marty.set_moment((0, 0))
        self.remove(marty)
        mobjects_to_fadeout = [
            *nails,
            *[nail.svg for nail in nails],
        ]
        if rope is not None:
            mobjects_to_fadeout.append(rope.redrawn_mobjects["curve"])
        self.play(
            FadeOut(
                *[
                    mobject
                    for mobject in mobjects_to_fadeout
                    if mobject in self.mobjects
                ]
            ),
            Flash(marty, color=YELLOW),
        )
        for mobject in mobjects_to_fadeout:
            del mobject


class IntroPuzzle(PuzzleScene):
    def construct(self):
        marty, _unused_rope, nails, nails_group = self.setup_puzzle(do_add=False)

        self.play(FadeIn(nails[0].svg), FadeIn(nails[1].svg))
        self.add(nails[0])
        self.add(nails[1])
        self.make_static_body(nails_group)

        self.play(FadeIn(marty))
        if not DEV_MODE:
            self.play(FadeIn(marty.image))
        self.make_rigid_body(marty)

        rope = self.make_rope(
            # *get_teardrop_curve(LEFT * 3, ORIGIN, 2),
            *PuzzleScene.get_curve("BT"),
            k=12,
            do_loop=True,
            pendant=marty,
            color=ORANGE,
        )

        # marty.set_force((0.2, 0))
        marty.set_moment((0.2, 0))
        self.wait(1)

        # NEXT_PARAGRAPH
        marty.set_moment((0.1, 0))
        self.wait(5)

        # PULL STAKES OUT
        nails_group.disappears()
        marty.set_moment((0.3, 0))
        self.wait(10)

        self.reset_puzzle(marty, rope, nails, nails_group)


class PuzzleExample1(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (puzzle := self.setup_puzzle())
        marty.set_force((0.1, 0))
        marty.set_moment((0.2, 0))
        self.wait(2)  # like 10 for prod
        marty.set_moment((0.2, 0))

        nails[0].disappear()
        # self.wait(3)
        marty.set_moment((0.2, 0))
        self.reset_puzzle(*puzzle)
        self.wait(1)


class PuzzleExample2(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                *get_teardrop_curve(
                    np.array([-3, 1.5, 0]),
                )
            )
        )
        marty.set_force((0.2, 0))
        self.wait(0.8)
        marty.set_force((0.07, 0))
        self.wait(2)  # like 10 for prod

        nails[1].disappear()
        marty.set_force((0.07, 0))
        self.wait(5)

        self.reset_puzzle(*puzzle)


class PuzzleExample3_1(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(*PuzzleScene.get_curve("BTB'"))
        )

        self.wait(1)
        marty.set_force((0.1, 0))
        marty.set_moment((0.2, 0))
        self.wait(5)

        nails[0].disappear()

        marty.set_moment((0.8, 0))
        self.wait(5)

        self.reset_puzzle(*puzzle)
        self.wait(1)


class PuzzleExample3_2(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(*PuzzleScene.get_curve("BTB'"))
        )

        nails[1].disappear()

        marty.set_force((0.05, 0))
        marty.set_moment((0.3, 0))
        self.wait(5)


class IntroSummarySlide(Scene):
    def construct(self):
        text = f"""
        Summary of Puzzle:
        1. There are two stakes.
        2. Marty is leashed when no stakes are pulled out.
        3. Marty can be unleashed when either stake is pulled out.
        """.strip().replace(
            " " * 8, ""
        )

        lines = text.split("\n")

        par = (
            Paragraph(
                *text.split("\n"), line_spacing=2, font="cmr10", disable_ligatures=True
            )
            .scale(0.8)
            .shift(LEFT * 8)
        )

        highlight_texts = [
            [],
            ["two"],
            ["leashed", "no stakes"],
            ["unleashed", "either stake"],
        ]

        for i in range(len(par)):
            for text in highlight_texts[i]:
                par[i][lines[i].find(text) : lines[i].find(text) + len(text)].set_color(
                    YELLOW
                )

        self.play(FadeOut(par))

        hint = "Hint:\nSuppose you found the answer. How would \nyou describe your answer to someone \nwithout drawing it for them?"
        self.play(
            Write(
                Paragraph(
                    *hint.split("\n"), line_spacing=2, font="cmr10", align="center"
                ).scale(0.8)
            )
        )
        self.wait(5)
