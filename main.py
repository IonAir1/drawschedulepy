from tabulate import tabulate
from html2image import Html2Image
from bs4 import BeautifulSoup
import re


title = "Schedule"
headers = ["Time","Monday","Tuesday", "Wednesday", "Thursday", "Friday"]
formatted_table = [["1:00PM-3:00PM","math","sci","math","sci","math"],["3:00PM-6:00PM","duplicate","duplicate","eng","break","eng"]]
subjects_sample = [
    {
        "Code": "math",
        "Name": "Mathematics",
        "Color": "lightgreen",
        "Schedule": [['MWF',1,3],['T',1.5,4]]
    },
    {
        "Code": "sci",
        "Name": "Science",
        "Color": "pink",
        "Schedule": [['MWF',3,6],['TH',1.5,4]]
    },
    {
        "Code": "eng",
        "Name": "English",
        "Color": "lightblue",
        "Schedule": [['T',4,6]]
    }
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
    duplicates = soup.find_all('td', string=re.compile("duplicate"))
    for element in duplicates:
        cell_above = element.parent.parent.find_all("tr")[element.parent.parent.index(element.parent)-3].find_all("td")[element.parent.index(element)]
        if not 'rowspan' in cell_above.attrs:
            cell_above.attrs['rowspan'] = 1
        cell_above.attrs['rowspan'] += 1
        
    for element in duplicates:
        element.decompose()

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




html_table = tabulate(formatted_table, headers, tablefmt="html")
html = """
    <!DOCTYPE html><html>
    <body><h1><b>{}</b></h1>{}</body></html>
""".format(title, merge_cells(html_table))

html = format_subjects(html, css_sample, subjects_sample)
render(html, (500,200), "output.png")


