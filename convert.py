import os
def convert():
    pyui_files = os.listdir("pyui/")
    for file in pyui_files:
        if file.endswith(".py"):
            os.remove("pyui/" + file)
    ui_files = os.listdir("ui/")
    for file in ui_files:
        if not file.endswith(".ui"):
            continue
        a = os.system("pyuic5 ui/" + file + " -o pyui/" + file[:-3] + ".py") 
        print("success" if a == 0 else a)

if __name__ == "__main__":
    convert()