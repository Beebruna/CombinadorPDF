from PIL import ImageTk, Image
from fitz import *

class CombinadorPDF:
    def __init__(self):
        self.pdf = {}
        self.nome_arquivos = []

    def adicionar_arquivos(self, nome_arquivos):
        "insere arquivos nos atributos da classe"
        for nome_arquivo in nome_arquivos:
            self.nome_arquivos.append(nome_arquivo)
            self.pdf[nome_arquivo] = fitz.open(nome_arquivo)

    def excluir_arquivos(self, nome_arquivos):
        "remove arquivos dos atributos da classe"
        for nome_arquivo in nome_arquivos:
            self.nome_arquivos.remove(nome_arquivo)
            self.pdf.pop(nome_arquivo)

    def mover_cima(self, nome_arquivo):
        "troca de lugar o arquivo e seu antecessor na lista nome_arquivos"

        index = self.nome_arquivos.index(nome_arquivo)
        if index == 0:
            return
        
        self.nome_arquivos.remove(nome_arquivo)
        self.nome_arquivos.insert(index - 1, nome_arquivo)
        
    def mover_baixo(self, nome_arquivo):
        "troca de lugar o arquivo e o seu sucessor na lista nome_arquivos"
        
        index = self.nome_arquivos.index(nome_arquivo)
        if index == len(self.nome_arquivos) - 1:
            return
        
        self.nome_arquivos.remove(nome_arquivo)
        self.nome_arquivos.insert(index + 1, nome_arquivo)

    def extrair_dados(self, nome_arquivo):
        '''
        calcula o numero de paginas do pdf selecionado
        cria uma lista com objetos PhotoImage das paginas para serem usados na GUI
        '''
        # numero de paginas
        pdf = self.pdf[nome_arquivo]
        tamanho_arquivo = len(pdf)

        # criando lista com objetos PhotoImage
        lista_imagens = []
        for pagina in range(tamanho_arquivo):
            pix = pdf.getPagePixmap(pagina)
            mode = 'RGBA' if pix.alpha else 'RGB'
            image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            image = image.resize((round(680/pix.height*pix.width), round(680)))
            lista_imagens.append(ImageTk.PhotoImage(image))

        return lista_imagens, tamanho_arquivo
