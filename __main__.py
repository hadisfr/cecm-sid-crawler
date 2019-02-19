#!/usr/bin/env python3

import requests
import re
from getpass import getpass
from csv import DictWriter


def get_students_list(course_id, session):
    std_pattern = (
        r"<tr[^>]*class=\"\"[^>]*id=\"user-index-participants-[0-9]+?_r[0-9]+\"[^>]*>.*?"
        + r"<td[^>]*id=\"user-index-participants-.+?_c1\"[^>]*>"
        + r"<a[^>]*href=\"https://cecm\.ut\.ac\.ir/user/view\.php\?id=(?P<id>[0-9]+)&amp;course=[0-9]+?\"[^>]*>"
        + r"<img[^>]*>(?P<name>[^<]+)"
        + r"</a>"
        + r"</td>"
        + r".*?<td[^>]*id=\"user-index-participants-.+?_c2\"[^>]*>(?P<email>[^<]+)</td>"
        + r".*?</tr>"
    )
    return [entry.groupdict() for entry in re.finditer(std_pattern, requests.post(
        "https://cecm.ut.ac.ir/user/index.php?id=%d&perpage=5000" % course_id,  # &tsort=lastname could be added
        cookies={'MoodleSession': session},
        data={
            'unified-filters[]': "4:5",  # role: student
            'unified-filter-submitted': 1,
        }
    ).text.replace("\n", ""))]


def get_student_sid(course_id, session, studentd_id):
    sid_pattern = r"<dl><dt>Student No</dt><dd>(?P<sid>[0-9]+)</dd></dl>"
    obj = re.search(sid_pattern, requests.get(
        "https://cecm.ut.ac.ir/user/view.php?id=%d&course=%d" % (studentd_id, course_id),
        cookies={'MoodleSession': session},
    ).text.replace("\n", ""))
    return obj.groupdict()['sid'] if obj else None


def print_progressbar(i, l):
    percentage = i / l * 100
    print("%s\t%.2f%% (%d of %d)\t" % (int(percentage / 10) * "|" + (10 - int(percentage / 10)) * ".", percentage, i, l), end='\r')


def main():
    print("Get Students from CECM")
    course_id = int(input("CourseID: "))
    session = getpass("Session[MoodleSession]: ")
    file_name = input("Output CSV File Name: ")

    students = get_students_list(course_id, session)
    for i in range(len(students)):
        print_progressbar(i + 1, len(students))
        students[i]['sid'] = get_student_sid(course_id, session, int(students[i]['id']))

    if not len(students):
        print("No student detected.")
        exit()
    with open("%s.csv" % file_name, "w") as f:
        writer = DictWriter(f, students[0].keys())
        writer.writeheader()
        writer.writerows(students)
    print("Students' data are wrote in %s.csv" % file_name)


if __name__ == '__main__':
    main()
