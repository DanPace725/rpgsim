"""
Tiny RP/GCO-style tick to illustrate how a game rule engine could look.

Run: python examples/minimal_rp_sim.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# Primitives for clarity
ONTOLOGY, GEOMETRY, CONSTRAINT, DYNAMICS, EPISTEMIC, META = (
    "ONTOLOGY",
    "GEOMETRY",
    "CONSTRAINT",
    "DYNAMICS",
    "EPISTEMIC",
    "META",
)


@dataclass
class Entity:
    id: str
    kind: str
    state: Dict[str, float] = field(default_factory=dict)


@dataclass
class Relation:
    primitive: str
    source: str
    target: str | None
    payload: Dict[str, float]


@dataclass
class World:
    entities: Dict[str, Entity]
    relations: List[Relation]


def apply_geometry(world: World) -> Dict[str, Dict[str, float]]:
    """Compute proximity flags."""
    geom_state: Dict[str, Dict[str, float]] = {}
    for rel in world.relations:
        if rel.primitive != GEOMETRY:
            continue
        src = world.entities[rel.source]
        tgt = world.entities[rel.target]
        dx = src.state["x"] - tgt.state["x"]
        dy = src.state["y"] - tgt.state["y"]
        dist2 = dx * dx + dy * dy
        if dist2 <= rel.payload["radius"] ** 2:
            geom_state.setdefault(src.id, {})["near"] = tgt.id
    return geom_state


def apply_constraint(world: World) -> None:
    """Clamp positions to bounds."""
    for rel in world.relations:
        if rel.primitive != CONSTRAINT:
            continue
        ent = world.entities[rel.source]
        xmin, xmax = rel.payload["xmin"], rel.payload["xmax"]
        ent.state["x"] = max(xmin, min(xmax, ent.state["x"]))


def apply_epistemic(world: World, geom_state: Dict[str, Dict[str, float]]) -> Dict[str, str]:
    """Agents know who is near."""
    knowledge: Dict[str, str] = {}
    for rel in world.relations:
        if rel.primitive != EPISTEMIC:
            continue
        if rel.source in geom_state and "near" in geom_state[rel.source]:
            knowledge[rel.source] = geom_state[rel.source]["near"]
    return knowledge


def apply_dynamics(world: World, knowledge: Dict[str, str]) -> None:
    """Move predator toward prey if known."""
    for rel in world.relations:
        if rel.primitive != DYNAMICS:
            continue
        ent = world.entities[rel.source]
        target_id = knowledge.get(ent.id)
        if not target_id:
            continue
        tgt = world.entities[target_id]
        speed = rel.payload.get("speed", 1.0)
        dx = tgt.state["x"] - ent.state["x"]
        dy = tgt.state["y"] - ent.state["y"]
        # simple sign-based move
        ent.state["x"] += speed * (1 if dx > 0 else -1 if dx < 0 else 0)
        ent.state["y"] += speed * (1 if dy > 0 else -1 if dy < 0 else 0)


def apply_meta(world: World) -> None:
    """Example: spawn food every tick if none exists."""
    has_food = any(e.kind == "Food" for e in world.entities.values())
    if has_food:
        return
    new_id = f"food{len(world.entities)}"
    world.entities[new_id] = Entity(new_id, "Food", {"x": 5.0, "y": 5.0})


def run_gco(world: World) -> None:
    """GCO closure: prune duplicate relations."""
    seen: set[Tuple[str, str, str | None, Tuple[Tuple[str, float], ...]]] = set()
    deduped: List[Relation] = []
    for rel in world.relations:
        key = (rel.primitive, rel.source, rel.target, tuple(sorted(rel.payload.items())))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(rel)
    world.relations = deduped


def step(world: World) -> None:
    geom_state = apply_geometry(world)
    apply_constraint(world)
    knowledge = apply_epistemic(world, geom_state)
    apply_dynamics(world, knowledge)
    apply_meta(world)
    run_gco(world)


def demo() -> None:
    world = World(
        entities={
            "pred": Entity("pred", "Predator", {"x": 0.0, "y": 0.0}),
            "prey": Entity("prey", "Prey", {"x": 3.0, "y": 0.0}),
        },
        relations=[
            Relation(GEOMETRY, "pred", "prey", {"radius": 10.0}),
            Relation(CONSTRAINT, "pred", None, {"xmin": -10.0, "xmax": 10.0}),
            Relation(EPISTEMIC, "pred", None, {}),
            Relation(DYNAMICS, "pred", None, {"speed": 1.0}),
        ],
    )
    print("Initial:", {k: e.state for k, e in world.entities.items()})
    for i in range(4):
        step(world)
        print(f"After step {i+1}:", {k: e.state for k, e in world.entities.items()})


if __name__ == "__main__":
    demo()
