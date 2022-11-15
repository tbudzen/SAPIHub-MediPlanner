import numpy as np


def calculate_SCORE(plec, wiek, pal, cisn_sk, cholest_cal):
    ## ocena ryzyka sercowo-naczyniowego

    # SCORE - http://wroclaw.ptkardio.pl/kalkulator (Kalkulator 10-letniego
    # ryzyka zgonu z powodu chorób sercowo-naczyniowych wg kart ryzyka SCORE (Systematic Coronary Risk Evaluation)  u osób bez choroby sercowo-naczyniowej
    if cisn_sk >= 180:
        cisn_sksc = 0
    elif cisn_sk >= 160:
        cisn_sksc = 1
    elif cisn_sk >= 140:
        cisn_sksc = 2
    else:
        cisn_sksc = 3

    if cholest_cal < 190:
        cholest_calsc = 0
    elif cholest_cal < 230:
        cholest_calsc = 1
    elif cholest_cal < 270:
        cholest_calsc = 2
    elif cholest_cal < 310:
        cholest_calsc = 3
    else:
        cholest_calsc = 4

    if wiek >= 70:
        wieksc = 0
    elif wiek >= 65:
        wieksc = 1
    elif wiek >= 60:
        wieksc = 2
    elif wiek >= 55:
        wieksc = 3
    elif wiek >= 50:
        wieksc = 4
    else:
        wieksc = 5

    coord1 = wieksc * 4 + cisn_sksc  # P: was never reaching 0 & when age <50 etc. =>out of bound -> to be verified
    coord2 = plec * 10 + pal * 5 + cholest_calsc  # P: was never reaching 0 - to be verified

    tabscore = [[17, 20, 24, 28, 32, 32, 37, 43, 49, 55, 28, 33, 38, 43, 50, 49, 56, 62, 69, 76],
                [12, 14, 17, 20, 24, 23, 27, 32, 37, 42, 20, 24, 28, 32, 38, 37, 43, 49, 55, 62],
                [8, 10, 12, 14, 17, 17, 20, 23, 27, 32, 14, 17, 20, 24, 28, 27, 32, 37, 43, 49],
                [6, 7, 8, 10, 12, 12, 14, 17, 20, 23, 10, 12, 14, 17, 20, 20, 23, 27, 32, 37],
                [9, 10, 12, 15, 17, 17, 20, 24, 28, 32, 17, 20, 24, 28, 32, 32, 37, 43, 49, 55],
                [6, 7, 9, 10, 12, 12, 14, 17, 20, 23, 12, 14, 17, 20, 24, 23, 27, 32, 37, 43],
                [4, 5, 6, 7, 9, 8, 10, 12, 14, 17, 9, 10, 12, 14, 17, 17, 20, 23, 27, 32],
                [3, 3, 4, 5, 6, 6, 7, 8, 10, 12, 6, 7, 9, 10, 12, 12, 14, 17, 20, 23],
                [5, 6, 7, 8, 9, 9, 11, 13, 15, 18, 11, 13, 15, 18, 21, 21, 25, 29, 34, 39],
                [3, 4, 5, 5, 7, 6, 8, 9, 11, 13, 8, 9, 11, 13, 15, 15, 18, 21, 25, 29],
                [2, 3, 3, 4, 5, 5, 5, 6, 8, 9, 5, 6, 8, 9, 11, 11, 13, 15, 18, 21],
                [2, 2, 2, 3, 3, 3, 4, 4, 5, 6, 4, 4, 5, 6, 8, 7, 9, 11, 13, 15],
                [3, 3, 4, 4, 5, 5, 6, 8, 9, 11, 7, 8, 10, 12, 14, 14, 17, 20, 23, 27],
                [2, 2, 3, 3, 4, 4, 4, 5, 6, 7, 5, 6, 7, 8, 10, 10, 12, 14, 17, 20],
                [1, 1, 2, 2, 3, 3, 3, 4, 4, 5, 3, 4, 5, 6, 7, 7, 8, 10, 12, 14],
                [1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 2, 3, 3, 4, 5, 5, 6, 7, 8, 10],
                [2, 2, 2, 3, 3, 3, 4, 5, 5, 7, 5, 6, 7, 8, 9, 9, 11, 13, 16, 18],
                [1, 1, 2, 2, 2, 2, 3, 3, 4, 5, 3, 4, 5, 6, 7, 6, 8, 9, 11, 13],
                [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 2, 3, 3, 4, 5, 5, 5, 6, 8, 9],
                [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 4, 5, 5, 6],
                [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 2, 2, 3, 3, 4, 4, 4, 5, 6, 8],
                [0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5],
                [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 4],
                [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3]]

    #print(np.shape(tabscore))
    #print(coord1, coord2)
    score = tabscore[coord1][coord2]
    return score
