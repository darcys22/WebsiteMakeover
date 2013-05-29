import string, os, sys, getopt, re, htmltotext, traceback
from xml.dom import minidom


__author__ = 'Luis Rei <luis.rei@gmail.com>'
__homepage__ = 'http://luisrei.com'
__version__ = '1.0'
__date__ = '2008/03/23'


def convert(infile, outdir, authorDirs, categoryDirs):
    """Convert Wordpress Export File to multiple html files.
    
    Keyword arguments:
    infile -- the location of the Wordpress Export File
    outdir -- the directory where the files will be created
    authorDirs -- if true, create different directories for each author
    categoryDirs -- if true, create directories for each category
    
    """
    
    
    # First we parse the XML file into a list of posts.
    # Each post is a dictionary
    
    dom = minidom.parse(infile) ## dom = Document Object Model and parse simple returns it as a Document Object

    blog = [] # list that will contain all posts

    for node in dom.getElementsByTagName('item'):
    	post = dict()
	
	try:
	    	post["title"] = node.getElementsByTagName('title')[0].firstChild.data
	    	post["date"] = node.getElementsByTagName('wp:post_date')[0].firstChild.data
		post["date"]= post["date"].split()[0]
	    	##post["author"] = node.getElementsByTagName('dc:creator')[0].firstChild.data
	    	##post["id"] = node.getElementsByTagName('wp:post_id')[0].firstChild.data
	    	
	    	if node.getElementsByTagName('content:encoded')[0].firstChild != None:
	    	    post["text"] = node.getElementsByTagName(
	    	                    'content:encoded')[0].firstChild.data
	    	else:
	    	    post["text"] = ""
	except Exception, err:
		print traceback.format_exc()
    	
    	# wp:attachment_url could be use to download attachments

    	# Get the categories
    	##tempCategories = []
    	##for subnode in node.getElementsByTagName('category'):
    	##	 tempCategories.append(subnode.getAttribute('nicename'))
    	##categories = [x for x in tempCategories if x != '']
    	##post["categories"] = categories 

    	# Add post to the list of all posts
    	blog.append(post)
    	
    
    # Then we create the directories and HTML files from the list of posts.
    
    # The "base" directory
    outdir += "/wordpress/"
    if os.path.exists(outdir) == False:
        os.makedirs(outdir)
    os.chdir(outdir)
    
    for post in blog:
        # The "category" directories
        path = ""
        if authorDirs == True:
            path += post["author"].encode('utf-8') + "/"
        
        # This creates a path for the file in the format
        # category1/category2/category3/file. Note that the category list was
        # sorted.
        
        if categoryDirs == True:
            if (post["categories"] != None):
                path += string.join(post["categories"],"/")

        if os.path.exists(path) == False and path != "":
            os.makedirs(path)
        
        # And finally the file itself
	try:
		path = outdir + path
		title = post["title"]
		re.sub(r'([^\s])\s([^\s])', r'\1_\2',title)
		title.encode('utf-8')
		filename = path + "/" + post["date"] + ' - ' + title \
		            + '.md'
		
		f = open(filename, 'w')
	

		## Add the header that Benjen wants
		f.write("title: "+ post["title"].encode('utf-8') + "\n" + "date: " + post["date"].encode('utf-8') + "\n")

		##For consistency make it all HTML before changing back to markup
		##post["date"].encode('ascii','ignore')		
		post["text"] = post["text"].replace("\n", "<br/>")

		## Format the text into markdown using htmltotext 
		# Convert the unicode object to a string that can be written to a file
		# with the proper encoding (UTF-8)
		text = htmltotext.HTML2Text() 
		text.body_width = 0
		##print type (post["text"])
		##print post["text"]    
		
		f.write(text.handle(post["text"].encode('ascii','ignore')))
		
		f.close()
	except Exception, err:
		print traceback.format_exc()

def usage(pname):
    """Displays usage information
    
    keyword arguments:
    pname -- program name (e.g. obtained as argv[0])
    
    """
    
    
    print """python %s [-hac] [-o outdir] infile
    Converts a Wordpress Export File to multiple html files.
    
    Options:
        -h,--help\tDisplays this information.
        -a,--authors\tCreate different directories for each author.
        -c,--categories\tCreate directory structure from post categories.
        -o,--outdir\tSpecify a directory for the output.
        
    Example:
    python %s -c -o ~/TEMP ~/wordpress.2008-03-20.xml
        """ % (pname, pname)


def main(argv):
    outdir = ""
    authors = False
    categories = False
	
    try:
		opts, args = getopt.getopt(
		    argv[1:], "ha:o:c", ["help", "authors", "outdir", "categories"])	
    except getopt.GetoptError, err:
		print str(err)
		usage(argv[0])
		sys.exit(2)
	
    for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage(argv[0])
			sys.exit()
		elif opt in ("-a", "--authors"):
			authors = True
		elif opt in ("-c", "--categories"):
		    categories = True
		elif opt in ("-o", "--outdir"):
		    outdir = arg
		
    infile = "".join(args)
	
    if infile == "":
	    print "Error: Missing Argument: missing wordpress export file."
	    usage(argv[0])
	    sys.exit(3)
	
    if outdir == "":
	    # Use the current directory
	    outdir = os.getcwd()
	
    convert(infile, outdir, authors, categories)
	

if __name__ == "__main__":
	main(sys.argv)
