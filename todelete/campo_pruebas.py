import datetime
import json
import os
import time
import sys
import pickle
import jsonpickle

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from data.WebOrderLine import WebOrderLine
from tools.CNMWebOrdersScrapper import CNMWebOrdersScrapper

import pandas as pd


def main():


    # float_string = "1,25.00"
    # f = float(str(float_string).replace(".", "").replace(",","."))
    # print(f)
    #
    # l1 = [1,2,3,4,5]
    #
    # print(l1)
    # savingFilePath = './persistence/data'
    # #fase de volcado de las ordenes de compra del listado webOrders a un fichero usando pickle
    # pickle.dump(l1, open(savingFilePath + '/cnmOrders.pickle', 'wb'))
    #
    # l2 = pickle.load(open(savingFilePath + '/cnmOrders.pickle', 'rb'))
    #
    # print(l2)
    #
    #
    # p = Product("IDM","ref vendedor","un fabricante","ref fabricante","UN","una descp",1.258)
    # p2 = Product("Amidata", "ref vendedor", "un fabricante", "ref fabricante", "UN", "una descp", 1.2454558)
    #
    #
    # wol = WebOrderLine(p,1,252)
    # wol2 = WebOrderLine(p2, 2, 22)
    #
    # wols = list()
    # wols.append(wol)
    # wols.append(wol2)
    #
    # wo = WebOrder("0102","david","amidata","hiper","XJ","obs","status",2222,None,wols,None)
    #
    # wolJSONData = json.dumps(wols, indent=4, cls=WebOrderLine.WebOrderLineEncoder)
    # print(wolJSONData)
    #
    # df = pd.read_json(wolJSONData)
    # df.to_csv('test.csv', encoding='utf-8', index=False)

    #fase de recuperacion de los argumentos pasados durante la llamada al main
    argumentsList = sys.argv[1:]

    login_url = argumentsList[0]
    orders_url = argumentsList[1]
    user = argumentsList[2]
    password = argumentsList[3]

    # primer año con registros en la web de compras del cnm
    first_count_year = int(argumentsList[4])
    from_year = int(argumentsList[5])

    # correción from_year si es menor al primer año del cual se tienen registros en la web de compras del cnm
    if from_year < first_count_year:
        from_year = first_count_year
    to_year = int(argumentsList[6])

    # correción to_year si es mayor al año actual
    if to_year > datetime.datetime.now().year:
        to_year = datetime.datetime.now().year

    savingFilePath = argumentsList[7]

    # options en caso que queramos trabajar en silent mode, etc..
    options = Options()
    #    options.add_argument('--headless')
    #    options.add_argument('--disable-gpu')  # Last I checked this was necessary.

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    # fase de creación del scrapper
    cnmWebOrdersScrapper = CNMWebOrdersScrapper(driver,
                                                login_url,
                                                orders_url,
                                                user,
                                                password,
                                                first_count_year,
                                                from_year,
                                                to_year)

    # fase de login para entrar en la intranet del cnm
    cnmWebOrdersScrapper.doLogin()

    # fase de direccionamiento a una pagina determinada de la intranet del cnm
    cnmWebOrdersScrapper.goToPage(orders_url)

    webOrders = list()

    cnmWebOrdersScrapper.goToPageOfYear(2021)

    # espera a la carga de la pagina
    time.sleep(1)

    # recopilación de los códigos de los pedidos hechos en ese año y. Son necesarios para el acceso a cada una de las ordenes de compra
    yearOrdersList = cnmWebOrdersScrapper.getActualYearPage_OrdersList()

    for code, usuario, fecha, centro_coste, vendedor, importe, estado in yearOrdersList:
        # acceso a la orden de compra identificada por orderCode
        cnmWebOrdersScrapper.goToOrderPage(code)
        # espera a la carga de la pagina
        time.sleep(2)
        # recopilación de los datos de la orden de compra
        webOrderData = cnmWebOrdersScrapper.getOrderData()
        webOrderData.codigo = code
        webOrderData.usuario = usuario
        webOrderData.fecha = fecha
        webOrderData.centro_coste = centro_coste
        webOrderData.vendedor = vendedor
        webOrderData.total = importe
        webOrderData.status = estado

        webOrders.append(webOrderData)

        # fase de volcado de las lineas de las ordenes de compra del listado webOrders a un fichero de texto human-readable (csv)
        allWebOrders_Lines = list()
        for webOrder in webOrders:
            for webOrderLine in webOrder.lineas:

                try:
                    webOrderLine.product.vendedor = webOrder.vendedor
                    webOrderLine.fechaCompra = webOrder.fecha  # fecha en la que se da de alta una nueva solicitud de compra
                    # en el sistema de compras de administracion del cnm
                except KeyError:
                    # es posible que no exista historico en pedidos (orders) cuyo estado sea diferente a 'Passada a comanda'.
                    # en estos casos no hacemos nada, simplemente mostrar un mensaje por pantalla y seguir con el proceso
                    print("Pedido sin historia. No es posible acceder a la fecha del pedido")

                allWebOrders_Lines.append(webOrderLine)

        wolsJSONData = json.dumps(allWebOrders_Lines, indent=4, cls=WebOrderLine.WebOrderLineEncoder)
        print(wolsJSONData)

        df = pd.read_json(wolsJSONData)
        df.to_csv(savingFilePath + '/cnmOrders.csv', encoding='utf-8', index=False)

        # fase de finalización
        driver.close()

if __name__ == "__main__":
    main()

