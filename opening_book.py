class OpeningBook:
    def __init__(self):
        self.dic = {}

        with open('70_book.gam') as book:
            for line in book:
                for index in range(0,30,3):
                    prefix = line[0:index]
                    move = line[index:index+3]
                    self.dic[prefix]=move

        #for key in self.dic.keys():
        #    print (key +": " + self.dic[key])