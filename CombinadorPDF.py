from PIL import ImageTk, Image
from fitz import *

class CombinadorPDF:
    
    @staticmethod
    def get_images(nome_arquivo):
        "retorna o numero de paginas e uma lista de objetos PhotoImage para serem usados no tkinter"
        pdf = fitz.open(nome_arquivo)
        tamanho = len(pdf)
        
        # redimensionando e adicionando imagem a lista
        lista_imagens = []
        for pagina in range(tamanho):
            pix = pdf.getPagePixmap(pagina)
            mode = 'RGBA' if pix.alpha else 'RGB'
            image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            image = image.resize((round(680/pix.height*pix.width), round(680)))
            lista_imagens.append(ImageTk.PhotoImage(image))
        
        return lista_imagens, tamanho
