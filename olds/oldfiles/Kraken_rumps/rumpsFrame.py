# -*- coding: utf-8 -*-

import rumps


class Frame(rumps.App):
    def __init__(self):
        super(Frame, self).__init__(name=' ', title=None, icon='icon.png')
        self.quit_button = rumps.MenuItem('Quit', key='q')
        self.menu = ('downloading', 'completed', 'save directory', ('interval', ('none', 'short', 'long')), None)
        self.menu['interval']['short'].state = True
        self.interval_time = 1

    @rumps.clicked('interval', 'none')
    @rumps.clicked('interval', 'short')
    @rumps.clicked('interval', 'long')
    def toggle(self, sender):
        i2s_intervals = {0: 'none', 1: 'short', 3: 'long'}
        self.menu['interval'][i2s_intervals[self.interval_time]].state = False
        sender.state = True
        s2i_intervals = {'none': 0, 'short': 1, 'long': 3}
        self.interval_time = s2i_intervals[sender.title]
        print(self.interval_time)


if __name__ == '__main__':
    Frame().run()
