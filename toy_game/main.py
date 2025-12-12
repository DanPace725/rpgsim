"""
Advanced RP-style Rule Engine Demo - Showcasing RPE Principles

Run:
  python toy_game/main.py

Controls:
  Arrow keys: Move player (blue square)
  SPACE: Dash (costs stamina, grants brief invulnerability)
  S: Activate shield (costs energy, blocks one hit)

RPE Primitives Demonstrated:
  - GEOMETRY: Proximity, line-of-sight with wall occlusion, influence fields
  - CONSTRAINT: Bounds, stamina/energy limits, cooldowns, resource caps
  - EPISTEMIC: Memory (last known positions), alert propagation, fog of war
  - DYNAMICS: Movement, abilities (dash/shield), patrol patterns, pursuit AI
  - META: Difficulty scaling, wave spawning, faction conversion, rule mutations
  - GCO: Dedupe, contradiction resolution, status cleanup, state freezing
"""

from __future__ import annotations

import math
import random
import tkinter as tk
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

# ═══════════════════════════════════════════════════════════════════════════════
# PRIMITIVE LABELS
# ═══════════════════════════════════════════════════════════════════════════════
ONTOLOGY, GEOMETRY, CONSTRAINT, EPISTEMIC, DYNAMICS, META = (
    "ONTOLOGY", "GEOMETRY", "CONSTRAINT", "EPISTEMIC", "DYNAMICS", "META"
)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODEL (Enhanced)
# ═══════════════════════════════════════════════════════════════════════════════
@dataclass
class Entity:
    """A discrete world participant with rich state."""
    id: str
    kind: str
    color: str
    x: float
    y: float
    state: Dict[str, Any] = field(default_factory=dict)
    # Common state keys:
    # - vx, vy: velocity
    # - speed: movement rate
    # - stamina, max_stamina: for abilities
    # - energy, max_energy: for shields
    # - shield_active: bool
    # - invulnerable_until: tick when invuln ends
    # - memory: dict of entity_id -> {x, y, tick} for last known positions
    # - alert_level: 0-1 awareness
    # - patrol_points: list of (x,y) for patrol
    # - patrol_idx: current patrol target


@dataclass
class Relation:
    """A typed edge connecting entities or expressing a property."""
    primitive: str
    source: str
    target: Optional[str]
    payload: Dict[str, Any]


@dataclass
class Wall:
    """An occlusion obstacle for line-of-sight."""
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass
class GeometryContext:
    """Output of GEOMETRY phase - spatial foundation for subsequent phases."""
    proximity: Dict[str, List[Tuple[str, float]]]  # entity -> [(other, dist), ...]
    line_of_sight: Dict[str, Set[str]]  # entity -> set of visible entities
    influence_fields: Dict[str, float]  # entity -> danger level at position
    occluded_by: Dict[Tuple[str, str], Wall]  # (src, tgt) -> blocking wall


@dataclass
class World:
    """The complete simulation state."""
    entities: Dict[str, Entity]
    relations: List[Relation]
    walls: List[Wall]
    width: int
    height: int
    tick: int = 0
    game_over: bool = False
    game_win: bool = False
    score: int = 0
    goal: int = 10
    wave: int = 1
    difficulty: float = 1.0
    enemy_speed_boost: float = 0.0  # Accumulated speed boost from player eating food
    # GCO report for debugging/visualization
    gco_report: Dict[str, Any] = field(default_factory=dict)
    # Closure events for narrative
    events: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# GEOMETRY PHASE - Spatial, structural, topological evaluation
# ═══════════════════════════════════════════════════════════════════════════════
def line_intersects_wall(x1: float, y1: float, x2: float, y2: float, wall: Wall) -> bool:
    """Check if line segment (x1,y1)-(x2,y2) intersects wall segment."""
    def ccw(ax, ay, bx, by, cx, cy):
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)
    
    a1, a2 = (x1, y1), (x2, y2)
    b1, b2 = (wall.x1, wall.y1), (wall.x2, wall.y2)
    
    if ccw(a1[0], a1[1], b1[0], b1[1], b2[0], b2[1]) != ccw(a2[0], a2[1], b1[0], b1[1], b2[0], b2[1]):
        if ccw(a1[0], a1[1], a2[0], a2[1], b1[0], b1[1]) != ccw(a1[0], a1[1], a2[0], a2[1], b2[0], b2[1]):
            return True
    return False


def compute_distance(e1: Entity, e2: Entity) -> float:
    """Euclidean distance between two entities."""
    return math.sqrt((e1.x - e2.x) ** 2 + (e1.y - e2.y) ** 2)


def apply_geometry(world: World) -> GeometryContext:
    """
    GEOMETRY Phase: Build geometric snapshot for the tick.
    - Compute proximity relations
    - Determine line-of-sight with wall occlusion
    - Calculate influence/danger fields
    """
    ctx = GeometryContext(
        proximity={},
        line_of_sight={},
        influence_fields={},
        occluded_by={}
    )
    
    entities = list(world.entities.values())
    
    # Proximity computation
    for ent in entities:
        ctx.proximity[ent.id] = []
        for other in entities:
            if other.id == ent.id:
                continue
            dist = compute_distance(ent, other)
            ctx.proximity[ent.id].append((other.id, dist))
        # Sort by distance
        ctx.proximity[ent.id].sort(key=lambda x: x[1])
    
    # Line-of-sight with wall occlusion
    for ent in entities:
        ctx.line_of_sight[ent.id] = set()
        for other in entities:
            if other.id == ent.id:
                continue
            blocked = False
            blocking_wall = None
            for wall in world.walls:
                if line_intersects_wall(ent.x, ent.y, other.x, other.y, wall):
                    blocked = True
                    blocking_wall = wall
                    break
            if not blocked:
                ctx.line_of_sight[ent.id].add(other.id)
            else:
                ctx.occluded_by[(ent.id, other.id)] = blocking_wall
    
    # Influence/danger fields - hostiles emit danger
    player = world.entities.get("player")
    if player:
        danger = 0.0
        for ent in entities:
            if ent.kind in ("Hostile", "Converted"):
                dist = compute_distance(player, ent)
                if dist < 150:
                    # Inverse square falloff
                    danger += (150 - dist) / 150 * world.difficulty
        ctx.influence_fields["player_danger"] = min(danger, 1.0)
    
    return ctx


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT PHASE - Physical, systemic, resource bounds
# ═══════════════════════════════════════════════════════════════════════════════
def apply_constraint(world: World) -> List[str]:
    """
    CONSTRAINT Phase: Enforce bounds and resource limits.
    - Clamp positions to world bounds (respecting walls)
    - Enforce stamina/energy caps
    - Apply cooldowns
    - Validate state consistency
    """
    violations: List[str] = []
    
    for rel in world.relations:
        if rel.primitive != CONSTRAINT:
            continue
        ent = world.entities.get(rel.source)
        if not ent:
            continue
        
        constraint_type = rel.payload.get("type", "bounds")
        
        if constraint_type == "bounds":
            # Position clamping
            xmin = rel.payload.get("xmin", 0)
            xmax = rel.payload.get("xmax", world.width)
            ymin = rel.payload.get("ymin", 0)
            ymax = rel.payload.get("ymax", world.height)
            
            old_x, old_y = ent.x, ent.y
            ent.x = max(xmin, min(xmax, ent.x))
            ent.y = max(ymin, min(ymax, ent.y))
            
            if old_x != ent.x or old_y != ent.y:
                violations.append(f"{ent.id} hit boundary")
        
        elif constraint_type == "resource":
            # Resource clamping (stamina, energy)
            resource = rel.payload.get("resource", "stamina")
            max_key = f"max_{resource}"
            current = ent.state.get(resource, 0)
            maximum = ent.state.get(max_key, 100)
            
            if current < 0:
                ent.state[resource] = 0
                violations.append(f"{ent.id} {resource} depleted")
            elif current > maximum:
                ent.state[resource] = maximum
        
        elif constraint_type == "cooldown":
            # Cooldown enforcement
            ability = rel.payload.get("ability", "dash")
            cooldown_key = f"{ability}_cooldown"
            if ent.state.get(cooldown_key, 0) > 0:
                ent.state[cooldown_key] -= 1
    
    # Wall collision constraint
    for ent in world.entities.values():
        for wall in world.walls:
            # Simple point-to-line-segment distance push
            closest = closest_point_on_segment(ent.x, ent.y, wall.x1, wall.y1, wall.x2, wall.y2)
            dist = math.sqrt((ent.x - closest[0]) ** 2 + (ent.y - closest[1]) ** 2)
            if dist < 8:
                # Push away from wall
                if dist > 0:
                    push_x = (ent.x - closest[0]) / dist * (8 - dist)
                    push_y = (ent.y - closest[1]) / dist * (8 - dist)
                    ent.x += push_x
                    ent.y += push_y
    
    return violations


