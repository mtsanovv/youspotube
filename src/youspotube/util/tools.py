class Tools:
    def time_to_seconds(time):
        return sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(time.split(':'))))
