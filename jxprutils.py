from decimal import Rounded
from manim import *
from jxprmat import CirumscribedJMatrix
import toml
from box import Box
from dataclasses import dataclass
from beartype import beartype
from typing import Union, List, Tuple

DEFAULTS = Box(toml.load("defaults.toml"), box_dots=True, frozen_box=True)


@beartype
def vgroup(*args, copy: bool = False) -> VGroup:
    expr = VGroup()
    if copy:
        args = list(map(lambda x: x.copy(), args))

    for arg in args:
        if isinstance(arg, CirumscribedJMatrix):
            expr += arg.matrix
        else:
            expr += arg

    return expr


@beartype
def make_circummat(
    matrix: Union[List, Tuple],
    circumitems: str = DEFAULTS.matrix.circumitems,
    circumshape: Mobject = None,
    **kwargs
) -> CirumscribedJMatrix:

    defaults = Box(
        {
            "element_to_mobject": Text,
            "element_to_mobject_config": {
                "font": DEFAULTS.fonts.mono,
                "color": DEFAULTS.fonts.color,
                "font_size": DEFAULTS.fonts.size,
            },
            "v_buff": DEFAULTS.matrix.v_buff,
            "h_buff": DEFAULTS.matrix.h_buff,
            "element_alignment_corner": DEFAULTS.matrix.element_alignment_corner,
        }
    )

    matargs = Box(defaults) + Box(kwargs, default_box=True)
    mat = MobjectMatrix(matrix, **matargs)
    mat.get_brackets().set_opacity(0)

    if circumshape is None:
        circumshape = RoundedRectangle(
            **DEFAULTS.box.options, **DEFAULTS.box.sizes[circumitems]
        )
    return CirumscribedJMatrix(mat, ("get_" + circumitems), circumshape)


make_term = make_circummat


@beartype
def make_verb(verb: str, **kwargs) -> Text:
    format = Box(
        {
            "font": DEFAULTS.fonts.mono,
            "color": DEFAULTS.verb.color,
            "font_size": DEFAULTS.verb.font_size,
        }
    ) + Box(kwargs, default_box=True)
    return Text(verb, **format)


@beartype
def make_equals(equals: str, **kwargs) -> Tex:
    format = Box(
        {"color": DEFAULTS.equals.color, "font_size": DEFAULTS.equals.font_size},
    ) + Box(kwargs, default_box=True)
    return Tex(equals, **format)


@beartype
def make_title(
    markup_string: str,
    fill_color: str = DEFAULTS.title.fill_color,
    stroke_color: str = DEFAULTS.title.stroke_color,
    font: str = DEFAULTS.fonts.sans,
) -> VGroup:

    title = VGroup()
    box = Rectangle(
        height=1.00,
        width=13,
        fill_color=fill_color,
        stroke_color=stroke_color,
        fill_opacity=0.10,
    )

    if font is not None:
        markup_string = "<span font_family='" + font + "'>" + markup_string + "</span>"

    text = MarkupText(markup_string).scale(1.00).move_to(box.get_center())

    title.add(box, text).to_edge(UP - 0.25 * UP)
    title.to_edge(UP).shift([0, 0.30, 0])

    return title


@dataclass(frozen=True)
class SceneConfig:
    title: VGroup
    font_sans: str = DEFAULTS.fonts.sans
    font_mono: str = DEFAULTS.fonts.mono
    wait_time: int = DEFAULTS.scene.wait_time
