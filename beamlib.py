import numpy as np
import plotly.express as px
import plotly.io

from settings import span_approx, config

# Definizioni delle classi.
class Trave:
    def __init__(self, len):
        self.len = len

class Forza:
    def __init__(self, val, dist, dir):
        self.val = val
        self.dist = dist
        self.dir = dir

class Carico:
    def __init__(self, qS, qD, dist, len):
        self.qS = qS
        self.qD = qD
        self.dist = dist
        self.len = len

class Momento:
    def __init__(self, val, dist):
        self.val = val
        self.dist = dist

def getAzioni(fv=None, fh=None, carichi=None, momenti=None):
    azioni = []
    if fv is not None:
        for f in fv:
            azioni.append(f)
    if fh is not None:
        for f in fh:
            azioni.append(f)
    if carichi is not None:
        for q in carichi:
            azioni.append(q)
    if momenti is not None:
        for m in momenti:
            azioni.append(m)
    return azioni

# Funzione che determina tutti i punti (nodi) della trave.
def puntiTrave(trave, fv=None, fh=None, carichi=None, momenti=None):
    puntiTrave = []
    if fv is not None:
        for f in fv:
            puntiTrave.append(float(f[1]))
    if fh is not None:
        for f in fh:
            puntiTrave.append(float(f[1]))
    if carichi is not None:
        for q in carichi:
            puntiTrave.append(float(q[2]))
            puntiTrave.append(float(q[2])+float(q[3]))
    if momenti is not None:
        for m in momenti:
            puntiTrave.append(float(m[1]))
    if len(getAzioni(fv, fh, carichi, momenti)) > 0:
        puntiTrave.append(0)
        puntiTrave.append(float(trave[0]))
    puntiTrave = list(dict.fromkeys(puntiTrave))
    puntiTrave.sort()
    return puntiTrave

def normaleP(trave, p, forze_h):
    n = 0
    for f in forze_h:
        if (f[1] < p).any():
            n -= f[0]+(p*0)
        if ((f[1] == p).all() and (p == trave[0]).all()):
            n -= f[0]+(p*0)
    if (type(n) == int):
        return np.array([0]*span_approx)
    return n

def taglioP(trave, p, forze_v, carichi):
    v = p*0
    for f in forze_v:
        if (f[1] < p).any():
            v += f[0]+(p*0)
            # NOTA: si aggiunge +p*0 perché altrimenti il linspace verrebbe appiattito ad un punto, non trovando un riferimento a se stesso (come avviene ad esempio per i carichi, dove la distanza x determina la forza verticale)
        if ((f[1] == p).all() and (p == trave[0]).all()):
            v += f[0]+(p*0)
        if ((p == 0).any() and (f[1] == p).any()):
            v += p*0
    for q in carichi:
        if (q[2] < p).any():
            if (p > q[2]).any() and (p < q[2]+q[3]).any():
                x_taglio = p-q[2]
            else:
                x_taglio = q[3]+(p*0)
            if (q[0] == 0 or q[1] == 0):
                if q[0] == 0:
                    v += (q[1]/(2*q[3]))*(x_taglio)**2
                if q[1] == 0:
                    v += -(q[0]/(2*q[3]))*(x_taglio)**2+(q[0]*(x_taglio))
            if (q[0] < q[1] or q[1] < q[0]) and q[1] != 0 and q[0] != 0:
                v += ((q[1]-q[0])/(2*q[3]))*(x_taglio)**2+(q[0]*(x_taglio))
            if q[0] == q[1]:
                v += q[0]*(x_taglio)
    return v

