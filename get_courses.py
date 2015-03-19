import csv
import re
import urllib
import get_schedule
import get_catalog

def aggregate(courses):
    i = 0
    while i < len(courses):
        c = courses[i]
        if c['Course']['Type'] == 'P':
            i += 1
            c['Sections'] = []
            #print c['Course']
            continue
        if c['Course']['Type'] == 'S':
            # lookup primary course (p)
            j = i
            while j > 0:
                j -= 1
                p = courses[j]
                n = p['Course']['Number']
                m = p['Course']['Section'][-1]
                if c['Course']['Number'] == n and c['Course']['Section'][0] == m:
                    p['Sections'] += [c]
                    courses.remove(c)
                    break
            continue
    return courses

def add_catalog_info(courses, catalog):
    cat_info = {}
    for c in catalog['Courses']:
        key = c['Course']['Number']
        value = {}
        if 'Description' in c:
            value['Syllabus'] = c['Description']
        else:
            value['Syllabus'] = ''
        if 'Prerequisites' in c:
            value['Prerequisites'] = c['Prerequisites']
        else:
            value['Prerequisites'] = ''
        cat_info[key] = value
    for c in courses:
        key = str(c['Course']['Number'])
        if key in cat_info:
            c['Syllabus'] = cat_info[key]['Syllabus']
            c['Prerequisites'] = cat_info[key]['Prerequisites']
    return courses

def output_section(course):
    output = {}
    output['Section'] = course['Course']['Section'] + ' ' + course['Course']['Kind']
    try:
        output['Days/Time'],output['Location'] = course['Location'].split(',')
    except: 
        output['Days/Time']  = course['Location']
        output['Location']  = ''
    output['Instructor'] = course['Instructor']
    output['CCN'] = course['Course Control Number']
    return output

def make_ccn_link(schedule_url, sched_params, ccn):
    p = {'p_ccn': str(ccn), 'p_term': sched_params['p_term']}
    # sample URL: http://osoc.berkeley.edu/OSOC/osoc?p_ccn=53609&p_term=SU
    url = schedule_url + urllib.urlencode(p)
    html = '<a target="_blank" href="' + url + '">' + str(ccn) + '</a>'
    return html

def format_sections(schedule_url, sched_params, courses):
    if len(courses) == 0:
        return str('')
    keys  = ['Section', 'Days/Time','Location','Instructor','CCN']
    width = ['15%',     '25%',      '25%',     '25%',       '10%']
    html = '<table class="course-data">'
    # header row
    html += '<tr>'
    for k,w in map(None, keys, width):
        html += '<th width="'+str(w)+'">' + str(k) + '</th>'
    html += '</tr>'
    # data rows
    for c in courses:
        output = output_section(c)
        if output['Days/Time'] == 'CANCELLED':
            output['Days/Time'] = '<em style="font-weight:bold;color:#ba0000;">CANCELLED</em>'
        if re.match(r'^(\d+)$', output['CCN']) != None:
            output['CCN'] = make_ccn_link(schedule_url, sched_params, output['CCN'])
        html += '<tr>'
        for k in keys:
            if output[k]: 
                html += '<td>' + str(output[k]) + '</td>'
            else:
                html += '<td>&nbsp;</td>'
        html += '</tr>'
    html += '</table>'
    #print html
    return html

def format_schedule(schedule_url, sched_params, course):
    html = format_sections(schedule_url, sched_params, [course])
    if 'Final Exam Group' in course: # fall or spring semester
        keys  = ['Units/Credit', 'Final Exam Group', 'Enrollment']
        width = ['15%',          '35%',              '50%'       ]
    else:
        keys  = ['Units/Credit', 'Session Dates', 'Enrollment']
        width = ['15%',          '35%',           '50%'       ]
    html += '<table class="course-data">'
    # header row
    html += '<tr>'
    for k,w in map(None, keys, width):
        html += '<th width="'+str(w)+'">' + str(k) + '</th>'
    html += '</tr>'
    # data row
    html += '<tr>'
    for k in keys:
        html += '<td>' + str(course[k]) + '</td>'
    html += '</tr>'
    html += '</table>'
    # other properties
    keys = ['Restrictions', 'Summer Fees', 'Note']
    for k in keys:
        if k in course and course[k]:
            html += '<p class="course-data"><strong>' + str(k) + ':</strong>&nbsp;' + str(course[k]) + '</p>'
    # escape dollar sign to avoid collision with MathJax
    return html.replace('$', '\$')

def format_notes(course):
    html = ''
    keys = ['Prerequisites', 'Syllabus', 'Office', 'Office Hours', 'Required Text',
            'Recommended Reading', 'Grading', 'Homework', 'Course Webpage']
    for k in keys:
        if k in course and course[k]:
            html += '<p class="course-data"><strong>' + str(k) + ':</strong>&nbsp;' + str(course[k]) + '</p>'
        else:
            html += '<p class="course-data"><strong>' + str(k) + ':</strong>&nbsp;</p>'
    return html

def output_course(schedule_url, sched_params, course):
    o = {}
    o['Course Number'] = course['Course']['Number']
    o['Section'] = course['Course']['Section'] + ' ' + course['Course']['Kind']
    o['Course Title'] = course['Course Title']
    try: o['Days/Time'], o['Location'] = course['Location'].split(',')
    except: 
        o['Days/Time']  = course['Location']
        o['Location']  = ''
    o['Location'] = ' '.join(o['Location'].split())
    o['Instructor'] = course['Instructor']
    o['Course Control Number'] = course['Course Control Number']
    o['Schedule Info'] = format_schedule(schedule_url, sched_params, course)
    o['Sections'] = format_sections(schedule_url, sched_params, course['Sections'])
    o['Notes'] = format_notes(course)
    return o

if __name__ == '__main__':
    from optparse import OptionParser

    usage = 'usage: %prog options'
    parser = OptionParser(usage)
    parser.add_option('-d', '--dept', dest='dept', default='MATH',
                      help='department abbreviation, e.g. MATH')
    parser.add_option('-t', '--term', dest='term', default='FL',
                      help='term/semester code (FL or SP or SU)')
    parser.add_option('-f', '--file', dest='file', default='courses.csv',
                      help='name of output file (in csv format)')
    (options, args) = parser.parse_args()

    # base URL for searching course schedules
    schedule_url = 'http://osoc.berkeley.edu/OSOC/osoc?'
    # minimum set of search parameters
    sched_params = {'p_dept': options.dept, 'p_term': options.term}
    # base URL for seaching course catalog
    catalog_url = 'http://osoc.berkeley.edu/catalog/gcc_search_sends_request?'
    # minimum set of search parameters
    cat_params = {'p_dept_cd': options.dept}
    # text browser pipe command
    pipecmd = 'w3m -dump -no-cookie -cols 500'
    # output keys
    keys = ['Course Number', 'Section', 'Course Title', 'Days/Time', 'Location',
            'Instructor', 'Course Control Number', 'Schedule Info', 'Sections', 'Notes']
    # Output file
    f = open(options.file, 'wb')
    
    schedule = get_schedule.get_all_courses(schedule_url, sched_params, pipecmd)
    courses = aggregate(schedule['Courses'])
    catalog = get_catalog.get_catalog(catalog_url, cat_params, pipecmd)
    courses = add_catalog_info(courses, catalog)

    w = csv.writer(f)
    w.writerow(keys)
    for c in courses:
        o = output_course(schedule_url, sched_params, c)
        r = []
        for k in keys:
            r += [o[k]]
        #print r
        w.writerow(r)
    f.close()
