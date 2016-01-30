import json
import sys

class table:
    """
    Represents a nicely printable table.
    
    Example usage:
    t = table(('heading A', 'heading B'))
    t.add_row((3, 5))
    print(t)
    """
    
    def __init__(self, headings):
        self.content = []
        for heading in headings:
            self.content.append([heading])
    
    def add_row(self, values):
        if (len(values) is not len(self.content)):
            raise ValueError('Length of table row must be equal to the number \
                of columns.')
            return
        for i, value in enumerate(values):
            self.content[i].append(value)
        
    def __repr__(self):
        widths = []
        for column in self.content:
            length = 0
            for value in column:
                if len(str(value)) > length:
                    length = len(str(value))
            widths.append(length)
        
        string = ""
        # Draw table
        for i in range(len(self.content[0])):
            string += '| '
            for j in range(len(self.content)):
                string += str(self.content[j][i]).ljust(widths[j]) + ' | '
            string += '\n'
            if i == 0:
                string += '|'
                for width in widths:
                    string += '-'*(width+2) + '|'
                string += ' \n'
        
        return string
        
def print_json(obj):
    print json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))

def progress_bar(value, max_value, width, fill_char='#', space_char='-'):
    """
    Create string such as [####-----].
    """
    value = min(max(value, 0), max_value)
    num_hashes = int(round(width*value/max_value))
    num_dashes = width-num_hashes
    return '[' + fill_char*num_hashes + space_char*num_dashes + ']'

def title(string, level):
    """
    Create title string. H1 and H2 (levels 1 and 2) are drawn with = and -
    below them. Lower levels are drawn with the appropriate number of #s before
    the title string.

    Usage:
    print title('Heading 1', 1)
    """
    if level==1:
        return string + '\n' + '='*len(string)
    if level==2:
        return string + '\n' + '-'*len(string)
    if level>2:
        return '#'*level + ' ' + string
    raise ValueError('Second argument to title() must be a positive integer')

