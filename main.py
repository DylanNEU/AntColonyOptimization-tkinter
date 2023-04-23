import tkinter
from TSP import TSP
from global_vars import city_num


if __name__ == '__main__':
    print(u"\n"
          u"    ==================================\n"
          u"         《人工智能》课程大作业\n"
          u"       蚁群算法解决中国省会城市TSP问题\n"
          u"    ==================================\n"
          u"    ")
    TSP(tkinter.Tk(), 800, 600, city_num).mainloop()
