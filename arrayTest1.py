import shelve
s = shelve.open('TestBoxData.db')
try:
    s['global'] = {
                    'maxpos':35,'btn':0,'del':0,'pos':1
                }

    s['data'] = {   
                    1:  {'title':'CX482', 'buttons':
                        {0:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        1:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        2:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        3:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        4:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        5:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        6:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5}}},
                    1:  {'title':'CX482', 'buttons':
                        {0:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        1:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        2:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        3:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        4:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        5:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        6:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5}}},
                    2:  {'title':'CD539', 'buttons':
                        {0:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        1:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        2:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        3:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        4:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        5:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        6:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5}}},
                    3:  {'title':'LD540', 'buttons':
                        {0:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        1:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        2:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        3:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        4:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        5:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5},
                        6:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5}}}
                }
finally:
    s.close()
