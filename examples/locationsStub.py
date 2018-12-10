'''Exercise to complete printLocations as described below.
Create file locations.py.'''

def printLocations(s, target):
    '''s is a string to search through, and target is the substring to look for.
    Print each index where the target starts.
    For example:
    >>> printLocations('Here, there, everywhere!', 'ere')
    1
    8
    20
    '''

    repetitions = s.count(target)
    #  ?? add initialization
    for i in range(repetitions):
        #  ?? add loop body lines
       

def main():
    phrase = 'Here, there, everywhere!'
    print('Phrase:', phrase)
    for target in ['ere', 'er', 'e', 'eh', 'zx']:
        print('finding:', target)
        printLocations(phrase, target)
    print('All done!')

main()
