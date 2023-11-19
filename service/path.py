import os


def abs_path():
    current_script_path = str(os.path.abspath(__file__)).split("/")
    final_path = ""
    for i in current_script_path[:-2]:
        print(i)
        final_path += i + "/"
    return final_path
