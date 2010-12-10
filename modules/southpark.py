import datetime
import web, time, re

STRING = 'The next new episode of South Park will air on \x0300%s\x03.'

HTMLEntities = {
    '&nbsp;'    : ' ',
    '&lt;'      : '<',
    '&gt;'      : '>',
    '&amp;'     : '&',
    '&quot;'    : '"',
    '&#39;'     : "'"
};

def htmlDecode (html):
    for k, v in HTMLEntities.iteritems(): html = html.replace(k, v)
    return html

def southpark (jenney, input):
    text = input.group().split()
    if len(text) > 1:
        if text[1] == 'times':
            southparktimes(jenney,input)
            return
    today = time.localtime()
    src = web.get('http://en.wikipedia.org/wiki/List_of_South_Park_episodes')
    parts = src.split('Season 15 (2011)')
    cont = parts.pop()
    parts = cont.split('Shorts and unaired episodes')
    cont = parts[0]
    tds = cont.split('<td>')
    data = None
    for i in range(len(tds)):
        m = re.match('^[A-Z][a-z]{2,8} \d{1,2}, \d{4}', tds[i])
        if m is None:
            continue
        else:
            dt = time.strptime(m.group(), "%B %d, %Y")
            if dt < today:
                continue
            else:
                jenney.say(STRING % m.group())
                break
southpark.commands = ['southpark']
southpark.priority = 'low'

def southparktimes (jenney, input):
    src = web.get('http://www.comedycentral.com/tv_schedule/index.jhtml?seriesId=11600&forever=please')
    parts = src.split('<div id="tv_schedule_content">')
    cont = parts[1]
    parts = cont.split('<div id="tv_schedule_bottom">')
    cont = parts[0]
    schedule = cont.split('<div class="schedDiv">')
    del schedule[0]
    info = []
    count = 5
    maxtitlelen = 0
    for s in schedule:
        s = s.replace('\n',' ')
        s = htmlDecode(s)

        ## gets the date
        sidx = s.index('<div class="schedDateText">')
        send = s.index('</div>', sidx)
        if sidx == -1 or send == -1: break

        m = re.search('>([^<]{2,})$', s[sidx:send])
        if m is None: break

        date = m.group(1).strip()
        sdate = time.strptime(date, '%A %b %d %Y')

        ## get episodes for the s-th date
        tepi = s.split('<td class="mtvn-cal-time"')
        del tepi[0]
        for t in tepi:

            ## gets the schedule time
            sidx = t.index('<nobr>')
            send = t.index('</nobr>', sidx)

            if sidx == -1 or send == -1: break

            stime = t[sidx+6:send].strip()

            ## gets the schedule episode name
            sidx = t.index('<b>', send)
            send = t.index('</b>', sidx)

            if sidx == -1 or send == -1: break
            
            stitle = t[sidx+3:send].strip()
            m = re.search('\(([^)]+)\)$', stitle)
            if m is None: break
            sepi = m.group(1)
            stitle = stitle.replace(m.group(), '')
            lenstitle = len(stitle)
            if lenstitle > maxtitlelen: maxtitlelen = lenstitle

            ## gets the schedule episode desc
            sidx = send
            send = t.index('</span>', sidx)

            if send == -1: break

            m = re.search('>([^<]{2,})$', t[sidx:send])

            if m is None: break

            sdesc = m.group(1).strip()

            info.append([sdate, sepi, stitle, stime])

            count -= 1
            if count == 0: break
        if count == 0: break

    for i in info:
        jenney.say('%s:  Episode #%s - \x02%s\x02 %s (%s)   %s' % (time.strftime('%a %b %d', i[0]), i[1], i[2], ' '*(maxtitlelen-len(i[2])+5) , i[3], 'Comedy Central'))


# time.strptime("30 Nov 00", "%d %b %y")
# http://www.comedycentral.com/tv_schedule/index.jhtml?seriesId=11600&forever=please

if __name__ == '__main__':
    print __doc__.strip()
