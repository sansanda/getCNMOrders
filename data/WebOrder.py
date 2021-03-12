import json

class WebOrder():

    def __init__(self,
                 codigo = None,
                 nomre_usuario = None,
                 fecha = None,
                 vendedor = None,
                 centro_coste = None,
                 responsable = None,
                 observaciones = None,
                 status = None,
                 total = None,
                 oferta=None,
                 lineas=None,
                 historia=None):

        self.codigo = codigo
        self.nombre_usuario = nomre_usuario
        self.fecha = fecha
        self.vendedor = vendedor
        self.centro_coste = centro_coste
        self.responsable = responsable
        self.observaciones = observaciones
        self.status = status
        self.oferta = oferta
        self.lineas = lineas
        self.historia = historia
        self.total = total

    def __repr__(self):
        repr = str()
        repr = repr + " ************ Web Order ************** " + "\n"

        for a in [a for a in dir(self) if not a.startswith('__')]:

            repr = repr + a + ": " + str(self.__dict__[a]) + "\n"

        return repr
