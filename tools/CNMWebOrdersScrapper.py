from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

import time
import datetime

from data.WebOrder import WebOrder
from data.WebOrderLine import WebOrderLine
from data.Product import Product


class CNMWebOrdersScrapper():

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
        # print(self.driver.page_source)

    def goToPage(self, url):
        print("Going to page " + url + " ....")
        self.driver.get(url)

    def goToPageOfYear(self, year):
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
        print("Getting the actual year page order codes...")

        ordersCodes = list()
        baseTable = self.driver.find_element_by_id("theList")
        bodyTable = baseTable.find_element_by_tag_name("tbody")
        tableRows = bodyTable.find_elements_by_tag_name("tr")
        for row in tableRows[1:]:  # skip header
            # print(row.text)
            cols = row.find_elements_by_tag_name("td")

            #cols[0] es el codigo del pedido
            #cols[1] es el nombre del usuario que hizo el pedido
            #cols[2] es la fecha del pedido
            #cols[3] es el centro de coste al cual se carga el pedido
            #cols[4] es el proveedor o vendedor al cual se dirige el pedido
            #cols[5] es el importe del pedido
            #cols[6] es el estado del pedido

            ordersCodes.append((cols[0].text,
                                cols[1].text,
                                cols[2].text,
                                cols[3].text,
                                cols[4].text,
                                cols[5].text,
                                cols[6].text))
        return ordersCodes

    def goToOrderPage(self, orderCode):
        print("Going to order code " + orderCode + " page...")
        self.driver.execute_script("purchase.viewRequest('" + orderCode + "');")


    def getOrderData(self):
        print("Getting the order data...")

        webOrder = WebOrder()

        form = self.driver.find_element_by_tag_name("form")
        form_inputs = form.find_elements_by_tag_name("input")  # form que contiene los datos de la order de compra

        #webOrder.codigo = form_inputs[0].get_attribute('value')
        #webOrder.nombre_usuario = form_inputs[1].get_attribute('value')
        #webOrder.vendedor = form_inputs[2].get_attribute('value')
        #webOrder.centro_coste = form_inputs[3].get_attribute('value')
        webOrder.responsable = form_inputs[4].get_attribute('value')
        #webOrder.status = form_inputs[5].get_attribute('value')

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
                webOrder.historia[cols[2].text] = cols[1].text

        except NoSuchElementException:
            # es posible que no exista la tabla historia en pedidos (orders) cuyo estado sea diferente a 'Passada a comanda'.
            # en estos casos no hacemos nada, simplemente mostrar un mensaje por pantalla y seguir con el proceso
            print("Pedido sin historia.")

        return webOrder
