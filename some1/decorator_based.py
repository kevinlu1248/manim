from typing import Callable

from manim import *


def newScene(construct: Callable[[Scene], None]) -> None:
    globals()[construct.__name__ + "__scene__"] = type(
        construct.__name__, tuple([Scene]), {"construct": construct}
    )


@newScene
def MyScene(scene):
    scene.wait()


@newScene
def NextScene(scene):
    scene.wait()
