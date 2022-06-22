from cProfile import run
from ctypes import alignment
from dataclasses import replace
from socket import create_connection
from tkinter import CENTER, E
from manim import *
from toolz.itertoolz import concat
from typing import Union, Iterable
from pathlib import Path
from functools import partial
from jxprutils import make_title, SceneConfig, vgroup
from jxprlib import get_terms, get_verb, get_equals
from jxprmgr import JExpressionManager
from jxprmat import CirumscribedJMatrix
import toml
from box import Box
from beartype import beartype

LIB = Box(toml.load("lib.toml"), frozen_box=True)
DEFAULTS = Box(toml.load("defaults.toml"), frozen_box=True)

SCENE_CONFIG = SceneConfig(
    title=make_title(
        markup_string='<span foreground="#58C4DD" size="x-large"> + </span> and <span foreground="#58C4DD" size="x-large"> " </span>'
    )
)

Text = partial(Text, font=SCENE_CONFIG.font_sans)
empty_box = Box(default_box=True)

# [self.remove(*x) for x in expr.grouped_expr]
class IntroductionScene(Scene):
    mobs = Box(default_box=True, default_box_attr=[])
    mobs.descr = Text("Let's examine that last case in more detail...").scale(0.9)

    def construct(self):
        self.add(SCENE_CONFIG.title)
        self.play(Write(self.mobs.descr))
        self.wait(SCENE_CONFIG.wait_time)


class PlusRankScene(Scene):

    CONFIG = {"run_time": 0.1}

    mobs = Box(default_box=True, default_box_attr=[])

    @beartype
    def show_mobj(
        self,
        mobj,
        replace_mobj=None,
        attr: str = None,
        creation_animation=FadeIn,
        replacement_animation=FadeTransform,
        **kwargs
    ):

        if attr is not None:
            self.mobs[attr].append(mobj)

        if replace_mobj is None:
            self.play(creation_animation(mobj), **kwargs)
            self.wait(SCENE_CONFIG.wait_time)
        else:
            self.play(replacement_animation(replace_mobj, mobj), **kwargs)
            self.wait(SCENE_CONFIG.wait_time)

    @beartype
    def get_expr(
        self,
        terms_index: int = 0,
        verb: str = None,
        equals: str = None,
        terms_kwargs: Union[dict, Box] = empty_box,
        verb_kwargs: Union[dict, Box] = empty_box,
        equals_kwargs: Union[dict, Box] = empty_box,
    ):
        terms = get_terms(
            topic="PlusRank", scene=type(self).__name__, mobmatrix_args=terms_kwargs
        )[terms_index]

        verb = (
            {"verb": get_verb(entry=verb, **verb_kwargs)}
            if verb is not None
            else empty_box
        )
        equals = (
            {"equals": get_equals(entry=equals, **equals_kwargs)}
            if equals is not None
            else empty_box
        )

        return JExpressionManager({**terms, **verb, **equals})

    def add_title(self, title=SCENE_CONFIG.title):
        self.add(title)


class SimplerProblemScene(PlusRankScene):
    def text(self, x):
        return Text(x).scale(0.9).next_to(SCENE_CONFIG.title, DOWN).shift([0, -0.75, 0])

    def setup(self):

        self.mobs.expr = (
            self.get_expr(verb="plus_rank00")
            .set_order(["x", "verb", "y"])
            .reorder()
            .set_scale(0.9, subexpr=["verb"])
            .set_opacity(circumshapes=0, subexpr=["x", "y"])
        )

        self.place_expr = lambda x, y: x.grouped_expr.next_to(y, DOWN).shift(DOWN)

    def show_problem(self):

        self.show_mobj(
            attr="descr",
            mobj=self.text("How does the simpler sentence below work?"),
            replace_mobj=IntroductionScene.mobs.descr,
            replacement_animation=TransformFromCopy,
        )

        self.show_mobj(
            attr="show_expr",
            mobj=self.place_expr(
                self.mobs.expr.copy().update({"verb": get_verb("plus")}),
                self.mobs.descr[-1],
            ),
            creation_animation=Create,
        )

    def show_expansion(self):

        self.show_mobj(
            attr="descr",
            mobj=self.text("Expressed in terms of rank it looks like this, "),
            replace_mobj=self.mobs.descr[-1],
            replacement_animation=ReplacementTransform,
        )

        self.show_mobj(
            attr="show_expr",
            mobj=self.place_expr(self.mobs.expr, self.mobs.descr[-1]),
            replace_mobj=self.mobs.show_expr[-1],
            replacement_animation=ReplacementTransform,
        )

    def construct(self):
        self.add_title()
        self.show_problem()
        self.show_expansion()


