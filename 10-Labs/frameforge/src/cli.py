"""FrameForge CLI — build a storyboard from a character sheet + shot list.

Usage:
    python3 -m frameforge.cli lock <name> <sheet.txt> <out.json>
    python3 -m frameforge.cli build <title> <lock.json> <shots.json> <out_dir>
    python3 -m frameforge.cli compile <frame_dir> <out.mp4> [--title T]
"""

from __future__ import annotations

import argparse
import json
import sys

from .character import CharacterLock, lock_character, load_lock
from .engine import Shot, build_storyboard, write_storyboard
from .compile import compile_video


def _cmd_lock(args: argparse.Namespace) -> int:
    lock = lock_character(args.name, open(args.sheet, encoding="utf-8").read())
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(lock.to_json())
    print(f"Locked '{lock.name}' -> {args.out} (seed {lock.seed}, palette {len(lock.palette)} colors)")
    return 0


def _cmd_build(args: argparse.Namespace) -> int:
    lock = load_lock(args.lock)
    shots_data = json.load(open(args.shots, encoding="utf-8"))
    shots = [Shot(**s) for s in shots_data]
    sb = build_storyboard(args.title, lock, shots)
    written = write_storyboard(sb, args.out_dir)
    print(f"Storyboard '{sb.title}': {len(sb.frames)} frames -> {args.out_dir}")
    for w in written:
        print(f"  wrote {w}")
    return 0


def _cmd_compile(args: argparse.Namespace) -> int:
    out = compile_video(args.frame_dir, args.out, title=args.title)
    print(f"Compiled video -> {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="frameforge")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("lock", help="lock a character from a reference sheet")
    pl.add_argument("name")
    pl.add_argument("sheet")
    pl.add_argument("out")
    pl.set_defaults(fn=_cmd_lock)

    pb = sub.add_parser("build", help="build a storyboard")
    pb.add_argument("title")
    pb.add_argument("lock")
    pb.add_argument("shots")
    pb.add_argument("out_dir")
    pb.set_defaults(fn=_cmd_build)

    pc = sub.add_parser("compile", help="compile frames to video")
    pc.add_argument("frame_dir")
    pc.add_argument("out")
    pc.add_argument("--title", default="FrameForge Storyboard")
    pc.set_defaults(fn=_cmd_compile)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
