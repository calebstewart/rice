#/bin/sh

output=$(looking-glass-client 2>&1)

if [ "$?" -ne 0 ]; then
    error_info=$(echo "$output" | grep "Error: " | head -n1 | cut -d':' -f1 | trim)
    notify-send "Looking Glass" "$error_info" \
        --icon "looking-glass" \
        --app-name "looking-glass" \
        --urgency "critical"
fi
