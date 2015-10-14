import csv
import re
import urllib
import get_schedule
import get_catalog

def aggregate(courses):
    keys = [c['Course']['Sort Key'] for c in courses]
    dc = dict(zip(keys, courses))
    for k in sorted(keys):
        c = dc[k]
        if c['Course']['Type'] == 'P':
           dc[k] = c
        elif c['Course']['Type'] == 'S':
           pk = k[:-2].ljust(11,'0')
           if pk in dc:
              if not 'Sections' in dc[pk]:
                  dc[pk]['Sections'] = []
              dc[pk]['Sections'] += [c]
              del dc[k]
        else:
           raise Exception, 'Unknown course type'
    courses = [dc[k] for k in sorted(dc.keys())] 
    return courses

def add_catalog_info(courses, catalog):
    cat_info = {}
    for c in catalog['Courses']:
        key = c['Course']['Number']
        value = {}
        if 'Description' in c:
            value['Description'] = c['Description']
        else:
            value['Description'] = ''
        if 'Prerequisites' in c:
            value['Prerequisites'] = c['Prerequisites']
        else:
            value['Prerequisites'] = ''
        if 'Grading/Final exam status' in c:
            value['Grading'] = c['Grading/Final exam status']
        elif 'Grading' in c:
            value['Grading'] = c['Grading']
        else:
            value['Grading'] = ''
        cat_info[key] = value
    for c in courses:
        key = str(c['Course']['Number'])
        if key in cat_info:
            c['Description'] = cat_info[key]['Description']
            c['Prerequisites'] = cat_info[key]['Prerequisites']
            c['Grading'] = cat_info[key]['Grading']
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
    keys = ['Prerequisites', 'Description', 'Office', 'Office Hours', 'Required Text',
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
    o['Sort Key'] = course['Course']['Sort Key']
    o['Course Title'] = course['Course Title']
    try: o['Days/Time'], o['Location'] = course['Location'].split(',')
    except: 
        o['Days/Time']  = course['Location']
        o['Location']  = ''
    o['Location'] = ' '.join(o['Location'].split())
    o['Instructor'] = course['Instructor']
    o['Course Control Number'] = course['Course Control Number']
    o['Schedule Info'] = format_schedule(schedule_url, sched_params, course)
    if 'Sections' in course:
        o['Sections'] = format_sections(schedule_url, sched_params, course['Sections'])
    else:
        o['Sections'] = ''
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
    catalog_url = 'http://guide.berkeley.edu/courses'
    # minimum set of search parameters
    cat_params = {'p_dept_cd': options.dept}
    # text browser pipe command
    pipecmd = 'w3m -dump -no-cookie -cols 500'
    # output keys
    keys = ['Course Number', 'Section', 'Sort Key', 'Course Title', 'Days/Time', 'Location',
            'Instructor', 'Course Control Number', 'Schedule Info', 'Sections', 'Notes']
    # Output file
    f = open(options.file, 'wb')
    
    schedule = get_schedule.get_all_courses(schedule_url, sched_params, pipecmd)
    courses = schedule['Courses']
    courses = aggregate(courses)
    catalog = get_catalog.get_catalog(catalog_url, options.dept)
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
