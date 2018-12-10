from examples.graphics import *
from math import *
import numpy as np
from pynput.mouse import Controller

TITLE = "Prototipo"
FILE = "best.txt"
WIN_Y = 400
WIN_X = 1000
MARGIN_Y = 100
MARGIN_X = 50

CIRCLE_SIZE = 10
CIRCLE_COL = "RED"
RECT_WIDTH = 50
RECT_HEIGHT = 20
RECT_COL = "blue"
LINE_WIDTH = 5


# Comienzo con aleatoriedad ?
RAND_START = False
# Valores iniciales simulacion
INIT_VALUE = np.array([WIN_X/2, 0.2, 0.3]) # q, tita1, tita2
# Valores iniciales derivadas
INIT_VALUE_P = np.array([0,0,0])
G = 9.8 # Gravedad
H = 0.1 # Paso iteracion
D = 1000 # Amortiguacion
M = 100 # Masa carretilla
M1 = 10
M2 = 10
L1 = 70
L2 = 120
DRAG = 0.99

# Valores net neuronal
SIZE = [6, 20,20,  1]
LIMIT = 100000
LIMIT_TRAIN = LIMIT // 1
MAX_FORCE = 600000
NORM = [[WIN_X, pi,pi],[10,10,10]] # Normalizar entrada

# Valores de genetica
GENERATIONS = 1000 # Generaciones totales
POBLATION = 100 # Tamaño de la poblacion inicial 
SURVIVORS = 10 # Seleccion de los mejores
MUTATE_PROB = 0.8 # Probabilidad de que ocurra una mutacion lineal
MUTATE_LINEAL = 0.01 # Valor alrededor del cual se suma o resta
MUTATE_CHANGE = 0.01 # Probabilidad de dar nuevo valor
COMBINATION_PROB = 0.4 # Probabilidad de heredar parametros de primer padre
LOSSER_KEEP = 5
OUT = 30 # Si pasan mas de x ciclos, se reinicia


def circle(win,p):
    c = Circle(p,CIRCLE_SIZE)
    c.setFill(CIRCLE_COL)
    c.draw(win)
    return c
def rect(win,p1,p2):
    r = Rectangle(p1,p2)
    r.setFill(RECT_COL)
    r.draw(win)
    return r
def line(win,p1,p2):
    l = Line(p1,p2)
    l.setWidth(LINE_WIDTH)
    l.draw(win)
    return l
def init(win,y):
    # q -> posicion x de la caja
    # tita1 -> angulo (rad) respecto la vertical (derecha positivo, izquierda negativo) de la primera barra
    # tita2 -> angulo (rad) respecto la vertical de la segunda barra

    q, tita1, tita2 = y
    q0 = np.array([q,0])
    q1 = np.array([q + L1*sin(tita1), L1*cos(tita1)])
    q2 = q1 + np.array([L2*sin(tita2), L2*cos(tita2)])

    q0 += MARGIN_Y
    q1 += MARGIN_Y
    q2 += MARGIN_Y

    p0 = Point(*q0)
    p1 = Point(*q1)
    p2 = Point(*q2)

    pr1 = Point(q0[0]-RECT_WIDTH/2,q0[1])
    pr2 = Point(q0[0]+RECT_WIDTH/2,q0[1]+RECT_HEIGHT)

    win.setBackground("white")
    l1=line(win,p0,p1)
    l2=line(win,p1,p2)

    c1=circle(win,p1)
    c2=circle(win,p2)
    
    r=rect(win,pr1,pr2)

    return l1,l2,c1,c2,r

def graf(win, y, obj ):

    undraw(win,obj)
    obj = init(win,y)

    return obj 
def undraw(win,obj):
    for o in obj:
        o.undraw()