class Plus00Rank1XRank1YScene(PlusRankScene):
    mobs = Box(default_box=True, default_box_attr=[])

    SUBEXPR_COLORS = Box(DEFAULTS.matrix.color_palette.three_color)

    def setup_expr(self):
        self.mobs.expr = (
            self.get_expr(
                verb="plus_rank00",
                equals="downarrow",
                terms_kwargs={"x_plus_y": {"h_buff": 2.25}},
            )
            .set_order(["x", "verb", "y", "equals", "x_plus_y"])
            .reorder()
            .set_scale(0.9, subexpr=["verb"])
            .set_opacity(circumshapes=0, subexpr=["x", "y"])
            .set_opacity(0, subexpr=["equals", "x_plus_y"])
        )

        self.mobs.expr.set_grouper(
            lambda j: vgroup(
                vgroup(j.x, j.verb, j.y).arrange(RIGHT, buff=0.4),
                j.equals,
            )
            .arrange(DOWN, buff=0.4)
            .next_to(SCENE_CONFIG.title, 3 * DOWN)
        )

        self.mobs.expr.jexpr.x_plus_y.matrix.next_to(
            self.mobs.expr.jexpr.equals, 5 * DOWN
        )

    @beartype
    def reveal_rank(
        self, term: str, color: str, opacity: float = 1.0, indices: List[int] = None
    ):
        texpr = self.mobs.expr.jexpr[term]

        texpr.set_opacity(circumshapes=opacity, indices=indices)

        indexes = indices or range(texpr.nitems)
        mics = [x for i, x in enumerate(iter(texpr)) if i in indexes]

        # Set color for all elements
        if indices is not None:
            texpr.set_color(color, indices=[i for i in indices if i not in indexes])

        return concat(
            [
                [
                    Write(cs.set_color(color).set_opacity(opacity).set_fill(opacity=0)),
                    ReplacementTransform(mi.copy(), mi.set_color(color)),
                ]
                for mi, cs in mics
            ]
        )

    def color_verb_rankxy(self):
        verb = self.mobs.expr.jexpr.verb
        verb_copy = verb.copy()
        verb.set_color(DARKER_GRAY)
        verb[1].set_color(DARK_GRAY)
        verb[2].set_color(LIGHT_GRAY)
        verb[3].set_color(self.SUBEXPR_COLORS.x)
        verb[4].set_color(self.SUBEXPR_COLORS.y)

        return ReplacementTransform(verb_copy, verb)

    @beartype
    def color_subexpr(
        self,
        lag: float = 0.15,
        xargs: Union[dict, Box] = {},
        yargs: Union[dict, Box] = {},
    ):
        self.play(self.color_verb_rankxy())
        self.play(
            AnimationGroup(
                *self.reveal_rank(term="x", color=self.SUBEXPR_COLORS.x, **xargs),
                *self.reveal_rank(term="y", color=self.SUBEXPR_COLORS.y, **yargs),
                lag_ratio=lag,
            )
        )

    @beartype
    def move_subexpr_to_target(
        self,
        item: str,
        index: int,
        v_dist: float = 1.1,
        h_buff: float = 0.6,
        h_buff_scale: float = 1.0,
        scale: float = 0.7,
    ):
        expr = self.mobs.expr
        if isinstance(expr.jexpr[item], CirumscribedJMatrix):
            subexpr = expr.jexpr[item].copy().matrix_items[index]
        else:
            subexpr = expr.jexpr[item][1].copy()

        center = expr.jexpr.x_plus_y.circumshapes[index].get_center()

        subexpr.generate_target()
        subexpr.target.move_to(
            center + v_dist * UP + h_buff_scale * h_buff * LEFT
        ).scale(scale)

        self.play(MoveToTarget(subexpr))

        return subexpr

    def animate_explanation(self):
        expr = self.mobs.expr

        self.play(
            FadeIn(expr.jexpr.verb.set_color(DARKER_GRAY)[1].set_color(LIGHT_GRAY)),
            run_time=2,
        )

        self.play(Create(expr.jexpr.equals.set_opacity(1)))
        self.wait(SCENE_CONFIG.wait_time)

        self.play(
            ReplacementTransform(
                expr.copy().grouped_expr,
                expr.set_opacity(0.25, subexpr=["x", "y"]).grouped_expr,
            )
        )

        set_focus = lambda t, i: expr.jexpr[t].set_focus([i])
        for i in range(expr.jexpr.x.nitems):
            self.play(FadeIn(vgroup(set_focus("x", i), set_focus("y", i))))

            terms = []
            for s, t in enumerate(["x", "verb", "y"]):
                terms.append(self.move_subexpr_to_target(t, i, h_buff_scale=1.0 - s))

            self.play(FadeIn(expr.jexpr.x_plus_y.set_opacity(1, indices=[i]).matrix))
            self.wait(SCENE_CONFIG.wait_time)

            self.play(VGroup(*terms).animate.set_opacity(0.25))
            expr.jexpr.x_plus_y.set_opacity(0.25, indices=range(i + 1))

        self.play(FadeIn(expr.set_opacity(1).grouped_expr))

        self.wait(SCENE_CONFIG.wait_time + 3)

    @beartype
    def replicate_items(self, term: str = "x", dir: str = "left"):
        item = self.mobs.expr.jexpr[term]
        if dir == "left" or dir == "bottom":
            start, stop, step = (item.nitems - 1), 0, -1
        else:
            start, stop, step = 0, (item.nitems - 1), 1

        for i in range(start, stop, step):
            item_copy = item.copy()
            entry = VGroup(item_copy.circumshapes[i], item_copy.matrix_items[i])
            entry.generate_target()
            entry.target.set_opacity(1)
            entry.target.move_to(item.circumshapes[i + step].get_center())
            self.play(MoveToTarget(entry))
            item.set_opacity(1, indices=[i + step])
            self.remove(entry)
            self.wait(SCENE_CONFIG.wait_time)


