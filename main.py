from html2image import Html2Image
from bs4 import BeautifulSoup
import re


css_sample = """

    body {
        background: white;
        font-family: arial;
        text-align:center;
        margin: 10px;
    }

    h1 {
        margin: 0;
        font-size: 15px;
    }

    th {
        background:lightgray;
    }

    table {
        border-collapse: collapse;
        width: 100%;
    }

    table, th, td {
        border: 1px solid;
    }

    td:first-child {
        width: 20%
    }
"""

#replace subject codes with names, add classes to the cells, and style the colors properly
def format_subjects(html, css, subjects):
    soup = BeautifulSoup(html, "html.parser")
    for subject in subjects:
        code = subject['Code']
        name = subject['Name']
        for element in soup.find_all('td', string=re.compile(code)):
            element['class'] = code
            element.string = name
        
        css += "\ntd.{} {{background: {} }}".format(code, subject['Color'])

    return """<!DOCTYPE html><html>
    <head><title>Schedule</title><style>{}</style></head>
    {}</html>""".format(css, soup.find('body'))


#save html as file and render as picture
def render(html, render_size, output):
    with open('test.html', 'w') as file:
        file.write(html)
    hti = Html2Image(size=render_size)
    hti.screenshot(html_str=html, css_str=css_sample, save_as=output)


#time integer to formatted string
def format_time(time, am_pm):
    minutes = str(int((time - int(time))*60))
    if len(minutes) < 2:
        minutes = "0" + minutes
    
    if am_pm:
        if int(time) in [0,24]:
            return "12:" + minutes + "AM"
        elif int(time) < 12:
            return str(int(time)) + ":" + minutes + "AM"
        elif int(time) == 12:
            return str(int(time)) + ":" + minutes + "PM"
        else :
            return str(int(time)-12) + ":" + minutes + "PM"
    else:
        return str(int(time)) + ":" + minutes


#build an html table from a subjects dictionary
def build_table(subjects, **kwargs):
    time_interval = kwargs.get("time_interval", 0.5)
    am_pm = kwargs.get("am_pm", True)

    min_time = 24
    max_time = 0
    days = []
    schedule_table = []

    #add time to table
    for i in range(int(24/time_interval)):
        time = i*time_interval
        time_string = format_time(time, am_pm) + " - " + format_time(time+time_interval, am_pm)
        schedule_table.append([time_string, "", "", "", "", "", "", ""])

    #plot schedule
    for subject in subjects:
        for schedule in subject["Schedule"]:
            
            #add subject to all time slots within the specified range
            time_slots = []
            min_schedule = int(schedule[1] / time_interval)
            time_slot_ammount = int((schedule[2] - schedule[1]) / time_interval)
            for i in range(time_slot_ammount):
                time_slots.append(min_schedule + i)

            byte = schedule[0]
            if byte & 1:
                days.append("Monday") if "Monday" not in days else days
                for time_slot in time_slots:
                    if time_slots.index(time_slot) == 0:
                        schedule_table[time_slot][1] = (subject['Code'], time_slot_ammount)
                    else:
                        schedule_table[time_slot][1] = "^^"
            if byte >> 1& 1:
                days.append("Tuesday") if "Tuesday" not in days else days
                for time_slot in time_slots:
                    if time_slots.index(time_slot) == 0:
                        schedule_table[time_slot][2] = (subject['Code'], time_slot_ammount)
                    else:
                        schedule_table[time_slot][2] = "^^"
            if byte >> 2 & 1:
                days.append("Wednesday") if "Wednesday" not in days else days
                for time_slot in time_slots:
                    if time_slots.index(time_slot) == 0:
                        schedule_table[time_slot][3] = (subject['Code'], time_slot_ammount)
                    else:
                        schedule_table[time_slot][3] = "^^"
            if byte >> 3 & 1:
                days.append("Thursday") if "Thursday" not in days else days
                for time_slot in time_slots:
                    if time_slots.index(time_slot) == 0:
                        schedule_table[time_slot][4] = (subject['Code'], time_slot_ammount)
                    else:
                        schedule_table[time_slot][4] = "^^"
            if byte >> 4 & 1:
                days.append("Friday") if "Friday" not in days else days
                for time_slot in time_slots:
                    if time_slots.index(time_slot) == 0:
                        schedule_table[time_slot][5] = (subject['Code'], time_slot_ammount)
                    else:
                        schedule_table[time_slot][5] = "^^"
            if byte >> 5 & 1:
                days.append("Saturday") if "Saturday" not in days else days
                for time_slot in time_slots:
                    if time_slots.index(time_slot) == 0:
                        schedule_table[time_slot][6] = (subject['Code'], time_slot_ammount)
                    else:
                        schedule_table[time_slot][6] = "^^"
            if byte >> 6 & 1:
                days.append("Sunday") if "Sunday" not in days else days
                for time_slot in time_slots:
                    if time_slots.index(time_slot) == 0:
                        schedule_table[time_slot][7] = (subject['Code'], time_slot_ammount)
                    else:
                        schedule_table[time_slot][7] = "^^"
            
    #remove empty time
    old_schedule_table = schedule_table.copy()
    for period in old_schedule_table:
        if list(filter(None,period[1:])):
            break
        else:
            schedule_table.pop(0)
    reversed_schedule_table = schedule_table.copy()
    reversed_schedule_table.reverse()
    for period in reversed_schedule_table:
        if list(filter(None,period[1:])):
            break
        else:
            schedule_table.pop(-1)
    
    #remove empty days
    days = sorted(days, key=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"].index)
    deleted_days = 0
    for i in range(7):
        empty = True
        for period in schedule_table:
            if period[i+1-deleted_days] != "":
                empty = False
        if empty:
            for period in schedule_table:
                period.pop(i+1-deleted_days)
            deleted_days += 1
            

    #format to html
    formatted_table = "<tr><th>Time</th>"
    for day in days:
        formatted_table += "<th>{}</th>".format(day)
    formatted_table += "</tr>"
    
    for row in schedule_table:
        formatted_row = ""
        for cell in row:
            if type(cell) is str:
                if cell != "^^":
                    formatted_row += "<td>{}</td>".format(cell)
            else:
                if cell[1] > 1:
                    formatted_row += "<td rowspan={}>{}</td>".format(cell[1], cell[0])
                else:
                    formatted_row += "<td/>".format(cell[0])
        formatted_table += "<tr>{}</tr>\n".format(formatted_row)

    formatted_table = "<table>{}</table>".format(formatted_table)

    return formatted_table

# title = "Schedule"
# subjects_sample = [
#     {
#         "Code": "math",
#         "Name": "Mathematics",
#         "Color": "lightgreen",
#         "Schedule": [[0b10101,1,3],[0b10,1.5,4]]
#     },
#     {
#         "Code": "sci",
#         "Name": "Science",
#         "Color": "pink",
#         "Schedule": [[0b10101,5,6],[0b1000,1.5,4]]
#     },
#     {
#         "Code": "eng",
#         "Name": "English",
#         "Color": "lightblue",
#         "Schedule": [[0b10,4,6]]
#     }
# ]
# 
# formatted_table = build_table(subjects_sample)
# html = """
#     <!DOCTYPE html><html>
#     <body><h1><b>{}</b></h1>{}</body></html>
# """.format(title, formatted_table)
# html = format_subjects(html, css_sample, subjects_sample)
# render(html, (1280,720), "output.png")