def closest_point_on_segment(px, py, x1, y1, x2, y2) -> Tuple[float, float]:
    """Find closest point on line segment to a point."""
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return (x1, y1)
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return (x1 + t * dx, y1 + t * dy)


# ═══════════════════════════════════════════════════════════════════════════════
# EPISTEMIC PHASE - Knowledge, perception, memory
# ═══════════════════════════════════════════════════════════════════════════════

# AI behavioral states (for smart state machine)
AI_STATE_PATROL = "patrol"
AI_STATE_HUNT = "hunt"          # Can see player, direct pursuit
AI_STATE_SEARCH = "search"       # Lost player, searching last known area
AI_STATE_AMBUSH = "ambush"       # Waiting near food/chokepoint
AI_STATE_FLANK = "flank"         # Coordinating with allies to surround
AI_STATE_INTERCEPT = "intercept" # Cutting off predicted escape route


@dataclass
class KnowledgeGraph:
    """Per-entity knowledge state - rich tactical awareness."""
    visible_entities: Set[str]
    remembered_positions: Dict[str, Tuple[float, float, int]]  # id -> (x, y, tick)
    alert_level: float  # 0.0 to 1.0
    threats: Set[str]
    # Enhanced tactical knowledge
    player_velocity: Tuple[float, float]  # Observed player movement direction
    player_predicted_pos: Tuple[float, float]  # Where player will likely be
    nearby_allies: List[str]  # Other hostiles we can coordinate with
    nearby_food: List[Tuple[float, float]]  # Food locations for ambush planning
    search_points: List[Tuple[float, float]]  # Points to check when searching
    current_search_idx: int  # Current search point index


def apply_epistemic(world: World, geo_ctx: GeometryContext) -> Dict[str, KnowledgeGraph]:
    """
    EPISTEMIC Phase: Determine what each entity knows.
    - Visibility based on line-of-sight and range
    - Memory of last known positions
    - Player velocity tracking and prediction
    - Alert propagation between nearby hostiles
    - Tactical awareness (allies, food positions, search patterns)
    """
    knowledge: Dict[str, KnowledgeGraph] = {}
    player = world.entities.get("player")
    
    # Track player velocity globally for prediction
    player_vel = (0.0, 0.0)
    if player:
        player_vel = (player.state.get("vx", 0) * player.state.get("speed", 2.8),
                      player.state.get("vy", 0) * player.state.get("speed", 2.8))
    
    # Gather food positions for ambush planning
    food_positions = [(e.x, e.y) for e in world.entities.values() if e.kind == "Food"]
    
    for rel in world.relations:
        if rel.primitive != EPISTEMIC:
            continue
        
        ent = world.entities.get(rel.source)
        if not ent:
            continue
        
        sense_radius = rel.payload.get("sense_radius", 100)
        memory_duration = rel.payload.get("memory_duration", 60)  # ticks
        
        # Initialize knowledge graph with tactical fields
        kg = KnowledgeGraph(
            visible_entities=set(),
            remembered_positions={},
            alert_level=ent.state.get("alert_level", 0.0),
            threats=set(),
            player_velocity=(0.0, 0.0),
            player_predicted_pos=(0.0, 0.0),
            nearby_allies=[],
            nearby_food=[],
            search_points=ent.state.get("search_points", []),
            current_search_idx=ent.state.get("current_search_idx", 0)
        )
        
        # Copy existing memory
        if "memory" in ent.state:
            for mem_id, mem_data in ent.state["memory"].items():
                if world.tick - mem_data[2] < memory_duration:
                    kg.remembered_positions[mem_id] = mem_data
        
        # Check visibility
        los = geo_ctx.line_of_sight.get(ent.id, set())
        for other_id, dist in geo_ctx.proximity.get(ent.id, []):
            if other_id in los and dist <= sense_radius:
                kg.visible_entities.add(other_id)
                other = world.entities.get(other_id)
                if other:
                    # Update memory with current position
                    kg.remembered_positions[other_id] = (other.x, other.y, world.tick)
                    
                    # Threat assessment
                    if ent.kind == "Player" and other.kind in ("Hostile", "Converted"):
                        kg.threats.add(other_id)
                    elif ent.kind in ("Hostile", "Converted") and other.kind == "Player":
                        kg.threats.add(other_id)
                        kg.alert_level = 1.0  # Spotted player!
                        # Track player velocity when visible
                        kg.player_velocity = player_vel
                        # Predict where player will be in ~20 ticks
                        predict_ticks = 20
                        kg.player_predicted_pos = (
                            other.x + player_vel[0] * predict_ticks,
                            other.y + player_vel[1] * predict_ticks
                        )
                    elif ent.kind == "Hostile" and other.kind == "Passive":
                        kg.threats.add(other_id)  # Target
                    elif ent.kind == "Passive" and other.kind == "Hostile":
                        kg.threats.add(other_id)  # Danger!
        
        # Find nearby allies (for coordination)
        if ent.kind in ("Hostile", "Converted"):
            for other in world.entities.values():
                if other.id != ent.id and other.kind in ("Hostile", "Converted"):
                    if compute_distance(ent, other) < 150:
                        kg.nearby_allies.append(other.id)
        
        # Find nearby food (for ambush planning)
        for fx, fy in food_positions:
            dist = math.sqrt((ent.x - fx) ** 2 + (ent.y - fy) ** 2)
            if dist < 200:
                kg.nearby_food.append((fx, fy))
        
        # Alert decay
        if not kg.threats:
            kg.alert_level = max(0, kg.alert_level - 0.02)
        
        # Update entity state with knowledge
        ent.state["memory"] = kg.remembered_positions
        ent.state["alert_level"] = kg.alert_level
        
        knowledge[ent.id] = kg
    
    # Enhanced alert propagation with tactical info sharing
    hostiles = [e for e in world.entities.values() if e.kind in ("Hostile", "Converted")]
    for h1 in hostiles:
        kg1 = knowledge.get(h1.id)
        if not kg1 or kg1.alert_level < 0.5:
            continue
        for h2 in hostiles:
            if h1.id == h2.id:
                continue
            kg2 = knowledge.get(h2.id)
            if not kg2:
                continue
            dist = compute_distance(h1, h2)
            if dist < 120 and h2.id in geo_ctx.line_of_sight.get(h1.id, set()):
                # Propagate alert and player memory
                kg2.alert_level = max(kg2.alert_level, kg1.alert_level * 0.8)
                if "player" in kg1.remembered_positions:
                    kg2.remembered_positions["player"] = kg1.remembered_positions["player"]
                    # Share velocity and prediction info!
                    if kg1.player_velocity != (0.0, 0.0):
                        kg2.player_velocity = kg1.player_velocity
                        kg2.player_predicted_pos = kg1.player_predicted_pos
                world.entities[h2.id].state["alert_level"] = kg2.alert_level
    
    return knowledge


