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
config.frame_rate = 15
config.frame_rate = 30
# DEV_MODE = True
# if not DEV_MODE:
#     config.frame_rate = 60


class PuzzleScene(SpaceSceneWithRopes):
    def setup_puzzle(
        self,
        curve_function=None,
        t_range=None,
        nail_positions=[LEFT * 2 + UP, LEFT * 2 + DOWN],
        nail_radius=0.5,
        marty_pos=ORIGIN,
        do_add=True,
        use_circle_nails=False,
        rope_config=None,
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

        marty = Dot(marty_pos, color=YELLOW)
        # self.play(FadeIn(marty))

        marty.image = SVGMobject("some1/marty.svg").scale(0.3)
        # marty.image = ImageMobject(img).scale(0.3)
        animations.append(FadeIn(marty.image))
        marty.image.add_updater(
            lambda im: im.next_to(marty, np.array([0.5, 0.0, 0.0]))
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
            default_rope_config = {
                "k": 12,
                "do_loop": True,
                "pendant": marty,
                "color": ORANGE,
            }
            if rope_config is not None:
                default_rope_config.update(rope_config)
            rope = self.make_rope(
                curve_function,
                t_range,
                **default_rope_config
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
            if _self.svg in self.mobjects:
                self.play(FadeOut(_self), FadeOut(_self.svg, shift=np.array(UP)))
            else:
                self.play(FadeOut(_self))

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
        if tokens[0] == "T'" or tokens[0] == "B":
            result[1] = (-1, 0.2)
        if tokens[-1] == "T'" or tokens[-1] == "B":
            result.append((-2, -0))
            result.append((-1, -0))
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
    def get_points(
        notation=None, file_name=None, raw_points=None, points=None, **kwargs
    ):
        if (
            notation is None
            and file_name is None
            and raw_points is None
            and points is None
        ):
            raise TypeError("Need file_name or curve_points or points")
        if notation is not None:
            return PuzzleScene.notation_to_points(notation, **kwargs)
        if file_name is not None:
            return PuzzleScene.get_points_from_file(file_name, **kwargs)
        elif raw_points is not None:
            return PuzzleScene.parse_points(raw_points, **kwargs)
        else:
            return points

    def get_curve(
        notation=None, file_name=None, raw_points=None, points=None, **kwargs
    ):
        return get_interpolator(
            PuzzleScene.get_points(notation, file_name, raw_points, points, **kwargs)
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
            marty.image
        ]
        if rope is not None:
            mobjects_to_fadeout.append(rope.redrawn_mobjects["curve"])
        if [mobject for mobject in mobjects_to_fadeout if mobject in self.mobjects]:
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
        else:
            self.play(Flash(marty, color=YELLOW))
        for mobject in mobjects_to_fadeout:
            del mobject


class IntroScreenPuzzle(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                *PuzzleScene.get_curve("T'BTB"),
                rope_config={"rope_creation_speed": 5, "k": 18},
            )
        )

        marty.set_moment((0.2, 0))
        self.wait(3)

        nails[1].disappear()
        marty.set_moment((0.3, 0))
        self.wait(3)
        marty.set_moment((0.5, 0))
        self.wait(8)

        self.reset_puzzle(*puzzle)


class IntroPuzzle(PuzzleScene):
    def construct(self):
        marty, _unused_rope, nails, nails_group = (
            puzzle := self.setup_puzzle(do_add=False)
        )

        self.play(FadeIn(nails[0].svg), FadeIn(nails[1].svg))
        self.add(nails[0], nails[1])
        self.make_static_body(nails_group)

        self.play(FadeIn(marty), FadeIn(label := Text("← Marty", font="cmr10").next_to(marty, RIGHT * 4)), FadeIn(marty.image))
        self.make_rigid_body(marty)

        rope = self.make_rope(
            # *get_teardrop_curve(LEFT * 3, ORIGIN, 2),
            *PuzzleScene.get_curve("BT"),
            k=12,
            do_loop=True,
            pendant=marty,
            color=ORANGE,
        )

        self.play(FadeOut(label))
        marty.set_moment((0.2, 0))
        self.wait(1)

        # NEXT_PARAGRAPH
        marty.set_moment((0.1, 0))
        self.wait(5)

        marty.set_moment((0.1, 0.1))
        self.wait(5)

        marty.set_moment((0.1, -0.1))
        self.wait(5)

        # PULL STAKES OUT
        nails_group.disappears()
        marty.set_moment((0.3, 0))
        self.wait(5)

        self.reset_puzzle(*puzzle)

class IntroPuzzle_2(Scene):
    def construct(self):
        self.play(Write(but_text := Text("But...", font="cmr10").scale(0.8)))
        self.wait(1)
        self.play(Write(text_1 := Text("Marty released when one stake is pulled", font="cmr10").scale(0.8)), but_text.animate.shift(UP * 2))
        self.wait(1)
        self.play(Write(Text("Marty not released when neither stakes are pulled", font="cmr10").scale(0.8).shift(DOWN * 2)))
        # self.play(FadeOut(*self.mobjects))
        self.wait(1)


class PuzzleTitle(Scene):
    def construct(self):
        self.play(Write(Text("The Puzzle", font="cmr10").scale(3)), run_time=3)
        self.wait(1)


class PuzzleExample1(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (puzzle := self.setup_puzzle())
        marty.set_force((0.1, 0))
        marty.set_moment((0.2, 0))
        self.wait(4)  # like 10 for prod
        marty.set_moment((0.2, 0))

        nails[0].disappear()
        # self.wait(3)
        # marty.set_moment((0.2, 0))
        self.wait(3)
        self.reset_puzzle(*puzzle)


class PuzzleExample2_1(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                *PuzzleScene.get_curve("T'")
            )
        )
        marty.set_force((0.2, 0))
        self.wait(0.8)
        marty.set_force((0.07, 0))
        self.wait(6)  # like 10 for prod

        nails[1].disappear()
        marty.set_force((0.07, 0))
        self.wait(3)

        self.reset_puzzle(*puzzle)

class PuzzleExample2_2(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(
                *PuzzleScene.get_curve("T'")
            )
        )
        marty.set_force((0.2, 0))
        self.wait(0.8)
        marty.set_force((0.07, 0))
        self.wait(6)  # like 10 for prod

        nails[0].disappear()
        marty.set_force((0.07, 0))
        self.wait(3)

        self.reset_puzzle(*puzzle)

class PuzzleExample3_1(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(*PuzzleScene.get_curve("BTB'"))
        )

        marty.set_force((0.1, 0))
        marty.set_moment((0.3, 0))
        self.wait(2)

        nails[0].disappear()

        marty.set_moment((0.5, 0))
        self.wait(3)

        self.reset_puzzle(*puzzle)


class PuzzleExample3_2(PuzzleScene):
    def construct(self):
        marty, rope, nails, nails_group = (
            puzzle := self.setup_puzzle(*PuzzleScene.get_curve("BTB'"))
        )

        marty.set_force((0.1, 0))
        marty.set_moment((0.3, 0))
        self.wait(2)

        nails[1].disappear()

        marty.set_moment((0.5, 0))
        self.wait(3)

        self.reset_puzzle(*puzzle)


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
                *text.split("\n"),
                line_spacing=2,
                font="cmr10",
                disable_ligatures=True,
                alignment="left",
            ).scale(0.8)
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
            self.play(Write(par.chars[i]))
            self.wait(0.5)

        self.wait(3)

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


class ChemPhysEquations(ModifiedSpaceScene):
    def construct(self):
        self.space.space.gravity = (0, -5)
        self.play(
            Create(
                ground := Rectangle(width=10, height=0.05, color=ORANGE)
                .shift(DOWN * 3)
                .set_fill(ORANGE, opacity=1)
            )
        )
        self.make_static_body(ground)

        eqs = [
            (r"pH=pK_a+\log(\frac{[A^-]}{[HA]})", GREEN),
            (r"PV=nRT", BLUE),
            (r"k=Ae^{\frac{-E_a}{RT}}", YELLOW),
            (r"P=e\sigma AT", RED),
        ]

        for eq, color in eqs:
            text = MathTex(eq, color=color)
            self.play(Write(text))
            for char in text.family_members_with_points():
                self.make_rigid_body(char)
            self.wait(4)

class NoNumbers(Scene):
    def construct(self):
        self.play(FadeIn(
            *(texts := [
                MathTex("\pi").shift(2 * LEFT + UP * 1.5),
                MathTex("e").shift(2 * RIGHT + UP / 2),
                MathTex("N_a").shift(2 * LEFT + DOWN / 2),
                MathTex("TREE(3)").shift(1.5 * RIGHT + DOWN * 1.5)
            ])
        ))

        self.play(Create(
            circle := Circle(radius=3.5, color=RED)
        ))

        self.play(Create(line := Line(3.5 / np.sqrt(2) * (LEFT + DOWN), 3.5 / np.sqrt(2) * (UP + RIGHT), color=RED)))

        self.wait(1)