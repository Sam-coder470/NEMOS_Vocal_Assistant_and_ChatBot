import multiprocessing

def startNemos():
    """Lance l'assistant vocal N.E.M.O.S."""
    print("🟢 Lancement de N.E.M.O.S...")
    from main import start
    start()

def listenHotword():
    """Active la détection de hotword."""
    print("🟢 Activation de la reconnaissance des mots-clés...")
    from engine.features import hotword
    hotword()

if __name__ == '__main__':
    p1 = multiprocessing.Process(target=startNemos)
    p2 = multiprocessing.Process(target=listenHotword)

    p1.start()
    p2.start()

    p1.join()
    p2.join()  # Ajout du join pour éviter un arrêt prématuré

    print("🛑 Système arrêté.")