# ═══════════════════════════════════════════════════════════════════════════════
# DYNAMICS PHASE - Movement, abilities, behaviors
# ═══════════════════════════════════════════════════════════════════════════════
def apply_dynamics(world: World, knowledge: Dict[str, KnowledgeGraph], geo_ctx: GeometryContext) -> None:
    """
    DYNAMICS Phase: Apply state changes.
    - Player movement and abilities
    - AI decision-making based on knowledge
    - Patrol patterns
    - Combat resolution
    """
    for rel in world.relations:
        if rel.primitive != DYNAMICS:
            continue
        
        ent = world.entities.get(rel.source)
        if not ent:
            continue
        
        speed = ent.state.get("speed", rel.payload.get("speed", 1.0))
        kg = knowledge.get(ent.id)
        
        if ent.kind == "Player":
            # Player movement with stamina regen
            vx = ent.state.get("vx", 0)
            vy = ent.state.get("vy", 0)
            
            # Dash handling
            if ent.state.get("dashing", False):
                dash_dir = ent.state.get("dash_direction", (0, 0))
                ent.x += dash_dir[0] * speed * 4
                ent.y += dash_dir[1] * speed * 4
                ent.state["dash_frames"] = ent.state.get("dash_frames", 0) - 1
                if ent.state["dash_frames"] <= 0:
                    ent.state["dashing"] = False
            else:
                ent.x += vx * speed
                ent.y += vy * speed
            
            # Stamina regeneration
            stamina = ent.state.get("stamina", 100)
            max_stamina = ent.state.get("max_stamina", 100)
            if stamina < max_stamina and not ent.state.get("dashing", False):
                ent.state["stamina"] = min(max_stamina, stamina + 0.5)
            
            # Energy regeneration
            energy = ent.state.get("energy", 50)
            max_energy = ent.state.get("max_energy", 50)
            if energy < max_energy:
                ent.state["energy"] = min(max_energy, energy + 0.2)
        
        elif ent.kind == "Hostile":
            apply_hostile_ai(ent, world, kg, speed)
        
        elif ent.kind == "Converted":
            apply_converted_ai(ent, world, kg, speed)
        
        elif ent.kind == "Passive":
            apply_passive_ai(ent, world, kg, speed)


def apply_hostile_ai(ent: Entity, world: World, kg: Optional[KnowledgeGraph], speed: float) -> None:
    """
    Smart Hostile AI with behavioral state machine:
    - HUNT: Direct pursuit when player visible
    - INTERCEPT: Cut off predicted escape route
    - FLANK: Coordinate with allies to surround
    - SEARCH: Methodically search last known area
    - AMBUSH: Wait near food/chokepoints
    - PATROL: Default patrol behavior
    """
    player = world.entities.get("player")
    current_state = ent.state.get("ai_state", AI_STATE_PATROL)
    
    # Determine best state based on knowledge
    new_state = determine_ai_state(ent, world, kg, player)
    if new_state != current_state:
        ent.state["ai_state"] = new_state
        ent.state["state_tick"] = world.tick
    
    # Execute behavior based on state
    if new_state == AI_STATE_HUNT:
        execute_hunt(ent, world, kg, player, speed)
    elif new_state == AI_STATE_INTERCEPT:
        execute_intercept(ent, world, kg, player, speed)
    elif new_state == AI_STATE_FLANK:
        execute_flank(ent, world, kg, player, speed)
    elif new_state == AI_STATE_SEARCH:
        execute_search(ent, world, kg, speed)
    elif new_state == AI_STATE_AMBUSH:
        execute_ambush(ent, world, kg, speed)
    else:  # PATROL
        execute_patrol(ent, world, kg, speed)


def determine_ai_state(ent: Entity, world: World, kg: Optional[KnowledgeGraph], player: Optional[Entity]) -> str:
    """Determine the best AI state based on current knowledge."""
    if not kg:
        return AI_STATE_PATROL
    
    has_allies = len(kg.nearby_allies) > 0
    can_see_player = player and "player" in kg.visible_entities
    has_memory = "player" in kg.remembered_positions
    memory_age = world.tick - kg.remembered_positions.get("player", (0, 0, 0))[2] if has_memory else 999
    has_food_nearby = len(kg.nearby_food) > 0
    
    # Priority 1: If we can see the player
    if can_see_player and player:
        # Check if we should flank or intercept vs direct hunt
        if has_allies and len(kg.nearby_allies) >= 1:
            # Coordinate with allies - some flank, some intercept
            ally_count = len(kg.nearby_allies)
            # Use entity ID hash to consistently assign roles
            role_hash = hash(ent.id) % (ally_count + 1)
            if role_hash == 0:
                return AI_STATE_INTERCEPT  # Cut off escape
            elif role_hash == 1 and ally_count >= 2:
                return AI_STATE_FLANK  # Flank
            else:
                return AI_STATE_HUNT  # Direct pursuit
        else:
            # Solo - direct pursuit or intercept based on player movement
            if kg.player_velocity != (0.0, 0.0):
                # Player is moving - try to intercept
                return AI_STATE_INTERCEPT
            return AI_STATE_HUNT
    
    # Priority 2: Recent memory - search the area
    if has_memory and memory_age < 60:
        return AI_STATE_SEARCH
    
    # Priority 3: Alert but no recent sighting - ambush near food
    if kg.alert_level > 0.3 and has_food_nearby:
        return AI_STATE_AMBUSH
    
    # Default: Patrol
    return AI_STATE_PATROL


def execute_hunt(ent: Entity, world: World, kg: KnowledgeGraph, player: Entity, speed: float) -> None:
    """Direct pursuit - chase player aggressively."""
    if player:
        chase_target(ent, player.x, player.y, speed * world.difficulty * 1.1)


def execute_intercept(ent: Entity, world: World, kg: KnowledgeGraph, player: Optional[Entity], speed: float) -> None:
    """Cut off the player's predicted escape route."""
    if kg.player_predicted_pos != (0.0, 0.0):
        pred_x, pred_y = kg.player_predicted_pos
        # Clamp to world bounds
        pred_x = max(20, min(world.width - 20, pred_x))
        pred_y = max(20, min(world.height - 20, pred_y))
        chase_target(ent, pred_x, pred_y, speed * world.difficulty * 1.2)
    elif player:
        # Fallback to direct chase
        chase_target(ent, player.x, player.y, speed * world.difficulty)


def execute_flank(ent: Entity, world: World, kg: KnowledgeGraph, player: Optional[Entity], speed: float) -> None:
    """Coordinate with allies to approach from a different angle."""
    if not player:
        execute_patrol(ent, world, kg, speed)
        return
    
    # Calculate flanking position - perpendicular to player-to-entity vector
    dx = player.x - ent.x
    dy = player.y - ent.y
    dist = math.sqrt(dx * dx + dy * dy)
    
    if dist < 30:
        # Close enough, just attack
        chase_target(ent, player.x, player.y, speed * world.difficulty)
        return
    
    # Perpendicular offset for flanking (alternates based on entity ID)
    perp_sign = 1 if hash(ent.id) % 2 == 0 else -1
    perp_x = -dy / dist * 50 * perp_sign
    perp_y = dx / dist * 50 * perp_sign
    
    # Target position is offset from player
    flank_x = player.x + perp_x
    flank_y = player.y + perp_y
    
    # Clamp to bounds
    flank_x = max(20, min(world.width - 20, flank_x))
    flank_y = max(20, min(world.height - 20, flank_y))
    
    chase_target(ent, flank_x, flank_y, speed * world.difficulty)


