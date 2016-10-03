from scrape_schedule import scrape_schedule
import re

def get_schedule(searchresults, exclude):
    course_headers = ('Department', 'Number', 'Title')
    section_headers = ('Class', 'Number', 'Type', 'Days/Times', 'Location',
        'Instructor', 'Status', 'Sort Key')
    courses = scrape_schedule(searchresults)
    classes = []
    exclude_list = exclude.split(',')
    for c in courses:
        (dept, course_num, course_title) = split_course_title(c[0])
        #print (dept, course_num, course_title)
        course_info = dict(zip(course_headers, (dept, course_num, course_title)))
        course_sections = c[1]
        for section in course_sections:
            (class_num, section_num, section_type, days_times, location,
                instructor, status) = get_section_schedule(section)
            if section_type in exclude_list:
                # drop sections from exclude list
                continue
            #print (class_num, section_num, section_type, days_times, location,
            #    instructor, status)
            sortkey = section_sortkey(course_num, section_num, section_type)
            #print sortkey
            section_info = dict(zip(section_headers, (class_num, section_num, section_type, days_times, location,
                instructor, status, sortkey)))
            classes += [{'Course': course_info, 'Section': section_info}]
    return classes

def split_course_title(course_title):
    l = course_title.split()
    dept, num, title = l[0], l[1], ' '.join(l[3:])
    return (dept, num, title)

def get_section_schedule(section):
        class_num = section[0]
        section_title = section[1].split()[0]
        section_num = section_title.split('-')[0]
        section_type = section_title.split('-')[1]
        days_times = section[2]
        location = section[3]
        instructor = section[4]
        # remove annoying 'Staff' instructor
        if instructor == 'Staff':
            instructor = ''
        # skipping "Begin/End Dates"
        status = section[6]
        return (class_num, section_num, section_type, days_times, location,
            instructor, status)

def section_sortkey(course_num, section_num, section_type):
    r = r'(^\D?)(\d+)(\D*)$'
    i = 0
    m = re.match(r, course_num)
    m1 = m.group(1).rjust(1, ' ')
    m2 = m.group(2).rjust(3, '0')
    m3 = m.group(3).ljust(2, ' ')
    n = section_num
    if section_type == 'DIS':
        n = n.rjust(5, '0')
    else:
        n = n.ljust(5, '0')
    return m2 + m3 + m1 + n

if __name__ == '__main__':
    from optparse import OptionParser
    from json import dump
    usage = 'usage: %prog options'
    parser = OptionParser(usage)
    parser.add_option('-i', '--input', dest = 'searchresults', default = 'searchresults.html',
                      help='name of search results file in html format, default "searchresults.html"')
    parser.add_option('-e', '--exclude', dest='exclude', default='IND,COL',
                      help='comma separated section types to be excluded from search results, default "IND,COL"')
    parser.add_option('-o', '--output', dest = 'outputfile', default = 'schedule.json',
                      help='name of output file in json format, default "schedule.json"')
    (options, args) = parser.parse_args()
    schedule = get_schedule(options.searchresults, options.exclude)
    print '%d class section(s) parsed' % len(schedule)
    f = open(options.outputfile, 'w')
    dump(schedule, f, sort_keys = True, indent = 2)
    f.close()
    print 'see output in "%s"' % options.outputfile
