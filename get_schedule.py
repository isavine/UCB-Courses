import urllib
import pipes
import re
import json

def get_all_courses(baseurl, params, pipecmd):
    start = total = 1
    courses = []
    pars = params
    while start <= total:
        pars['p_start_row'] = str(start)
        # sample URL: http://osoc.berkeley.edu/OSOC/osoc?p_term=SU&p_dept=MATH&p_start_row=1
        url = baseurl + urllib.urlencode(pars)
        #print url
        # command to dump text from a schedule page
        #print pipecmd + " '" + url + "'"
        t = pipes.Template()
        t.prepend(pipecmd + " '" + url + "'", '.-')
        f = t.open('-', 'r')
        lines = f.readlines()
        f.close()
        # match summary line
        r = r'^ *Displaying (\d+)-(\d+) of (\d+) matches to your request for (\w+) (\d{4,4}): *\n'
        m = re.match(r, lines[5])
        #print m.groups()
        (start, end, total, term, year) = m.group(1,2,3,4,5)
        (start, end, total) = (int(start), int(end), int(total))
        courses += get_courses(lines[6:])
        start = end + 1
    for c in courses:
        c = strip_links(c)
        c['Course'] = split_course_info(c['Course'])
    if total != len(courses):
        print 'The number of parsed courses ' + str(len(courses)) + ' does not match the web total ' +  str(total) +'!'
        exit(1)
    comment = str(total) + ' courses matched the schedule for ' + term + ' ' + year
    return {'Comment': comment, 'Courses': courses}

# keys for parsing the schedule page
keys = ['Course', 'Course Title', 'Location', 'Instructor', 'Course Control Number',
        'Units/Credit', 'Final Exam Group', 'Session Dates', 'Restrictions', 'Summer Fees',
        'Note', r'Enrollment on \d\d/\d\d/\d\d']

def strip_links(course):
    course['Course'] = re.sub(r' *\(course website\)$', '', course['Course'])
    course['Course Title'] = re.sub(r' *\[\(catalog description\)\]$', '', course['Course Title'])
    course['Course Control Number'] = re.sub(r' *\[View Books\]$', '', course['Course Control Number'])
    return course

def split_course_info(course_field_value):
    d = {}
    (d['Number'], d['Type'], d['Section'], d['Kind']) = course_field_value.split()[-4:]
    d['Department'] = ' '.join(course_field_value.split()[:-4])
    return d

def get_courses(lines):
    courses = []
    course = {}
    fields = read_page(lines)
    for k, v in fields:
        if k == 'Course' and course:
            courses += [course]
            course = {}
        # moving variable part of the enrollment key to the value
        m = re.match(r'Enrollment on (\d\d/\d\d/\d\d)', k)
        if m:
            k, v = 'Enrollment', str(v) + ' [on ' + m.group(1) + ']'
        course[k] = v
    if course:
        courses += [course]
    #print len(courses)
    return courses

def read_page(lines):
    fields = []
    for l in lines:
        l = l.split('\n')[0]
        for k in keys:
            m = re.match(r'^(\[sp\]){0,1} *(' + k + r'): *(([^ ]+ +)*[^ ]+)* *', l)
            if m:
                #print m.group(2,3)
                if m.group(3):
                    fields += [m.group(2,3)]
                else:
                    fields += [(m.group(2), '')]
    return fields

if __name__ == '__main__':
    from optparse import OptionParser

    usage = 'usage: %prog options'
    parser = OptionParser(usage)
    parser.add_option('-d', '--dept', dest='dept', default='MATH',
                      help='department abbreviation, e.g. MATH')
    parser.add_option('-t', '--term', dest='term', default='FL',
                      help='term/semester code (FL or SP or SU)')
    parser.add_option('-f', '--file', dest='file', default='schedule.json',
                      help='name of output file (in json format)')
    (options, args) = parser.parse_args()
 
    # base URL for searching course schedules
    baseurl = 'http://osoc.berkeley.edu/OSOC/osoc?'
    # minimum set of search parameters
    params = {'p_dept': options.dept, 'p_term': options.term}
    # text browser pipe command
    pipecmd = 'w3m -dump -no-cookie -cols 500'
    # output file
    f = open(options.file, 'wb')

    schedule = get_all_courses(baseurl, params, pipecmd)
    json.dump(schedule, f, sort_keys=True, indent=4)
    f.close()
