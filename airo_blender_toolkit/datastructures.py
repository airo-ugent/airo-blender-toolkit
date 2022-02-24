import bisect


class InterpolatingDict(dict):
    def __getitem__(self, key):
        sorted_keys = sorted(self)
        index = bisect.bisect_left(sorted_keys, key)

        if index == 0:
            return dict.__getitem__(self, sorted_keys[0])

        if index == len(self):
            return dict.__getitem__(self, sorted_keys[-1])

        key_low = sorted_keys[index - 1]
        key_high = sorted_keys[index]
        key_range = key_high - key_low
        fraction_low = (key - key_low) / key_range
        fraction_high = (key_high - key) / key_range
        value_low = dict.__getitem__(self, key_low)
        value_high = dict.__getitem__(self, key_high)
        value = fraction_low * value_low + fraction_high * value_high
        return value
