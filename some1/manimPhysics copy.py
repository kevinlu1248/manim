from manim import *
from manim_physics import *
import pymunk

# config.frame_rate = 120  # otherwise clips
config.frame_rate = 60


def to_3D(vector_like):
    return np.array([vector_like[0], vector_like[1], 0])


# use a SpaceScene to utilize all specific rigid-mechanics methods
class Chains(SpaceScene):
    gap = 0.1

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

    def make_chained_body(
        self,
        # *mobs,
        chain1,
        chain2,
        chain3,
        elasticity=0.8,
        density=1,
        friction=0.8,
    ):
        for chain in (chain1, chain2, chain3):
            self.init_body(chain, elasticity, density, friction)
            self.add_body(chain)
            chain.add_updater(simulate)

        constraint1 = pymunk.constraints.PivotJoint(
            chain1.body, chain2.body, (0.5 + self.gap, 0), (-(0.5 + self.gap), 0)
        )

        constraint2 = pymunk.constraints.PivotJoint(
            chain2.body, chain3.body, (0.5 + self.gap, 0), (0.5 + self.gap, 0)
        )

        self.space.space.add(constraint1)
        self.space.space.add(constraint2)

    def make_chain(
        self, func, t_range, k=20, thickness=0.1, gap_ratio=0.99, color=WHITE
    ):  # parametric
        # self.add(ParametricFunction(func, t_range=t_range, color=GREY))
        segments = []
        constraints = []
        prev_point = func(0)
        for section in range(k + 1):
            t = t_range[0] + (t_range[1] - t_range[0]) * section / k
            point = func(t)
            if section > 0:
                center = (prev_point + point) / 2
                delta = point - prev_point

                dist = np.linalg.norm(delta)
                dot_product = np.dot(delta / dist, [1, 0, 0])
                sign = -np.sign(np.cross(delta / dist, [1, 0, 0])[-1])
                if sign >= 0:
                    sign = 1
                angle = np.arccos(sign * dot_product)

                rect = (
                    Rectangle(width=dist * (1 - (1 - gap_ratio) * 2), height=thickness)
                    .set_fill(color, 1)
                    .set_color(color, 1)
                    .shift(center)
                    .rotate(angle)
                )
                segments.append(rect)
                self.init_body(rect)
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

                rect.add_updater(simulate)

                prev_center = center
                prev_dist = dist
                prev_rect = rect
                prev_sign = sign

            prev_point = point

    def construct(self):
        self.gap = 0.1
        self.space.space.gravity = 0, -1

        # wall stuff
        # ground = Line([-4, -3.5, 0], [4, -3.5, 0])
        # wall1 = Line([-4, -3.5, 0], [-4, 3.5, 0])
        # wall2 = Line([4, -3.5, 0], [4, 3.5, 0])
        nail1 = Circle(0.3).shift(LEFT).set_fill(RED, 1)
        nail2 = Circle(0.3).shift(RIGHT).set_fill(RED, 1)
        walls = VGroup(nail1, nail2)
        self.add(walls)

        # self.make_chained_body(chain1, chain2, chain3)

        func = lambda t: np.array([t * 2, 3 - t ** 2, 0])
        self.make_chain(func, t_range=np.array([-1.5, 1.5]))

        self.make_static_body(walls)  # Mobjects will stay in place
        self.wait(5)
