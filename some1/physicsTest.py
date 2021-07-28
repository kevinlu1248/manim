import random

from manim import *
import pymunk


class Space(Mobject):
    def __init__(self, dt, **kargs):
        Mobject.__init__(self, **kargs)
        self.space = pymunk.Space()
        self.space.gravity = 0, -9.8
        self.dt = dt

    def add_body(self, body):
        if body.body != self.space.static_body:
            self.space.add(body.body)
        self.space.add(body.shape)


def step(space, dt):
    space.space.step(dt)


def simulate(b):
    x, y = b.body.position
    b.move_to(x * RIGHT + y * UP)
    b.rotate(b.body.angle - b.angle)
    b.angle = b.body.angle


class PhysicTest(Scene):
    def construct(self):
        space = Space(1 / self.camera.frame_rate)
        self.add(space)

        circle = Circle().shift(UP)
        circle.set_fill(RED, 1)
        circle.shift(DOWN + RIGHT)

        circle.body = pymunk.Body()
        circle.body.position = circle.get_center()[0], circle.get_center()[1]
        circle.shape = pymunk.Circle(circle.body, circle.get_width() / 2)
        circle.shape.elasticity = 0.8
        circle.shape.density = 1
        circle.angle = 0

        rect = Square().shift(UP)
        rect.rotate(PI / 4)
        rect.set_fill(YELLOW_A, 1)
        rect.shift(UP * 2)
        rect.scale(0.5)

        rect.body = pymunk.Body()
        rect.body.position = rect.get_center()[0], rect.get_center()[1]
        rect.body.angle = PI / 4
        rect.shape = pymunk.Poly.create_box(rect.body, (1, 1))
        rect.shape.elasticity = 0.4
        rect.shape.density = 2
        rect.shape.friction = 0.8
        rect.angle = PI / 4

        ground = Rectangle(width=20, height=0.1)
        ground.shift(3 * DOWN)
        ground.body = space.space.static_body
        ground.shape = pymunk.Segment(ground.body, (-10, -3), (10, -3), 0.1)
        ground.shape.elasticity = 0.99
        ground.shape.friction = 0.8
        self.add(ground)

        wall1 = Rectangle(width=0.1, height=10)
        wall1.shift(4 * LEFT)
        wall1.body = space.space.static_body
        wall1.shape = pymunk.Segment(wall1.body, (-4, -5), (-4, 5), 0.1)
        wall1.shape.elasticity = 0.99
        self.add(wall1)

        wall2 = Rectangle(width=0.1, height=10)
        wall2.shift(4 * RIGHT)
        wall2.body = space.space.static_body
        wall2.shape = pymunk.Segment(wall2.body, (4, -5), (4, 5), 0.1)
        wall2.shape.elasticity = 0.99
        self.add(wall2)

        self.play(DrawBorderThenFill(circle), DrawBorderThenFill(rect))
        self.wait()

        space.add_body(circle)
        space.add_body(rect)
        space.add_body(ground)
        space.add_body(wall1)
        space.add_body(wall2)
        space.add_updater(step)
        circle.add_updater(simulate)
        rect.add_updater(simulate)
        self.wait(10)


class TextTest(Scene):
    def construct(self):
        space = Space(1 / self.camera.frame_rate)
        self.add(space)
        space.add_updater(step)

        ground = Line(5 * LEFT + 3 * DOWN, 5 * RIGHT + 3 * DOWN)
        self.play(Create(ground))
        ground.body = space.space.static_body
        ground.shape = pymunk.Segment(ground.body, (-5, -3), (5, -3), 0.05)
        ground.shape.elasticity = 0.9
        ground.shape.friction = 0.8
        space.add_body(ground)

        def add_physic(text):
            parts = text.family_members_with_points()
            for p in parts:
                self.add(p)
                p.body = pymunk.Body()
                p.body.position = p.get_center()[0], p.get_center()[1]
                p.shape = pymunk.Poly.create_box(
                    p.body, (p.get_width(), p.get_height())
                )
                p.shape.elasticity = 0.4
                p.shape.density = 1
                p.shape.friction = 0.8

                p.angle = 0
                space.add_body(p)
                p.add_updater(simulate)

        forms = [
            r"a^2-b^2=(a+b)(a-b)",
            r"x_{1,2}=\frac{-b\pm \sqrt{b^2-4ac}}{2a}",
            r"e^{i\pi}+1=0",
            r"\cos(x+y)=\cos x \cos y - \sin x \sin y",
            r"e^x=\sum_{i=0}^\infty \frac{x^i}{i!}",
        ]

        for f in forms:
            text = MathTex(f)
            self.play(Write(text))
            self.remove(text)
            add_physic(text)
            self.wait(5)


def createWall(start, end, space):
    obj = Line(start, end)
    obj.body = space.space.static_body
    obj.shape = pymunk.Segment(obj.body, (start[0], start[1]), (end[0], end[1]), 0)
    obj.shape.elasticity = 0.98
    obj.shape.friction = 0.5
    obj.shape.elasticity = 0.98
    obj.shape.friction = 0.5
    return obj


class Plinko(Scene):
    def construct(self):
        space = Space(1 / self.camera.frame_rate)
        self.add(space)
        space.space.gravity = 0, -3
        space.add_updater(step)

        for i in range(14):
            for j in range(5):
                x = float(i) - 7
                y = float(j) - 1.5
                if j % 2 == 0:
                    x += 0.5
                plk = Circle()
                plk.scale(0.3)
                plk.move_to(x * RIGHT + y * UP)
                plk.set_fill(RED, opacity=1)
                self.add(plk)

                plk.body = pymunk.Body(body_type=pymunk.Body.STATIC)
                plk.body.position = (x, y)
                plk.shape = pymunk.Circle(plk.body, plk.get_width() / 2)
                space.add_body(plk)

        leftWall = createWall(LEFT * 7 + DOWN * 4, LEFT * 7 + UP * 4, space)
        self.add(leftWall)
        space.add_body(leftWall)

        rightWall = createWall(RIGHT * 7 + DOWN * 4, RIGHT * 7 + UP * 4, space)
        self.add(rightWall)
        space.add_body(rightWall)

        ground = createWall(LEFT * 10 + DOWN * 3.5, RIGHT * 10 + DOWN * 3.5, space)
        self.add(ground)
        space.add_body(ground)

        for i in range(28):
            x = float(i) / 2 - 7
            wall = createWall(RIGHT * x + DOWN * 3.5, RIGHT * x + DOWN * 2, space)
            self.add(wall)
            space.add_body(wall)

        # 80
        for i in range(80):
            radius = 0.15
            ball = Circle(radius=radius)
            new_x = 2 * random.random() - 1
            ball.set_fill(BLUE, opacity=1)
            ball.body = pymunk.Body()
            ball.body.position = new_x, 4
            ball.move_to(np.array([new_x, 4, 0]))
            ball.shape = pymunk.Circle(ball.body, radius)
            ball.shape.elasticity = 0.1
            ball.shape.friction = 0.1
            ball.shape.density = 1

            self.add(ball)
            space.add_body(ball)
            ball.add_updater(simulate)
            self.wait(0.5)

        self.wait(30)