class SimplerProblemExplanationScene(Plus00Rank1XRank1YScene):
    def show_explanation(self):
        prev_scene = SimplerProblemScene()
        prev_scene.setup()

        expr = self.mobs.expr
        grouper = expr.grouper
        center = expr.jexpr.verb.get_center()

        expr.set_grouper(
            lambda j: vgroup(j.x, j.verb, j.y).arrange(RIGHT, buff=0.4)
        )  # subset expr

        self.play(
            FadeTransform(prev_scene.mobs.expr.grouped_expr, expr.grouped_expr),
            run_time=2,
        )

        self.color_subexpr(lag=0.25)

        self.show_mobj(
            attr="descr",
            mobj=Text(
                "Apply verb to atoms of x and y",
                t2w={"atoms": BOLD},
                t2c={
                    "x": self.SUBEXPR_COLORS["x"],
                    " y": self.SUBEXPR_COLORS["y"],
                },
            )
            .scale(0.9)
            .to_edge(DOWN),
            creation_animation=Write,
        )
        self.wait(SCENE_CONFIG.wait_time)

        self.play(Uncreate(self.mobs.descr[-1]))
        self.play(expr.grouped_expr.animate.move_to(center))
        self.wait(SCENE_CONFIG.wait_time)

        expr.set_grouper(grouper)  # restore grouper
        expr.set_color(self.SUBEXPR_COLORS.result, subexpr=["x_plus_y"])

    def construct(self):
        self.add_title()
        self.setup_expr()
        self.show_explanation()
        self.animate_explanation()


