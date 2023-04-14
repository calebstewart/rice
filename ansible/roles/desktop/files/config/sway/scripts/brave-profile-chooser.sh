#!/bin/sh
# Name: brave-profile-chooser.sh
# Description: Use wofi to prompt for which profile to use for a URL.
#              This is useful to pair with a desktop entry, and use it
#              as your default browser. Then, you can click a link and
#              select a profile easier.
# Author: Caleb Stewart <caleb.stewart94@gmail.com>
# License: MIT

if [ -z "$BRAVE" ]; then
    BRAVE=$(which brave 2>/dev/null)
fi

if [ -z "$BRAVE" ]; then
    BRAVE=$(which brave-browser 2>/dev/null)
fi

# Grab a list of profile cache details
PROFILE_CACHE=$(jq '.profile.info_cache | to_entries[]' <"$HOME/.config/BraveSoftware/Brave-Browser/Local State")

# Extract just the profile names
PROFILE_NAMES=$(echo "$PROFILE_CACHE" | jq -s -r '.[].value.name')

# Ask the user which profile to use
SELECTED=$(echo "$PROFILE_NAMES" | wofi --show dmenu --prompt "Select a Profile")

# Nothing selected
if [ -z "$SELECTED" ]; then
    exit
fi

# Translate the profile name back to the internal profile name (because chrome is dumb)
PROFILE_NAME=$(echo "$PROFILE_CACHE" | jq -s -r '.[] | select(.value.name == "'"$SELECTED"'") | .key')

# Launch chrome in the correct profile with the same arguments
exec "$BRAVE" --profile-directory="$PROFILE_NAME" $@
