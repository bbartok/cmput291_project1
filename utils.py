import os

def clear_screen():
    os.system('clear')

class Display:
    '''
    For easier management of UI.
    '''
    def __init__(self):
        self.buf = []

    def show(self):
        clear_screen()
        for each in self.buf:
            print(each)

    def add(self, content):
        self.buf.append(content)

    def refresh(self):
        self.buf = []
