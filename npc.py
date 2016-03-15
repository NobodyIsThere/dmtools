import dmtools
import names
import random
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
            return_string += " - " + note + "\n"
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

def generate_notes(moral_alignment, law_alignment):
    data_path = dmtools.get_data_path()
    with open(data_path + "npcs/appearance.txt") as f:
        appearance = random.choice(f.readlines()).strip()
    with open(data_path + "npcs/mannerisms.txt") as f:
        mannerism = random.choice(f.readlines()).strip()
    with open(data_path + "npcs/interaction.txt") as f:
        interaction = random.choice(f.readlines()).strip()
    with open(data_path + "npcs/abilities.txt") as f:
        abilities = f.readlines()
        ability1 = random.choice(abilities)
        abilities.remove(ability1)
        ability1 = ability1.strip()
        ability2 = random.choice(abilities).strip()
    with open(data_path + "npcs/talents.txt") as f:
        talent = random.choice(f.readlines()).strip()
    with open(data_path + "npcs/ideals_"
              + alignment_to_string[moral_alignment] + ".txt") as f:
        moral_ideal = random.choice(f.readlines()).strip()
    with open(data_path + "npcs/ideals_"
              + alignment_to_string[law_alignment] + ".txt") as f:
        law_ideal = random.choice(f.readlines()).strip()
    with open(data_path + "npcs/bonds.txt") as f:
        bond = random.choice(f.readlines()).strip()
    with open(data_path + "npcs/flaws.txt") as f:
        flaw = random.choice(f.readlines()).strip()
    
    return [appearance,
            mannerism,
            interaction,
            ability1, ability2,
            talent,
            "Ideals: " + moral_ideal + ", " + law_ideal.lower(),
            "Bond: " + bond,
            "Flaw: " + flaw]

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
        npc.notes = generate_notes(npc.moral_alignment, npc.law_alignment)
        return npc

def generate_trade():
    return ""
