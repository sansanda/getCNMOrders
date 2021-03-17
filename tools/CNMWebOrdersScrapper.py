import unicodedata

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

import time
import datetime

from data.WebOrder import WebOrder
from data.WebOrderLine import WebOrderLine
from data.Product import Product


class CNMWebOrdersScrapper():
    """ Clase CNMWebOrdersScrapper para permitir el acceso a la intranet del IMB-CNM-CSIC utlizando
        herramientas como selenium con el objetivo de automatizar ciertas tareas para la obtención
        del historico de compras del usuario que se identifique con su user y password
    """

    def __init__(self, driver, login_url, orders_url, user, password, first_count_year, startYear, lastYear):
        self.driver = driver
        self.login_url = login_url
        self.orders_url = orders_url
        self.user = user
        self.password = password
        self.firstCountYear = first_count_year
        self.startYear = startYear
        self.lastYear = lastYear
        self.actualYear = datetime.datetime.now().year

    def doLogin(self):
        """
        Metodo que accede a la intranet del cnm utilizando los parámetros login_url, orders_url, user y password
        pasados duarnte la fase de creacion de la instancia (constructor)
        :return: None
        """
        print("Doing login to page " + self.login_url)

        self.driver.get(self.login_url)

        login_user = self.driver.find_element_by_id('login_user')
        login_password = self.driver.find_element_by_id('login_password')
        login_btn = self.driver.find_element_by_id('login_btn')
        login_user.send_keys(self.user)
        login_password.send_keys(self.password)
        login_btn.click()

        # volvemos a pedir la pagina, esta vez ya logeados
        self.driver.get(self.login_url)

    def goToPage(self, url):
        """
        Metodo para la direccion a cualquiera de las páginas de la intranet del cnm.
        Se da por hecho que, al llamar al método, ya estamos logeados y dentro de la intranet del IMB, en pagina de
        inicio (https://intranet.imb-cnm.csic.es/intranet/index.php)
        :param url: La url de la pagina a la cualse quiere acceder
        :return: None
        """
        print("Going to page " + url + " ....")
        self.driver.get(url)

    def goToPageOfYear(self, year):
        """
        Metodo que permite acceder a la pagina web de la intranet del IMB correspondiente al
        listado de ordenes de compra correspopndiente al año indicado como pámetro.
        Se da por hecho que, al llamar al método, estamos en la página web del listado de solicitudes (https://intranet.imb-cnm.csic.es/intranet/compres/list.php)
        :param year: El año del cual queremos ver el listado de compras
        :return: None
        """
        correctedYear = year

        if year > self.actualYear:
            correctedYear = self.actualYear
        elif year < self.firstCountYear:
            correctedYear = self.firstCountYear

        print("Going to page of year " + str(correctedYear) + " ....")

        self.driver.execute_script("purchase.listRequests(" + str(correctedYear) + ",1,'Tot');")

    #        for year in range(self.actualYear, year, -1):
    #            time.sleep(2)
    #            self.driver.execute_script('purchase.prevRequests();')

    def getActualYearPage_OrdersList(self):

        """
        Metodo que permite recorrer la lista de todas las ordenes de compra correspondientes a la pagina (año) en la
        cual nos encontremos
        :return: list de tuplas donde cada tupla contiene los datos correspondientes a cada orden de compre.
        (codigo_pedido, usuario, fecha, centro de coste, vendedor, importe total, estado del pedido)
        """
        print("Getting the actual year page order codes...")

        ordersCodes = list()
        baseTable = self.driver.find_element_by_id("theList")
        bodyTable = baseTable.find_element_by_tag_name("tbody")
        tableRows = bodyTable.find_elements_by_tag_name("tr")
        for row in tableRows[1:]:  # skip header
            # print(row.text)
            cols = row.find_elements_by_tag_name("td")

            # cols[0] es el codigo del pedido
            # cols[1] es el nombre del usuario que hizo el pedido
            # cols[2] es la fecha del pedido
            # cols[3] es el centro de coste al cual se carga el pedido
            # cols[4] es el proveedor o vendedor al cual se dirige el pedido
            # cols[5] es el importe del pedido
            # cols[6] es el estado del pedido

            ordersCodes.append((cols[0].text,
                               cols[1].text,
                               cols[2].text,
                               cols[3].text,
                               cols[4].text,
                               cols[5].text,
                               cols[6].text))
        return ordersCodes

    def goToOrderPage(self, orderCode):
        """
        Método que permite el acceso a la página web con los detalles ede una orden de compra identificada por el parametro de entrada orderCOde.
        Se da por hecho que,al ejecutar el método, nos encontramos en la pagina con el listado de ordenes de compra para un año determinado.
        :param orderCode: Con el código de orden de compravpara poder acceder a la página web con los detalles de la orden de compra.
        [lineas, historico, responsable, etc...]
        :return: None
        """
        print("Going to order code " + orderCode + " page...")
        self.driver.execute_script("purchase.viewRequest('" + orderCode + "');")

    def getOrderData(self):
        """
        Metodo que permite recopilar los detalles de una orden de compra.
        Se da por hecho que, al ejecutar dicho método, nos encontramos en la página web que muestra los detalles de
        dicha orden de compra.
        :return: WebOrder con los detalles de una orden de compra en concreto.
        """
        print("Getting the order data...")

        webOrder = WebOrder()

        form = self.driver.find_element_by_tag_name("form")
        form_inputs = form.find_elements_by_tag_name("input")  # form que contiene los datos de la order de compra

        # webOrder.codigo = form_inputs[0].get_attribute('value')
        # webOrder.nombre_usuario = form_inputs[1].get_attribute('value')
        # webOrder.vendedor = form_inputs[2].get_attribute('value')
        # webOrder.centro_coste = form_inputs[3].get_attribute('value')
        webOrder.responsable = form_inputs[4].get_attribute('value')
        # webOrder.status = form_inputs[5].get_attribute('value')

        # la tabla que contiene las lineas del pedido a veces carecen de body
        #        poTableRows = form.find_element_by_id("poTable").\
        #                find_element_by_tag_name("tbody"). \
        #                find_elements_by_tag_name("tr")

        poTableRows = form.find_element_by_id("poTable"). \
            find_elements_by_tag_name("tr")

        webOrderLines = list()

        # obtenemos todas las lineas del pedido
        for row in poTableRows[2:-1]:  # skip first two lines and last row
            # print(row.text)
            cols = row.find_elements_by_tag_name("td")
            webOrderLine = WebOrderLine()
            product = Product()
            product.vendedor = webOrder.vendedor
            product.referencia_vendedor = cols[0].text
            product.unidad_embalaje = cols[1].text

            descripcion_sin_acentos = \
                ''.join((c for c in unicodedata.normalize('NFD', cols[2].text) if unicodedata.category(c) != 'Mn'))

            product.descripcion = cols[2].text

            try:
                precio = float(str(cols[3].text).replace(".", "").replace(",", "."))
            except ValueError:
                print("Sorry, that's not a valid float. We will set precio unitario to 0")
                precio = float(0)

            product.precio_unitario = precio

            webOrderLine.product = product

            try:
                cantidad = int(str(cols[4].text).split(",")[0])
            except ValueError:
                print("Sorry, that's not a valid int. We will set cantidad to 0")
                cantidad = int(0)

            webOrderLine.cantidad = cantidad

            # no tenemos en cuenta la 6 columna del total. Ya la calculamos nosotros
            webOrderLine.total = webOrderLine.cantidad * product.precio_unitario
            webOrderLines.append(webOrderLine)

        webOrder.lineas = webOrderLines

        # inicializamos la historia del pedido como un diccionario de fechas a notas
        webOrder.historia = dict()

        # Accedemos a la historia del pedido
        try:
            actionsListTableRows = form.find_element_by_id("actions_list"). \
                find_elements_by_tag_name("tr")

            for row in actionsListTableRows[1:]:  # skip first line (the head)
                cols = row.find_elements_by_tag_name("td")
                col1_sin_acentos = \
                    ''.join((c for c in unicodedata.normalize('NFD', cols[1].text) if unicodedata.category(c) != 'Mn'))
                col2_sin_acentos = \
                    ''.join((c for c in unicodedata.normalize('NFD', cols[2].text) if unicodedata.category(c) != 'Mn'))
                webOrder.historia[cols[2].text] = cols[1].text

        except NoSuchElementException:
            # es posible que no exista la tabla historia en pedidos (orders) cuyo estado sea diferente a 'Passada a comanda'.
            # en estos casos no hacemos nada, simplemente mostrar un mensaje por pantalla y seguir con el proceso
            print("Pedido sin historia.")

        return webOrder
