This is a set of python 2.x scripts for importing official UCB course
information into a departmental Drupal web site. The scripts are based
on a prototype kindly contributed by Prof. Jim Pitman
(http://math.berkeley.edu/people/faculty/james-pitman). The original
Drupal import module was written by Amit Asaravala
(http://returncontrol.com/).

There are two sources of course data: course catalog and course
schedule. Here is an example of course catalog for the department of
Mathematics:

http://guide.berkeley.edu/courses/math/

Similarly, here is an example of Fall 2014 course schedule for the
department of Mathematics:

http://osoc.berkeley.edu/OSOC/osoc?p_term=FL&p_dept=MATH&p_start_row=1

The scripts get the catalog and schedule data from the web and produce a
CSV spreadsheet suitable for importing to Drupal CMS. Here is a list
of courses from the above two sources on the Math department web site:

https://math.berkeley.edu/courses/offerings/fall-2015

Note a JavaScript button on the right side above the course list. It
allows to switch the view from list to table format and vice versa.

Each course is a full Drupal node that can be assigned to and edited by
an instructor. See e.g. this course page:

https://math.berkeley.edu/courses/fall-2015-math-1b-002-lec
