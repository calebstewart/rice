#!/usr/bin/env python3
import subprocess
import argparse
import json

if __name__ == "__main__":

    # Retrieve all outputs and sort by their X-position
    outputs = json.loads(
        subprocess.run(
            ["swaymsg", "-t", "get_outputs"], stdout=subprocess.PIPE, check=True
        ).stdout
    )
    outputs = sorted(outputs, key=lambda output: output["rect"]["x"])

    builtin_index = 0
    for idx, output in enumerate(outputs):
        if output["name"].lower() == "edp-1":
            builtin_index = idx
            break

    # if builtin_index == -1:
    #     raise Exception("could not find builtin output")

    # Ensure any new workspaces adhere to the naming-output scheme
    for idx, output in enumerate(outputs):
        for ws in range(1, 11):
            subprocess.run(
                [
                    "swaymsg",
                    "workspace",
                    f"{idx+1}-{ws}",
                    "output",
                    output["name"],
                    "eDP-1",
                ],
                stdout=subprocess.DEVNULL,
                check=True,
            )

    workspaces = json.loads(
        subprocess.run(
            ["swaymsg", "-t", "get_workspaces"], stdout=subprocess.PIPE, check=True
        ).stdout
    )
    focused = None
    for workspace in workspaces:
        if workspace["focused"]:
            focused = workspace["name"]

        if "-" not in workspace["name"]:
            output_index = builtin_index
        else:
            output_index = int(workspace["name"].split("-")[0]) - 1

        # Workspaces for outputs that aren't connected are ignored
        if output_index >= len(outputs):
            continue

        # Don't try to move workspaces already in the right place
        if outputs[output_index]["name"] == workspace["output"]:
            continue

        # Move to the workspace
        subprocess.run(
            ["swaymsg", "workspace", workspace["name"]],
            stdout=subprocess.DEVNULL,
            check=True,
        )

        # Move the workspace to the correct output
        subprocess.run(
            [
                "swaymsg",
                "move",
                "workspace",
                "to",
                "output",
                outputs[output_index]["name"],
            ],
            stdout=subprocess.DEVNULL,
            check=True,
        )

    if focused is not None:
        # Move back to old focused workspace
        subprocess.run(
            ["swaymsg", "workspace", focused], stdout=subprocess.DEVNULL, check=True
        )
