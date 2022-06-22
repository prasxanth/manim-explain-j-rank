from manim import *
from jxprmat import CirumscribedJMatrix
from jxprutils import SceneConfig, make_title, vgroup
from jxprlib import get_terms, get_verb, get_equals
from functools import partial
from box import Box
import toml
from beartype import beartype

DEFAULTS = Box(toml.load("defaults.toml"), box_dots=True, frozen_box=True)


SCENE_CONFIG = SceneConfig(
    title=make_title(
        markup_string='The <span foreground="#58C4DD" size="x-large"> + </span> Dyad'
    )
)


@beartype
def make_toc(font_mono: str = SCENE_CONFIG.font_sans):

    entries = [
        list(map(lambda x: Text(x, font=font_mono), y))
        for y in [["0", "n"], ["n", "n"], ["n", "m"]]
    ]

    labels_kwargs = {"color": GREEN, "font": font_mono, "weight": BOLD}

    toc = MobjectTable(
        entries,
        col_labels=[
            Text("Rank x", **labels_kwargs).scale(1.25),
            Text("Rank y", **labels_kwargs).scale(1.15),
        ],
    )

    toc.remove(*toc.get_vertical_lines())
    hl = toc.get_horizontal_lines()
    hl.set_color(DARK_GREY)

    return toc


@beartype
def focus_table_row(tbl: MobjectTable, row: int):
    rows = tbl.get_rows()
    # Assumes header = row 0
    for i in range(len(rows)):
        if i > 0 and i != row:  # Skip header row and target row
            rows[i].set_opacity(0.10)
        else:
            rows[i].set_opacity(1.00)

    return tbl


@beartype
def make_plusexpr(
    x: CirumscribedJMatrix, y: CirumscribedJMatrix, x_plus_y: CirumscribedJMatrix
) -> VGroup:
    colors = DEFAULTS.matrix.color_palette.two_color
    return vgroup(
        x.set_color(colors.xy).set_opacity(circumshapes=0),
        get_verb("plus"),
        y.set_color(colors.xy).set_opacity(circumshapes=0),
        get_equals("rightarrow"),
        x_plus_y.set_color(colors.result).set_opacity(circumshapes=0),
    ).arrange(RIGHT, buff=0.4)


Text = partial(Text, font=SCENE_CONFIG.font_sans)


class IntroductionScene(Scene):
    mobs = Box(box_dots=True, default_box=True, default_box_attr=[])

    def setup(self):
        self.mobs.intro = (
            Text(
                """
            In order of increasing complexity, consider each case of
            addition across varying ranks of x and y
            """,
                line_spacing=1.00,
                t2c={" x": RED, " y": RED},
            )
            .scale(0.825)
            .next_to(SCENE_CONFIG.title, DOWN)
        )

        self.mobs.footnote = (
            Text(
                (
                    "NOTE : Since + is commutative, x and y can be "
                    + "interchanged in the table above"
                ),
                color=GREY,
                t2w={"NOTE": "BOLD"},
            )
            .scale(0.55)
            .to_edge(DOWN)
            .shift([0, -0.40, 0])
        )

        self.mobs.toc = (
            make_toc().scale(0.90).next_to(self.mobs.intro, DOWN).shift([0, -0.10, 0])
        )

    def construct(self):
        self.add(SCENE_CONFIG.title)
        self.add(self.mobs.intro)
        self.add(self.mobs.footnote)
        self.play(FadeIn(self.mobs.toc))
        self.wait(SCENE_CONFIG.wait_time)


