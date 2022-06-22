from tkinter import CENTER
from xmlrpc.client import Boolean
from manim import *
from copy import deepcopy
from typing import Union, Optional, Callable
from beartype import beartype
from collections.abc import Iterable


class CirumscribedJMatrix:
    @beartype
    def __init__(self, matrix: MobjectMatrix, get_items: str, circumshape: Mobject):
        self.matrix = matrix.copy()
        self.matrix_items = getattr(self.matrix, get_items)()

        self.nitems = len(self.matrix_items)
        itemnums = range(self.nitems)

        self.circumshapes = circumshape
        if not isinstance(circumshape, list):
            self.circumshapes = [circumshape.copy() for _ in itemnums]

        for i in itemnums:
            self.circumshapes[i].move_to(self.matrix_items[i].get_center())
            self.matrix.add(VGroup(self.circumshapes[i], self.matrix_items[i]))

    def copy(self):
        return deepcopy(self)

    @beartype
    def set_property(
        self,
        attr: str,
        all: Optional[Union[int, float, str]] = None,
        circumshapes: Optional[Union[int, float, str]] = None,
        items: Optional[Union[int, float, str]] = None,
        indices: Optional[Iterable[int]] = None,
        *args,
        **kwargs
    ):

        if all is not None:
            circumshapes = items = all

        indexes = indices or range(self.nitems)
        mics = [x for i, x in enumerate(iter(self)) if i in indexes]

        for mi, cs in mics:
            if circumshapes is not None:
                getattr(cs, attr)(circumshapes, *args, **kwargs)
                cs.set_fill(opacity=0)
            if items is not None:
                getattr(mi, attr)(items, *args, **kwargs)

        return self

    def __getitem__(self, index):
        return (self.matrix_items[index], self.circumshapes[index])

    def set_color(self, *args, **kwargs):
        return self.set_property("set_color", *args, **kwargs)

    def set_stroke(self, *args, **kwargs):
        return self.set_property("set_stroke", *args, **kwargs)

    def set_opacity(self, *args, **kwargs):
        return self.set_property("set_opacity", *args, **kwargs)

    def set_scale(self, *args, **kwargs):
        return self.set_property("scale", *args, **kwargs)

    @beartype
    def set_focus(self, indices: Iterable[int], defocus: float = 0.1):

        indexes = list(set(range(self.nitems)) - set(indices))
        self.set_opacity(circumshapes=defocus, items=defocus, indices=indexes)

        self.set_opacity(circumshapes=1.0, items=1.0, indices=indices)

        return self

    @beartype
    def align(self, along="entries"):
        """
        Aligns all entries to the 0th item.
        """
        items = self.matrix.get_columns() if along=="columns" else self.matrix.get_rows()         
        mi, cs = self.matrix_items, self.circumshapes

        dir = LEFT if along=="rows" else UP 
        for i, m in enumerate(items):
            if along=="row" or along=="columns":
                cs[i].align_to(cs[0], dir)
                mi[i].align_to(mi[0], dir)
            else:
                for j, _ in enumerate(m):
                    cs[i * len(m) + j].align_to(cs[i * len(m)], DOWN)
                    mi[i * len(m) + j].align_to(mi[i * len(m)], DOWN)

                    # Align entries of first column
                    if not j:
                        cs[i * len(m) + j].align_to(cs[0], LEFT)
                        mi[i * len(m) + j].align_to(mi[0])
                        
        return self

    @beartype
    def animate(
        self,
        all: Optional[Union[Callable, Animation]] = None,
        items: Optional[Union[Callable, Animation]] = None,
        circumshapes: Optional[Union[Callable, Animation]] = None,
        indices: Optional[Iterable[int]] = None,
    ):
    
        """
        self.play(*expr.animate(Wiggle, indices=[9, 10, 11]), run_time=3)
        """

        if all is not None:
            circumshapes = items = all

        indexes = indices or range(self.nitems)
        mics = [x for i, x in enumerate(iter(self)) if i in indexes]

        anims = []
        for mi, cs in mics:
            anims += [items(mi)] if items is not None else []
            anims += [circumshapes(cs)] if circumshapes is not None else []

        return anims
