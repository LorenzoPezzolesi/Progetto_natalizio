# Progetto_natalizio

Questo codice implementa una versione del gioco UNO utilizzando Flask per l'interfaccia web. Il gioco include funzionalità di base come la gestione di un mazzo di carte, la gestione dei giocatori, e le regole per l'esecuzione dei turni. L'applicazione consente a due giocatori (uno umano e uno controllato dal computer) di giocare a UNO tramite un'interfaccia web.

## Struttura del Codice
Il codice è organizzato in più classi che gestiscono i vari aspetti del gioco:

### Card: 
Rappresenta una carta del gioco. Ogni carta ha un colore (es. "red", "green", "blue", "yellow" o "wild") e un valore (es. numero o effetto).

### Deck: 
Rappresenta un mazzo di carte. Ha metodi per creare il mazzo, mischiarlo, estrarre carte e ottenere la carta in cima al mazzo.

### Player: 
Rappresenta un giocatore. Ogni giocatore ha un nome e un elenco di carte. I giocatori possono aggiungere o rimuovere carte, e dichiarare "UNO" quando hanno solo una carta.

### Game: 
Gestisce lo stato del gioco, inclusi i turni dei giocatori, la gestione delle carte giocate, l'esecuzione degli effetti delle carte speciali (come "reverse", "skip", "picker", e "pick_four"), e la verifica delle condizioni di vittoria.

### Flask app: 
Un'applicazione web Flask che gestisce le richieste HTTP. La logica del gioco viene eseguita su ogni richiesta, e il risultato (compreso lo stato del gioco) viene inviato al client attraverso il rendering del template HTML.

## Funzionamento del Gioco
Il gioco funziona con due giocatori:

1) Il giocatore umano che può scegliere di: pescare una carta, passare il turno, giocare una carta, o dichiarare "UNO".
2) Un avversario controllato dal computer che gioca automaticamente ogni turno.
I giocatori si alternano nei turni. Il mazzo di carte viene mischiato inizialmente e ciascun giocatore riceve 7 carte. Durante ogni turno, un giocatore può giocare una carta che corrisponde al colore o al valore della carta in cima al mazzo, oppure può pescare una carta dal mazzo.

Gli effetti speciali delle carte (come "reverse", "skip", "picker", e "pick_four") influenzano il flusso del gioco e possono modificare l'ordine dei turni o aggiungere carte ai giocatori.

## Dipendenze
### Flask: Web framework per Python.
### random: Per mescolare il mazzo di carte.
