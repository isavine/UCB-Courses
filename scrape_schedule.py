from lxml import html

def subtrees(x, l):
    '''Select items by XPath from all elements of a list'''
    return [e.xpath(x) for e in l]

def html2text(l):
    '''Convert HTML to unicode text in a list of nodes'''
    return [html.tostring(e, method='text', encoding='unicode') for e in l]

def trim_spaces(l):
    '''Trim white spaces in a list of text elements'''
    return [' '.join(e.split()) for e in l]

def scrape_schedule(search_results_file):
    tree = html.parse(search_results_file)
    sections_found = tree.xpath('//td[@class="SSSGROUPBOX"]/text()')
    #print sections_found[0]
    total = int(sections_found[0].split()[0])
    course_nodes = tree.xpath('//td[@class="PAGROUPBOXLABELLEVEL1"]/../..')
    courses = []
    nsec = 0
    for node in course_nodes:
        # get element containing course title
        e = node.xpath('.//td[@class="PAGROUPBOXLABELLEVEL1"]/div')[0]
        # convert it to text""
        s = html.tostring(e, method='text', encoding='unicode')
        # trim spaces
        title = ' '.join(s.split())
        sections = []
        section_rows = node.xpath('.//td[@class="PSLEVEL3GRIDROW"]/..')
        # section headers: Class Number, Section Title, Days/Times, Location,
        #     Begin/End Dates, Enrollment Status
        for row in section_rows:
            # get list of section elements from each row
            l = row.xpath('.//td[@class="PSLEVEL3GRIDROW"]')
            # treat the last element (status) differently
            status = l[6].xpath('.//img/@alt')[0]
            #print l[6].xpath('.//img/@alt')[0]
            # extract text from first 6 elements
            l = html2text(l[:6])
            # trim spaces
            l = trim_spaces(l)
            # add status element
            l += [status]
            sections += [l]
            nsec += 1
        courses += [(title, sections)]
    if nsec != total:
        raise Exception, 'The number of parsed class sections %d does not match the web total %d!' % (nsec, total)
    #print courses
    return courses

if __name__ == '__main__':
    from optparse import OptionParser
    from json import dump
    usage = 'usage: %prog options'
    parser = OptionParser(usage)
    parser.add_option('-i', '--input', dest = 'searchresults', default = 'searchresults.html',
                      help='name of search results file in html format, default "searchresults.html"')
    parser.add_option('-o', '--output', dest = 'outputfile', default = 'scraped_schedule.json',
                      help='name of output file in json format, default "scraped_schedule.json"')
    (options, args) = parser.parse_args()
    parseresults = scrape_schedule(options.searchresults)
    print '%d course(s) scraped' % len(parseresults)
    nsec = 0
    for c in parseresults:
        nsec += len(c[1])
    print '%d class section(s) scraped' % nsec
    f = open(options.outputfile, 'w')
    dump(parseresults, f, sort_keys = True, indent = 2)
    f.close()
    print 'see output in "%s"' % options.outputfile
