from tkinter import *
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from tkinter import ttk

class Application:
    def __init__(self, master):
        "criando widgets na tela inicial"
        self.master = master
        self.criar_menu()
        
    def criar_menu(self):
        "define todas as opçoes do menu"
        self.menu = Menu(self.master)
        self.master.config(menu=self.menu)

        # criando itens do menu
        self.menu_arquivos = Menu(self.menu)
        self.menu.add_cascade(label='Arquivos', menu=self.menu_arquivos)
        
        # criando opçoes em cada item
        self.menu_arquivos.add_command(label='Abrir arquivos', command=self.selecionar_arquivos)
        self.menu_arquivos.add_separator()
        self.menu_arquivos.add_command(label='Sair', command=self.master.quit)
        
    def selecionar_arquivos(self):
        "abre janela de seleção de arquivos e separa os arquivos em formato pdf"
        arquivos_selecionados = askopenfilenames()
        self.lista_arquivos = []
        for a in arquivos_selecionados:
            if a.endswith('.pdf'):
                self.lista_arquivos.append(a)
        
        # mostrando arquivos em uma tabela
        self.criar_tabela()
        
    def criar_tabela(self):
        '''
        Cria uma tabela usando treeview
        Mostra os arquivos selecionados pelo usuario de
        acordo com a ordem da lista
        '''
        # definindo os widgets
        self.frame_tabela = Frame(self.master)
        self.tabela = ttk.Treeview(self.frame_tabela)
        
        # configurando a tabela
        self.tabela.heading('#0', text='Arquivos selecionados')
        self.tabela.column('#0', stretch=True)
        
        # inserindo os itens
        for arquivo in self.lista_arquivos:
            self.tabela.insert(parent='', index='end', text=arquivo)
        
        # mostrando widgets
        self.frame_tabela.pack(fill=BOTH, expand=1)
        self.tabela.pack(fill=X, expand=1, pady=10)      



root = Tk()
Application(root)
root.mainloop()
