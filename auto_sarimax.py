#!/usr/bin/env python
# coding: utf-8

# # 01 - AUTO-SARIMAX

# In[1]:


# importamos librerías
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import os
from itertools import product


#from numpy.random import normal, seed
#from scipy.stats import norm
from scipy.stats import boxcox

#from statsmodels.tsa.arima_model import ARMA
from statsmodels.tsa.stattools import adfuller
#from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
#from statsmodels.tsa.arima_process import ArmaProcess
from statsmodels.tsa.arima.model import ARIMA

import statsmodels.api as sm


#import math
#from sklearn.metrics import mean_squared_error
#from scipy import stats
from scipy.stats import normaltest

import warnings
warnings.filterwarnings('ignore')


# In[2]:


def auto_sarimax(serie, maxps = 3, maxqs = 3, maxPs = 3, maxQs = 3, tendencia = 'n', frequencia = 7):
    if tendencia not in ['n', 'c', 't', 'ct']:
        print('el argumento tendencia tiene que ser igual a uno de los siguientes valores [n, c, t ,ct]')
    
    
    #PASO 0: INSUFICIENTES DATOS:
    if len(serie) < 20:
        modelo_final = np.mean(serie)
        print('DATOS INSUFICIENTES, LA PREDICCIÓN ES LA MEDIA')
    else: 


        # EL PASO 1. IDENTIFICACIÓN 
        
        # TRANSFORMACION LOGARITMICA
        if ((np.min(serie) > 0) & (adfuller(serie)[1] > 0.05)):
            serie = np.log(serie) 

        #DIFERENCIACION CON DICKEY-FULLER    
        if adfuller(serie)[1] > 0.05:
            d = 1
            print('La serie se ha diferenciado 1 vez')

        if adfuller(np.diff(serie))[1] > 0.05:
            d = 2
            print('La serie se ha diferenciado 2 vez')
        else:
            d = 0



        ## 2. ESTIMACION

       # Creas el orden maximo de 3
        Qs = range(0, maxQs)
        qs = range(0, maxqs)
        Ps = range(0, maxPs)
        ps = range(0, maxps)
        parameters = product(ps, qs, Ps, Qs)
        parameters_list = list(parameters)
        len(parameters_list)

        # # RECORREMOS LA LISTA ITERANDO MODELOS Y LOS GUARDAMOS EN UNA LISTA
        lista_modelos = []


        for i in parameters_list:
            try:
                q = i[0]
                p = i[1]
                Q = i[2]
                P = i[3]
                #print(q,p)
                arima_nc = sm.tsa.statespace.SARIMAX(serie, order = (q,d,p), 
                                                     seasonal_order=(Q,0, P, frequencia),initialization='approximate_diffuse' ).fit(disp = False, trend = tendencia, enforce_invertibility = False)
            except ValueError:
                print('wrong parameters:', q, p)
                continue
            except LinAlgError:
                print('LinAlgError wrong parameters:', q, p)
                continue   
            lista_modelos.append(arima_nc)



        ### 3. VALIDACION

        #CON ESTO NOS QUEDAMOS UNICAMENTE CON LOS MODELOS VALIDOS POR PARAMETROS

        lista_modelos_validos = []
        for i in lista_modelos:
            #print(lista_modelos)
            criterio = np.mean((i.pvalues.values < 0.05) * 1)
            #print(criterio)
            if criterio == 1.0:
                lista_modelos_validos.append(i)

        ##MODELOS CON RESIDUOS NORMALES

        lista_modelos_2_val = []

        for i in lista_modelos_validos:
            if normaltest(i.resid)[1] < 0.05:
                lista_modelos_2_val.append(i)


        #ahora hay que comparar los criterios de akaike de todos los modelos
        akaike = []
        for i in lista_modelos_2_val:
            akaike.append(i.aic)


        # NOS QUEDAMOS CON EL MODELO DE CRITERIO DE AKAIKE MAS BAJO    
        modelo_final = lista_modelos_2_val[akaike.index(min(akaike))]
        lista_modelos_2_val[akaike.index(min(akaike))]

    return(modelo_final)


# In[ ]:





# In[ ]:




