from tabula import read_pdf
from tabulate import tabulate
import re
import random
import main
import pandas as pd


colors = ["lightcoral","lightsalmon","lightpink","lightyellow","moccasin","khaki","lavander","plum","thistle","palegreen","lightseagreen","yellowgreen","lightcyan","lightsteelblue","powderblue","gainsboro"]


def convert_time(text):
    time_list = text.replace("AM","").replace("PM","").split(":")
    time = 0
    if "12:" in text:
        if "AM" in text:
            time = 0
        elif "PM" in text:
            time = 12
    elif "AM" in text:
        time = int(time_list[0])
        time += int(time_list[1])/60
    elif "PM" in text:
        time = int(time_list[0])+12
        time += int(time_list[1])/60
    return time


def extract_sched(text):
    schedules = text.split("\r")
    formatted_schedules = []
    for schedule in schedules:
        formatted_schedule = []
        time_index_start = re.search(r"\d", schedule).start()
        time_index_end = schedule.rfind("AM") + 2
        time_index_end2 = schedule.rfind("PM") + 2
        if time_index_end < time_index_end2:
            time_index_end = time_index_end2

        
        days = schedule[:time_index_start].replace('TH','H').replace('SA','S').replace('SU',"U")
        formatted_days = 0b0
        if 'M' in days:
            formatted_days += 0b1
        if 'T' in days:
            formatted_days += 0b10
        if 'W' in days:
            formatted_days += 0b100
        if 'H' in days:
            formatted_days += 0b1000
        if 'F' in days:
            formatted_days += 0b10000
        if 'S' in days:
            formatted_days += 0b100000
        if 'U' in days:
            formatted_days += 0b1000000
        formatted_schedule.append(formatted_days)

        time_range = schedule[time_index_start:time_index_end].split(" - ")
        for time in time_range:
            formatted_schedule.append(convert_time(time))

        formatted_schedules.append(formatted_schedule)
    return formatted_schedules
        

def read_pdf_table(file):
    schedule = read_pdf(file, pages="all")[1]

    #remove nan
    if len(schedule.columns) >5:
        new_schedule = pd.DataFrame({'SUBJECT CODE':[],'DESCRIPTION':[],'SECTION':[],'DAYSCHEDULEROOM':[]})

        for index, row in schedule.iterrows():
            curr_row = row.to_list()
            dayscheduleroom = "".join(curr_row[3:6])
            if curr_row[0] == curr_row[0]:
                new_schedule = pd.concat([new_schedule, pd.DataFrame({'SUBJECT CODE':[curr_row[0]],'DESCRIPTION':[curr_row[1]],'SECTION':[curr_row[2]],'DAYSCHEDULEROOM':[dayscheduleroom]})])
            else:
                new_schedule.iloc[len(new_schedule)-1]['DAYSCHEDULEROOM'] += "\r" + dayscheduleroom
        schedule = new_schedule


    subjects = []
    for i in range(len(schedule["SUBJECT CODE"])):
        subject = {}
        subject['Code'] = schedule.iloc[i]["SUBJECT CODE"]
        subject['Name'] = schedule.iloc[i]['DESCRIPTION']
        subject['Schedule'] = extract_sched(schedule.iloc[i]['DAYSCHEDULEROOM'])

        color = random.choice(colors)
        colors.remove(color)
        subject['Color'] = color

        subjects.append(subject)
    return subjects



subjects = read_pdf_table("3.pdf")
formatted_table = main.build_table(subjects, start=12.5)
html = """
    <!DOCTYPE html><html>
    <body><h1><b>{}</b></h1>{}</body></html>
""".format("SCHEDULE", formatted_table)
html = main.format_subjects(html, main.css_sample, subjects)
main.render(html, (1280,720), "output.png")