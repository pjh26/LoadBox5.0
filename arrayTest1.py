import shelve
s = shelve.open('test1.db')
try:
    s['key1'] = {'maxpos':1,'btn':0,'del':0,'pos':1,1:
                    {'title':'CX482', 'buttons':
                        {0:{'title':'0','func':'DC','frq':100,'dc':101},
                        1:{'title':'0','func':'DC','frq':100,'dc':101},
                        2:{'title':'0','func':'DC','frq':100,'dc':101},
                        3:{'title':'0','func':'DC','frq':100,'dc':101},
                        4:{'title':'0','func':'DC','frq':100,'dc':101},
                        5:{'title':'0','func':'DC','frq':100,'dc':101},
                        6:{'title':'0','func':'DC','frq':100,'dc':101}}}}
finally:
    s.close()
