import roll

def parse(string):
    args = string.split(" and ")
    npcs = []
    for group in args:
        parts = group.split(" ")
        name = "npc_" + parts[-1]
        number = roll.parse(parts[0]) if len(parts) > 1 else 1
        if name[-1] is 's':
            name = name[:-1]
        npcs.append((name, number))
    return npcs