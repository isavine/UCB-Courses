import urllib
import pipes
import re
import json

# key for parsing the catalog page
keys = ['Course Title', 'Dept Code', 'Course Number', 'Units', 'Course Format', 'Prerequisites', 'Credit option', 'Description', 'Semesters']

def read_page(baseurl, params, pipecmd):
    url = baseurl + urllib.urlencode(params)
    t = pipes.Template()
    t.prepend(pipecmd + " '" + url + "'", '.-')
    f = t.open('-', 'r')
    lines = f.readlines()
    f.close()
    fields = []
    # read summary lines
    m = re.match(r'^ *There were (\d+) matches to your request:', lines[9])
    if m:
        total = int(m.group(1))
    else:
        print 'No courses found -- verify your search request!'
        exit(2)
    m = re.match(r'^ *\((.*)\)', lines[10])
    comment = m.group(1)
    comment = ' '.join(comment.split()[1:])
    for l in lines:
        l = l.split('\n')[0]
        #print l
        # matching course title
        m = re.match(r'^ +(.*  --  .*)$', l)
        if m:
            fields += [('Course', m.group(1))]
        for k in keys:
            m = re.match(r'^ *(' + k + r'): +(.*)$', l)
            if m:
                if m.group(2):
                    fields += [m.group(1,2)]
                else:
                    fields += [(m.group(1), '')]
        # matching semesters
        m = re.match(r'^ *\((F|SP|F,SP)\)$', l)
        if m:
            fields += [('Semesters', m.group(1))]
    return (total, comment, fields)

def split_course_info(course_field_value):
    title, rest = course_field_value.split('  --  ')
    m = re.match(r'^(\w+)  \((\w+)\) (\w+) (\[(\d+|\d+-\d+) units\]){0,1}$', rest)
    d = {}
    d['Title'] = str(title)
    d['Department'], d['Dept Code'], d['Number'] = m.group(1,2,3)
    if m.group(5):
        d['Units/Credit'] = m.group(5)
    return d

def get_catalog(baseurl, params, pipecmd):
    courses = []
    course = {}
    (total, comment, fields) = read_page(baseurl, params, pipecmd)
    for k, v in fields:
        if k == 'Course' and course:
            courses += [course]
            course = {}
        course[k] = v
    if course:
        courses += [course]
    #print len(courses)
    for c in courses:
        c['Course'] = split_course_info(c['Course'])
    if total != len(courses):
        print 'The number of parsed courses ' + str(len(courses)) + ' does not match the web total ' + str(total) + '!'
        exit(1)
    comment = str(total) + ' courses matched ' + comment
    return {'Comment': comment, 'Courses': courses}

if __name__ == '__main__':
    from optparse import OptionParser

    usage = 'usage: %prog options'
    parser = OptionParser(usage)
    parser.add_option('-d', '--dept', dest='dept', default='MATH',
                      help='department abbreviation, e.g. MATH')
    parser.add_option('-f', '--file', dest='file', default='catalog.json',
                      help='name of output file (in json format)')
    (options, args) = parser.parse_args()
    # base URL for searching course catalog
    baseurl = 'http://osoc.berkeley.edu/catalog/gcc_search_sends_request?'
    # minimum set of search parameters
    params = {'p_dept_cd': options.dept}
    # text browser pipe command
    pipecmd = 'w3m -dump -no-cookie -cols 500'
    # output file
    f = open(options.file, 'wb')

    catalog = get_catalog(baseurl, params, pipecmd)
    json.dump(catalog, f, sort_keys=True, indent=4)
    f.close()
