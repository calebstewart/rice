#!/usr/bin/env python3
import subprocess
import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Move the focused container to another workspace on the same output"
    )
    parser.add_argument(
        "workspace", type=int, help="Workspace number on the current output"
    )
    args = parser.parse_args()

    outputs = json.loads(
        subprocess.run(
            ["swaymsg", "-t", "get_outputs"], stdout=subprocess.PIPE, check=True
        ).stdout
    )
    outputs = sorted(outputs, key=lambda output: output["rect"]["x"])

    for idx, output in enumerate(outputs):
        # Ignore unfocused outputs
        if not output["focused"]:
            continue

        subprocess.run(
            [
                "swaymsg",
                "move",
                "container",
                "to",
                "workspace",
                f"{idx+1}-{args.workspace}",
            ],
            stdout=subprocess.DEVNULL,
            check=True,
        )
        break
    else:
        raise Exception("could not find focused output")
