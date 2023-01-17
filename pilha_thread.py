from time import process_time
from threading import Lock



class PilhaThread:
    def __init__(self, tamanho_maximo):
        self.array = [0 for i in range(tamanho_maximo+1)]
        self.indice = -1
        self.lock = Lock()

    
    def is_empty(self):
        self.lock.acquire()
        result = self.indice == -1
        self.lock.release()
        return result

    def pop(self):
        a = process_time()
        self.lock.acquire()

        obj = self.array[self.indice]

        if self.indice == -1:
            self.lock.release()
            return None
        if obj != None:
            self.indice-=1

        self.lock.release()
       
        return obj
    
    def push(self, obj):
        self.lock.acquire()
        
        self.indice+=1
        self.array[self.indice] = obj

        self.lock.release()