#!/usr/bin/env python3
import json
import subprocess

def read_state_file() -> tuple[str | None, str]:
    """ Read /tmp/gammastep-state, which should exist if the gammastep hook is
    installed properly. """

    try:
        with open("/tmp/gammastep-state") as filp:
            state = filp.read().strip()
            if state == "none":
                return None, "off"
            else:
                return state, "on"
    except (FileNotFoundError, PermissionError):
        return None, "on"

def query_state() -> str | None:
    """ Execute 'gammastep -p' to query the gammastep state. This is innacurate
    since it does not report when it has been disabled through SIGUSR1. """

    try:
        proc = subprocess.run(
            ["gammastep", "-p"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            check=True,
            text=True,
        )
        output = proc.stderr.strip()
        for line in output.split("\n"):
            if line.startswith("Notice: Period: "):
                return line.split("Notice: Period: ")[1].lower()
        return None
    except subprocess.CalledProcessError:
        return None

if __name__ == "__main__":

    state, clazz = read_state_file()
    if state is None:
        state = query_state()

    state_map = {
        "night": "\uf186",
        "day": "\uf185",
    }

    if clazz == "on":
        alt = "Gammastep on"
    else:
        alt = "Gammastep off"

    print(
        json.dumps(
            {
                "text": " " + state_map.get(state, "\uf185") + " ",
                "class": clazz,
                "alt": alt,
                "tooltip": alt,
            }
        )
    )
