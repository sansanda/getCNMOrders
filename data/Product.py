import json

class Product():

    def __init__(self,
                 vendedor=None,
                 referencia_vendedor=None,
                 fabricante=None,
                 ref_fabricante=None,
                 unidad_embalaje=None,
                 descripcion=None,
                 precio_unitario=None):

        self.vendedor = vendedor
        self.referencia_vendedor = referencia_vendedor
        self.fabricante = fabricante
        self.ref_fabricante = ref_fabricante
        self.unidad_embalaje = unidad_embalaje
        self.descripcion = descripcion
        self.precio_unitario = precio_unitario

    def __repr__(self):
        repr = str()
        repr = repr + "["

        for a in [a for a in dir(self) if not a.startswith('__')]:
            repr = repr + a + ": " + str(self.__dict__[a]) + ", "
        repr = repr[:-2]
        repr = repr + "]"

        return repr


