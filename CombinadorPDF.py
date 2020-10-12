import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import PyPDF2

class CombinadorPDF:

    def __init__(self):
        self.pdfFiles = list() #Lista que guardará os nomes de todos os arquivos PDF selecionados pelo usuário
        #filename é uma tupla, então eu faço um casting de list
        self.pdfWriter = PyPDF2.PdfFileWriter()  #Retorna somente um valor que representa um documento PDF ser criado em Python
                        #Essa ação não criará o arquivo PDF propriamente dito
                        #pdfWriter irá armazenar as páginas combinadas
                        #Deve ser criado apenas uma única vez

    #Recebe os arquivos selecionados pelo usuário quando ele clica no botão de Procurar Arquivos
    def openFileDirectory(self):

        #primeiro definimos as opções
        self.opcoes = {} # as opções são definidas em um dicionário
        self.opcoes['defaultextension'] = '.pdf' #adiciona a extensão pdf por padrão
        self.opcoes['filetypes'] = [('Arquivos PDF', '.pdf')] #filtra os arquivos apenas para o formato pdf
        self.opcoes['title'] = 'Diálogo que retorna o nome de um arquivo para ser aberto'

        #retorna uma tupla com o NOME de um arquivo ou mais arquivos
        self.filename = filedialog.askopenfilenames(**self.opcoes) #filename é uma tupla que contém os caminhos dos arquivos selecionados
        
        for file in self.filename:
            self.pdfFiles.append(file)

        return self.pdfFiles


    '''       
    #Quando o botão inserir é acionado, essa função é acionada
    #Tem a finalidade de armazenar as páginas desejadas pelo usuário
    def insertPages(self, pdfFiles, option, positionFile):

        pdfFileObj = open(pdfFiles[positionFile], 'rb') #abre o arquivo PDF que o usuário escolheu, em modo de leitura binária 
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj) #pdfReader recebe um objeto PdfFileReader do arquivo PDF

        if option == 1: #Todas as páginas sáo selecionadas
            for pageNum in range(pdfReader.numPages):#percorre todas as páginas do PDF
                pageObj = pdfReader.getPage(pageNum) #pageObj recebe uma página específica
                self.pdfWriter.addPage(pageObj) #a página é adicionada em um objeto com valor de PDF
        else: #apenas os intervalos desejados são selecionados
            pagTotFiles = list() #Lista que guarda as páginas do intervalo que o usuário escolheu
            #ainda não sei implementar
            #lembrar que a contagem começa em zero, independentemente do número da página

        return self.pdfWriter

    #Essa função é acionada quando o botão combinar é acionado
    #Tem a finalidade de combinar todos os arquivos selecionados em um novo PDF.
    def combineFiles(self, pdfWriterTemp):

        pdfOutputFile = open('combinePdfs.pdf', 'wb')
        pdfWriterTemp.write(pdfOutputFile)
        pdfOutputFile.close()

    '''
class MainApplication(tk.Frame):

    def __init__(self, master):

        tk.Frame.__init__(self, master)
        self.master = master
        master.title('CombinadorPDF')
        
        self.combinadorPDF = CombinadorPDF()

        # ------------------------------------- widgets ----------------------------------------
        self.frame_arquivos = FrameArquivos(self)
        self.frame_visualizar = FrameVisualizar(self)
        self.frame_inserir = FrameInserir(self)
        self.frame_combinacao = FrameCombinacao(self)
        
        
        # ------------------------------------- layout -----------------------------------------
        self.grid_columnconfigure(0, weight=1)
        self.frame_arquivos.grid( row=0, column=0, padx=10, pady=5, sticky='we')
        self.frame_visualizar.grid(row=1, column=0, rowspan=7, padx=10, pady=5, ipadx=10, ipady=10)
        self.frame_inserir.grid(row=0, column=1, rowspan=3, padx=10, pady=5, ipadx=10, ipady=10)
        self.frame_combinacao.grid(row=3, column=1, rowspan=5, sticky='NSEW', padx=10, pady=5)


