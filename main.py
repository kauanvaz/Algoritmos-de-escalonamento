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

def calcula_tEspera(p, i):
	if p.chegada >= i:
		p.tEspera += 1

processos = organiza_processos()

temp = processos[0].chegada
for p in processos:
	p.chegada -= temp

p_atual = 0 # Índice referente ao processo atualmente em análise
tempo_total = sum(map(lambda p: int(p.duracao), processos)) # Tempo total necessario para execução de todos os processos
quantum = 2
exec = 0 # Unidades de tempo que um processo passa executando

espera = []
for i in range(tempo_total):
	if processos[p_atual].duracao == 0:
		if p_atual == len(processos)-1:
			p_atual = 0
		else:
			while processos[p_atual].duracao == 0: # Passa os processos na lista que já terminaram a execução
				p_atual += 1
				
	processos[p_atual].duracao -= 1
	print("i: ", i, " atual: ", p_atual, " t: ",processos[p_atual].duracao)

	processos[p_atual].tRetorno = i+1 - processos[p_atual].chegada

	espera = list(map(lambda p: calcula_tEspera(p, i) if p is not processos[p_atual] and p.duracao != 0 else p.tEspera, processos))

	exec += 1
	if exec == quantum or processos[p_atual].duracao == 0: # Se o processo já executou por um quantum ou já terminou
		if p_atual == len(processos)-1:
			p_atual = 0
		else: p_atual += 1
		exec = 0

print(list(map(lambda p: p.tRetorno, processos)))
print(espera)