def play(win):
    win.autoflush = False
    mouse = Controller()
    y = INIT_VALUE
    yp = INIT_VALUE_P
    x = np.array([y,yp])
    u = 0.0
    obj = init(win,y) 
    obj = graf(win, tuple(y), obj)


    for i in range(1000000):
        u,_ = mouse.position 
        u = (u-500)*100
        x = itera(x,u,H/2)
        x[0][0] = max(min(x[0][0], WIN_X-MARGIN_X*3),  MARGIN_X)
        obj = graf(win, tuple(x[0]), obj)
        win.flush()
        undraw(win,obj)
        #if i % 100:
            #print(u)


# ------------------------------ Simulacion -----------------

def Mf(y):
    _, tita1, tita2  = tuple(y)
    Mm = np.array( [[ M+M1+M2, L1*(M1+M2)*cos(tita1), M2*L2*cos(tita2)],
                    [ L1*(M1+M2)*cos(tita1), L1**2*(M1+M2), L1*L2*M2*cos(tita1-tita2)],
                    [ L2*M2*cos(tita2), L1*L2*M2*cos(tita1-tita2), L2**2*M2]])
    return Mm
def f(y,yp,u):
    _, tita1, tita2  = tuple(y)
    qp, tita1p, tita2p  = tuple(yp)
    f = np.array([ L1*(M1+M2)*tita1p**2*sin(tita1) + M2*L2*tita2p**2*sin(tita2),
                    -L1*L2*M2*tita2p**2*sin(tita1-tita2) + G*(M1+M2)*L1*sin(tita1),
                    L1*L2*M2*tita1p**2*sin(tita1-tita2)+G*L2*M2*sin(tita2)])
    f = f - np.array([ D*qp, D*tita1p, D*tita2p]) + np.array([ u, 0, 0])
    return f
def derFunc(y,yp,u):
    inv = np.linalg.inv(Mf(y))
    return np.array([yp, np.dot(inv,f(y,yp,u))])
def itera(x,u,h):
    a = derFunc(*x,u=u)
    b = derFunc(*(x+h/2*a),u=u)
    c = derFunc(*(x+h/2*b),u=u)
    d = derFunc(*(x+h*c),u=u)
    return x + h/6 *(a+ 2*b + 2*c + d)


def check(y,yp,u):
    print("M: {}".format(Mf(y)))
    print("f: {}".format(f(y,yp,u)))
    print("derFunc: {}".format(derFunc(y,yp,u)))
    print("iter: {}".format(itera(y,yp,u,H)))
# ------------------------------- Network Neuronal -----------
class Network(object):
    """ Network neuronal simple
    """
    @staticmethod
    def rectified_linear(v):
        return np.vstack([x if x > 0 else 0 for x in v])

    @staticmethod
    def arctan(v):
        return np.vstack([atan(x) for x in v])

    def __init__(self, sizes):
        self.sizes = sizes
        self.layers = len(sizes)

    def initialize(self):
        self.bias = [np.random.randn(i, 1) / i for i in self.sizes[1:]]
        self.weights = [np.random.randn(j, i) / (j + i)
                        for i, j in zip(self.sizes[:-1], self.sizes[1:])]

    def feedforward(self, inp):
        for w, b in zip(self.weights[:-1], self.bias[:-1]):
            inp = Network.arctan(np.dot(w, inp) + b)
        inp = Network.arctan(np.dot(self.weights[-1], inp) + self.bias[-1])
        return inp

# ------------------------------ Genetica ---------------

def evaluate(net,limit,grf = False, win = None, end = True):
    y = INIT_VALUE + np.random.randn(3)/2 if RAND_START else INIT_VALUE
    yp = INIT_VALUE_P
    x = np.array([y,yp])
    u = 0.0
    if grf:
        win.autoflush = False
        obj = init(win,y) 
        obj = graf(win, tuple(y), obj)

    punt = 0

    for i in range(limit):
        aux = x[:,:]
        aux = np.divide(aux,NORM)
        u = net.feedforward(np.vstack([np.vstack(o) for o in aux]))
        x = itera(x,u[0][0]*MAX_FORCE,H)

        #x[0][0] = max(min(x[0][0], WIN_X-MARGIN_X*3),  MARGIN_X)
        if x[0][0] > WIN_X-MARGIN_X*3:
            x[0][0] = MARGIN_X
        if x[0][0] < MARGIN_X:
            x[0][0] = WIN_X-MARGIN_X*3

        x[1][0] *= DRAG

        if grf:
            obj = graf(win, tuple(x[0]), obj)
            win.flush()
            #if limit / 10:
                #print("u: {}".format(u[0][0]))
        _, tita1, tita2 = x[0]
        punt += i #- (1-abs(u[0][0]))**2
        if end and (L2*cos(tita2) < 0 or  L1*cos(tita1)) < 0:
            break

    if grf:
        undraw(win,obj)
    return punt