#Parte em que os arquivos serão procurados
class FrameArquivos(tk.LabelFrame):

    def __init__(self, master):

        self.master = master
        tk.LabelFrame.__init__(self, master, text='Seleção de arquivos')

        self.combinadorPDF = master.combinadorPDF

        # ------------------------------------- widgets ----------------------------------------
        self.botao_procurar = tk.Button(self, text='Procurar arquivos', command=self.combinadorPDF.openFileDirectory)
        #a minha intenção é que quando o esse botão é pressionaso, a função openFileDirectory() da classe CombinadorPDF abra uma janela que permita o usuário procurar os arquivos que ele deseja inserir no programa. Essa função irá retornar uma lista de arquivos que o usuário escolheu. Depois eu passo essa lista para a classe FrameInserir, para que os arquivos sejam inseridos no menu de opções.

        # ------------------------------------- layout -----------------------------------------
        self.grid_columnconfigure(0, weight=1)
        self.botao_procurar.grid(row=0, column=0, padx=10, pady=10, sticky='WE')


#Parte em que os arquivos serão exibidos
class FrameVisualizar(tk.LabelFrame):

    def __init__(self, master):

        self.master = master
        tk.LabelFrame.__init__(self, master, text='Visualizar')

        # ------------------------------------- widgets ----------------------------------------
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.scale = ttk.Scale(self)
        self.botao_voltar = tk.Button(self, text='<')
        self.botao_avancar = tk.Button(self, text='>')
        self.label_pagina = tk.Label(self, text='Página 1 de ?')

        # ------------------------------------- layout -----------------------------------------
        #self.label_imagem.grid(row=0, column=1, pady=10)
        self.separator.grid(row=1, column=0, columnspan=3, sticky='WE', pady=10)
        self.botao_voltar.grid(row=2, column=0, padx=10)
        self.scale.grid(row=2, column=1, padx=10, sticky='WE')
        self.botao_avancar.grid(row=2, column=2, padx=10)
        self.label_pagina.grid(row=3, column=1)


#Parte em que os arquivos estarão disponíveis em uma lista
class FrameInserir(tk.LabelFrame):

    def __init__(self, master):

        self.master = master
        tk.LabelFrame.__init__(self, master, text='Arquivos Selecionados')
        
        self.combinadorPDF = master.combinadorPDF
    
        # opçoes teste
        self.pdfFiles = self.combinadorPDF.openFileDirectory()
        print(self.pdfFiles) #coloquei só para eu ver se pdfFiles tem arquivos
        self.selecionado = tk.StringVar()
        self.selecionado.set(self.pdfFiles[0])
        
        # ------------------------------------- widgets ----------------------------------------
        self.option_menu = tk.OptionMenu(self, self.selecionado, *self.pdfFiles)
        self.label_opcoes = tk.Label(self, text='Intervalo das Páginas:')
        
        #botão para selecionar Todas as Páginas
        self.botao_radio_todas = tk.Radiobutton(self, text='Todas as páginas', variable=self.selecionado, value=1)
        self.frame_entry = tk.Frame(self)
        
        #botão para selecionar um Intervalo as Páginas
        self.botao_radio_intervalo = tk.Radiobutton(self.frame_entry, text='Páginas:', variable=self.selecionado, value=2)
        self.entry_paginas = tk.Entry(self.frame_entry, width=25)
        self.label_exemplo = tk.Label(self.frame_entry, text='Exemplo: 1,5-9,12')
        self.botao_inserir = tk.Button(self, text='Inserir')
        
        # ------------------------------------- layout -----------------------------------------
        self.option_menu.grid(row=0, column=0, sticky='WE', padx=10, pady=5)
        self.label_opcoes.grid(row=1, column=0, sticky='W', pady=5)
        self.botao_radio_todas.grid(row=2, column=0, sticky='W')
        self.frame_entry.grid(row=3, column=0)
        self.botao_radio_intervalo.grid(row=0, column=0)
        self.entry_paginas.grid(row=0, column=1)
        self.label_exemplo.grid(row=1, column=1, sticky='W')
        self.botao_inserir.grid(row=4, column=0, sticky='W', padx=20)


class FrameCombinacao(tk.LabelFrame):

    def __init__(self, master):

        self.master = master
        tk.LabelFrame.__init__(self, master, text='Arquivos combinados')
        
        # ------------------------------------- widgets ----------------------------------------
        self.lista_arquivos = tk.Listbox(self, selectmode=tk.SINGLE)  # talvez adicionar scrollbar à lista
        self.frame_botoes = tk.Frame(self)
        self.botao_baixar = tk.Button(self, text='Baixar')

        # ------------------------------------- layout -----------------------------------------
        self.lista_arquivos.configure(width=40, height=13)
        self.lista_arquivos.grid(row=0, column=0, padx=10, pady=10, sticky='NSEW')
        self.botao_baixar.grid(row=1, column=0)


if __name__ == '__main__':

    root = tk.Tk()
    MainApplication(root)
    root.mainloop()
