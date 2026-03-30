#!/usr/bin/env python3
"""
Earth2037 map coordinate conversion: tileID / VillageID / CityID ↔ (x, y)
Matches server Maps class logic. Include coords when displaying map.
"""

import math

# Main map mapId=1: Count=802, axes [-400,401] (matches live main map)
MAIN_COUNT_X = 802
MAIN_MAX = 401
MAIN_MIN = -400

# Small map mapId=2: 162×162, X/Y ∈ [-80, 81]
MINI_COUNT_X = 162
MINI_MAX = 81
MINI_MIN = -80


def _v_main(x):
    """Main map boundary wrap"""
    if x > MAIN_MAX:
        return x - MAIN_COUNT_X
    if x < MAIN_MIN:
        return x + MAIN_COUNT_X
    return x


def _v_mini(x):
    """Small map boundary wrap"""
    if x > MINI_MAX:
        return x - MINI_COUNT_X
    if x < MINI_MIN:
        return x + MINI_COUNT_X
    return x


def get_x(tile_id, mini=False):
    """tileID → X coord"""
    count = MINI_COUNT_X if mini else MAIN_COUNT_X
    max_val = MINI_MAX if mini else MAIN_MAX
    v_fn = _v_mini if mini else _v_main
    val = ((tile_id % count) + count) % count - max_val
    return v_fn(val)


def get_y(tile_id, mini=False):
    """tileID → Y coord"""
    x = get_x(tile_id, mini)
    count = MINI_COUNT_X if mini else MAIN_COUNT_X
    max_val = MINI_MAX if mini else MAIN_MAX
    v_fn = _v_mini if mini else _v_main
    val = (max_val + 1) - math.ceil((tile_id - x) / count)
    return v_fn(int(val))


def get_id(x, y, mini=False):
    """(x, y) → tileID"""
    count = MINI_COUNT_X if mini else MAIN_COUNT_X
    max_val = MINI_MAX if mini else MAIN_MAX
    v_fn = _v_mini if mini else _v_main
    return (max_val + 1 - v_fn(y)) * count + v_fn(x) - max_val


def get_xy(tile_id, mini=False):
    """tileID → (x, y)"""
    return get_x(tile_id, mini), get_y(tile_id, mini)


def format_xy(tile_id, mini=False):
    """tileID → display string '(x,y)'"""
    x, y = get_xy(tile_id, mini)
    return f"({x},{y})"


def ascii_map_window(cx, cy, radius=3, mini=False):
    """
    Text wireframe: rows = y (top = larger y), columns = x.
    '@' = center, '·' = neighbors. Same (x,y) / tileID as server Maps.
    """
    xs = list(range(cx - radius, cx + radius + 1))
    ys = list(range(cy + radius, cy - radius - 1, -1))
    cw = 6
    pad = "      "
    header_pad = " " * len(f"y={0:>4}|")
    lines = []
    tag = "mini map 162×162" if mini else "main map 802×802 (mapId=1)"
    lines.append(f"# Earth2037 — {tag}")
    lines.append(f"# window: center=({cx},{cy})  radius={radius}  |  +x east")
    lines.append("")
    lines.append(header_pad + "".join(f"{x:^{cw}}|" for x in xs))
    row_sep = pad + "+" + "+".join("-" * cw for _ in xs) + "+"
    lines.append(row_sep)
    for y in ys:
        row = f"y={y:>4}|"
        for x in xs:
            ch = "@" if (x == cx and y == cy) else "·"
            row += f"{ch:^{cw}}|"
        lines.append(row)
        lines.append(row_sep)
    tid = get_id(cx, cy, mini)
    lines.append("")
    lines.append(f"# center (x,y) = ({cx},{cy})")
    lines.append(f"# tileID={tid} (internal only; do not emphasize to players)")
    lines.append("# legend: @ = center; · = neighbors")
    return "\n".join(lines)


def ascii_map_from_tile_id(tile_id, radius=3, mini=False):
    """ASCII window centered on tile_id's (x,y)."""
    x, y = get_xy(tile_id, mini)
    return ascii_map_window(x, y, radius=radius, mini=mini)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage:")
        print("  maps_util.py <tileID> [--mini]")
        print("  maps_util.py --id <x> <y> [--mini]")
        print("  maps_util.py --ascii <cx> <cy> [radius] [--mini]   # ASCII wireframe around (cx,cy)")
        print("  maps_util.py --ascii-tile <tileID> [radius] [--mini]")
        print("  tileID/VillageID/CityID: same value → (x,y)")
        sys.exit(1)
    args = sys.argv[1:]
    mini = "--mini" in args
    if "--mini" in args:
        args.remove("--mini")
    if args[0] == "--ascii" and len(args) >= 3:
        cx, cy = int(args[1]), int(args[2])
        r = 3
        if len(args) >= 4:
            try:
                r = int(args[3])
            except ValueError:
                r = 3
        print(ascii_map_window(cx, cy, radius=r, mini=mini))
    elif args[0] == "--ascii-tile" and len(args) >= 2:
        tid = int(args[1])
        r = 3
        if len(args) >= 3:
            try:
                r = int(args[2])
            except ValueError:
                r = 3
        print(ascii_map_from_tile_id(tid, radius=r, mini=mini))
    elif args[0] == "--id" and len(args) >= 3:
        x, y = int(args[1]), int(args[2])
        print(get_id(x, y, mini))
    else:
        tid = int(args[0])
        x, y = get_xy(tid, mini)
        print(f"(x,y)=({x},{y})  # tileID={tid} (internal)")