def mutate(v):
    random_value = np.random.rand(len(v))
    r = np.random.rand(len(v))
    v = [x+(c-0.5)*MUTATE_LINEAL if rv < MUTATE_PROB else x for x,c,rv in zip(v,r,random_value) ]
    random_value = np.random.rand(len(v))
    r = np.random.rand(len(v))
    v = [x if rv > MUTATE_CHANGE else c for x,c,rv in zip(v,r,random_value)]
    return v

def combine(neta,netb):
    net = Network(neta.sizes)
    wa = neta.weights
    wb = netb.weights
    mnew = []
    for ma,mb in zip(wa,wb):
        shape = ma.shape
        va = ma.flatten()
        vb = mb.flatten()    
        binom = np.random.binomial(1,COMBINATION_PROB,len(va))
        c = np.multiply(binom,va) + np.multiply([1-x for x in binom],vb)
        mnew.append(np.array(mutate(c)).reshape(shape))
    net.weights = mnew

    ba = neta.bias
    bb = netb.bias
    bnew = []
    for ca,cb in zip(ba,bb):
        shape = ca.shape
        va = ca.flatten()
        vb = cb.flatten()    
        binom = np.random.binomial(1,COMBINATION_PROB,len(va))
        c = np.multiply(binom,va) + np.multiply([1-x for x in binom],vb)
        bnew.append(np.array(mutate(c)).reshape(shape))
    net.bias = bnew

    return net



def reproduce(nets):
    networks = []
    keep = True
    while(keep):
        for na in nets:
            for nb in nets:
                if na != nb:
                    new = combine(na,nb)
                    networks.append(new)
                    if len(networks) > POBLATION:
                        keep=False
    networks.extend(nets) # Las mejores pasan sin ser modificadas

    return networks

    
