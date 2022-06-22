from typing import Union, Callable, List
from xmlrpc.client import Boolean
from beartype import beartype
from manim import RIGHT
from jxprutils import vgroup
from copy import deepcopy
from box import Box

class JExpressionManager:

    # from jxprlib import get_terms, get_op
    # self.mobs["expr"] = {
    #     **get_terms(topic="PlusRank", scene="SimplerProblemScene",
    #                 kwargs={"lhs2": {"h_buff": 2.0}})[0],
    #     **{"verb": get_verb(entry="plus00")},
    # }

    # expr = JExpressionManager(self.mobs["expr"])
    # (
    #     expr.update({"verb": get_op(entry="plus")})
    #     .set_color(items=BLUE, circumshapes=RED, subexpr=["y"], indices=[1])
    #     .set_color(GREEN, subexpr=["verb"])
    #     .set_opacity(circumshapes=0.75, subexpr=["y"])
    #     .set_opacity(items=0.5, indices=[0, 2], subexpr=["x"])
    #     .scale(1.5, subexpr=["x"])
    # )

    # self.play(Write(expr.grouped_expr))
    # self.wait()
    # self.remove(*expr.grouped_expr)
    # self.wait(3)
    # expr.set_color(items=RED, subexpr=["x"], indices=[0,2])
    # self.play(Write(expr.grouped_expr))
    # self.remove(expr.grouped_expr)
    #
    # FadeToColor
    # self.play(
    #     ReplacementTransform(expr.copy().grouped_expr,
    #                          expr.set_color(YELLOW, subexpr=["verb"]).grouped_expr),
    #     run_time=3)
    #
    # FadeToOpacity
    # self.play(
    #     ReplacementTransform(
    #         expr.copy().grouped_expr,
    #         expr.transform(subexpr=["verb"],
    #                        func = lambda x: x[0].set_opacity(1)).grouped_expr),
    #     run_time=3)

    # self.play(
    #     ReplacementTransform(
    #         expr.copy().grouped_expr,
    #         expr.transform(subexpr=["verb"],
    #                        func = lambda x: x[1].set_opacity(1)).grouped_expr),
    #     run_time=3)

    @beartype
    def __init__(self, expr: Union[dict, Box]):
        self.__jexpr__ = Box(expr, box_dots=True)
        self.__grouper__ = lambda x: vgroup(*x.values()).arrange(RIGHT, buff=0.4)
        self.regroup()
        self.__order__ = []

    def copy(self):
        return deepcopy(self)

    @beartype
    def set_order(self, order: List[str]):
        self.__order__ = order
        return self

    @beartype
    def regroup(self):
        self.__grouped_jexpr__ = self.__grouper__(self.__jexpr__)
        return self

    @beartype
    def reorder(self, order: List[str] = []):
        order = order or self.__order__
        self.__jexpr__ = Box({k: self.__jexpr__[k] for k in order})
        self.regroup()
        return self

    @property
    def grouper(self):
        return self.__grouper__

    @beartype
    def set_grouper(self, val: Callable):
        self.__grouper__ = val
        self.regroup()
        return self

    @property
    def jexpr(self):
        return self.__jexpr__

    @property
    def grouped_expr(self):
        return self.__grouped_jexpr__

    @beartype
    def update(self, subexpr: Union[dict, Box]):
        self.__jexpr__ |= Box(subexpr)
        self.regroup()
        return self       
        
    @beartype
    def set_property(self, func: str, *args, **kwargs):
        keys = (
            kwargs.pop("subexpr")
            if "subexpr" in kwargs.keys()
            else self.__jexpr__.keys()
        )

        for k in keys:
            if hasattr(self.__jexpr__[k], func):
                getattr(self.__jexpr__[k], func)(*args, **kwargs)
            else:  # CircumscribedJMatrix and attr is undefined
                getattr(self.__jexpr__[k].matrix, func)(*args, **kwargs)
        return self

    def set_opacity(self, *args, **kwargs):
        return self.set_property("set_opacity", *args, **kwargs)

    def set_color(self, *args, **kwargs):
        return self.set_property("set_color", *args, **kwargs)

    def set_scale(self, *args, **kwargs):
        return self.set_property("scale", *args, **kwargs)

    @beartype
    def transform(self, func: Callable, subexpr: List[str] = []):
        keys = self.__jexpr__.keys() if not subexpr else subexpr

        for k in keys:
            self.__jexpr__[k] = func(self.__jexpr__[k])
            
        return self

