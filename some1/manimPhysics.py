from manim import *
from manim_physics import *
import pymunk

# config.frame_rate = 90  # otherwise clips
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

    def make_chain(self, func, t_range, k=20, thickness=0.02, gap_ratio=0.99):  # parametric
        self.add(ParametricFunction(func, t_range=t_range, color=GREY))
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

                    if False:
                        start = to_3D(prev_rect.body.position)
                        end = to_3D(
                            prev_rect.body.local_to_world([(prev_sign * prev_dist) / 2 / gap_ratio, 0])
                        )

                        self.add(Dot(start, color=ORANGE))
                        self.add(Text(f"{section}s{'+' if prev_sign > 0 else '-'}").scale(0.3).shift(start + UP * 0.5))
                        self.add(
                            Line(
                                start=start,
                                end=end,
                                color=BLUE,
                            )
                        )
                        self.add(Text(f"{section}e{'+' if prev_sign > 0 else '-'}").scale(0.3).shift(end + DOWN * 0.5))

                    if False:
                        start = to_3D(rect.body.position)
                        end = to_3D(
                            rect.body.local_to_world([(sign * dist) / 2 / gap_ratio, 0])
                        )

                        self.add(Dot(start, color=ORANGE))
                        self.add(Text(f"{section}s{'+' if sign > 0 else '-'}").scale(0.3).shift(start + UP * 0.5))
                        self.add(
                            Line(
                                start=start,
                                end=end,
                                color=BLUE,
                            )
                        )
                        self.add(Text(f"{section}e{'+' if sign > 0 else '-'}").scale(0.3).shift(end + DOWN * 0.5))

                    self.space.space.add(constraints[-1])

                rect.add_updater(simulate)

                prev_center = center
                prev_dist = dist
                prev_rect = rect
                prev_sign = sign

            prev_point = point

    def construct(self):
        self.gap = 0
        self.gap = 0.1

        chain1 = (
            Rectangle(height=0.05, width=1)
            .shift(UP * 3 + LEFT * (1 + self.gap * 2))
            .set_stroke(RED)
            .set_fill(RED)
            .rotate(PI / 6)
            .shift(
                # trust the calculations
                DOWN * (np.arcsin(PI / 6) * (1 + self.gap) / 2)
                + RIGHT * (0.5 + self.gap) * (1 - np.cos(PI / 6))
            )
        )

        chain2 = (
            Rectangle(height=0.05, width=1)
            .shift(UP * 3)
            .set_stroke(BLUE)
            .set_fill(BLUE)
        )

        chain3 = (
            Rectangle(height=0.05, width=1)
            .shift(UP * 3 + RIGHT * (1 + self.gap * 2))
            .set_stroke(GREEN)
            .set_fill(GREEN)
            .rotate(5 * PI / 6)
            .shift(
                DOWN * (np.arcsin(PI / 6) * (1 + self.gap) / 2)
                + LEFT * (0.5 + self.gap) * (1 - np.cos(PI / 6))
            )
        )

        # wall stuff
        ground = Line([-4, -3.5, 0], [4, -3.5, 0])
        wall1 = Line([-4, -3.5, 0], [-4, 3.5, 0])
        wall2 = Line([4, -3.5, 0], [4, 3.5, 0])
        # wall3 = Line([0, -3.5, 0], [1, 0, 0])
        nail = Circle(1)
        walls = VGroup(ground, wall1, wall2, nail)
        self.add(walls)

        # self.make_chained_body(chain1, chain2, chain3)

        func = lambda t: np.array([t * 2, 3 - t ** 2, 0])
        self.make_chain(func, t_range=np.array([-1, 1]))

        # self.make_rigid_body(chain1, chain2)
        self.make_static_body(walls)  # Mobjects will stay in place
        self.wait(5)