class RankXRankYScene(Scene):

    mobs = Box(box_dots=True, default_box=True, default_box_attr=[])

    def init_mobs(self, previous_scene_class, current_scene_obj):
        self.prev_scene = previous_scene_class()
        self.prev_scene.setup()
        self.mobs.toc = self.prev_scene.mobs.toc
        self.get_exprs(scene=current_scene_obj.__class__.__name__)

    def get_exprs(self, scene):
        termargs = Box(
            {
                k: {
                    "element_to_mobject_config": {"font_size": 60},
                    "v_buff": 1.3,
                    "h_buff": 1.3,
                }
                for k in ["x", "y", "x_plus_y"]
            }
        )

        terms = get_terms(topic="PlusDyad", scene=scene, mobmatrix_args=termargs)

        self.mobs.expr = [make_plusexpr(**t) for t in terms]

    def show_mobj(
        self,
        mobj,
        replace_mobj=None,
        attr: str = None,
        creation_animation=FadeIn,
        replacement_animation=FadeTransform,
    ):
        if attr is not None:
            self.mobs[attr].append(mobj)

        if replace_mobj is None:
            self.play(creation_animation(mobj))
            self.wait(SCENE_CONFIG.wait_time)
        else:
            self.play(replacement_animation(replace_mobj, mobj))
            self.wait(SCENE_CONFIG.wait_time)

    def update_toc(self, target_row: int = 1):

        intro = IntroductionScene.mobs.intro
        footnote = IntroductionScene.mobs.footnote

        if target_row == 1:
            self.mobs.toc.generate_target()
            focus_table_row(self.mobs.toc.target, row=target_row)

            self.mobs.toc.target.scale(1.25).next_to(SCENE_CONFIG.title, 1.50 * DOWN)

            self.play(FadeOut(intro, footnote))
            self.play(MoveToTarget(self.mobs.toc), run_time=2)
            self.wait(SCENE_CONFIG.wait_time)
        else:
            focus_table_row(self.mobs.toc, row=target_row)
            self.mobs.toc.scale(1.25).next_to(SCENE_CONFIG.title, 1.50 * DOWN)
            self.remove(intro, footnote)

    def show_next_topic(self, focus_row: int, mobj: VGroup = None, descr: dict = None):
        self.update_toc(target_row=focus_row)
        if focus_row > 1:
            self.show_mobj(attr="descr", mobj=self.mobs.toc, replace_mobj=mobj)

        self.show_mobj(
            attr="descr",
            mobj=Text(**descr).scale(0.85).next_to(self.mobs.toc, 2.50 * DOWN),
            creation_animation=Write,
        )
        self.remove(self.mobs.descr[-1])

    def walk_expressions(self):

        self.show_mobj(mobj=self.mobs.expr[0], replace_mobj=self.mobs.descr[-1])

        if (nexprs := len(self.mobs.expr)) > 1:
            for i in range(nexprs - 1):
                self.show_mobj(
                    attr="expr",
                    mobj=self.mobs.expr[i + 1],
                    replace_mobj=self.mobs.expr[i],
                )


class Rank0RankNScene(RankXRankYScene):
    def setup(self):
        super().init_mobs(IntroductionScene, self)
        self.mobs.expr[3].shift([0, -0.60, 0])

    def construct(self):
        self.add(SCENE_CONFIG.title)
        self.show_next_topic(
            focus_row=1, descr={"text": "Let's consider the first case..."}
        )
        self.show_mobj(
            attr="descr",
            mobj=Text("Atoms (Rank 0) can be added " + "to arrays of any rank").scale(
                0.9
            ),
            replace_mobj=self.mobs.toc,
        )

        self.walk_expressions()


class RankNRankNScene(RankXRankYScene):
    def setup(self):
        super().init_mobs(Rank0RankNScene, self)
        [self.mobs.expr[i].scale(0.95) for i in range(len(self.mobs.expr))]

    def construct(self):
        self.add(SCENE_CONFIG.title)
        self.show_next_topic(
            focus_row=2,
            mobj=self.prev_scene.mobs.expr[-1].shift([0, -0.60, 0]),
            descr={"text": "Now consider the second case..."},
        )
        self.show_mobj(
            attr="descr",
            mobj=Text("Arrays of the same " + "rank can be added together").scale(0.9),
            replace_mobj=self.mobs.toc,
        )

        self.walk_expressions()


class RankNRankMScene(RankXRankYScene):
    def setup(self):
        super().init_mobs(RankNRankNScene, self)
        self.mobs.expr[0].scale(0.95)

    def construct(self):
        self.add(SCENE_CONFIG.title)
        self.show_next_topic(
            focus_row=3,
            mobj=self.prev_scene.mobs.expr[-1],
            descr={"text": "The last case is the most general...."},
        )
        self.show_mobj(
            attr="descr",
            mobj=Text(
                "Arrays of differing ranks can be added if they agree",
                t2s={"agree": ITALIC},
            ).scale(0.9),
            replace_mobj=self.mobs.toc,
        )

        self.walk_expressions()
