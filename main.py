from tabulate import tabulate
from html2image import Html2Image
from bs4 import BeautifulSoup
import re


title = "Schedule"
headers = ["Time","Monday","Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
formatted_table = [["1:00PM-3:00PM","math","sci","math","sci","math"],["3:00PM-6:00PM","duplicate","duplicate","eng","break","eng"]]
subjects_sample = [
    {
        "Code": "math",
        "Name": "Mathematics",
        "Color": "lightgreen",
        "Schedule": [[0b10101,1,3],[0b10,1.5,4]]
    }
    # {
    #     "Code": "sci",
    #     "Name": "Science",
    #     "Color": "pink",
    #     "Schedule": [[0b10101,5,6],[0b1000,1.5,4]]
    # },
    # {
    #     "Code": "eng",
    #     "Name": "English",
    #     "Color": "lightblue",
    #     "Schedule": [[0b10,4,6]]
    # }
]

css_sample = """

    body {
        background: white;
        font-family: arial;
        text-align:center;
        margin: 10px;
    }

    h1 {
        margin: 0;
        font-size: 20px;
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
"""


#merge cells containing "duplicate" with the cell above
def merge_cells(html):
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.find('tbody').find_all('tr')
    old_rows = rows.copy()

    for row in rows:

        row_above = old_rows[rows.index(row) - 1]
        duplicates = row.find_all('td', string=re.compile("duplicate"))

        for duplicate in duplicates:

            if rows.index(row) > 2:
                break

            print(str(row_above), [duplicate.parent.index(duplicate)])
            cell_above = row_above.find_all('td')[duplicate.parent.index(duplicate)]
            # print(str(row_above),cell_above)
            print(cell_above)
            while "duplicate" in cell_above.string:
                row_above = old_rows[rows.index(row_above) - 1]

                cell_above = row_above.find_all('td')[duplicate.parent.index(duplicate)]
            print(cell_above)

            cell_change = rows.find_all('tr')[old_rows.index(row_above)].find_all('td')[row_above.index(cell_above)]
            if not 'rowspan' in cell_above.attrs:
                cell_change.attrs['rowspan'] = 1
            # print(row_above)
            cell_change.attrs['rowspan'] += 1
        
        for duplicate in rows.find_all('td', string=re.compile("duplicate")):
            duplicate.decompose()

    return soup.find('table')


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
        else:
            return str(int(time)-12) + ":" + minutes + "PM"
    else:
        return str(int(time)) + ":" + minutes


#build a matrix from "subjects" dictionary schedule
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
            time_slot_ammount = int((schedule[2] - schedule[1]) / time_interval) + 1
            for i in range(time_slot_ammount):
                time_slots.append(min_schedule + i)

            byte = schedule[0]
            if byte & 1:
                days.append("Monday") if "Monday" not in days else days
                for time_slot in time_slots:
                    if time_slots.index(time_slot) == 0:
                        schedule_table[time_slot][1] = subject['Code']
                    else:
                        schedule_table[time_slot][1] = "duplicate"
            if byte >> 1& 1:
                days.append("Tuesday") if "Tuesday" not in days else days
                for time_slot in time_slots:
                    if time_slots.index(time_slot) == 0:
                        schedule_table[time_slot][2] = subject['Code']
                    else:
                        schedule_table[time_slot][2] = "duplicate"
            if byte >> 2 & 1:
                days.append("Wednesday") if "Wednesday" not in days else days
                for time_slot in time_slots:
                    if time_slots.index(time_slot) == 0:
                        schedule_table[time_slot][3] = subject['Code']
                    else:
                        schedule_table[time_slot][3] = "duplicate"
            if byte >> 3 & 1:
                days.append("Thursday") if "Thursday" not in days else days
                for time_slot in time_slots:
                    if time_slots.index(time_slot) == 0:
                        schedule_table[time_slot][4] = subject['Code']
                    else:
                        schedule_table[time_slot][4] = "duplicate"
            if byte >> 4 & 1:
                days.append("Friday") if "Friday" not in days else days
                for time_slot in time_slots:
                    if time_slots.index(time_slot) == 0:
                        schedule_table[time_slot][5] = subject['Code']
                    else:
                        schedule_table[time_slot][5] = "duplicate"
            if byte >> 5 & 1:
                days.append("Saturday") if "Saturday" not in days else days
                for time_slot in time_slots:
                    if time_slots.index(time_slot) == 0:
                        schedule_table[time_slot][6] = subject['Code']
                    else:
                        schedule_table[time_slot][6] = "duplicate"
            if byte >> 6 & 1:
                days.append("Sunday") if "Sunday" not in days else days
                for time_slot in time_slots:
                    if time_slots.index(time_slot) == 0:
                        schedule_table[time_slot][7] = subject['Code']
                    else:
                        schedule_table[time_slot][7] = "duplicate"
            
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

    #add function to remove empty days




    for i in schedule_table:
        print(i)

    return schedule_table



formatted_table = build_table(subjects_sample)
html_table = tabulate(formatted_table, headers, tablefmt="html")
html = """
    <!DOCTYPE html><html>
    <body><h1><b>{}</b></h1>{}</body></html>
""".format(title, merge_cells(html_table))

html = format_subjects(html, css_sample, subjects_sample)
render(html, (500,200), "output.png")


