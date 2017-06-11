#!/bin/bash

#Aquest scrip executa en un nou terminal la comanda empleada
gnome-terminal -e "python Sequencer.py"
gnome-terminal -e "python Tracker.py"
gnome-terminal -e "python PeersManager.py"
#gnome-terminal -e "python User1.py"
#gnome-terminal -e "python User2.py"
#gnome-terminal -e "python User3.py"
#gnome-terminal -e "python User4.py"

#Abans de que s'executi això, hem de tencar el Sequencer, d'aquesta manera provarem el bully
sleep 20
gnome-terminal -e "python User5.py"
