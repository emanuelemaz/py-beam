from flask import Flask, render_template, jsonify, request
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

import json
import numpy as np

from beamlib import Forza, Carico, Momento, Trave, getDiagrams, normaleP, taglioP, momentoP

@app.route('/')
def main():
    return render_template("home.html")

@app.route('/diag', methods=["POST"])
def diag():
    azioni = json.loads(request.form["azioni"])
    trave = json.loads(azioni["trave"])
    forze = json.loads(azioni["forze"])
    carichi = json.loads(azioni["carichi"])
    momenti = json.loads(azioni["momenti"])
    
    traveObj = Trave(0)
    forzeList = []
    carichiList = []
    momentiList = []

    for t in trave:
        traveObj = Trave(t["len"])
    for f in forze:
      forzeList.append(Forza(f["val"], f["dist"], f["dir"]))
    for q in carichi:
      carichiList.append(Carico(q["qS"], q["qD"], q["dist"], q["len"]))
    for m in momenti:
      momentiList.append(Momento(m["val"], m["dist"]))
    
    diagrammi = getDiagrams(traveObj, forzeList, carichiList, momentiList)

    diagrammiResponse = {
        "normale": diagrammi[0],
        "taglio": diagrammi[1],
        "momento": diagrammi[2]
    }
    
    return diagrammiResponse

@app.route('/pointValues', methods=["POST"])
def pointValues():
    azioni = json.loads(request.form["azioni"])
    trave = json.loads(azioni["trave"])
    forze = json.loads(azioni["forze"])
    carichi = json.loads(azioni["carichi"])
    momenti = json.loads(azioni["momenti"])

    pV = float(request.form["punto"]);
    point = np.array([pV]);
    
    Fv, Fh, Q, M, T = [], [], [], [], np.array([0])
    
    for t in trave:
        T[0] = np.array(t["len"])
    for f in forze:
      if f["dir"] == "V":
        Fv.append(np.array([f["val"], f["dist"]]))
      if f["dir"] == "H":
        Fh.append(np.array([f["val"], f["dist"]]))
      if f["dir"] != "V" and f["dir"] != "H":
        Fv.append(np.array([f["val"]*np.sin(np.deg2rad(float(f["dir"]))), f["dist"]]))
        Fh.append(np.array([f["val"]*np.cos(np.deg2rad(float(f["dir"]))), f["dist"]]))

    for q in carichi:
      Q.append(np.array([q["qS"], q["qD"], q["dist"], q["len"]]))
    for m in momenti:
      M.append(np.array([m["val"], m["dist"]]))
    
    pointValues = {
      "normale": float(normaleP(T, point, Fh)[0]),
      "taglio": float(taglioP(T, point, Fv, Q)),
      "momento": float(momentoP(T, point, Fv, Q, M))
    }

    return pointValues


if __name__ == "__main__":
    app.run(threaded=True)
