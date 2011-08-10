def every_pair(args):
    pairs = []
    for i in range(0, len(args)):
        for j in range(i + 1, len(args)):
            pairs.append((args[i], args[j]))
    return pairs