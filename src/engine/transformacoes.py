import math


# Matrizes homogêneas 3x3

def identidade():
    return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def translacao(tx, ty):
    return [[1, 0, tx], [0, 1, ty], [0, 0, 1]]


def escala(sx, sy):
    return [[sx, 0, 0], [0, sy, 0], [0, 0, 1]]


def rotacao(theta):
    c, s = math.cos(theta), math.sin(theta)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def multiplica_matrizes(a, b):
    r = [[0] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                r[i][j] += a[i][k] * b[k][j]
    return r


def aplica_transformacao(m, pontos):
    novos = []
    for x, y in pontos:
        novos.append((
            m[0][0] * x + m[0][1] * y + m[0][2],
            m[1][0] * x + m[1][1] * y + m[1][2],
        ))
    return novos