def execute_search(ent: Entity, world: World, kg: KnowledgeGraph, speed: float) -> None:
    """Methodically search the area where player was last seen."""
    if "player" not in kg.remembered_positions:
        execute_patrol(ent, world, kg, speed)
        return
    
    last_x, last_y, last_tick = kg.remembered_positions["player"]
    
    # Generate search points if we don't have them or they're stale
    if not kg.search_points or ent.state.get("search_origin") != (last_x, last_y):
        # Create a search pattern around last known position
        search_radius = 60
        kg.search_points = [
            (last_x, last_y),  # Start at last known pos
            (last_x + search_radius, last_y),
            (last_x + search_radius, last_y + search_radius),
            (last_x, last_y + search_radius),
            (last_x - search_radius, last_y + search_radius),
            (last_x - search_radius, last_y),
            (last_x - search_radius, last_y - search_radius),
            (last_x, last_y - search_radius),
            (last_x + search_radius, last_y - search_radius),
        ]
        # Clamp to bounds
        kg.search_points = [
            (max(20, min(world.width - 20, x)), max(20, min(world.height - 20, y)))
            for x, y in kg.search_points
        ]
        kg.current_search_idx = 0
        ent.state["search_points"] = kg.search_points
        ent.state["search_origin"] = (last_x, last_y)
        ent.state["current_search_idx"] = 0
    
    # Move to current search point
    if kg.current_search_idx < len(kg.search_points):
        target = kg.search_points[kg.current_search_idx]
        dist = math.sqrt((ent.x - target[0]) ** 2 + (ent.y - target[1]) ** 2)
        
        if dist < 15:
            # Reached this point, move to next
            kg.current_search_idx += 1
            ent.state["current_search_idx"] = kg.current_search_idx
        else:
            move_toward_with_wall_avoidance(ent, target[0], target[1], speed * 0.7 * world.difficulty, world)
    else:
        # Finished search pattern, go back to patrol
        ent.state["ai_state"] = AI_STATE_PATROL
        ent.state["search_points"] = []


def execute_ambush(ent: Entity, world: World, kg: KnowledgeGraph, speed: float) -> None:
    """Position near food and wait for player to approach."""
    if not kg.nearby_food:
        execute_patrol(ent, world, kg, speed)
        return
    
    # Find the best food to ambush near (closest)
    target_food = min(kg.nearby_food, key=lambda f: (ent.x - f[0]) ** 2 + (ent.y - f[1]) ** 2)
    
    # Position slightly away from food (ambush distance)
    ambush_dist = 35
    dx = ent.x - target_food[0]
    dy = ent.y - target_food[1]
    current_dist = math.sqrt(dx * dx + dy * dy)
    
    if current_dist < ambush_dist - 5:
        # Too close, back off slightly
        if current_dist > 0:
            ent.x += (dx / current_dist) * speed * 0.3
            ent.y += (dy / current_dist) * speed * 0.3
    elif current_dist > ambush_dist + 10:
        # Too far, move closer
        chase_target(ent, target_food[0], target_food[1], speed * 0.6)
    # else: In position, hold and wait (small random movement to look natural)
    else:
        if world.tick % 30 == 0:
            ent.x += random.uniform(-2, 2)
            ent.y += random.uniform(-2, 2)


def execute_patrol(ent: Entity, world: World, kg: Optional[KnowledgeGraph], speed: float) -> None:
    """Default patrol behavior."""
    patrol_points = ent.state.get("patrol_points", [])
    if patrol_points:
        idx = ent.state.get("patrol_idx", 0)
        target = patrol_points[idx]
        dist = math.sqrt((ent.x - target[0]) ** 2 + (ent.y - target[1]) ** 2)
        if dist < 10:
            ent.state["patrol_idx"] = (idx + 1) % len(patrol_points)
        else:
            move_toward_with_wall_avoidance(ent, target[0], target[1], speed * 0.5, world)
        return
    
    # No patrol points - wander
    if world.tick % 20 == 0:
        ent.state["vx"] = random.choice([-1, 0, 1])
        ent.state["vy"] = random.choice([-1, 0, 1])
    ent.x += speed * 0.5 * ent.state.get("vx", 0)
    ent.y += speed * 0.5 * ent.state.get("vy", 0)


def apply_converted_ai(ent: Entity, world: World, kg: Optional[KnowledgeGraph], speed: float) -> None:
    """
    Converted AI: More aggressive version of hostile.
    Uses prediction heavily and never gives up pursuit.
    """
    player = world.entities.get("player")
    
    # Always prioritize interception if we have velocity info
    if kg and kg.player_velocity != (0.0, 0.0) and player:
        # Aggressive prediction - aim further ahead
        predict_ticks = 30  # Look further ahead than regular hostile
        pred_x = player.x + kg.player_velocity[0] * predict_ticks
        pred_y = player.y + kg.player_velocity[1] * predict_ticks
        
        # Clamp to bounds
        pred_x = max(20, min(world.width - 20, pred_x))
        pred_y = max(20, min(world.height - 20, pred_y))
        
        # Choose: direct chase or intercept based on angle
        dist_to_player = compute_distance(ent, player) if player else 999
        dist_to_pred = math.sqrt((ent.x - pred_x) ** 2 + (ent.y - pred_y) ** 2)
        
        # If prediction is closer, intercept; otherwise direct chase
        if dist_to_pred < dist_to_player * 0.8:
            chase_target(ent, pred_x, pred_y, speed * world.difficulty * 1.2)
        else:
            chase_target(ent, player.x, player.y, speed * world.difficulty * 1.1)
        return
    
    # Can see player - direct aggressive chase
    if kg and "player" in kg.visible_entities and player:
        chase_target(ent, player.x, player.y, speed * world.difficulty * 1.1)
        return
    
    # Have memory - relentlessly pursue last known position
    if kg and "player" in kg.remembered_positions:
        mem = kg.remembered_positions["player"]
        move_toward_with_wall_avoidance(ent, mem[0], mem[1], speed * world.difficulty, world)
        return
    
    # No info - aggressive random search
    if world.tick % 8 == 0:
        ent.state["vx"] = random.choice([-1, 0, 1])
        ent.state["vy"] = random.choice([-1, 0, 1])
    ent.x += speed * 0.8 * ent.state.get("vx", 0)
    ent.y += speed * 0.8 * ent.state.get("vy", 0)


def apply_passive_ai(ent: Entity, world: World, kg: Optional[KnowledgeGraph], speed: float) -> None:
    """Passive AI: Flee threats, seek food (with wall-aware pathfinding)."""
    # Priority 1: Flee from visible threats (with wall avoidance)
    if kg and kg.threats:
        # Average threat direction
        flee_x, flee_y = 0.0, 0.0
        for threat_id in kg.threats:
            threat = world.entities.get(threat_id)
            if threat:
                flee_x += ent.x - threat.x
                flee_y += ent.y - threat.y
        if flee_x != 0 or flee_y != 0:
            mag = math.sqrt(flee_x ** 2 + flee_y ** 2)
            # Calculate flee target position
            flee_target_x = ent.x + (flee_x / mag) * 100
            flee_target_y = ent.y + (flee_y / mag) * 100
            move_toward_with_wall_avoidance(ent, flee_target_x, flee_target_y, speed * 1.5, world)
            return
    
    # Priority 2: Seek food (with wall-aware pathfinding)
    foods = [e for e in world.entities.values() if e.kind == "Food"]
    if foods:
        nearest = min(foods, key=lambda f: (f.x - ent.x) ** 2 + (f.y - ent.y) ** 2)
        move_toward_with_wall_avoidance(ent, nearest.x, nearest.y, speed, world)
        return
    
    # Priority 3: Wander (with wall avoidance)
    if world.tick % 15 == 0:
        ent.state["vx"] = random.choice([-1, 0, 1])
        ent.state["vy"] = random.choice([-1, 0, 1])
    wander_x = ent.x + ent.state.get("vx", 0) * 50
    wander_y = ent.y + ent.state.get("vy", 0) * 50
    move_toward_with_wall_avoidance(ent, wander_x, wander_y, speed, world)


