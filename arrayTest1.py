import shelve
s = shelve.open('TestBoxData.db')
try:
    s['global'] = {
                    'maxpos':35,'btn':0,'del':0,'pos':1
                }

    s['data'] = {
                    1:  {'title':'CX482', 'buttons':
                        {0:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':50},
                        1:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':100},
                        2:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':150},
                        3:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':200},
                        4:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':250},
                        5:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':200},
                        6:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':150}}},

                    2:  {'title':'CD539', 'buttons':
                        {0:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':50},
                        1:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':100},
                        2:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':150},
                        3:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':200},
                        4:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':250},
                        5:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':200},
                        6:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':150}}},
                    3:  {'title':'LD540', 'buttons':
                        {0:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':50},
                        1:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':100},
                        2:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':150},
                        3:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':200},
                        4:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':250},
                        5:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':200},
                        6:{'title':'0','func':'DC','frq':100,'dc':101,'MaxCurrent':5,'SR':150}}}
                }
finally:
    s.close()