class OperandAgreementAcrossDyadScene(Plus00Rank1XRank1YScene):
    def show_description(self):
        self.show_mobj(
            attr="descr",
            mobj=Text("For differing ranks, entire cells of the operand"),
            creation_animation=Write,
        )
        self.show_mobj(
            attr="descr",
            mobj=Text(
                "with the shorter frame are replicated", t2s={"shorter": ITALIC}
            ).move_to(DOWN),
            creation_animation=Write,
        )
        self.wait(SCENE_CONFIG.wait_time + 3)

        self.play(*[Uncreate(mob) for mob in self.mobs.descr])

    def show_explanation(self):
        expr = self.mobs.expr
        self.show_mobj(
            attr="descr",
            mobj=Text("Consider the simple expression").next_to(
                self.mobs["title"], 3 * DOWN
            ),
            creation_animation=Write,
        )

        expr = self.mobs.expr
        grouper = expr.grouper
        center = expr.jexpr.verb.get_center()

        expr.set_grouper(
            lambda j: vgroup(j.x, j.verb, j.y)
            .arrange(RIGHT, buff=0.4)
            .next_to(self.mobs.descr[-1], 2 * DOWN)
        )  # subset expr

        self.show_mobj(
            attr="show_expr",
            mobj=expr.copy()
            .transform(subexpr=["verb"], func=lambda x: x[1])
            .set_opacity(0, subexpr=["x"], indices=[0, 1])
            .grouped_expr,
            creation_animation=Write,
        )

        self.show_mobj(
            attr="descr",
            mobj=Text("This is expanded as").next_to(self.mobs["title"], 3 * DOWN),
            replace_mobj=self.mobs.descr[-1],
            replacement_animation=ReplacementTransform,
        )

        self.play(ReplacementTransform(self.mobs.show_expr[-1], expr.grouped_expr))
        self.wait(SCENE_CONFIG.wait_time)

        self.color_subexpr(xargs={"indices": [2]})

        self.wait(SCENE_CONFIG.wait_time)

        self.show_mobj(
            attr="descr",
            mobj=Text(
                "Since x is the shorter than y, it is replicated",
                t2f={"x": SCENE_CONFIG.font_mono, "y": SCENE_CONFIG.font_mono},
                t2c={
                    "x": self.SUBEXPR_COLORS["x"],
                    "y": self.SUBEXPR_COLORS["y"],
                },
            ).next_to(self.mobs["title"], 3 * DOWN),
            replace_mobj=self.mobs.descr[-1],
            replacement_animation=ReplacementTransform,
        )

        self.replicate_items()
        self.wait(SCENE_CONFIG.wait_time)

        self.play(Uncreate(self.mobs.descr[-1]))
        self.play(expr.grouped_expr.animate.move_to(center))
        self.wait(SCENE_CONFIG.wait_time)

        expr.set_grouper(grouper)  # restore grouper
        expr.set_color(self.SUBEXPR_COLORS.result, subexpr=["x_plus_y"])

    def play_outro(self):
        self.play(FadeOut(*self.mobjects))
        self.wait(SCENE_CONFIG.wait_time)

        txt = Text(
            (
                '"0 0 is the fundamental case since all'
                + "\ndyadic forms ultimately get reduced to"
                + "\natom-atom operations"
            ),
            color=GOLD,
            line_spacing=1.25,
            t2f={'"0 0': SCENE_CONFIG.font_mono},
            t2s={"fundamental case": ITALIC},
            t2c={"[0:4]": BLUE},
            t2w={"all": BOLD},
        ).scale(1.1)
        txt[64:73].set_color(BLUE_D)

        self.play(FadeIn(txt))
        self.play(Create(Underline(mobject=txt[8:23], buff=0.2), run_time=2))
        self.play(
            Circumscribe(
                txt, fade_out=False, color=GOLD, time_width=1.0, buff=0.4, run_time=3
            )
        )
        self.play(FadeIn((SurroundingRectangle(txt, buff=0.4, color=GOLD))))
        self.wait(SCENE_CONFIG.wait_time + 3)

    def construct(self):
        self.mobs["title"] = make_title(markup_string="Operand Agreement across Dyads")
        self.add_title(title=self.mobs["title"])

        self.setup_expr()
        self.mobs.expr.jexpr.y.align()
        self.mobs.expr.set_opacity(0, subexpr=["x"], indices=[0, 1])

        self.show_description()
        self.show_explanation()
        self.animate_explanation()
        self.play_outro()