def chase_target(ent: Entity, tx: float, ty: float, speed: float) -> None:
    """Move entity toward target position."""
    dx = tx - ent.x
    dy = ty - ent.y
    dist = math.sqrt(dx * dx + dy * dy)
    if dist > 0:
        ent.x += (dx / dist) * speed
        ent.y += (dy / dist) * speed


def move_toward_with_wall_avoidance(ent: Entity, tx: float, ty: float, speed: float, world: World) -> None:
    """
    Move entity toward target with wall avoidance (simple steering behavior).
    This is used by passives to pathfind around walls instead of getting stuck.
    """
    dx = tx - ent.x
    dy = ty - ent.y
    dist = math.sqrt(dx * dx + dy * dy)
    if dist < 1:
        return
    
    # Normalize desired direction
    desired_x = dx / dist
    desired_y = dy / dist
    
    # Check if direct path is blocked by a wall
    blocked = False
    blocking_wall = None
    lookahead = min(dist, 40)  # Look ahead up to 40 pixels or target distance
    
    test_x = ent.x + desired_x * lookahead
    test_y = ent.y + desired_y * lookahead
    
    for wall in world.walls:
        if line_intersects_wall(ent.x, ent.y, test_x, test_y, wall):
            blocked = True
            blocking_wall = wall
            break
    
    if blocked and blocking_wall:
        # Calculate wall tangent direction for steering around
        wall_dx = blocking_wall.x2 - blocking_wall.x1
        wall_dy = blocking_wall.y2 - blocking_wall.y1
        wall_len = math.sqrt(wall_dx * wall_dx + wall_dy * wall_dy)
        if wall_len > 0:
            # Normalize wall direction (tangent)
            tangent_x = wall_dx / wall_len
            tangent_y = wall_dy / wall_len
            
            # Choose which direction along the wall gets us closer to target
            # by checking dot product with desired direction
            dot = tangent_x * desired_x + tangent_y * desired_y
            if dot < 0:
                tangent_x = -tangent_x
                tangent_y = -tangent_y
            
            # Blend: mostly tangent with a bit of perpendicular push away from wall
            closest = closest_point_on_segment(ent.x, ent.y, 
                                               blocking_wall.x1, blocking_wall.y1,
                                               blocking_wall.x2, blocking_wall.y2)
            away_x = ent.x - closest[0]
            away_y = ent.y - closest[1]
            away_dist = math.sqrt(away_x * away_x + away_y * away_y)
            if away_dist > 0:
                away_x /= away_dist
                away_y /= away_dist
            
            # Combine tangent movement with push away from wall
            steer_x = tangent_x * 0.7 + away_x * 0.3
            steer_y = tangent_y * 0.7 + away_y * 0.3
            steer_len = math.sqrt(steer_x * steer_x + steer_y * steer_y)
            if steer_len > 0:
                ent.x += (steer_x / steer_len) * speed
                ent.y += (steer_y / steer_len) * speed
                return
    
    # No wall blocking, move directly toward target
    ent.x += desired_x * speed
    ent.y += desired_y * speed


# ═══════════════════════════════════════════════════════════════════════════════
# META PHASE - Rules about rules, structural mutations
# ═══════════════════════════════════════════════════════════════════════════════
def apply_meta(world: World) -> List[str]:
    """
    META Phase: System-level mutations and rule changes.
    - Spawn food to maintain minimum
    - Wave-based enemy spawning
    - Difficulty scaling
    - Faction conversions
    - Role changes
    """
    events: List[str] = []
    
    # Ensure minimum food exists
    foods = [e for e in world.entities.values() if e.kind == "Food"]
    food_target = 3 + world.wave
    if len(foods) < food_target and world.tick % 25 == 0:
        new_id = f"food_{world.tick}"
        x = random.uniform(50, world.width - 50)
        y = random.uniform(50, world.height - 50)
        # Avoid spawning on walls
        valid = True
        for wall in world.walls:
            closest = closest_point_on_segment(x, y, wall.x1, wall.y1, wall.x2, wall.y2)
            if math.sqrt((x - closest[0]) ** 2 + (y - closest[1]) ** 2) < 20:
                valid = False
                break
        if valid:
            world.entities[new_id] = Entity(new_id, "Food", "yellow", x, y)
            events.append(f"META: Spawned {new_id}")
    
    # Wave progression - spawn more enemies when score hits thresholds
    wave_threshold = world.wave * 3
    if world.score >= wave_threshold and world.wave < 5:
        world.wave += 1
        world.difficulty += 0.15
        events.append(f"META: Wave {world.wave} - Difficulty increased to {world.difficulty:.2f}")
        
        # Spawn new hostile (with accumulated speed boost from player eating food)
        new_id = f"hostile_w{world.wave}_{world.tick}"
        spawn_x = random.uniform(world.width * 0.6, world.width - 50)
        spawn_y = random.uniform(50, world.height - 50)
        patrol = generate_patrol_points(world, spawn_x, spawn_y)
        base_speed = 1.3 + world.wave * 0.1 + world.enemy_speed_boost
        world.entities[new_id] = Entity(
            new_id, "Hostile", "red", spawn_x, spawn_y,
            {"speed": base_speed, "vx": 0, "vy": 0, "patrol_points": patrol, "patrol_idx": 0}
        )
        rebuild_relations(world)
        events.append(f"META: Spawned {new_id}")
    
    # Hostile-Hostile collision -> Converted (demonstrate faction change)
    hostile_ids = [e.id for e in world.entities.values() if e.kind == "Hostile"]
    for i in range(len(hostile_ids)):
        for j in range(i + 1, len(hostile_ids)):
            a = world.entities[hostile_ids[i]]
            b = world.entities[hostile_ids[j]]
            if compute_distance(a, b) <= 12:
                for ent in (a, b):
                    ent.kind = "Converted"
                    ent.color = "purple"
                    ent.state["speed"] = 1.5 + world.enemy_speed_boost  # Inherit speed boost
                    ent.state["last_conversion_tick"] = world.tick
                events.append(f"META: {a.id} and {b.id} collided -> Converted")
                rebuild_relations(world)
    
    # Hostile converts Passive on contact
    passives = [e for e in world.entities.values() if e.kind == "Passive"]
    hostiles = [e for e in world.entities.values() if e.kind == "Hostile"]
    for h in hostiles:
        if world.tick - h.state.get("last_conversion_tick", -100) < 15:
            continue
        for p in passives:
            if world.tick - p.state.get("last_conversion_tick", -100) < 15:
                continue
            if compute_distance(h, p) <= 10:
                p.kind = "Converted"
                p.color = "purple"
                p.state["speed"] = 1.4 + world.enemy_speed_boost  # Inherit speed boost
                p.state["last_conversion_tick"] = world.tick
                events.append(f"META: {h.id} converted {p.id}")
                rebuild_relations(world)
                break
    
    return events


