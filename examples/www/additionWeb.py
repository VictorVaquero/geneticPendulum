'''Prompt the user for two integers and display a web page with the sum.'''

def processInput(numStr1, numStr2):  # NEW
    '''Process input parameters and return the final page as a string.'''
    num1 = int(numStr1) # transform input to output data
    num2 = int(numStr2)
    total = num1+num2
    return fileToStr('additionTemplate.html').format(**locals())

def main(): # NEW
    numStr1 = input('Enter an integer: ')  # obtain input
    numStr2 = input('Enter another integer: ')  
    contents = processInput(numStr1, numStr2)   # process input into a page
    browseLocal(contents) # display page

def fileToStr(fileName): 
    """Return a string containing the contents of the named file."""
    fin = open(fileName); 
    contents = fin.read();  
    fin.close() 
    return contents

def strToFile(text, filename):
    """Write a file with the given name and the given text."""
    output = open(filename,"w")
    output.write(text)
    output.close()

def browseLocal(webpageText, filename='tempBrowseLocal.html'):
    '''Start your webbrowser on a local file containing the text
    with given filename.'''
    import webbrowser, os.path
    strToFile(webpageText, filename)
    webbrowser.open("file:///" + os.path.abspath(filename)) #elaborated for Mac

main()