class Plus10Rank1XRank1YScene(Plus00Rank1XRank1YScene):
    def setup_expr(self):
        self.mobs.expr = (
            self.get_expr(
                verb="plus_rank10",
                equals="downarrow",
                terms_kwargs={"x": {"circumitems": "rows"}},
            )
            .set_order(["x", "verb", "y", "equals", "x_plus_y"])
            .reorder()
            .set_scale(0.9, subexpr=["verb"])
            .set_opacity(circumshapes=0, subexpr=["x", "y"])
            .set_opacity(0, subexpr=["equals", "x_plus_y"])
        )

    def setup_result_exprs(self):
        expr = self.mobs.expr

        expr.set_grouper(
            lambda j: vgroup(
                vgroup(j.x, j.verb, j.y).arrange(RIGHT, buff=0.4), j.equals.scale(0.9)
            )
            .arrange(DOWN, buff=0.1)
            .next_to(SCENE_CONFIG.title, DOWN)
        )

        self.mobs.expr00 = expr00 = JExpressionManager(
            Box(
                **get_terms(
                    topic="PlusRank",
                    scene="Quiz1Scene",
                    mobmatrix_args={"v": {"v_buff": 1.10}},
                    entries_filter=lambda x: x in ["x", "v", "y"],
                )[1],
                **{"equals": get_equals(entry="rightarrow")},
            )
        )

        expr00.set_scale(0.75, subexpr=["x", "y"])

        expr00.jexpr.x.set_color(self.SUBEXPR_COLORS.x)
        expr00.jexpr.y.set_color(self.SUBEXPR_COLORS.y)
        expr00.jexpr.v.set_color(DEFAULTS.verb.color).set_color(
            circumshapes=BLACK
        ).set_scale(0.75)

        expr00.jexpr.x.align().matrix.next_to(expr.jexpr.x.matrix, 5 * DOWN).align_to(
            expr.jexpr.x.matrix, LEFT
        )

        expr00.jexpr.y.align().matrix.next_to(expr00.jexpr.x.matrix, 11 * RIGHT)

        verb_center = (
            expr00.jexpr.x.matrix.get_center() + expr00.jexpr.y.matrix.get_center()
        ) / 2
        expr00.jexpr.v.matrix.move_to(verb_center)

        expr00.jexpr.equals.scale(0.75).next_to(expr00.jexpr.y.matrix, 1.5 * RIGHT)

        (
            expr.jexpr.x_plus_y.matrix.scale(0.75)
            .next_to(expr00.jexpr.equals, RIGHT)
            .align_to(expr.jexpr.y.matrix, RIGHT)
        )

        expr00.set_opacity(0, subexpr=["x", "v", "y", "equals"])

        self.add(expr.jexpr.x_plus_y.matrix)

        [self.add(expr00.jexpr[j].matrix) for j in ["x", "v", "y"]]
        self.add(expr00.jexpr.equals)

    @beartype
    def move_subexpr_to_target(
        self,
        y_indices: Iterable[int],
        x00_indices: Iterable[int],
        y00_indices: Iterable[int],
        x_indices: Iterable[int] = [0],
    ) -> VGroup:
        expr = self.mobs.expr.jexpr
        expr00 = self.mobs.expr00.jexpr

        subexpr = vgroup(
            *[expr.x.matrix_items[x] for x in x_indices],
            expr.verb[1],
            *[expr.y.matrix_items[y] for y in y_indices],
        ).copy()

        subexpr.generate_target()

        verb_center = (
            expr00.x.matrix_items[max(x00_indices)].get_center()
            + expr00.y.matrix_items[min(y00_indices)].get_center()
        ) / 2

        subexpr00 = vgroup(
            *[expr00.x.matrix.get_entries()[x] for x in x00_indices],
            expr.verb[1].copy().move_to(verb_center),
            *[expr00.y.matrix_items[y] for y in y00_indices],
        ).copy()

        subexpr.target.become(subexpr00.set_opacity(0.75))

        self.play(MoveToTarget(subexpr), run_time=2)
        self.wait(SCENE_CONFIG.wait_time)

        return subexpr

    def animate_explanation(self):

        expr = self.mobs.expr
        expr00 = self.mobs.expr00

        self.play(
            FadeIn(expr.jexpr.verb.set_color(DARKER_GRAY)[1].set_color(LIGHT_GRAY)),
            run_time=2,
        )

        for i in range(0, 3):
            row_item_indices = [3 * i + x for x in range(0, 3)]
            subexpr = self.move_subexpr_to_target(
                y_indices=[i], x00_indices=row_item_indices, y00_indices=[3 * i]
            )

            self.play(
                FadeOut(subexpr[3], run_time=2),
                FadeIn(expr00.jexpr.v.matrix[0][i].set_opacity(1), run_time=3),
            )

            self.play(
                FadeIn(
                    vgroup(
                        expr00.jexpr.x.set_opacity(1, indices=row_item_indices),
                        expr00.jexpr.y.set_opacity(1, indices=row_item_indices),
                    )
                )
            )

            if i == 0:
                self.play(Write(expr00.jexpr.equals.set_opacity(1)))

            self.wait(SCENE_CONFIG.wait_time)

            self.play(
                FadeIn(
                    expr.jexpr.x_plus_y.set_opacity(1, indices=row_item_indices).matrix
                )
            )
            self.wait(SCENE_CONFIG.wait_time)

            self.remove(*[s for s in subexpr])

            def fade_to_opacity(obj, indices, opacity=0.25):
                return obj.animate(
                    items=lambda j: j.animate.set_opacity(opacity),
                    circumshapes=lambda j: j.animate.set_opacity(opacity).set_fill(
                        opacity=0
                    ),
                    indices=indices,
                )

            self.play(
                *concat(
                    [
                        fade_to_opacity(expr00.jexpr.x, row_item_indices),
                        fade_to_opacity(expr00.jexpr.v, [i]),
                        fade_to_opacity(expr00.jexpr.y, row_item_indices),
                        fade_to_opacity(expr.jexpr.x_plus_y, row_item_indices),
                    ]
                )
            )

            self.wait(SCENE_CONFIG.wait_time)

        self.play(
            *fade_to_opacity(
                expr.jexpr.x_plus_y,
                indices=None,
                opacity=1,
            )
        )
        self.wait(SCENE_CONFIG.wait_time)


class QuizScene(Scene):
    @beartype
    def add_questioner_image(self, image: Union[str, Path]):
        self.mobs.questioner = (
            ImageMobject(image).scale(0.35).to_edge(LEFT).shift([-1, -0.5, 0])
        )

        self.add(self.mobs.questioner)


