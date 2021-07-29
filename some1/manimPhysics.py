from collections import namedtuple
import functools

from manim import *
from manim_physics import *
import pymunk
import scipy as sp
import scipy.interpolate

DEV_MODE = True
config.frame_rate = 15 if DEV_MODE else 60
EPS = 1e-09


def to_3D(vector_like):
    return np.array([vector_like[0], vector_like[1], 0])


def cart2polar(x, y):
    return np.sqrt(x ** 2 + y ** 2), np.arctan(y / 2)


def polar2cart(r, theta):
    return r * np.cos(theta), r * np.sin(theta)


def get_interpolator(vectors, offset=0.001, do_use_polar=False, use_periodic=False):
    vectors = vectors + [vectors[0] + np.array([offset, offset])]
    # vectors = vectors + [vectors[0], vectors[1]]
    x, y = zip(*vectors)

    if do_use_polar:
        x, y = np.array(x), np.array(y)
        r = np.sqrt(x ** 2 + y ** 2)
        theta = np.arctan2(y, x)
        tck, _unused_u = sp.interpolate.splprep([r, theta], k=3, s=0)
        return (
            lambda t: to_3D(polar2cart(*next(zip(*sp.interpolate.splev([t], tck))))),
            [0, 1],
        )
    tck, _unused_u = sp.interpolate.splprep([x, y], k=3, s=0, per=bool(use_periodic))
    return lambda t: to_3D(next(zip(*sp.interpolate.splev([t], tck)))), [0, 1]


class ModifiedSpaceScene(SpaceScene):
    """
    Add an init_body helper function, as well as fixing a bug in the static scene.
    """

    def init_body(self, p, elasticity=0.8, density=1, friction=0.8):  # type: ignore
        self.add(p)
        p.body = pymunk.Body()
        p.body.position = p.get_x(), p.get_y()
        get_angle(p)
        if not hasattr(p, "angle"):
            p.angle = 0
        p.body.angle = p.angle
        get_shape(p)
        p.shape.density = density
        p.shape.elasticity = elasticity
        p.shape.friction = friction
        p.spacescene = self

    def make_static_body(self, *mobs, elasticity=1, friction=0.8):
        for mob in mobs:
            if isinstance(mob, VGroup or Group):
                return self.make_static_body(*mob)
            mob.body = self.space.space.static_body
            mob.body.position = mob.get_x(), mob.get_y()
            get_shape(mob)
            mob.shape.elasticity = elasticity
            mob.shape.friction = friction
            self.add_body(mob)


