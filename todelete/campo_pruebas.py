import pickle
from data.Product import Product
from data.WebOrderLine import WebOrderLine
from data.WebOrder import WebOrder

import json
import jsonpickle
import pandas as pd

def main():
    float_string = "1,25.00"
    f = float(str(float_string).replace(".", "").replace(",","."))
    print(f)

    l1 = [1,2,3,4,5]

    print(l1)
    savingFilePath = './persistence/data'
    #fase de volcado de las ordenes de compra del listado webOrders a un fichero usando pickle
    pickle.dump(l1, open(savingFilePath + '/cnmOrders.pickle', 'wb'))

    l2 = pickle.load(open(savingFilePath + '/cnmOrders.pickle', 'rb'))

    print(l2)


    p = Product("IDM","ref vendedor","un fabricante","ref fabricante","UN","una descp",1.258)
    p2 = Product("Amidata", "ref vendedor", "un fabricante", "ref fabricante", "UN", "una descp", 1.2454558)


    wol = WebOrderLine(p,1,252)
    wol2 = WebOrderLine(p2, 2, 22)

    wols = list()
    wols.append(wol)
    wols.append(wol2)

    wo = WebOrder("0102","david","amidata","hiper","XJ","obs","status",2222,None,wols,None)

    wolJSONData = json.dumps(wols, indent=4, cls=WebOrderLine.WebOrderLineEncoder)
    print(wolJSONData)

    df = pd.read_json(wolJSONData)
    df.to_csv('test.csv', encoding='utf-8', index=False)





if __name__ == "__main__":
    main()

