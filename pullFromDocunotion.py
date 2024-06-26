import subprocess
from datetime import datetime

import requests
import os
import shutil
import re

token=os.environ['NOTION_TOKEN']
pageId=os.environ['NOTION_PAGEID']
docunotionPath = os.environ['NOTION_DOCUNOTION_PATH']
def transform_markdown(text, folderName):
    new_text = re.sub(r'\!\[([^\]]+)\]\(([^\)]+)\)', r'![\1](\2)<br/><GreyItalicText>\1</GreyItalicText>', text) #Image text
    new_text = new_text.replace("<ReactPlayer", "<ReactPlayer width='100%' height='auto' ")
    new_text = re.sub(r"((?:-|[0-9].) .*)\n\n(?=-|[0-9])", r"\1\n", new_text)
    new_text = re.sub(r"contributors: (.*)\n---\n", r"contributors: \1\n---\nContributors: \1\n", new_text)
    new_text = re.sub(r"Contributors: \"(.*)\"\n", r"Contributors: \1\n", new_text)
    dateString = datetime.strptime(new_text.splitlines()[4].replace("last_edited: ", ""), '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%d %B %Y %H:%M:%S")
    new_text = new_text + f"\n\n---\n<RightAlignedText>Last Updated: { dateString }</RightAlignedText>"
    return new_text

def process_dir(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for name in files:
            if name.endswith(".md"):
                file_path = os.path.join(root, name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    contents = f.read()
                new_contents =  transform_markdown(contents, os.path.basename(root))
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_contents)

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    for stdout_line in iter(popen.stderr.readline, ""):
        yield stdout_line
    popen.stdout.close()
    popen.wait()

if __name__ == '__main__':
    if os.path.exists("./docs"):
        shutil.rmtree("./docs")
    result = execute(["npm.cmd", "run",  "--prefix", docunotionPath, "ts", "--", "-n", token, "-r", pageId]) #Cloned from https://github.com/jellejurre/docu-notion
    resultList = []
    for r in result:
        print(r, end='')
        resultList.append(r)
    result = list(result)
    while any("error" in x.lower() for x in resultList):
        result = execute(["npm.cmd", "run",  "--prefix", docunotionPath, "ts", "--", "-n", token, "-r", pageId])  # Cloned from https://github.com/jellejurre/docu-notion
        resultList = []
        for r in result:
            print(r, end='')
            resultList.append(r)
    shutil.copytree(docunotionPath + r"\docs", r".\docs")
    process_dir("docs")
    subprocess.run(["npm.cmd", "install"])
    subprocess.run(["npm.cmd", "start"])

