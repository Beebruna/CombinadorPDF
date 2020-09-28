from tkinter import *
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from tkinter import ttk

class Application:
    def __init__(self, master):
        "cria widgets na tela inicial"
        self.master = master
        
        # criando e configurando tabela usando treeview
        self.frame_tabela = Frame(self.master)
        self.tabela = ttk.Treeview(self.frame_tabela)
        
        self.tabela.heading('#0', text='Arquivos selecionados')
        self.tabela.column('#0', stretch=True)
        
        self.frame_tabela.pack(fill=BOTH, expand=1)
        self.tabela.pack(fill=X, expand=1, pady=10)
        
        # criando e configurando botoes para manipular a tabela
        self.botao_adicionar = Button(self.frame_tabela, text='Adicionar', command=self.adicionar_arquivos)
        self.botao_excluir = Button(self.frame_tabela, text='Excluir', command=self.excluir_arquivos)
        
        self.botao_adicionar.pack()
        self.botao_excluir.pack()
        
        
    def adicionar_arquivos(self):
        "abre janela de seleção de arquivos e adiciona os arquivos em formato pdf"
        arquivos_selecionados = askopenfilenames()
        for a in arquivos_selecionados:
            if a.endswith('.pdf'):
                self.tabela.insert(parent='', index='end', text=a)
        
    def excluir_arquivos(self):
        "exclui os arquivos selecionados da tabela"
        arquivos_selecionados = self.tabela.selection()
        for a in arquivos_selecionados:
            self.tabela.delete(a)    



root = Tk()
Application(root)
root.mainloop()
