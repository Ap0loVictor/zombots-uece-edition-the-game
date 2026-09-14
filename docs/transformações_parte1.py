def identidade():
    return [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
    ]

def translacao(tx, ty):
   return [
   [1, 0, tx],
   [0, 1, ty],
   [0, 0, 1]
   ]
   
def escala(sx, sy):
    return [
    [sx, 0, 0],
    [0, sy, 0],
    [0, 0, 1]
    ]   

def rotacao(theta):
    c = math.cos(theta)
    s = math.sin(theta)
    return [
    [c, -s, 0],
    [s, c, 0],
    [0, 0, 1]    
    ]

def cria_transformacao():
    return identide()    
    



   
   ]
    