def generate_patrol_points(world: World, start_x: float, start_y: float) -> List[Tuple[float, float]]:
    """Generate random patrol points near starting position."""
    points = [(start_x, start_y)]
    for _ in range(3):
        px = max(50, min(world.width - 50, start_x + random.uniform(-100, 100)))
        py = max(50, min(world.height - 50, start_y + random.uniform(-100, 100)))
        points.append((px, py))
    return points


# ═══════════════════════════════════════════════════════════════════════════════
# GCO - Global Closure Operator
# ═══════════════════════════════════════════════════════════════════════════════
def run_gco(world: World) -> Dict[str, Any]:
    """
    GCO Phase: Ensure world consistency and finalize tick.
    - Dedupe identical relations
    - Detect and resolve contradictions
    - Clean up expired status effects
    - Remove invalid references
    - Freeze stable states
    """
    report: Dict[str, Any] = {
        "deduped": 0,
        "contradictions": [],
        "cleaned_effects": [],
        "removed_invalid": [],
    }
    
    # 1. Dedupe identical relations
    seen: Set[tuple] = set()
    deduped: List[Relation] = []
    for rel in world.relations:
        key = (rel.primitive, rel.source, rel.target, tuple(sorted(rel.payload.items())))
        if key not in seen:
            seen.add(key)
            deduped.append(rel)
        else:
            report["deduped"] += 1
    world.relations = deduped
    
    # 2. Detect contradictions (e.g., entity both dead and alive - simplified)
    player = world.entities.get("player")
    if player:
        # Contradiction: shield active with zero energy
        if player.state.get("shield_active", False) and player.state.get("energy", 0) <= 0:
            player.state["shield_active"] = False
            report["contradictions"].append("Shield active with no energy -> disabled")
        
        # Contradiction: invulnerable but past duration
        if player.state.get("invulnerable_until", 0) > 0:
            if world.tick >= player.state["invulnerable_until"]:
                player.state["invulnerable_until"] = 0
                report["cleaned_effects"].append("Invulnerability expired")
    
    # 3. Remove relations referencing non-existent entities
    valid_ids = set(world.entities.keys())
    cleaned: List[Relation] = []
    for rel in world.relations:
        if rel.source not in valid_ids:
            report["removed_invalid"].append(f"Relation with invalid source: {rel.source}")
            continue
        if rel.target is not None and rel.target not in valid_ids:
            report["removed_invalid"].append(f"Relation with invalid target: {rel.target}")
            continue
        cleaned.append(rel)
    world.relations = cleaned
    
    # 4. Clean up memory references to despawned entities
    for ent in world.entities.values():
        if "memory" in ent.state:
            ent.state["memory"] = {
                k: v for k, v in ent.state["memory"].items()
                if k in valid_ids
            }
    
    # 5. Decay alert levels globally
    for ent in world.entities.values():
        if ent.kind in ("Hostile", "Converted"):
            alert = ent.state.get("alert_level", 0)
            if alert > 0:
                ent.state["alert_level"] = max(0, alert - 0.01)
    
    world.gco_report = report
    return report


# ═══════════════════════════════════════════════════════════════════════════════
# GAME LOGIC
# ═══════════════════════════════════════════════════════════════════════════════
def consume_food(world: World) -> List[str]:
    """Handle food consumption by player and passives."""
    events: List[str] = []
    food_ids = [e.id for e in world.entities.values() if e.kind == "Food"]
    eaters = [e for e in world.entities.values() if e.kind in ("Passive", "Player")]
    eaten = set()
    player_ate = False
    
    for eater in eaters:
        for fid in food_ids:
            if fid in eaten:
                continue
            food = world.entities.get(fid)
            if not food:
                continue
            if compute_distance(eater, food) <= 10:
                eaten.add(fid)
                if eater.kind == "Player":
                    world.score += 1
                    player_ate = True
                    events.append(f"Player ate {fid} (Score: {world.score})")
                    if world.score >= world.goal:
                        world.game_win = True
                        events.append("VICTORY!")
    
    for fid in eaten:
        world.entities.pop(fid, None)
    
    # META rule: When player eats food, ALL enemies get faster!
    # This creates escalating tension as you collect more food
    if player_ate:
        speed_boost = 0.08  # Each food makes enemies 8% faster
        world.enemy_speed_boost += speed_boost  # Track globally for new spawns
        for ent in world.entities.values():
            if ent.kind in ("Hostile", "Converted"):
                old_speed = ent.state.get("speed", 1.3)
                ent.state["speed"] = old_speed + speed_boost
        events.append(f"META: Enemies accelerated! (+{speed_boost:.0%} speed)")
    
    return events


def check_collisions(world: World) -> List[str]:
    """Check player-enemy collisions."""
    events: List[str] = []
    player = world.entities.get("player")
    if not player:
        return events
    
    # Check invulnerability
    if world.tick < player.state.get("invulnerable_until", 0):
        return events  # Can't be hit
    
    for ent in world.entities.values():
        if ent.kind not in ("Hostile", "Converted"):
            continue
        if compute_distance(player, ent) <= 10:
            # Shield check
            if player.state.get("shield_active", False):
                player.state["shield_active"] = False
                player.state["energy"] = 0
                events.append(f"Shield blocked hit from {ent.id}!")
                # Push enemy back
                dx = ent.x - player.x
                dy = ent.y - player.y
                dist = max(1, math.sqrt(dx * dx + dy * dy))
                ent.x += (dx / dist) * 30
                ent.y += (dy / dist) * 30
            else:
                world.game_over = True
                events.append(f"Game Over - Hit by {ent.id}")
                break
    
    return events


def step(world: World) -> None:
    """Execute one RPE tick cycle."""
    world.events.clear()
    
    # ⭐ Step 1: GEOMETRY
    geo_ctx = apply_geometry(world)
    
    # ⭐ Step 2: CONSTRAINT
    violations = apply_constraint(world)
    world.events.extend(violations)
    
    # ⭐ Step 3: EPISTEMIC
    knowledge = apply_epistemic(world, geo_ctx)
    
    # ⭐ Step 4: DYNAMICS
    apply_dynamics(world, knowledge, geo_ctx)
    
    # ⭐ Step 5: META
    meta_events = apply_meta(world)
    world.events.extend(meta_events)
    
    # Game logic (integrated with tick)
    food_events = consume_food(world)
    world.events.extend(food_events)
    
    collision_events = check_collisions(world)
    world.events.extend(collision_events)
    
    # ⭐ Step 6: GCO
    run_gco(world)
    
    world.tick += 1


# ═══════════════════════════════════════════════════════════════════════════════
# PLAYER ABILITIES
# ═══════════════════════════════════════════════════════════════════════════════
def player_dash(world: World) -> bool:
    """Execute dash ability if available."""
    player = world.entities.get("player")
    if not player:
        return False
    
    stamina = player.state.get("stamina", 0)
    dash_cost = 25
    cooldown = player.state.get("dash_cooldown", 0)
    
    if stamina >= dash_cost and cooldown <= 0:
        vx = player.state.get("vx", 0)
        vy = player.state.get("vy", 0)
        # Use last movement direction or default forward
        if vx == 0 and vy == 0:
            vx = 1  # Default right
        
        player.state["stamina"] = stamina - dash_cost
        player.state["dashing"] = True
        player.state["dash_direction"] = (vx, vy)
        player.state["dash_frames"] = 5
        player.state["dash_cooldown"] = 15
        player.state["invulnerable_until"] = world.tick + 8  # Brief invuln
        return True
    return False