def momentoP(trave, p, forze_v, carichi, momenti):
    m = p*0
    for mo in momenti:
        if (mo[1] < p).any():
            m += mo[0]+(p*0)
            # NOTA: si aggiunge +p*0 perché altrimenti il linspace verrebbe appiattito ad un punto, non trovando un riferimento a se stesso (come avviene ad esempio per i carichi, dove la distanza x determina la forza verticale)
        if ((mo[1] == p).all() and (p == trave[0]).all()):
            m += mo[0]+(p*0)
    for f in forze_v:
        if (f[1] < p).any():
            m += f[0]*(p-f[1])+(p*0)
        if (f[1] == p).any() and (p == 0).any():
            m += (p*0)
    for q in carichi:
        if (q[2] < p).any():
            if (p > q[2]).any() and (p < q[2]+q[3]).any():
                x = p-q[2]
                b_t1 = (p-q[2])/3
                b_t2_1 = (p-q[2])/2
                b_t2_2 = (2/3)*(p-q[2])
                b_tr1_1 = (p-q[2])/2
                b_tr1_2 = (p-q[2])/3
                b_tr2_1 = (p-q[2])/2
                b_tr2_2 = (2/3)*(p-q[2])
                b_ret = ((p-q[2])/2)
            else:
                x = q[3]
                b_t1 = p-q[2]-(2/3)*q[3]
                b_t2_1 = p-q[2]-q[3]/3
                b_t2_2 = 0
                b_tr1_1 = p-q[2]-q[3]/2
                b_tr1_2 = p-q[2]-(2/3)*q[3]
                b_tr2_1 = p-q[2]-q[3]/2
                b_tr2_2 = p-q[2]-q[3]/3
                b_ret = p-q[2]-(q[3]/2)

            if q[0] == 0 or q[1] == 0:
                if q[0] == 0:
                    m += ((q[1]/(2*q[3]))*x**2)*(b_t1)
                if q[1] == 0:
                    m += (((-q[0]/q[3])*x**2)+q[0]*x)*b_t2_1
                    m += ((q[0]/(2*q[3]))*x**2)*b_t2_2
            if (q[0] < q[1] or q[0] > q[1]) and q[1] != 0 and q[0] != 0:
                if q[0] > q[1]:
                    m += (q[0]*x)*(b_tr1_1)
                    m += (((q[1]-q[0])/(2*q[3]))*x**2)*(b_tr1_2)
                if q[0] < q[1]:
                    m += (((q[1]-q[0])/q[3])*x**2+q[0]*x)*(b_tr2_1)
                    m += (((q[0]-q[1])/(2*q[3]))*x**2)*(b_tr2_2)
            if q[0] == q[1]:
                m += (q[0]*(x))*b_ret
    return m

