from PIL import ImageTk, Image
from fitz import *

class CombinadorPDF:
    def __init__(self, nome_arquivo):
        self.pdf = fitz.open(nome_arquivo)

    def extrair_dados(self):
        '''
        calcula o numero de paginas do pdf
        cria uma lista com objetos PhotoImage para serem usados na GUI
        '''
        # numero de paginas
        self.tamanho_arquivo = len(self.pdf)
        
        # criando lista com objetos PhotoImage
        self.lista_imagens = []
        for pagina in range(self.tamanho_arquivo):
            pix = self.pdf.getPagePixmap(pagina)
            mode = 'RGBA' if pix.alpha else 'RGB'
            image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            image = image.resize((round(680/pix.height*pix.width), round(680)))
            self.lista_imagens.append(ImageTk.PhotoImage(image))