class Quiz1Scene(Plus10Rank1XRank1YScene, QuizScene):
    def question(self):

        self.mobs.expr.set_grouper(
            lambda j: vgroup(j.x, j.verb, j.y).arrange(RIGHT, buff=0.4)
        )  # subset expr

        self.play(
            FadeIn(
                self.mobs.expr.set_color(BLUE, subexpr=["verb"])
                .grouped_expr.next_to(self.mobs.title, DOWN)
                .next_to(self.mobs.questioner, RIGHT)
                .shift(2.25 * LEFT)
                .scale(0.85)
            )
        )

        self.play(FadeToColor(self.mobs.expr.jexpr.verb[3], RED))

    def transition_to_answer(self):

        expr = self.mobs.expr

        self.play(FadeOut(self.mobs.questioner))

        self.play(expr.grouped_expr.animate.move_to(ORIGIN))
        self.play(ScaleInPlace(self.mobs.expr.grouped_expr, 1.2))

        self.color_subexpr()

        self.play(expr.grouped_expr.animate.next_to(self.mobs.title, DOWN))
        self.wait(SCENE_CONFIG.wait_time)

    def construct(self):
        self.mobs.title = make_title(markup_string="Question: What is the result?")
        self.add_title(title=self.mobs.title)

        self.add_questioner_image(Path("images", "question1.png"))

        self.setup_expr()
        self.question()
        self.transition_to_answer()

        self.setup_result_exprs()
        self.animate_explanation()

        self.wait(SCENE_CONFIG.wait_time)

        self.play(
            FadeTransform(
                self.mobs.title, make_title(markup_string="Answer: 3×3 Matrix!")
            ),
            run_time=2,
        )

        self.wait(SCENE_CONFIG.wait_time)


class Plus00Rank1XRank2YScene(Plus10Rank1XRank1YScene):
    def setup_original_expr(self, index=0, terms_args={}):
        self.mobs.original_expr = (
            self.get_expr(
                verb="plus_rank00", terms_index=index, terms_kwargs=terms_args
            )
            .set_order(["x", "verb", "y"])
            .reorder()
            .set_scale(0.8, subexpr=["verb"])
            .set_opacity(circumshapes=0, subexpr=["x", "y"])
        )

    def setup_expr(
        self,
        index=1,
        terms_args={"x": {"circumitems": "entries"}, "y": {"circumitems": "entries"}},
        order=["x", "verb", "y", "equals", "x_plus_y"],
    ):
        self.mobs.expr = (
            self.get_expr(
                verb="plus_rank00",
                equals="rightarrow",
                terms_kwargs=terms_args,
                terms_index=index,
            )
            .set_order(order)
            .reorder()
            .set_scale(0.8, subexpr=["verb"])
            .set_opacity(circumshapes=0, subexpr=["x", "y"])
        )


