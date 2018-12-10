'''Skeleton for regular Python programs generating a web page with a template.
'''

def main(): 
    ## get data from user's keyboard
    # pythonVariable = input(yourPrompt) # for each variable
    ## ...
    contents = processInput(inputVariables) # REPLACE inputVariables with yours
    browseLocal(contents) 

def processInput(inputVariables):  # REPLACE inputVariables with yours
    '''Process input parameters and return the final page as a string.'''
    ## process input, generate output variables ...
    ## ...
    return fileToStr('YOUR_CHOICETemplate.html').format(**locals())
    ## Change YOUR_CHOICE to your chosen name; remember to create the Template!
    ## When this test program works, copy processInput into your CGI script.

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
