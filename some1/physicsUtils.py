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
        do_animate_curve=True,
        do_add_dots=False,
        do_self_intersect=False,
        offset=0.001,
        pendant=None,
        elasticity=0.1,
        density=0.1,
        friction=0.8,
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
                self.init_body(
                    rect, elasticity=elasticity, density=density, friction=friction
                )

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
                            (-signs[i] * dists[i] / 2 * gap_ratio, 0)
                        )
                    )
                interpolator, t_range = get_interpolator(vectors, offset=offset)
                curve = ParametricFunction(interpolator, t_range, color=color)
                return curve

            redrawn_mobjects["curve"] = always_redraw(get_curve)
            if do_animate_curve:
                self.play(Create(redrawn_mobjects["curve"]))
            else:
                self.add(redrawn_mobjects["curve"])
        if do_add_dots:

            def get_dots():
                dots = []
                for i in range(k):
                    dots.append(
                        Dot(
                            to_3D(
                                segments[i].body.local_to_world(
                                    (signs[i] * dists[i] / 2 * gap_ratio, 0)
                                )
                            )
                        )
                    )
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
            constraints.append(
                pymunk.constraints.PinJoint(
                    segments[0].body,
                    pendant.body,
                    (-signs[0] * dists[0] / 2 * gap_ratio, 0),
                )
            )
            self.space.space.add(constraints[-1])
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


def get_teardrop_curve(head=np.array([-1, 0, 0]), tail=np.array([1, 0, 0]), width=1, m=2):
    length = np.linalg.norm(head - tail) / 2
    center = (head + tail) / 2
    normalized = (head - tail) / np.linalg.norm(head - tail)
    angle = -np.arccos(np.dot(normalized, [-1, 0, 0]))
    _cos, _sin = np.cos(angle), np.sin(angle)
    rot_matrix = np.array(((_cos, -_sin), (_sin, _cos)))
    return (
        lambda t: center
        + to_3D(
            length
            * rot_matrix.dot(np.array([np.cos(t), width * np.sin(t) * np.sin(t / 2) ** m]))
        ),
        np.array([0, 2 * PI]),
    )


def get_smoother(t_range=[0, 1]):
    start, end = t_range
    return lambda t: end * ((2 * (t / end - 0.5)) ** 3 / 2 + 0.5)