def train():
    win = GraphWin(TITLE,WIN_X,WIN_Y)
    win.yUp()
    networks = []
    for p in range(POBLATION):
        net = Network(SIZE)
        net.initialize()
        networks.append(net)

    max_punt = -float("Inf")
    u = 0

    try:
        for g in range(GENERATIONS):
            print("Generacion {}".format(g))
            puntuation = [evaluate(net,LIMIT_TRAIN) for net in networks]
            best = [x for _,x in sorted(zip(puntuation,networks), key = lambda t: t[0], reverse = True)]
            aux = []
            aux.extend(best[:SURVIVORS])
            for i in range(LOSSER_KEEP):
                r = np.random.uniform(SURVIVORS-1,len(best))
                networks.append(best[floor(r)])

            networks = reproduce(best[:SURVIVORS])

            punt = evaluate(best[0], LIMIT, grf = True,win = win)
            print(best[0].weights, best[0].bias)
            print("Punts: {}".format(sorted(puntuation, reverse = True)[:SURVIVORS]))
            print("Puntuacion: {}".format(punt))

            if max_punt < punt:
                max_punt = punt
                best_net = [best[0].weights, best[0].bias]
                u = 0
            else:
                u += 1
            if u == OUT:
                nets = []
                for p in range(SURVIVORS//3,POBLATION):
                    net = Network(SIZE)
                    net.initialize()
                    nets.append(net)
                for o in range(SURVIVORS//3):
                    r = np.random.uniform(0,SURVIVORS-1)
                    nets.append(best[floor(r)])
                nets.extend(best[:2])
                networks = nets
                u = 0
                print("-------OUT-------")
    except KeyboardInterrupt:
        f = open(FILE,"w")
        f.write(str(best_net))

    f = open(FILE,"w")
    f.write(str(best_net))


    win.close()


# ------------------------------- Main -------------------

win = GraphWin(TITLE,WIN_X,WIN_Y)
win.yUp()

play(win)

#check(y,yp,u)

#train()


weights = [np.array([[ 6.34486436e-01,  5.15911415e-02, -1.38858399e-02,
        -2.18596206e-02,  2.83776628e-02, -5.15514965e-02],
       [ 4.73345043e-01, -9.33149493e-02,  7.75199349e-01,
         5.05750111e-02,  4.69783379e-02, -4.09210825e-03],
       [-3.25350186e-02,  6.49663406e-01,  4.60503464e-01,
        -4.34449496e-02,  1.41124341e-02,  4.70748389e-02],
       [-9.84707843e-02,  8.47838085e-02,  4.01928647e-02,
         9.63595548e-03,  2.43665561e-02, -5.11221653e-03],
       [ 1.44553467e-02, -2.08530675e-02,  5.61822649e-01,
         2.87979724e-02, -1.25818438e-02, -5.92073872e-03],
       [ 6.09009724e-02,  6.94812774e-03, -1.09633529e-02,
        -3.51474555e-02, -2.59139858e-02, -5.01470055e-02],
       [-6.39260019e-03,  1.43849119e-02,  3.72751306e-02,
        -5.82365066e-02,  1.61662912e-01,  6.67300423e-02],
       [-2.70415625e-02,  8.24883214e-01,  2.63053388e-02,
         5.05175552e-02,  4.70306094e-01, -7.71654979e-02],
       [ 1.59576727e-01, -5.45477928e-04,  2.69146911e-02,
         1.45370665e-02, -7.70982042e-03, -1.55880978e-02],
       [ 3.28128678e-01, -1.75891454e-02,  6.74694195e-02,
         6.87504355e-01, -3.90652469e-02,  2.95567288e-02],
       [ 3.98715990e-02,  6.96241501e-01, -3.30741410e-02,
        -1.65520680e-02, -4.27923527e-02, -1.46089020e-02],
       [-7.02728060e-02, -1.94697111e-02, -1.15879075e-01,
         8.21861933e-01,  9.15771822e-01, -2.12461762e-02],
       [-8.00073518e-02,  2.02966178e-02,  1.04598281e-02,
         4.11054874e-01,  5.30687727e-02,  7.75225173e-03],
       [ 6.36770710e-02,  3.05311841e-03,  1.73880263e-01,
         3.05714472e-02,  2.86824742e-01,  3.92735360e-02],
       [-6.43309982e-02, -6.00437578e-02, -6.72817652e-03,
         1.14236918e-02,  3.59161560e-02,  4.36088118e-01],
       [ 2.87626611e-02,  9.99099636e-02,  4.27654323e-03,
         2.35209333e-02, -1.71840553e-02,  8.69398829e-03],
       [ 6.04646851e-03,  2.82345167e-02,  1.19823350e-02,
         9.02679983e-01,  5.67169228e-02,  1.81533166e-01],
       [-2.56582867e-02, -4.47732030e-02, -4.49579812e-04,
         2.26287687e-02, -2.27867014e-02,  6.42483936e-02],
       [-2.12237692e-02,  4.50186396e-01,  2.15499452e-02,
        -4.00307085e-02,  3.42846403e-02, -2.92978610e-02],
       [ 9.17685634e-02, -3.53636910e-02, -3.71361891e-02,
         2.65037073e-02,  5.66107983e-01,  1.61645771e-01]]), np.array([[ 4.63534784e-02, -5.06903439e-03, -3.11667576e-02,
         4.15979132e-02,  3.41641290e-02, -5.66547159e-02,
         3.09246306e-01, -5.86837851e-02,  3.14274602e-02,
         6.73704838e-03,  5.38825336e-02,  3.17990583e-01,
        -3.16867619e-02, -7.17863377e-02,  1.47473989e-02,
         1.78966799e-02,  2.26293019e-02,  1.91791551e-01,
         4.42695644e-02,  5.74773247e-02],
       [ 4.54476898e-02,  6.89940551e-02, -7.22782715e-02,
         1.11247837e-02,  1.40248075e-02,  1.78329299e-01,
         2.45577826e-02,  1.22662485e-02,  6.07644442e-01,
        -5.09784106e-02,  4.58949515e-03,  4.06490623e-02,
         8.98979582e-01,  6.03842745e-02, -2.08193755e-02,
         4.77163912e-01,  2.31301755e-02, -1.71012418e-02,
         5.03861797e-02, -3.86001972e-02],
       [ 4.45252920e-02, -1.39517707e-02,  5.56602463e-01,
        -5.04109250e-03,  9.33440637e-02, -3.47917787e-03,
        -2.00011234e-02,  4.03895474e-01,  1.67013665e-02,
        -6.82930470e-04,  5.77685813e-02,  7.79527210e-01,
        -1.94463066e-02, -2.78670196e-03,  5.87403904e-02,
         9.23367482e-03,  5.78096518e-01,  4.83763817e-03,
         3.28240962e-01, -7.27642672e-02],
       [-4.33130660e-02,  3.55649096e-01,  2.30075113e-02,
        -4.08999695e-02, -1.35132197e-02,  2.02294943e-02,
        -3.04097612e-02, -1.95821983e-02,  6.78298962e-01,
        -2.14745543e-02,  2.14201429e-02,  1.85645150e-02,
         2.53701481e-02,  4.86481305e-01,  1.39765362e-03,
         6.53955581e-02,  3.66017876e-03,  4.29583568e-01,
         9.59842121e-01, -2.38783131e-02],
       [ 1.78631851e-01,  2.89762060e-02, -1.66254340e-02,
        -1.13386713e-03,  6.94342996e-01, -1.33118033e-02,
         9.27350543e-03,  3.80933976e-01,  3.00640032e-02,
         1.87431746e-02,  2.01793381e-02,  7.68325879e-01,
         7.78963261e-03,  1.97725399e-02,  4.86790843e-02,
         3.73141602e-02,  4.57977736e-01, -3.37398844e-03,
         2.36307452e-02,  4.08797615e-02],
       [-2.59497139e-02,  2.14821959e-03,  5.53438774e-01,
        -4.07714178e-02,  6.21238017e-01,  1.08398815e-02,
        -5.74302361e-04, -3.51656542e-03,  3.10555221e-01,
         5.22951029e-03,  5.71069662e-04,  4.58441670e-02,
         1.42821630e-01,  6.93524575e-01,  2.76931933e-01,
        -1.69881420e-02,  8.82314909e-03,  1.59952877e-02,
         9.07359518e-01, -1.80189857e-02],
       [-2.35771443e-02, -1.05199824e-02, -2.41854190e-02,
        -3.10399250e-02,  3.22117207e-02,  1.76778584e-02,
        -3.21366262e-02,  7.99805634e-01, -3.14133037e-03,
        -3.10415023e-02,  9.72424594e-01, -5.06839857e-02,
         2.42579066e-02,  1.24533615e-03, -8.36043002e-03,
        -6.28316084e-03, -3.26701268e-02, -2.86211053e-02,
         8.52162174e-03,  2.02284740e-02],
       [ 8.37072711e-03,  8.06042896e-01, -2.76692067e-02,
         5.26354632e-01,  2.84232210e-02,  9.50583109e-01,
         6.10330567e-01, -3.64401830e-02,  1.36635682e-02,
         3.96279696e-01,  6.72585422e-02, -2.30335743e-02,
         2.68589082e-02, -6.09404416e-03, -5.13603435e-03,
         5.50458104e-02, -4.98239304e-02, -3.17886802e-04,
         2.69605166e-02,  9.50333978e-01],
       [-4.20086646e-02, -3.31958070e-02,  9.92337335e-01,
         3.79134165e-02, -5.01053054e-03, -2.51776507e-02,
         7.24265041e-01, -9.13091239e-03,  9.21430519e-01,
        -1.93975026e-02,  2.12357209e-02,  9.07931862e-03,
        -2.37805199e-02, -1.92610040e-02,  8.22437677e-03,
         7.07043971e-01, -5.63853641e-02,  2.05454336e-02,
        -2.51050744e-02,  1.55583095e-02],
       [ 5.95417422e-03, -6.31962709e-03,  2.14369200e-01,
         5.11201876e-01,  6.86266676e-01, -5.10089229e-02,
        -3.04146062e-03,  5.77710495e-01,  1.62644892e-02,
        -5.78762999e-02,  1.10194401e-02,  5.52373988e-01,
         1.10813147e-02, -2.04174917e-02, -2.15199276e-02,
         1.00421611e-02, -6.20940238e-02,  7.28641018e-01,
         3.21042984e-02,  9.94085013e-01],
       [-1.05463978e-02,  8.72506575e-01,  7.65438924e-03,
         1.11044329e-01,  3.46033781e-02,  2.89128552e-02,
         4.16739027e-02,  4.92849577e-01,  7.10189549e-03,
        -1.76047166e-02,  3.67895151e-01,  9.04885764e-01,
        -6.57065271e-02, -4.16971806e-03, -2.41656923e-02,
         2.19506280e-02, -1.47764867e-03, -2.77858619e-03,
         2.44916592e-02,  4.72201039e-01],
       [-4.56331722e-02,  5.30029093e-01, -1.85089916e-02,
         2.19855125e-03,  2.40878168e-01,  3.32499025e-01,
        -1.57157790e-02,  9.62442059e-01,  8.16111312e-03,
         1.90849400e-01,  9.58979737e-03,  6.17133345e-01,
        -1.50492663e-02,  4.56236382e-02,  9.84099581e-01,
        -2.58772506e-02, -5.89318319e-02, -4.53771203e-02,
         6.86189007e-04,  9.09343517e-01],
       [-3.16532195e-02,  1.93410672e-02, -3.12289406e-02,
         3.49905240e-02, -5.47770378e-04,  2.24803123e-01,
         5.59529157e-02,  3.45859287e-01, -1.75151168e-02,
        -2.32338786e-02,  4.31772149e-02, -1.63074362e-02,
         6.99296731e-03,  2.56161087e-03, -4.43857029e-02,
        -2.69474621e-03,  4.78155415e-01,  4.96529204e-02,
        -1.57563849e-03,  2.49147326e-01],
       [ 2.32236011e-02,  5.26043403e-03, -2.39189998e-02,
        -7.29719545e-03,  7.22690250e-01,  1.57821232e-01,
        -2.57871472e-02, -1.22309532e-02, -5.16940065e-02,
         3.31746512e-02,  4.63956096e-01,  3.61364902e-03,
         1.00306823e-02,  6.15664669e-03, -2.10736779e-02,
        -6.84497356e-03, -1.68068915e-02, -4.75321323e-03,
        -2.26488531e-02, -2.89926526e-03],
       [ 4.17757690e-02,  3.14771598e-06,  1.28621254e-02,
         1.99545876e-02,  9.39083197e-01,  7.50991537e-01,
         2.65790156e-02,  1.31763138e-02,  8.17811092e-03,
         2.70629925e-02, -1.42039917e-02,  8.11895349e-01,
         8.27279506e-01, -1.67707547e-02, -3.32090326e-02,
        -2.24062170e-02,  9.74938956e-01,  9.75050622e-02,
        -1.88542037e-02,  4.78046006e-02],
       [ 1.39577532e-01,  3.64645323e-02,  6.70017695e-02,
         2.31496329e-01,  5.34777824e-03, -4.91572893e-02,
         1.64705577e-01, -2.62336097e-02,  1.87135511e-03,
         3.57694409e-02, -3.27541729e-04,  1.33435452e-02,
         2.87861869e-01,  1.28294647e-02,  2.85680946e-02,
        -7.99881873e-03,  7.63804647e-01,  2.76197198e-01,
         1.97424747e-02,  2.43762735e-02],
       [ 2.62418948e-02,  2.61436564e-02,  1.70741418e-02,
        -3.70427117e-02,  5.91028138e-03,  1.33952340e-02,
        -4.51364886e-02,  1.41115840e-02, -4.50604100e-03,
         2.68399884e-02,  1.66448636e-02,  3.21056652e-01,
         2.31297956e-02, -3.64136612e-02,  5.03980703e-03,
         1.60029522e-02,  1.33703634e-02, -7.23816947e-03,
        -4.70942830e-02,  1.60149319e-02],
       [ 1.37935366e-02,  2.14574897e-02,  4.29262342e-03,
        -4.35543079e-02, -1.61353163e-02, -2.40778234e-02,
         1.80593094e-01,  9.46971082e-01,  2.25086466e-02,
        -4.33519511e-02, -2.30416415e-02,  6.04076186e-02,
        -4.84547250e-02,  9.19500625e-01,  9.77322003e-01,
        -1.06395732e-02,  6.00970343e-02,  7.57458932e-03,
        -1.21131835e-02, -1.61695469e-02],
       [ 8.60115341e-01,  1.63151637e-02, -6.80820955e-02,
        -5.97131618e-03, -8.23768231e-02,  1.65604552e-02,
         4.63445851e-01,  4.38929872e-01,  2.28794829e-02,
         2.03997079e-02, -3.20428376e-02,  3.66298496e-02,
        -3.01601559e-02,  1.59046951e-02,  2.80301139e-01,
        -7.81723354e-02,  5.23099277e-01,  6.67688434e-01,
        -1.43245626e-03,  5.15850846e-01],
       [-1.37745222e-03,  2.17686954e-03, -2.91631001e-02,
         2.73784890e-01,  2.71230529e-02,  6.39161729e-01,
        -1.71891398e-02,  4.23689640e-02,  3.51857198e-02,
         3.02609005e-02,  8.72665848e-03, -6.98820724e-03,
         1.83842417e-03,  3.18949632e-01, -5.34628105e-02,
         3.10947744e-02,  1.16314140e-02,  1.94047547e-02,
        -4.39369243e-02,  1.52702057e-02]]), np.array([[ 0.04957418,  0.03607327, -0.03694757, -0.05346097, -0.10100999,
         0.06961022,  0.96518952, -0.02289198, -0.02071049,  0.02780539,
         0.01160354, -0.04969824,  0.00653829,  0.01714441, -0.07448522,
        -0.04509584,  0.04050439,  0.0439337 ,  0.02814785, -0.02260447]])]
bias = [np.array([[ 0.08442869],
       [ 0.03189091],
       [-0.0588796 ],
       [-0.07766212],
       [-0.0633279 ],
       [ 0.0202902 ],
       [ 0.03274303],
       [ 0.05437128],
       [ 0.00556284],
       [ 0.38160516],
       [-0.04315257],
       [ 0.03428186],
       [-0.03388925],
       [-0.07273318],
       [-0.10693117],
       [ 0.64090059],
       [ 0.02927609],
       [ 0.57834671],
       [-0.09668403],
       [ 0.09204159]]), np.array([[ 0.00632018],
       [ 0.45807447],
       [-0.04547428],
       [ 0.04212764],
       [-0.04605462],
       [-0.00315373],
       [ 0.03639717],
       [ 0.18681333],
       [-0.02980134],
       [-0.06740636],
       [ 0.90868146],
       [-0.06934477],
       [ 0.74686813],
       [ 0.04375008],
       [-0.0792534 ],
       [-0.01804679],
       [-0.00484743],
       [ 0.02664154],
       [-0.07544134],
       [ 0.52149954]]), np.array([[-0.00048186]])]
net = Network(SIZE) 
net.weights = weights
net.bias = bias
evaluate(net, LIMIT, True, win,end = False)

win.close()
