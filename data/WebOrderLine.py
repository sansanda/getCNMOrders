import json
from json import JSONEncoder

import jsonpickle


class WebOrderLine():

    def __init__(self,
                 fechaCompra=None, #Atributo no necesariamente de producto pero necesario para poder identificar la fecha de compra
                 product=None,
                 cantidad=None,
                 total=None):
        self.fechaCompra = fechaCompra
        self.product = product
        self.cantidad = cantidad
        self.total = total

    def __repr__(self):
        repr = str()
        repr = repr + "["

        for a in [a for a in dir(self) if not a.startswith('__')]:
            repr = repr + a + ": " + str(self.__dict__[a]) + ", "

        repr = repr[:-2]
        repr = repr + "]"

        return repr

    # subclass JSONEncoder
    class WebOrderLineEncoder(JSONEncoder):
        def default(self, o):

            d = o.product.__dict__
            d['fechaCompra'] = o.fechaCompra
            d['cantidad'] = o.cantidad
            d['total'] = o.total
            return d