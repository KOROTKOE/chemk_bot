import urllib.request
import bs4

class GroupInfo:
    def __init__(self,group):
        self.subjects = []
        self.lessons = []
        self.group = group

    def add_subject(self,lesson,subject="по расписании", cabinet=""):
        self.subjects.append({
            'lesson':lesson,
            'subject':subject,
            'cabinet':cabinet
        })

    def add_lesson(self,lesson,subject="по расписании", cabinet=""):
        if cabinet == "\xa0":
            cabinet = ""
        self.lessons.append({
            'lesson':lesson,
            'subject':subject,
            'cabinet':cabinet
        })

    def get_group(self):
        return self.group

    def get_subjects(self):
        return self.subjects

    def get_lessons(self):
        return self.lessons

    def remove_subjects(self):
        self.subjects = []

def get_current_schedule(url):
    site_text = urllib.request.urlopen(url).read()

    soup = bs4.BeautifulSoup(site_text).find('table')
    result = soup.find_all('tr')

    a = []
    last_group = ''
    for element in result:
        row_num = element.get('style').split(';')[0].split(':')[1]
        if row_num=='0' or row_num=='1' or row_num=="2":
            continue

        td_elements = element.find_all('td')
        group_name = td_elements[0].span.get_text().replace(" ", "")

        if td_elements.__len__() == 4:
            if group_name == "":
                continue

            if last_group != '':
                a.append(last_group)

            last_group = GroupInfo(group_name)
            last_group.add_subject(lesson=td_elements[1].span.get_text(),
                                   subject=td_elements[2].span.get_text(),
                                   cabinet=td_elements[3].span.get_text())

        elif td_elements.__len__() == 3:
            last_group.add_subject(lesson=td_elements[0].span.get_text(),
                                   subject=td_elements[1].span.get_text(),
                                   cabinet=td_elements[2].span.get_text())

    for group in a:
        for subject in group.get_subjects():
            lessons = subject['lesson'].split(',')
            for lesson in lessons:
                group.add_lesson(lesson,subject=subject['subject'],cabinet=subject['cabinet'])

    for group in a:
        group.remove_subjects()

    return a