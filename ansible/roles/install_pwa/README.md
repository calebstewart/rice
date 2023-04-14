# Role: `install_pwa`
This Ansible role is self-contained to install a [PWA] for a specific Brave profile.
This role will not *technically* install the PWA with the normal method inside of
Chromium browsers (e.g. the little "Install" button in the address bar), however it
will do the effective equivalent.

The role first downloads the PWA manifest, and saves it to
`~/.local/share/webapps/{{app.nam}}`. Next, it loads the manifest into Ansible as
a fact, and downloads the last icon in the icon list (normally the largest). It will
use this icon and the `xdg-icon-resource` command to install `32`, `64`, `128`, `256`
and `512` versions of the icon into the local user's theme. Next, the role will
install a Desktop Entry which runs brave with a command like:

``` sh
brave-browser --profile-directory="{{ app.profile }}" --app="{{ manifest.start_url }}"
```

The desktop entry is namespaced to the profile used, so the same app can be installed
for multiple profiles. Similarly, the installed icons are namespaced for the profile
name as well.

## Arguments

A variable named `app` must be defined with the following structure:

``` yaml
app:
    name: "messages.google.com"
    manifest_url: "https://messages.google.com/web/manifest.json"
    profile: "Personal"
```

This will create the following files:

- `~/.local/share/webapps/messages.google.com/Personal/manifest.json`
- `~/.local/share/webapps/messages.google.com/Personal/icon.png`
- `~/.local/share/webapps/messages.google.com/Personal/launcher.desktop`
- `~/.local/share/icons/{theme}/{size}/apps/brave-webapps-Personal-messages.google.com.png`
- `~/.local/share/applications/brave-webapps-Personal-messages.google.com.desktop`

## Examples

``` yaml
- name: "Install Brave Progressive Web Apps"
  include_role:
    name: "install_pwa"
  vars:
    app: "{{ item }}"
  loop:
    - name: "messages.google.com"
      manifest_url: "https://messages.google.com/web/manifest.json"
      profile: "Personal"
    - name: "spotify.com"
      manifest_url: "https://open.spotifycdn.com/cdn/generated/manifest-web-player.3a6f5207.json"
      profile: "Personal"
    - name: "spotify.com"
      manifest_url: "https://open.spotifycdn.com/cdn/generated/manifest-web-player.3a6f5207.json"
      profile: "AnotherProfile"
```

[PWA]: https://en.wikipedia.org/wiki/Progressive_web_app
