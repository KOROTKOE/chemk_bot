import xlrd

class Schedule:
    def __init__(self):
        workbook = xlrd.open_workbook("rasp.xlsx")
        self.worksheet = workbook.sheet_by_index(0)
        self.full_schedule = []
        i = 2
        while i < 121:
            group = self.worksheet.cell_value(8, i)
            if group != "":
                self.full_schedule.append({
                    'group': group,
                    "schedule": self.__get_schedule(i)
                })
            i += 1

    def __get_schedule(self, row_number):
        subjects = []
        i = 9
        number = 0
        rasp = []
        day_number = 0
        while i < 85:
            if i % 2 != 0:
                if number == 6:
                    number = 0
                    day_number += 1
                    rasp.append({
                        "day_number": day_number,
                        "subjects": subjects
                    })
                    subjects = []
                else:
                    number += 1
            if self.worksheet.cell_value(i, row_number) != "":
                name = self.worksheet.cell_value(i, row_number)
                is_have_more_lesson = name.startswith("*")
                second_name = None
                if is_have_more_lesson:
                    second_name = self.worksheet.cell_value(i, row_number+2)
                i += 1
                teacher = self.worksheet.cell_value(i, row_number)
                if is_have_more_lesson:
                    cabinet = self.worksheet.cell_value(i, row_number + 1)
                else:
                    cabinet = self.worksheet.cell_value(i, row_number + 3)
                subject = {
                    "number": number,
                    "name": name,
                    "teacher": teacher,
                    "cabinet": cabinet
                }
                if is_have_more_lesson:
                    subject["type"] = 0
                subjects.append(subject)
                if second_name != None and second_name != "":
                    subjects.append({
                        "number": number,
                        "name": second_name,
                        "teacher": self.worksheet.cell_value(i, row_number+2),
                        "cabinet": self.worksheet.cell_value(i, row_number+3),
                        "type": 1
                    })
            i += 1

        return rasp

    def get_full_schedule(self):
        return self.full_schedule

    def find_schedule(self, group_name):
        current_schedule = ""
        for schedule in self.full_schedule:
            if schedule['group'] == group_name:
                current_schedule = schedule

        if current_schedule == "":
            return False

        else:
            return current_schedule