class OriginalProblemScene(Plus00Rank1XRank2YScene):
    def group_xvy(self, next_to_mobj):
        return (
            lambda j: vgroup(j.x, j.verb, j.y)
            .arrange(RIGHT, buff=0.4)
            .next_to(next_to_mobj, 3 * DOWN)
        )

    def show_explanation(self):

        self.show_mobj(
            attr="descr",
            mobj=Text("Now back to that last case...")
            .scale(0.9)
            .next_to(self.mobs.title, 2 * DOWN),
            creation_animation=Write,
        )

        self.wait(SCENE_CONFIG.wait_time)

        expr = self.mobs.expr
        original_expr = self.mobs.original_expr

        expr.set_grouper(self.group_xvy(self.mobs.descr[-1]))
        original_expr.set_grouper(self.group_xvy(self.mobs.descr[-1]))

        expr.grouped_expr.align_to(original_expr.grouped_expr, LEFT)

        self.show_mobj(
            attr="show_original_expr",
            mobj=original_expr.copy().update({"verb": get_verb("plus")}).grouped_expr,
            creation_animation=FadeIn,
        )

        self.show_mobj(
            attr="descr",
            mobj=Text("This is expanded as, ")
            .scale(0.9)
            .next_to(self.mobs.title, 2 * DOWN),
            replace_mobj=self.mobs.descr[-1],
            replacement_animation=ReplacementTransform,
        )

        self.show_mobj(
            attr="show_original_expr",
            mobj=original_expr.grouped_expr,
            replace_mobj=self.mobs.show_original_expr[-1],
            creation_animation=ReplacementTransform,
        )

        self.show_mobj(
            attr="descr",
            mobj=Text("J is columnar, so this translates to,", t2c={"J": RED})
            .scale(0.9)
            .next_to(self.mobs.title, 2 * DOWN),
            replace_mobj=self.mobs.descr[-1],
            replacement_animation=ReplacementTransform,
        )

        for item, target in zip(
            reversed(original_expr.jexpr.x.matrix_items),
            reversed(expr.jexpr.x.matrix.get_columns()[2]),
        ):
            item.generate_target()
            item.target = target
            self.play(MoveToTarget(item))

        self.play(
            FadeTransform(
                original_expr.grouped_expr,
                expr.set_opacity(0, subexpr=["x"], indices=[0, 1]).grouped_expr,
            ),
            FadeOut(original_expr.grouped_expr),
        )

    def atomize_expr(self):
        col_expr = self.mobs.expr

        self.setup_expr(
            terms_args={
                "x": {"circumitems": "entries"},
                "y": {"circumitems": "entries"},
            }
        )
        expr = self.mobs.expr
        expr.set_grouper(self.group_xvy(self.mobs.descr[-1]))

        expr.jexpr.x.set_color(self.SUBEXPR_COLORS.x)
        expr.jexpr.y.set_color(self.SUBEXPR_COLORS.y)
        expr.jexpr.verb.set_color(DARK_GRAY)
        expr.jexpr.verb[1].set_color(LIGHT_GRAY)

        self.play(
            FadeTransform(col_expr.grouped_expr, expr.set_opacity(1).grouped_expr)
        )

    def show_result(self):
        expr = self.mobs.expr
        gexpr = expr.copy().grouped_expr

        self.remove(expr.grouped_expr)
        self.play(gexpr.animate.scale(0.70))

        expr.set_grouper(
            lambda j: vgroup(j.x, j.verb, j.y, j.equals, j.x_plus_y)
            .scale(0.70)
            .arrange(RIGHT, buff=0.4)
            .next_to(self.mobs.descr[-1], 5 * DOWN)
        )

        expr.set_opacity(0, subexpr=["equals", "x_plus_y"])
        self.play(gexpr.animate.align_to(expr.grouped_expr, DL))

        self.play(FadeIn(expr.grouped_expr), FadeOut(gexpr))

        self.play(expr.jexpr.equals.animate.set_opacity(1))

        set_focus = lambda t, i: expr.jexpr[t].set_focus([i])
        for i in range(expr.jexpr.x_plus_y.nitems):
            self.play(FadeIn(vgroup(set_focus("x", i), set_focus("y", i))))
            self.play(FadeIn(expr.jexpr.x_plus_y.set_opacity(1, indices=[i]).matrix))
            self.wait(0.25)

            expr.jexpr.x_plus_y.set_opacity(0.1, indices=[i])

        self.play(FadeIn(expr.set_opacity(1).grouped_expr), run_time=2)

    def construct(self):
        self.mobs.title = make_title(markup_string="Rank in Two Dimensions")
        self.add_title(title=self.mobs.title)

        self.setup_expr(
            terms_args={
                "x": {"circumitems": "columns"},
                "y": {"circumitems": "columns"},
            },
        )
        self.setup_original_expr()

        self.show_explanation()

        self.color_subexpr(xargs={"indices": [2]})
        self.replicate_items()

        self.show_mobj(
            attr="descr",
            mobj=Text("This reduces to atom-atom operations, ")
            .scale(0.9)
            .next_to(self.mobs.title, 2 * DOWN),
            replace_mobj=self.mobs.descr[-1],
            replacement_animation=ReplacementTransform,
        )

        self.atomize_expr()
        self.show_result()

        self.wait(SCENE_CONFIG.wait_time + 4)


