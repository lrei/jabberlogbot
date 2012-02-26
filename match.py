import sys, re

tagsRe='(#)((?:[a-z0-9]+))'
repliesRe='\s(@)((?:[a-z0-9]+))'

rawtags = re.compile(tagsRe,re.IGNORECASE)
rawReplies = re.compile(repliesRe,re.IGNORECASE)

while 1:
    line = raw_input('Enter a line ("q" to quit):')
    if line == 'q':
        break
    
    rtags = rawtags.findall(line)
    tags = [y for [x,y] in rtags]

    rrep = rawReplies.findall(line)
    replies = [y for [x,y] in rrep]
    
    print tags
    print replies