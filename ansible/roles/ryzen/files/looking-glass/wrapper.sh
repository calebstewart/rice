#/bin/sh

output=$(looking-glass-client 2>&1)

if [ "$?" -ne 0 ]; then
    error_info=$(echo "$output" | grep "Error: " | head -n1 | cut -d':' -f2 | awk '{$1=$1};1')
    notify-send "Looking Glass" "$error_info" \
        --icon "$HOME/.local/share/icons/looking-glass.png" \
        --app-name "looking-glass"
fi
