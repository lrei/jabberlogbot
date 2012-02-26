#!/usr/bin/python

# JabberLogBot: A simple jabber logging bot
# Copyright (c) 2007-2012 Luis Rei <me@luisrei.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of theCID GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Homepage: http://luisrei.com

import sys, getopt, re, MySQLdb
from pythonutils import ConfigObj
from jabberbot import JabberBot


__author__ = 'Luis Rei <me@luisrei.com>'
__homepage__ = 'http://luisrei.com'
__version__ = '0.3'
__date__ = '2008/05/17'
__year__ = '2008'


class JabberLogBot(JabberBot):
    def __init__(self, configFile, create=False, verbose=False):
        
        self.config = ConfigObj(configFile)

        JabberBot.__init__(self, self.config['JABBER']['user'],
                           self.config['JABBER']['passwd'])
        
        try:
            self.db = MySQLdb.connect(host=self.config['MYSQL']['host'],
                                      user=self.config['MYSQL']['user'],
                                      passwd=self.config['MYSQL']['passwd'],
                                      db=self.config['MYSQL']['dbname'],
                                      use_unicode=True, charset = "utf8")

        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            return None
        
        if create == True:
            self.createTable()
        
        if verbose == True:
            self.verbose = True
        else:
            self.verbose = False
               
    
    def createTable(self):
        """Creates the tables necessary in the database"""

        cur = self.db.cursor()
        
        cur.execute('''DROP TABLE IF EXISTS logs''')
        try:         
            cur.execute('''CREATE TABLE logs
                    (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    entry_date TIMESTAMP, user VARCHAR(128),
                    entry TEXT character set utf8 default NULL)''')  
        except MySQLdb.Error, e:
            print "Logs: Error %d: %s" % (e.args[0], e.args[1])
            print "Warning: program may not run correctly."
        
        
        cur.execute('''DROP TABLE IF EXISTS tags''')
        try:
            cur.execute('''CREATE TABLE tags
                    (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    postid INTEGER, tag VARCHAR(32)
                    character set utf8 default NULL)''')
        except MySQLdb.Error, e:
            print "Tags: Error %d: %s" % (e.args[0], e.args[1])
            print "Warning: program may not run correctly." 
        
        cur.execute('''DROP TABLE IF EXISTS replies''')
        try:              
            cur.execute('''CREATE TABLE replies
                    (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    postId INTEGER, reply VARCHAR(32)
                    character set utf8 default NULL)''')   
        except MySQLdb.Error, e:
            print "Replies: Error %d: %s" % (e.args[0], e.args[1])
            print "Warning: program may not run correctly."
        
        try:                
            # TRIGGER - delete tags and replies if log is deleted
            cur.execute('''CREATE TRIGGER delTagRep
                        AFTER DELETE ON logs
                        FOR EACH ROW
                        BEGIN
                          DELETE FROM tags WHERE tags.postId = OLD.logs.id;
                          DELETE FROM replies WHERE tags.postId = OLD.logs.id;
                          END;''')
        except MySQLdb.Error, e:
            print "delTagRep: Error %d: %s" % (e.args[0], e.args[1])
            print "Warning: program may not run correctly."

    
    def log(self, a):
        """Displays debug messages in verbose mode."""
        if self.verbose == True:
             print '%s: %s' % ( self.__class__.__name__, s, )
            
    def idle_proc(self):
        """This function will be called in the main loop.
           It should prevent timeouts (server disconnecting an idle bot)"""
        self.conn.sendPresence()
    
    def setTagsReplies(self, text, postId):
        tagsRe='(#)((?:[a-z0-9]+))'
        repliesRe='\s(@)((?:[a-z0-9]+))'

        rawtags = re.compile(tagsRe,re.IGNORECASE)
        rawReplies = re.compile(repliesRe,re.IGNORECASE)

        rtags = rawtags.findall(text)
        tags = [y for [x,y] in rtags]

        rrep = rawReplies.findall(text)
        replies = [y for [x,y] in rrep]
        
        # insert into DB
        cur = self.db.cursor()
        for tag in tags:
            t = (postId, tag.encode("utf8"))
            cur.execute("""INSERT INTO tags (postId, tag)
                           VALUES (%s, %s)""", (t))

        for reply in replies:
            t = (postId, reply.encode("utf8"))
            cur.execute("""INSERT INTO replies (postId, reply)
                           VALUES (%s, %s)""", (t))
        
        self.db.commit()
            
    def callback_message( self, conn, mess): 
        """Messages sent to the bot will arrive here."""
        cur = self.db.cursor()
        
        text = mess.getBody()
        
        
        # get jabber ID of the message sender
        to = mess.getFrom()
        user = to.getStripped()

        
        if text is not None:
            t = (user.encode("utf8"), text.encode("utf8"))
            
            cur.execute("""INSERT INTO logs (user, entry)
                           VALUES (%s, %s)""", (t))
            postId = self.db.insert_id()
            
            self.setTagsReplies(text, postId)
            self.db.commit()


def usage(pname):
        """Displays usage information

        keyword arguments:
        pname -- program name (e.g. obtained as argv[0])

        """


        print """Jabber Log Bot - logs messages sent to it in a database.
Version %s, %s
Copyright (C) %s, %s
%s

Usage:
    python %s [-hc] configfile

Options:
    -h, --help\t\tDisplays this information.
    -c, --create-table\tCreates the necessary table in the database.
    -v, --verbose\tDisplays debug messages.

Example:
    python %s ~/bot.conf
    """ % (__version__, __date__, __year__, __author__, __homepage__, pname,
           pname)


def main(argv):
    create = False
    verbose = False
    
    try:
		opts, args = getopt.getopt(
		    argv[1:], "hcv", ["help", "create-table", "--verbose"])	
    except getopt.GetoptError, err:
		print str(err)
		usage(argv[0])
		sys.exit(2)
	
    for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage(argv[0])
			sys.exit()
		elif opt in ("-c", "--create-table"):
		    create = True
		elif opt in ("-v", "--verbose"):
		    verbose = True

		
    conf = "".join(args)
	
    if conf == "":
	    conf = "./bot.conf"
	    print "Using ", conf
	    # TODO: check if file exists
	
	# Connect to the Jabber server
    bot = JabberLogBot(conf, create, verbose)
    bot.serve_forever()



if __name__ == "__main__":
	main(sys.argv)
