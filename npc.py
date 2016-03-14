import names
import roll

# Constants
UNALIGNED = 0
CHAOTIC = 1
EVIL = 2
GOOD = 3
LAWFUL = 4
NEUTRAL = 5

alignment_to_string = \
{
    UNALIGNED: "",
    EVIL: "evil",
    NEUTRAL: "neutral",
    GOOD: "good",
    CHAOTIC: "chaotic",
    LAWFUL: "lawful"
}

FEMALE = 1
MALE = 2

class NPC(object):
    moral_alignment = 0
    law_alignment = 0
    name = "Unnamed"
    race = "unknown"
    notes = []
    sex = 0
    trade = ""
    def __init__(self):
        super(NPC, self).__init__()
    def alignment(self):
        if self.moral_alignment == UNALIGNED \
           and self.law_alignment == UNALIGNED:
            return "unaligned"
        else:
            return alignment_to_string[self.law_alignment] + " " + \
                   alignment_to_string[self.moral_alignment]
    def description(self):
        return "%s:\n%s %s %s\n%s\n%s"%(
            self.name, self.sex_str().title(), self.race.title(), self.trade,
            self.alignment().title(), self.notes_str())
    def notes_str(self):
        return_string = ""
        for note in self.notes:
            return_string.append(" - " + note + "\n")
        return return_string
    def sex_str(self):
        if self.sex == 1:
            return "female"
        elif self.sex == 2:
            return "male"
        return ""

def generate_name(race):
    race = race.lower()
    if race == "half-elf":
        race = "elf" if roll.parse("d2") == 1 else "human"
    elif "orc" in race:
        race = "orc" if roll.parse("d2") == 1 else "human"
    elif race == "tiefling" and roll.parse("d2") == 2:
        race = "human"
    if roll.parse("d4") < 4:
        return names.generate_name(race) + " " + names.generate_name(race)
    return names.generate_name(race)

def generate_notes():
    return []

def generate_npc(string=""):
        npc = NPC()
        law = roll.parse("d3")
        if law == 1:
            npc.law_alignment = LAWFUL
        else:
            npc.law_alignment = CHAOTIC if law == 2 else NEUTRAL
        moral = roll.parse("d3")
        if moral == 1:
            npc.moral_alignment = GOOD
        else:
            npc.moral_alignment = EVIL if moral == 2 else NEUTRAL
        npc.sex = roll.parse("d2")
        race = roll.parse("d20")
        if race < 15:
            npc.race = "Human"
        elif race < 17:
            npc.race = "Dwarf"
        elif race == 17:
            npc.race = "Halfling"
        elif race == 18:
            npc.race = "Gnome"
        elif race == 19:
            npc.race = "Elf"
        else:
            race = roll.parse("d10")
            if race < 7:
                npc.race = "Half-Elf"
            elif race < 9:
                npc.race = "Half-Orc"
            elif race == 9:
                npc.race = "Dragonborn"
            else:
                npc.race = "Tiefling"
        npc.name = generate_name(npc.race)
        npc.trade = generate_trade()
        npc.notes = generate_notes()
        return npc

def generate_trade():
    return ""
