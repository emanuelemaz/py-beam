from flask import Flask, render_template, jsonify, request
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

import json

from beamlib import Forza, Carico, Momento, Trave, getDiagrams

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

if __name__ == "__main__":
    app.run(threaded=True)
