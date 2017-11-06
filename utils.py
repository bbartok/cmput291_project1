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

class PageView:
    '''
    Take a list and divide the list into pages, only return certain page at a
    time.
    '''
    def __init__(self, content, per_page):
        self.content = content
        self.per_page = per_page
        self.page = 0 # initial page number
        self.num_pages = len(content) // per_page

    def get_view(self):
        start = self.page * self.per_page
        end = start + self.per_page if self.page < self.num_pages else None
        return self.content[start : end]

    def next_page(self):
        self.page += 1
        self.page = min(self.num_pages, self.page)

    def prev_page(self):
        self.page -= 1
        self.page = max(0, self.page)
