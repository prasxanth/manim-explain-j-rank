from typing import Union, Callable
import toml
from box import Box
from jxprutils import make_circummat, make_verb, make_equals
from beartype import beartype

LIB = Box(toml.load("lib.toml"), frozen_box=True)

@beartype
def get_terms(
    topic: str,
    scene: str,
    lib: Union[dict, Box] = LIB,
    mobmatrix_args: Union[dict, Box] = {},
    entries_filter: Callable = lambda x: x in ["x", "y", "x_plus_y"],
):
    lib = Box(lib)
    
    mobmatrix_args = Box(mobmatrix_args, default_box=True)
    terms = []
    for t in lib.matrices[topic][scene]:
        terms.append(
            {
                k: make_circummat(v, **Box(mobmatrix_args[k], default_box=True))
                for k, v in t.items()
                if entries_filter(k)
            }
        )

    return terms

@beartype
def get_verb(entry: str, lib: Union[dict, Box] = LIB, **kwargs):
    lib = Box(lib)  # Since Box(a) == Box(Box(a))
    return make_verb(lib.verb[entry], **kwargs)

@beartype
def get_equals(entry: str, lib: Union[dict, Box] = LIB, **kwargs):
    lib = Box(lib) # Since Box(a) == Box(Box(a))
    return make_equals(lib.equals[entry], **kwargs)
