#!/usr/bin/env python

import cmd
import encounter
import json
import names
import npc
import printing
import roll

def get_data_path():
    try:
        with open("data_path.config", 'r') as f:
            data_path = f.readline()
            if data_path.endswith('\n'):
                data_path = data_path[:-1]
            return data_path
    except IOError:
        with open("data_path.config", 'w') as f:
            f.write("data/")
        return "data/"

class DMTools(cmd.Cmd):
    prompt = "\ndmtools > "
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.data_path = get_data_path()
        self.active_entities = {"encounter":self.load_json("encounter"), "notes":[]}
        self.previous = None
        self.current_id = 0
                
    def do_active(self, string):
        printing.print_json(self.active_entities)

    def do_describe(self, string):
        entity = self.load(string)
        if "description" in entity:
            print entity["description"]
            if "next" in entity:
                print "Next: %s"%entity["next"]
            self.previous = entity

    def do_d(self, string):
        self.do_describe(string)
        
    def do_encounter(self, string):
        npcs = encounter.parse(string)
        for group in npcs:
            for i in range(group[1]):
                entity = self.load_json(group[0])
                entity["key"] = self.get_next_id()
                entity["hp"] = roll.parse(entity["hp"])
                self.active_entities["encounter"].append(entity)
        self.do_status("")

    def do_forget(self, string):
        self.active_entities = {"encounter":[], "notes":[]}
        
    def get_next_id(self):
        self.current_id += 1
        return self.current_id
        
    def do_info(self, string):
        entity = self.load(string)
        printing.print_json(entity)

    def load(self, string):
        if string in self.active_entities:
            return self.active_entities[string]
        else:
            for npc in self.active_entities["encounter"]:
                if str(npc["key"]) == str(string):
                    return npc
            entity = self.load_json(string)
        self.active_entities[string] = entity
        return self.active_entities[string]
        
    def load_json(self, string):
        try:
            with open("%s%s.json"%(self.data_path, string), 'r') as f:
                    entity = json.load(f)
        except IOError:
            print "Couldn't find %s in %s"%(string, self.data_path)
            entity = {}
        return entity
        
    def do_next(self, string):
        if self.previous and "next" in self.previous:
            self.do_describe(self.previous["next"])
            
    def do_n(self, string):
        self.do_next(string)
        
    def do_name(self, string):
        name = names.generate_name(string)
        while len(name) < 3:
            name = names.generate_name(string)
        print name

    def do_note(self, string):
        self.active_entities["notes"].append(string)
        
    def do_npc(self, string):
        n = npc.generate_npc(string=string)
        print n.description()
            
    def do_previous(self, string):
        if self.previous:
            print self.previous["description"]
            
    def do_p(self, string):
        self.do_previous(string)

    def do_roll(self, string):
        _,_,_,_, result = roll.parse(string, value_only=False)
        print result

    def do_save(self, string):
        if len(string) > 0:
            if string in self.active_entities:
                entities_to_save = [string]
            else:
                print "%s is not an active entity!"%string
                return
        else:
            entities_to_save = self.active_entities
        for key in entities_to_save:
            with open("%s%s.json"%(self.data_path, key), 'w') as f:
                json.dump(self.active_entities[key], f, sort_keys=True,
                    indent=4, separators=(',', ': '))

    def do_set(self, string):
        name, property, value = string.split(" ", 2)
        entity = self.load(name)
        if value.startswith("--") or value.startswith("++"):
            mod = int(value[2:])
            entity[property] = int(entity[property]) - mod \
                if value.startswith("--") else int(entity[property]) + mod
        else:
            entity[property] = value
        
    def do_status(self, string):
        status_table = printing.table(
            ["key", "Name", "HP", "AC", "Attack", "Damage"])
        for npc in self.active_entities["encounter"]:
            status_table.add_row(
                [npc["key"], npc["name"], npc["hp"], npc["ac"], npc["attack"],
                    npc["damage"]])
        print status_table

    def do_treasure(self, string):
        num, cr = string.split()
        amount = 0
        denom = "gp"
        cr = int(cr)
        num = int(num)
        if cr == 0:
            for i in range(num):
                amount += roll.parse("1d10")
                denom = "cp"
        elif cr < 5:
            result = roll.parse("d100")
            for i in range(num):
                if result < 31:
                    amount += roll.parse("5d6")
                    denom = "cp"
                elif result < 61:
                    amount += roll.parse("4d6")
                    denom = "sp"
                elif result < 71:
                    amount += roll.parse("3d6")*10
                    denom = "sp"
                elif result < 96:
                    amount += roll.parse("3d6")
                    denom = "gp"
                else:
                    amount += roll.parse("1d6")*10
                    denom = "gp"
        print "%i %s"%(amount, denom)

    def do_exit(self, string):
        return True

    def do_sexit(self, string):
        self.do_save(string)
        return True

    def do_EOF(self, string):
        return True

if __name__ == '__main__':
    DMTools().cmdloop()