def player_shield(world: World) -> bool:
    """Activate shield if available."""
    player = world.entities.get("player")
    if not player:
        return False
    
    energy = player.state.get("energy", 0)
    shield_cost = 30
    
    if energy >= shield_cost and not player.state.get("shield_active", False):
        player.state["energy"] = energy - shield_cost
        player.state["shield_active"] = True
        return True
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# WORLD SETUP
# ═══════════════════════════════════════════════════════════════════════════════
def create_world(width: int, height: int) -> World:
    """Initialize world with entities, relations, and walls."""
    entities: Dict[str, Entity] = {
        "player": Entity("player", "Player", "blue", width * 0.15, height * 0.5, {
            "vx": 0, "vy": 0, "speed": 2.8,
            "stamina": 100, "max_stamina": 100,
            "energy": 50, "max_energy": 50,
            "shield_active": False,
            "dash_cooldown": 0,
            "invulnerable_until": 0,
            "memory": {},
        }),
    }
    
    # Hostiles with patrol routes
    hostile_configs = [
        (0.75, 0.25, [(0.7, 0.2), (0.8, 0.3), (0.7, 0.4)]),
        (0.65, 0.75, [(0.6, 0.7), (0.7, 0.8), (0.6, 0.9)]),
        (0.85, 0.5, [(0.8, 0.4), (0.9, 0.6), (0.8, 0.6)]),
    ]
    for idx, (px, py, patrol) in enumerate(hostile_configs, start=1):
        eid = f"hostile{idx}"
        patrol_points = [(width * p[0], height * p[1]) for p in patrol]
        entities[eid] = Entity(eid, "Hostile", "red", width * px, height * py, {
            "speed": 1.3, "vx": 0, "vy": 0,
            "patrol_points": patrol_points, "patrol_idx": 0,
            "alert_level": 0, "memory": {},
        })
    
    # Passives
    passive_positions = [(0.4, 0.2), (0.35, 0.8), (0.5, 0.5), (0.25, 0.6)]
    for idx, (px, py) in enumerate(passive_positions, start=1):
        eid = f"passive{idx}"
        entities[eid] = Entity(eid, "Passive", "green", width * px, height * py, {
            "vx": 0, "vy": 0, "speed": 0.9, "alert_level": 0, "memory": {},
        })
    
    # Walls for occlusion
    walls = [
        Wall(width * 0.5, height * 0.1, width * 0.5, height * 0.35),
        Wall(width * 0.5, height * 0.65, width * 0.5, height * 0.9),
        Wall(width * 0.3, height * 0.5, width * 0.4, height * 0.5),
    ]
    
    world = World(
        entities=entities,
        relations=[],
        walls=walls,
        width=width,
        height=height,
    )
    rebuild_relations(world)
    return world


def rebuild_relations(world: World) -> None:
    """Rebuild all relations based on current entity configuration."""
    rels: List[Relation] = []
    width, height = world.width, world.height
    player = world.entities.get("player")
    
    # Constraints for all mobile entities
    for ent in world.entities.values():
        if ent.kind == "Food":
            continue
        rels.append(Relation(CONSTRAINT, ent.id, None, {
            "type": "bounds", "xmin": 5, "xmax": width - 5, "ymin": 5, "ymax": height - 5
        }))
    
    # Player resource constraints
    if player:
        rels.append(Relation(CONSTRAINT, player.id, None, {"type": "resource", "resource": "stamina"}))
        rels.append(Relation(CONSTRAINT, player.id, None, {"type": "resource", "resource": "energy"}))
        rels.append(Relation(CONSTRAINT, player.id, None, {"type": "cooldown", "ability": "dash"}))
        rels.append(Relation(DYNAMICS, player.id, None, {"speed": player.state.get("speed", 2.8)}))
        rels.append(Relation(EPISTEMIC, player.id, None, {"sense_radius": 200, "memory_duration": 120}))
    
    hostiles = [e for e in world.entities.values() if e.kind == "Hostile"]
    converted = [e for e in world.entities.values() if e.kind == "Converted"]
    passives = [e for e in world.entities.values() if e.kind == "Passive"]
    
    # Hostile relations
    for h in hostiles:
        rels.append(Relation(EPISTEMIC, h.id, None, {"sense_radius": 140, "memory_duration": 60}))
        rels.append(Relation(DYNAMICS, h.id, None, {"speed": h.state.get("speed", 1.3)}))
    
    # Converted relations (more aggressive sensing)
    for c in converted:
        rels.append(Relation(EPISTEMIC, c.id, None, {"sense_radius": 160, "memory_duration": 90}))
        rels.append(Relation(DYNAMICS, c.id, None, {"speed": c.state.get("speed", 1.5)}))
    
    # Passive relations
    for p in passives:
        rels.append(Relation(EPISTEMIC, p.id, None, {"sense_radius": 100, "memory_duration": 30}))
        rels.append(Relation(DYNAMICS, p.id, None, {"speed": p.state.get("speed", 0.9), "mode": "wander"}))
    
    world.relations = rels


def reset_world(world: World, width: int, height: int) -> None:
    """Reset to fresh state."""
    fresh = create_world(width, height)
    world.entities = fresh.entities
    world.relations = fresh.relations
    world.walls = fresh.walls
    world.tick = 0
    world.score = 0
    world.wave = 1
    world.difficulty = 1.0
    world.enemy_speed_boost = 0.0  # Reset accumulated speed boost
    world.game_over = False
    world.game_win = False
    world.events.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# UI / RENDERING
