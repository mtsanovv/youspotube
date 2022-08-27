class Tools:
    def time_to_seconds(time):
        return sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(time.split(':'))))

    def get_track_string(track_name, track_artists, beautify=False):
        track_artists_title_separator = ' '
        track_artists_separator = ' '

        if beautify:
            track_artists_title_separator = ' - '
            track_artists_separator = ', '

        artists_string = track_artists[0]
        if len(track_artists) > 1:
            artists_string = track_artists_separator.join(track_artists)

        return track_artists_title_separator.join([
            artists_string,
            track_name
        ])
