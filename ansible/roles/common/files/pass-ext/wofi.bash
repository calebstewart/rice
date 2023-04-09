# Name: .extensions/wofi.bash
# Description: Password Store Wofi Menu Extension
# Author: Caleb Stewart <caleb.stewart94@gmail.com>
# License: MIT

# Find all password items
ITEMS=$(find "$PREFIX" -name '*.gpg' | sed 's|'"$PREFIX"'/||g;s|\.gpg$||g' | sort)

selected=$(echo "$ITEMS" | wofi -d)

# Nothing selected
[ "$?" -ne 0 ] || [ -z "$selected" ] && exit

# Copy it bby!
message=$(cmd_show --clip "$selected")
if [ "$?" -ne 0 ]; then
  notify-send "Password Store" "Copy failed."
else
  notify-send "Password Store" "$message"
fi
