import sys

class Processo:
	def __init__(self, tempoChegada, tempoDuracao):
		self.chegada = tempoChegada
		self.duracao = tempoDuracao
		self.tRetorno = 0
		self.tResposta = 0
		self.tEspera = 0
    	#self.OrigArrival = self.Arrival
    	#self.Response = 0
    	#self.TotalResponse = 0
    	#self.Wait = 0
    	#self.TurnAround = 0

def organiza_processos():
	processos = []
	for line in sys.stdin:
		t = str(line).replace("\r", "").replace("\n", "") # Remove possíveis \r e/ou \n
		cheg, dur = t.split()
		processos.append(Processo(int(cheg), int(dur))) # Cria e salva objetos Processo em um array

	processos.sort(key=lambda p: p.chegada) # Ordena os processos pelo tempo de chegada

	return processos

processos = organiza_processos()

#for p in processos:
#	print(p.chegada)

tempo_total = sum(map(lambda p: int(p.duracao), processos)) # Soma do tempo total necessario para todos os processos
quantum = 2

p_atual = 0 # Índice referente ao processo atual da lista de processos
for i in range(2, tempo_total):
	for p in range(p_atual, len(processos)):
		if processos[p].duracao == 0: continue
		if processos[p].duracao >= quantum: processos[p].duracao -= quantum
		else: processos[p].duracao = 0

		p_atual = p+1
		
		if p_atual == len(processos): p_atual = 0

		print(processos[p].duracao)
		break