class SpaceSceneWithRopes(ModifiedSpaceScene):
    num_of_chains = 0
    Rope = namedtuple(
        "Rope", ["segments", "redrawn_mobjects", "constraints", "signs", "dists"]
    )

    def make_rope(
        self,
        func,
        t_range,
        k=20 if DEV_MODE else 30,
        thickness=0.01,
        gap_ratio=1,
        do_loop=False,
        color=WHITE,
        do_smooth=True,
        do_add_dots=False,
        do_self_intersect=False,
        offset=0.001,
        pendant=None,
        elasticity=0.1,
        density=0.1,
        friction=0.8
    ) -> Rope:
        SpaceSceneWithRopes.num_of_chains += 1
        segments = []
        signs = []
        dists = []
        constraints = []
        redrawn_mobjects = {}
        prev_point = func(0)
        for section in range(k + 1):
            t = t_range[0] + (t_range[1] - t_range[0]) * section / k
            point = func(t)
            if section > 0:
                center = (prev_point + point) / 2
                delta = point - prev_point

                dist = np.linalg.norm(delta)
                dists.append(dist)
                dot_product = np.dot(delta / dist, [1, 0, 0])
                sign = -np.sign(np.cross(delta / dist, [1, 0, 0])[-1])
                if sign >= 0:
                    sign = 1
                signs.append(sign)
                angle = np.arccos(sign * dot_product)

                rect = (
                    Rectangle(width=dist * (1 - (1 - gap_ratio) * 2), height=thickness)
                    .set_fill(color, 0 if do_smooth else 1)
                    .set_stroke(color, 0 if do_smooth else 1)
                    .shift(center)
                    .rotate(angle)
                )
                segments.append(rect)
                self.init_body(rect, elasticity=elasticity, density=density, friction=friction)

                if not do_self_intersect:
                    rect.shape.filter = pymunk.ShapeFilter(
                        group=SpaceSceneWithRopes.num_of_chains
                    )

                self.add_body(rect)

                if section > 1:
                    constraints.append(
                        # pymunk.constraints.DampedSpring(
                        pymunk.constraints.PivotJoint(
                            prev_rect.body,
                            rect.body,
                            (prev_sign * prev_dist / 2 * gap_ratio, 0),
                            (-sign * dist / 2 / gap_ratio, 0),
                            # rest_length=0.0,
                            # stiffness=5,
                            # damping=1
                        )
                    )
                    self.space.space.add(constraints[-1])
                else:
                    first_dist = dist
                    first_rect = rect
                    first_sign = sign
                rect.add_updater(simulate)
                prev_dist = dist
                prev_rect = rect
                prev_sign = sign
            prev_point = point

        if do_smooth:

            def get_curve():
                vectors = []
                for i in range(k):
                    vectors.append(
                        segments[i].body.local_to_world(
                            (signs[i] * dists[i] / 2 * gap_ratio, 0)
                        )
                    )
                interpolator, t_range = get_interpolator(vectors, offset=offset)
                curve = ParametricFunction(interpolator, t_range, color=color)
                return curve

            redrawn_mobjects["curve"] = always_redraw(get_curve)
            self.add(redrawn_mobjects["curve"])
        if do_add_dots:

            def get_dots():
                dots = []
                for i in range(k):
                    dots.append(Dot(
                        to_3D(
                            segments[i].body.local_to_world(
                                (signs[i] * dists[i] / 2 * gap_ratio, 0)
                            )
                        )
                    ))
                return mobject.mobject.Group(*dots)

            redrawn_mobjects["dots"] = always_redraw(get_dots)
            self.add(redrawn_mobjects["dots"])

        if do_loop and np.linalg.norm(func(t_range[0]) - func(t_range[1])) < 1e-9:
            constraints.append(
                pymunk.constraints.PivotJoint(
                    prev_rect.body,
                    first_rect.body,
                    (prev_sign * prev_dist / 2 * gap_ratio, 0),
                    (-first_sign * first_dist / 2 / gap_ratio, 0),
                )
            )
            self.space.space.add(constraints[-1])

        if pendant != None:
            assert hasattr(pendant, "body"), "Must be rigid body!"
            if not do_self_intersect:
                pendant.shape.filter = pymunk.ShapeFilter(
                    group=SpaceSceneWithRopes.num_of_chains
                )
            pendant.body.position = segments[0].body.local_to_world(
                (-signs[0] * dists[0] / 2 * gap_ratio, 0)
            )
            # segments[0].set_stroke(GREEN)
            # self.add(Dot(
            #     to_3D(
            #     segments[0].body.local_to_world(
            #         (-signs[0] * dists[0] / 2 * gap_ratio, 0),
            #     )
            #     ), color=GREEN
            # ))
            constraints.append(
                pymunk.constraints.PinJoint(
                    segments[0].body,
                    pendant.body,
                    (-signs[0] * dists[0] / 2 * gap_ratio, 0),
                )
            )
            self.space.space.add(constraints[-1])
            # segments[-1].set_stroke(BLUE)
            # self.add(Dot(
            #     to_3D(
            #     segments[-1].body.local_to_world(
            #         (signs[-1] * dists[-1] / 2 * gap_ratio, 0),
            #     )
            #     ), color=BLUE
            # ))
            constraints.append(
                pymunk.constraints.PinJoint(
                    segments[-1].body,
                    pendant.body,
                    (signs[-1] * dists[-1] / 2 * gap_ratio, 0),
                )
            )
            self.space.space.add(constraints[-1])

        return SpaceSceneWithRopes.Rope(
            segments, redrawn_mobjects, constraints, signs, dists
        )

class MartyEscape(SpaceSceneWithRopes):
    def construct(self):
        from PIL import Image

        self.space.space.gravity = 0, 0
        self.space.space.damping = 0.05

        nail_radius = 0.5
        nail1 = (
            Circle(nail_radius).set_fill(WHITE, 1).set_stroke(WHITE, 1).shift(UP * 2 + LEFT)
        )
        nail2 = (
            Circle(nail_radius)
            .set_fill(WHITE, 1)
            .set_stroke(WHITE, 1)
            .shift(UP * 2 + RIGHT)
        )
        nails = VGroup(nail1, nail2)

        self.add(nails)

        self.make_static_body(nails)

        marty = Dot()

        img = Image.open("some1/dog_emoji.png")
        marty_image = ImageMobject(img).scale(0.3)
        self.add(marty_image)
        marty_image.add_updater(lambda im: im.next_to(marty, np.array([0., -0.5, 0.])))

        self.bring_to_front(marty)
        self.make_rigid_body(marty)
        self.add_foreground_mobjects(marty)

        func = lambda t: 1.8 * np.array(
            [np.cos(2 * PI * t - PI / 2), np.sin(2 * PI * t - PI / 2) + 1, 0]
        )
        rope = self.make_rope(
            func,
            np.array([0, 1]),
            do_loop=True,
            pendant=marty,
            color=ORANGE,
            # do_add_dots=True,
            # do_smooth=False
        )

        def set_force(_self, force):
            if hasattr(_self, "force_setter"):
                _self.remove_updater(_self.force_setter)
            def force_setter(_self):
                _self.body.force = force
            _self.add_updater(force_setter)
            _self.force_setter = force_setter
        
        marty.set_force = functools.partial(set_force, marty)

        marty.body.force = (0, -1)
        self.wait(0.4)
        marty.set_force((0, -0.05))
        self.wait(1)
        marty.set_force((0, -0.01))
        self.wait(2)

