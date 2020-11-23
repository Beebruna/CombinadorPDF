import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
import fitz

class CombinadorPDF:
    """
    Classe usada para combinar pdfs

    Atributos
    ---------
    docs : list
        lista de objetos fitz.fitz.Document
    nome_arquivos : list
        lista de nomes dos arquivos

    Métodos
    -------
    adicionar_arquivo(self, pdfFile)
        Adiciona nome do arquivo e objeto fitz.fitz.Document aos atributos
    combinar(self)
        Combina os pdfs da lista docs

    """

    def __init__(self):
        """"""

        self.docs = []
        self.nome_arquivos = []

    def adicionar_arquivo(self, nome_arquivo, doc):
        """
        Adiciona nome do arquivo e objeto fitz.fitz.Document aos atributos

        Parâmetros
        ----------
        nome_arquivo : str
            nome do arquivo incluindo endereço absoluto
        doc : fitz.fitz.Document
            documento pdf
        """

        self.nome_arquivos.append(nome_arquivo)
        self.docs.append(doc)

    def combinar(self):
        """
        Combina os pdfs contidos no atributo fitz_docs

        Retorno
        -------
        fitz.fitz.Document
            um documento pdf com todos os pdfs da lista docs combinados
        """

        doc_combinado = fitz.open()
        for doc in self.docs:
            doc_combinado.insertPDF(doc)
        return doc_combinado