def getDiagrams(trave, forzeList=None, carichiList=None, momentiList=None):
    # Creazioni liste e array numpy (le liste vengono convertite successivamente).
    Fv, Fh, Q, M, T = [], [], [], [], np.array([0])
    
    T[0] = np.array([trave.len])
    for forza in forzeList:
        if type(forza.dir) == float or type(forza.dir) == int:
            Fv.append(np.array([forza.val*np.sin(np.deg2rad(float(forza.dir))), forza.dist]))
            Fh.append(np.array([forza.val*np.cos(np.deg2rad(float(forza.dir))), forza.dist]))
        else:
            if(forza.dir.upper()) == "V":
                Fv.append(np.array([forza.val, forza.dist]))
            if (forza.dir.upper()) == "H":
                Fh.append(np.array([forza.val, forza.dist]))
    if carichiList is not None:
        for carico in carichiList:
            Q.append(np.array([carico.qS, carico.qD, carico.dist, carico.len]))
    if momentiList is not None:
        for momento in momentiList:
            M.append(np.array([momento.val, momento.dist]))
    print(f"Trave: {T}")
    print(f"Forze verticali: {Fv}")
    print(f"Forze orizzontali: {Fh}")
    print(f"Carichi: {Q}")
    print(f"Momenti: {M}")
    print(f"Punti della trave: {puntiTrave(trave=T, fv=Fv, fh=Fh, carichi=Q, momenti=M)}")

    puntiTrave_N = puntiTrave(trave=T, fh=Fh)
    puntiTrave_T = puntiTrave(trave=T, fv=Fv, carichi=Q)
    puntiTrave_M = puntiTrave(trave=T, fv=Fv, carichi=Q, momenti=M)

    puntiN_x = np.zeros(1)
    puntiN_y = np.zeros(1)
    puntiT_x = np.zeros(1)
    puntiT_y = np.zeros(1)
    puntiM_x = np.zeros(1)
    puntiM_y = np.zeros(1)

    for i, p in enumerate(puntiTrave_N):
        x0 = p
        try:
            x1 = puntiTrave_N[i+1]
        except:
            x1 = T[0]
        x = np.linspace(x0,x1,span_approx)
        y = normaleP(T, x, forze_h=Fh)
        puntiN_x = np.append(puntiN_x, x)
        puntiN_y = np.append(puntiN_y, y)


    normale = px.line(x=puntiN_x, y=puntiN_y, labels={"x":"Distanza (m)", "y": "Sforzo normale (kN)"}, title="Diagramma di sforzo normale", color_discrete_sequence=["rgba(0,0,0,0)"])
    normale.add_scatter(x=puntiN_x, y=puntiN_y, fill="tozeroy", fillcolor="rgba(226,40,40,0.25)", line=dict(color="red", width=1.5), hoverinfo="skip")
    normale.add_scatter(x=[0,T[0]], y=[0,0], line=dict(color="black", width=1.5), hoverinfo="skip")
    normale.update_xaxes(range=[-0.1,T[0]+0.1])
    normale.update_layout(showlegend=False, hovermode="closest")

    for i, p in enumerate(puntiTrave_T):
        x0 = p
        try:
            x1 = puntiTrave_T[i+1]
        except:
            x1 = T[0]
        x = np.linspace(x0,x1,span_approx)
        y = taglioP(T, x, forze_v = Fv, carichi=Q)
        puntiT_x = np.append(puntiT_x, x)
        puntiT_y = np.append(puntiT_y, y)
    
    taglio = px.line(x=puntiT_x, y=puntiT_y, labels={"x":"Distanza (m)", "y": "Sforzo di taglio (kN)"}, title="Diagramma di taglio", color_discrete_sequence=["rgba(0,0,0,0)"])
    taglio.add_scatter(x=puntiT_x, y=puntiT_y, fill="tozeroy", fillcolor="rgba(0,216,230,0.25)", line=dict(color="blue", width=1.5), hoverinfo="skip")
    taglio.add_scatter(x=[0,T[0]], y=[0,0], line=dict(color="black", width=1.5), hoverinfo="skip")
    taglio.update_xaxes(range=[-0.1,T[0]+0.1])
    taglio.update_layout(showlegend=False, hovermode="closest")
    
    for i, p in enumerate(puntiTrave_M):
        x0 = p
        try:
            x1 = puntiTrave_M[i+1]
        except:
            x1 = T[0]
        x = np.linspace(x0, x1, span_approx)
        y = momentoP(T, x, forze_v=Fv, carichi=Q, momenti=M)
        puntiM_x = np.append(puntiM_x, x)
        puntiM_y = np.append(puntiM_y, y)

    puntiM_y_conv = puntiM_y*(-1)
    momento = px.line(x=puntiM_x, y=puntiM_y_conv, labels={
                    "x": "Distanza (m)", "y": "Momento flettente (kNm)"}, title="Diagramma del momento", color_discrete_sequence=["rgba(0,0,0,0)"])
    momento.add_scatter(x=puntiM_x, y=puntiM_y_conv, fill="tozeroy",
                        fillcolor="rgba(20,200,20,0.25)", line=dict(color="green", width=1.5), hoverinfo="skip")
    momento.add_scatter(x=[0, T[0]], y=[0, 0], line=dict(
        color="black", width=1.5), hoverinfo="skip")
    momento.update_xaxes(range=[-0.1, T[0]+0.1])
    momento.update_layout(showlegend=False, hovermode="closest")

    # normale.show(config=config)
    # taglio.show(config=config)
    # momento.show(config=config)
    return [plotly.io.to_html(normale, config, full_html=False), plotly.io.to_html(taglio, config, full_html=False), plotly.io.to_html(momento, config, full_html=False)]