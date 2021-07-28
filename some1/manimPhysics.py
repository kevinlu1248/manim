from manim import *
from manim_physics import *
import pymunk
import scipy as sp
import scipy.interpolate

# config.frame_rate = 120  # otherwise clips
config.frame_rate = 60
EPS = 1e-09

def to_3D(vector_like):
    return np.array([vector_like[0], vector_like[1], 0])

def cart2polar(x, y):
    return np.sqrt(x ** 2 + y ** 2), np.arctan(y / 2)

def polar2cart(r, theta):
    return r * np.cos(theta), r * np.sin(theta)

def get_interpolator(vectors, offset=0.001, do_use_polar=False):
    vectors = vectors + [vectors[0] + np.array([offset, offset])]
    x, y = zip(*vectors)

    if do_use_polar:
        x, y = np.array(x), np.array(y)
        r = np.sqrt(x ** 2 + y ** 2)
        theta = np.arctan2(y, x)
        tck, _unused_u = sp.interpolate.splprep([r, theta], k=3, s=0)
        return lambda t: to_3D(polar2cart(*next(zip(*sp.interpolate.splev([t], tck))))), [0, 1]


    tck, _unused_u = sp.interpolate.splprep([x, y], k=3, s=0)
    return lambda t: to_3D(next(zip(*sp.interpolate.splev([t], tck)))), [0, 1]

    # kind = "cubic"
    # f = sp.interpolate.PPoly(range(len(x)), x)
    # # fy = sp.interpolate.PPoly(range(len(y)), y)
    # return lambda t: to_3D(f(t)), [0, len(x) - 1]

# use a SpaceScene to utilize all specific rigid-mechanics methods
class Chains(SpaceScene):
    gap = 0.1
    num_of_chains = 0

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

    def make_chain(
        self,
        func,
        t_range,
        k=19,
        thickness=0.01,
        gap_ratio=1,
        do_loop=False,
        color=WHITE,
        do_smooth=True,
        do_add_dots=False,
        offset=0.001
    ):  # parametric
        # self.add(ParametricFunction(func, t_range=t_range, color=GREY))
        Chains.num_of_chains += 1
        segments = []
        signs = []
        dists = []
        constraints = []
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
                    .set_fill(color, 0.0)
                    .set_stroke(color, 0.0)
                    .shift(center)
                    .rotate(angle)
                )
                segments.append(rect)
                self.init_body(rect)
                rect.shape.filter = pymunk.ShapeFilter(group=Chains.num_of_chains)
                self.add_body(rect)

                if section > 1:
                    constraints.append(
                        pymunk.constraints.PivotJoint(
                            prev_rect.body,
                            rect.body,
                            (prev_sign * prev_dist / 2 * gap_ratio, 0),
                            (-sign * dist / 2 / gap_ratio, 0),
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
            def redraw():
                mobjects = []
                vectors = []
                for i in range(k):
                    vector = segments[i].body.local_to_world((signs[i] * dists[i] / 2 * gap_ratio, 0))
                    vectors.append(vector)
                    mobjects.append(Dot(to_3D(vector), fill_opacity=0.0))
                interpolator, t_range = get_interpolator(vectors, offset=offset)
                curve = ParametricFunction(interpolator, t_range, color=BLUE)
                mobjects.append(curve)
                if do_add_dots:
                    return mobject.mobject.Group(*mobjects)
                else:
                    return curve

            self.add(always_redraw(redraw))
        else:
            for i in range(k):
                def redraw(sign=signs[i], rect=segments[i], dist=dists[i]):
                    vectors = to_3D(rect.body.local_to_world((sign * dist / 2 * gap_ratio, 0)))
                    return Dot(vectors)
                self.add(always_redraw(redraw))

        if do_loop:
            assert np.linalg.norm(func(t_range[0]) - func(t_range[1])) < 1e-9
            constraints.append(
                pymunk.constraints.PivotJoint(
                    prev_rect.body,
                    first_rect.body,
                    (prev_sign * prev_dist / 2 * gap_ratio, 0),
                    (-first_sign * first_dist / 2 / gap_ratio, 0),
                )
            )

            self.space.space.add(constraints[-1])

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

    def construct(self):
        self.gap = 0.1
        self.space.space.gravity = 0, -9.81

        r = 0.5

        nail1 = Circle(r).set_fill(WHITE, 1).set_stroke(WHITE, 1).shift(LEFT)
        nail2 = Circle(r).set_fill(WHITE, 1).set_stroke(WHITE, 1).shift(RIGHT)
        nails = VGroup(nail1, nail2)

        self.add(nails)

        self.make_static_body(nails)

        # func = lambda t: np.array([t * 2, 3 - t ** 2, 0])
        func = lambda t: 2 * np.array([np.cos(2 * PI * t), np.sin(2 * PI * t), 0])
        self.make_chain(func, t_range=np.array([0, 1]), do_loop=True)

        self.wait(5)
