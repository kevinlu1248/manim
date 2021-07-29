import functools

from manim import *
from manim_physics import *
import pymunk

from physicsUtils import *

DEV_MODE = True
config.frame_rate = 15 if DEV_MODE else 60
EPS = 1e-09


class PuzzleScene(SpaceSceneWithRopes):
    def setup_puzzle(
        self,
        curve_function=None,
        t_range=None,
        nail_positions=[LEFT * 2 + UP, LEFT * 2 + DOWN],
        nail_radius=0.5,
        do_add=True,
    ):
        from PIL import Image

        self.space.space.gravity = 0, 0
        self.space.space.damping = 0.3

        nails = []

        for position in nail_positions:
            nails.append(
                Circle(nail_radius)
                .set_fill(WHITE, 0)
                .set_stroke(WHITE, 0)
                .shift(position)
            )
            nails[-1].svg = (
                SVGMobject("some1/nail.svg")
                .scale(0.4)
                .rotate(-PI / 12)
                .next_to(nails[-1], ORIGIN)
            )
            if do_add:
                self.add(nails[-1].svg)

        nails_group = VGroup(*nails)
        if do_add:
            self.add(nails_group)
            self.make_static_body(nails_group)

        marty = Dot()

        if not DEV_MODE:
            img = Image.open("some1/dog_emoji.png")
            marty.image = ImageMobject(img).scale(0.3)
            if do_add:
                self.add(marty.image)
            marty.image.add_updater(
                lambda im: im.next_to(marty, np.array([0.0, -0.5, 0.0]))
            )

        if do_add:
            self.bring_to_front(marty)
            self.make_rigid_body(marty)

        if curve_function == None:
            curve_function, t_range = get_teardrop_curve(
                np.array([-3, 1.5, 0]), np.array([0, 0, 0])
            )

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

        marty.set_force = functools.partial(set_force, marty)

        def disappear(_self):
            _self.shape.filter = pymunk.ShapeFilter(
                group=SpaceSceneWithRopes.num_of_chains
            )
            self.play(FadeOut(_self))
            self.play(FadeOut(_self.svg, shift=np.array(UP)))

        for nail in nails:
            nail.disappear = functools.partial(disappear, nail)
        
        def disappears(_self):
            for item in _self:
                item.shape.filter = pymunk.ShapeFilter(
                    group=SpaceSceneWithRopes.num_of_chains
                )
            self.play(FadeOut(*_self))
            self.play(FadeOut(*[item.svg for item in _self], shift=np.array(UP)))
        nails_group.disappears = functools.partial(disappears, nails)

        return marty, rope, nails, nails_group


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
            *get_teardrop_curve(LEFT * 3, ORIGIN, 2.5),
            k=12,
            do_loop=True,
            pendant=marty,
            color=ORANGE,
        )

        marty.set_force((1, 0))
        self.wait(0.07)

        # NEXT_PARAGRAPH
        marty.set_force((0.01, 0))
        self.wait(5)

        # PULL STAKES OUT
        nails_group.disappears()
        marty.set_force((0.05, 0))
        self.wait(5)

        # for center
        # marty.body.force = (1, 0)
        # self.wait(5)
        # self.wait(0.4)
        # marty.set_force((0.05, 0))
        # self.wait(1)
        # marty.set_force((0.01, 0))
        # self.wait(2)