# ═══════════════════════════════════════════════════════════════════════════════
def draw(world: World, canvas: tk.Canvas) -> None:
    """Render the world state."""
    canvas.delete("all")
    
    # Draw walls
    for wall in world.walls:
        canvas.create_line(wall.x1, wall.y1, wall.x2, wall.y2, fill="gray", width=4)
    
    # Draw danger gradient for player (subtle red glow)
    player = world.entities.get("player")
    if player:
        danger = world.gco_report.get("influence_fields", {}).get("player_danger", 0)
        # We don't have it in gco_report, compute from geo context implicitly
        # Just use a simple calculation here
        hostile_count = sum(1 for e in world.entities.values() if e.kind in ("Hostile", "Converted"))
        if hostile_count > 0:
            # Draw faint danger indicator
            closest_dist = float('inf')
            for ent in world.entities.values():
                if ent.kind in ("Hostile", "Converted"):
                    d = compute_distance(player, ent)
                    closest_dist = min(closest_dist, d)
            if closest_dist < 150:
                alpha = int((1 - closest_dist / 150) * 80)
                danger_color = f"#ff{255-alpha:02x}{255-alpha:02x}"
                canvas.create_oval(
                    player.x - 25, player.y - 25, player.x + 25, player.y + 25,
                    fill="", outline=danger_color, width=2
                )
    
    # Draw entities
    for ent in world.entities.values():
        x, y = ent.x, ent.y
        size = 6 if ent.kind == "Food" else 8
        
        # Special rendering for player
        if ent.kind == "Player":
            # Shield indicator
            if ent.state.get("shield_active", False):
                canvas.create_oval(x - 12, y - 12, x + 12, y + 12, outline="cyan", width=2)
            # Invulnerability indicator
            if world.tick < ent.state.get("invulnerable_until", 0):
                canvas.create_oval(x - 14, y - 14, x + 14, y + 14, outline="white", width=1, dash=(2, 2))
            # Dashing trail
            if ent.state.get("dashing", False):
                canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="", outline="lightblue", width=2)
        
        # AI state indicator for hostiles - shows what they're thinking
        if ent.kind in ("Hostile", "Converted"):
            ai_state = ent.state.get("ai_state", AI_STATE_PATROL)
            alert = ent.state.get("alert_level", 0)
            
            # State icon and color
            state_indicators = {
                AI_STATE_PATROL: ("○", "gray"),       # Calm, patrolling
                AI_STATE_HUNT: ("◆", "red"),          # Direct pursuit
                AI_STATE_INTERCEPT: ("⟩", "orange"),  # Cutting off
                AI_STATE_FLANK: ("↗", "yellow"),      # Flanking
                AI_STATE_SEARCH: ("?", "cyan"),       # Searching
                AI_STATE_AMBUSH: ("◇", "magenta"),    # Waiting in ambush
            }
            icon, color = state_indicators.get(ai_state, ("○", "gray"))
            
            # Show state icon above entity
            if alert > 0.1 or ai_state != AI_STATE_PATROL:
                canvas.create_text(x, y - 14, text=icon, fill=color, font=("Helvetica", 10, "bold"))
            
            # Alert level indicator (exclamation when highly alert)
            if alert > 0.7:
                canvas.create_text(x + 8, y - 14, text="!", fill="yellow", font=("Helvetica", 8, "bold"))
        
        # Draw entity
        canvas.create_rectangle(x - size, y - size, x + size, y + size, fill=ent.color, outline="")
    
    # HUD
    if player:
        stamina = player.state.get("stamina", 0)
        max_stamina = player.state.get("max_stamina", 100)
        energy = player.state.get("energy", 0)
        max_energy = player.state.get("max_energy", 50)
        
        # Calculate average enemy speed for display
        enemies = [e for e in world.entities.values() if e.kind in ("Hostile", "Converted")]
        avg_enemy_speed = sum(e.state.get("speed", 1.3) for e in enemies) / max(1, len(enemies)) if enemies else 1.3
        speed_pct = int((avg_enemy_speed / 1.3) * 100)  # Base speed is 1.3
        
        # Score and wave
        canvas.create_text(10, 10, anchor="nw", fill="white",
                          text=f"Score: {world.score}/{world.goal}  Wave: {world.wave}  Tick: {world.tick}",
                          font=("Helvetica", 11, "bold"))
        
        # Enemy speed indicator (turns red as it increases)
        speed_color = "lime" if speed_pct <= 120 else ("yellow" if speed_pct <= 150 else "red")
        canvas.create_text(10, 55, anchor="nw", fill=speed_color,
                          text=f"Enemy Speed: {speed_pct}%", font=("Helvetica", 8))
        
        # Stamina bar
        bar_y = 30
        canvas.create_rectangle(10, bar_y, 110, bar_y + 8, fill="gray30", outline="")
        canvas.create_rectangle(10, bar_y, 10 + stamina, bar_y + 8, fill="lime", outline="")
        canvas.create_text(115, bar_y + 4, anchor="w", fill="lime", text="Stamina", font=("Helvetica", 8))
        
        # Energy bar
        bar_y = 42
        canvas.create_rectangle(10, bar_y, 60, bar_y + 8, fill="gray30", outline="")
        canvas.create_rectangle(10, bar_y, 10 + energy, bar_y + 8, fill="cyan", outline="")
        canvas.create_text(65, bar_y + 4, anchor="w", fill="cyan", text="Energy", font=("Helvetica", 8))
        
        # Shield indicator
        if player.state.get("shield_active", False):
            canvas.create_text(10, 67, anchor="nw", fill="cyan", text="[SHIELD]", font=("Helvetica", 9, "bold"))
        
        # Controls help
        canvas.create_text(world.width - 10, 10, anchor="ne", fill="gray",
                          text="Arrows: Move | SPACE: Dash | S: Shield", font=("Helvetica", 9))
    
    # Legend - entities
    legend_y = world.height - 70
    legend_items = [
        ("blue", "Player"), ("red", "Hostile"), ("purple", "Converted"),
        ("green", "Passive"), ("yellow", "Food"), ("gray", "Wall")
    ]
    for i, (color, name) in enumerate(legend_items):
        x = 10 + i * 80
        canvas.create_rectangle(x, legend_y, x + 10, legend_y + 10, fill=color, outline="")
        canvas.create_text(x + 15, legend_y + 5, anchor="w", fill="white", text=name, font=("Helvetica", 8))
    
    # Legend - AI states (shows what enemies are thinking)
    ai_legend_y = world.height - 50
    ai_states = [
        ("○", "gray", "Patrol"), ("◆", "red", "Hunt"), ("⟩", "orange", "Intercept"),
        ("↗", "yellow", "Flank"), ("?", "cyan", "Search"), ("◇", "magenta", "Ambush")
    ]
    canvas.create_text(10, ai_legend_y, anchor="nw", fill="gray", text="AI:", font=("Helvetica", 8))
    for i, (icon, color, name) in enumerate(ai_states):
        x = 35 + i * 70
        canvas.create_text(x, ai_legend_y + 5, text=icon, fill=color, font=("Helvetica", 9, "bold"))
        canvas.create_text(x + 10, ai_legend_y + 5, anchor="w", fill="gray", text=name, font=("Helvetica", 7))
    
    # Game over / win overlay
    if world.game_over:
        canvas.create_rectangle(0, 0, world.width, world.height, fill="black", stipple="gray50")
        canvas.create_text(world.width / 2, world.height / 2 - 15, fill="red",
                          text="GAME OVER", font=("Helvetica", 24, "bold"))
        canvas.create_text(world.width / 2, world.height / 2 + 15, fill="white",
                          text="Resetting...", font=("Helvetica", 12))
    
    if world.game_win:
        canvas.create_rectangle(0, 0, world.width, world.height, fill="black", stipple="gray50")
        canvas.create_text(world.width / 2, world.height / 2 - 15, fill="lime",
                          text="VICTORY!", font=("Helvetica", 24, "bold"))
        canvas.create_text(world.width / 2, world.height / 2 + 15, fill="white",
                          text=f"Final Score: {world.score} | Waves: {world.wave}", font=("Helvetica", 12))
    
    # Recent events log (bottom right)
    if world.events:
        events_text = "\n".join(world.events[-3:])
        canvas.create_text(world.width - 10, world.height - 70, anchor="se", fill="yellow",
                          text=events_text, font=("Helvetica", 8), justify="right")
    
    canvas.update()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    width, height = 700, 500
    world = create_world(width, height)
    
    root = tk.Tk()
    root.title("RPE Rule Engine Demo - Advanced Features")
    canvas = tk.Canvas(root, width=width, height=height, bg="#1a1a2e")
    canvas.pack()
    
    def on_key(event: tk.Event) -> None:
        player = world.entities.get("player")
        if not player or world.game_over or world.game_win:
            return
        
        if event.keysym == "Up":
            player.state["vy"] = -1
            player.state["vx"] = 0
        elif event.keysym == "Down":
            player.state["vy"] = 1
            player.state["vx"] = 0
        elif event.keysym == "Left":
            player.state["vx"] = -1
            player.state["vy"] = 0
        elif event.keysym == "Right":
            player.state["vx"] = 1
            player.state["vy"] = 0
        elif event.keysym == "space":
            player_dash(world)
        elif event.keysym.lower() == "s":
            player_shield(world)
    
    def on_key_release(event: tk.Event) -> None:
        player = world.entities.get("player")
        if not player:
            return
        if event.keysym in ("Up", "Down"):
            player.state["vy"] = 0
        if event.keysym in ("Left", "Right"):
            player.state["vx"] = 0
    
    root.bind("<KeyPress>", on_key)
    root.bind("<KeyRelease>", on_key_release)
    
    def loop() -> None:
        step(world)
        draw(world, canvas)
        
        if world.game_over:
            root.after(1500, lambda: reset_and_continue())
        elif world.game_win:
            root.after(2500, lambda: reset_and_continue())
        else:
            root.after(40, loop)
    
    def reset_and_continue():
        if world.game_over or world.game_win:
            world.game_over = False
            world.game_win = False
            reset_world(world, width, height)
        root.after(40, loop)
    
    root.after(40, loop)
    root.mainloop()


if __name__ == "__main__":
    main()
