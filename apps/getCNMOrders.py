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

    """
    Clase principal que ejecuta una serie de pasos con el objetivo de acceder y guardar (serializar, json y csv) todos los datos de las ordenes de compra
    (del imb-cnm-csic) de un periodo de tiempo marcado por dos años (parámetros de entrada) dado un usuario y pass determinado.
    Más tarde dicho csv puede ser importado por un programa de tratamiento de datos como excel y realizar filtros (p.e. por proveedor, etc...)
    :return: None
    """
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

    # fase de obtención de todos los datos correspondientes a los pedidos hechos y registrados en la web del cnm para el usuario dado como parámetro de entrada
    for y in range(from_year, to_year + 1):

        # una vez en la página del listado de solicitudes de compra de la intranet del cnm nos dirigimos al listado del año y
        cnmWebOrdersScrapper.goToPageOfYear(y)
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

    # fase de volcado de las ordenes de compra del listado webOrders a un fichero usando pickle
    pickle_file = open(savingFilePath + '/cnmOrders.pickle', 'wb')
    pickle.dump(webOrders, pickle_file)

    # fase de volcado de las ordenes de compra del listado webOrders a un fichero de texto human-readable (json)
    json_pickle_file = open(savingFilePath + '/cnmOrders.json', 'w')
    json_pickle_file.write(jsonpickle.encode(webOrders, unpicklable=False))

    # fase de volcado de las lineas de las ordenes de compra del listado webOrders a un fichero de texto human-readable (csv)
    allWebOrders_Lines = list()
    for webOrder in webOrders:
        for webOrderLine in webOrder.lineas:

            try:
                webOrderLine.product.vendedor = webOrder.vendedor
                webOrderLine.fechaCompra = webOrder.fecha   # fecha en la que se da de alta una nueva solicitud de compra
                                                            # en el sistema de compras de administracion del cnm
            except KeyError:
                # es posible que no exista historico en pedidos (orders) cuyo estado sea diferente a 'Passada a comanda'.
                # en estos casos no hacemos nada, simplemente mostrar un mensaje por pantalla y seguir con el proceso
                print("Pedido sin historia. No es posible acceder a la fecha del pedido")

            allWebOrders_Lines.append(webOrderLine)

    #Transformación de todas las ordenes de compra a objeto json
    wolsJSONData = json.dumps(allWebOrders_Lines, indent=4, cls=WebOrderLine.WebOrderLineEncoder)
    print(wolsJSONData)

    #transformacion de json a df de pandas (paso intermedio con el objetivo de usar pandas para guardar las ordenes de compra en formato csv)
    df = pd.read_json(wolsJSONData)

    #volcado de las ordenes de compra a csv
    df.to_csv(savingFilePath + '/cnmOrders.csv', encoding='utf-8', index=False)

    # fase de finalización
    driver.close()


if __name__ == "__main__":
    main()