class Quiz2Scene(Plus00Rank1XRank2YScene, QuizScene):
    def group_xvy(self):
        return (
            lambda j: vgroup(j.x, j.verb, j.y)
            .arrange(buff=0.4)
            .next_to(self.mobs.title, 3 * DOWN)
            .scale(0.9)
        )

    def question(self):

        original_expr = self.mobs.original_expr

        self.show_mobj(
            attr="show_original_expr",
            mobj=(
                original_expr.copy()
                .update({"verb": get_verb("plus")})
                .set_color(BLUE, subexpr=["verb"])
                .grouped_expr.next_to(self.mobs.title, DOWN)
                .next_to(self.mobs.questioner, RIGHT)
                .shift(1.25 * LEFT)
            ),
            creation_animation=FadeIn,
        )

    def transition_to_answer(self):

        original_expr = self.mobs.original_expr

        self.play(FadeOut(self.mobs.questioner))

        self.show_mobj(
            attr="show_original_expr",
            mobj=self.mobs.show_original_expr[-1]
            .copy()
            .align_to(self.mobs.expr.grouped_expr, DL)
            .scale(0.9),
            replace_mobj=self.mobs.show_original_expr[-1],
            creation_animation=ReplacementTransform,
        )

        self.show_mobj(
            attr="show_original_expr",
            mobj=original_expr.set_grouper(
                lambda j: vgroup(j.x, j.verb, j.y)
                .arrange(buff=0.4)
                .align_to(self.mobs.expr.grouped_expr, DOWN)
                .scale(0.9)
            ).grouped_expr,
            replace_mobj=self.mobs.show_original_expr[-1],
            creation_animation=ReplacementTransform,
        )

    def columnize_expr(self):
        expr = self.mobs.expr
        original_expr = self.mobs.original_expr

        expr.jexpr.x.matrix.align_to(expr.jexpr.y.matrix, UP)
        expr.jexpr.y.align("columns")

        self.play(
            FadeTransform(
                original_expr.grouped_expr,
                expr.set_opacity(0, subexpr=["x"], indices=[0, 1]).grouped_expr,
            )
        )

    def atomize_expr(self):
        col_expr = self.mobs.expr

        self.setup_expr(
            index=2,
            terms_args={
                "x": {"circumitems": "entries"},
                "y": {"circumitems": "entries"},
            },
            order=["x", "verb", "y"],
        )
        expr = self.mobs.expr

        expr.jexpr.x.set_color(self.SUBEXPR_COLORS.x)
        expr.jexpr.y.set_color(self.SUBEXPR_COLORS.y)
        expr.jexpr.verb.set_color(DARK_GRAY)
        expr.jexpr.verb[1].set_color(LIGHT_GRAY)

        self.play(
            FadeTransform(
                col_expr.grouped_expr,
                expr.set_grouper(self.group_xvy())
                .set_opacity(1)
                .set_opacity(0, subexpr=["x"], indices=[9, 10, 11, 12])
                .grouped_expr,
            )
        )

    def show_answer(self):
        expr = self.mobs.expr

        expr.jexpr.y.align("entries")

        self.play(
            FadeIn(
                expr.jexpr.x.set_opacity(1, indices=[9, 10, 11])
                .set_color(RED_D, indices=[9, 10, 11])
                .matrix_items[9:12]
            ),
            run_time=5,
        )
        self.play(ScaleInPlace(expr.grouped_expr, 0.9))
        self.play(expr.grouped_expr.animate.next_to(self.mobs.title, 3 * DOWN))

        self.show_mobj(
            attr="descr",
            mobj=Text(
                "Since the last row of x is missing, the operation is undefined",
                t2w={"undefined": BOLD},
                t2f={"x": DEFAULTS.fonts.mono},
                t2c={"x": self.SUBEXPR_COLORS.x, "undefined": RED},
            )
            .to_edge(DOWN)
            .scale(0.775),
            creation_animation=Write,
        )

        self.play(*expr.jexpr.x.animate(Wiggle, indices=[9, 10, 11]))

        self.wait(SCENE_CONFIG.wait_time)

    def construct(self):
        self.mobs.title = make_title(markup_string="Question: What is the result?")

        self.show_mobj(attr="heading", mobj=self.mobs.title, creation_animation=Write)

        self.add_questioner_image(Path("images", "question1.png"))

        self.setup_original_expr(
            terms_args={
                "x": {"element_alignment_corner": UR},
                "y": {"element_alignment_corner": UR, "h_buff": 1.75},
            }
        )

        self.setup_expr(
            terms_args={
                "x": {"circumitems": "columns", "element_alignment_corner": UR},
                "y": {
                    "circumitems": "columns",
                    "element_alignment_corner": UR,
                    "h_buff": 1.75,
                    "circumshape": RoundedRectangle(
                        **DEFAULTS.box.options, height=1.35 * 4, width=1.6
                    ),
                },
            },
            order=["x", "verb", "y"],
        )

        self.mobs.expr.set_grouper(self.group_xvy())

        self.question()

        # self.mobs.show_original_expr = []
        # self.mobs.show_original_expr.append(self.mobs.original_expr.grouped_expr)
        self.transition_to_answer()

        self.columnize_expr()
        self.color_subexpr(xargs={"indices": [2]})

        self.play(FadeIn(self.mobs.expr.jexpr.x.set_opacity(1, indices=[0, 1]).matrix))

        self.atomize_expr()
        self.show_answer()

        self.show_mobj(
            attr="heading",
            mobj=make_title(markup_string="Answer: <b>length error</b>!"),
            replace_mobj=self.mobs.heading[-1],
            replacement_animation=ReplacementTransform,
        )

        self.wait(SCENE_CONFIG.wait_time + 2)


# TODO
# - Quiz3: "0 1; x = 1x4, y = 4x3 # (i.4) (+"0 1) (i. 4 3)
# - Quiz4: "1 1; x = 1x4, y = 4x3 # (i.3) (+"1 1) (i. 4 3)
