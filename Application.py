from tkinter import *
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from tkinter import ttk

class Application:
    def __init__(self, master):
        "cria widgets na tela inicial"
        self.master = master

        # frame em que serao colocados os widgets
        self.frame_tabela = Frame(self.master)
        self.frame_tabela.pack(fill=BOTH, expand=1)

        # menu
        self.menu = Menu(self.frame_tabela)
        self.master.config(menu=self.menu)

        self.menu_arquivos = Menu(self.menu)
        self.menu.add_cascade(label='Arquivos', menu=self.menu_arquivos)

        self.menu_arquivos.add_command(
            label='Excluir todos registros', command=lambda: self.excluir_arquivos(self.tabela.get_children()))

        self.menu_ordenacao = Menu(self.menu)
        self.menu.add_cascade(label='Opções de ordenação',
                              menu=self.menu_ordenacao)

        self.menu_ordenacao.add_command(
            label='Nome', command=lambda: self.ordenar_tabela('nome'))
        self.menu_ordenacao.add_command(
            label='Nome com diretório', command=lambda: self.ordenar_tabela('diretorio'))
        self.menu_ordenacao.add_command(
            label='Data de modificação', command=lambda: self.ordenar_tabela('data'))

        # tabela utilizando treeview
        self.tabela = ttk.Treeview(self.frame_tabela)

        self.tabela.heading('#0', text='Arquivos selecionados')
        self.tabela.column('#0', stretch=True)

        self.tabela.pack(fill=X, expand=1, pady=10)

        # botoes
        self.botao_adicionar = Button(
            self.frame_tabela, text='Adicionar', command=lambda: self.adicionar_arquivos(askopenfilenames()))
        self.botao_excluir = Button(self.frame_tabela, text='Excluir',
                                    command=lambda: self.excluir_arquivos(self.tabela.selection()))

        self.botao_adicionar.pack()
        self.botao_excluir.pack()

    def adicionar_arquivos(self, arquivos_selecionados):
        "adiciona os arquivos em formato pdf selecionados"
        for a in arquivos_selecionados:
            if a.endswith('.pdf'):
                self.tabela.insert(parent='', index='end', text=a)

    def excluir_arquivos(self, arquivos_selecionados):
        "exclui os arquivos selecionados da tabela"
        for a in arquivos_selecionados:
            self.tabela.delete(a)

    def ordenar_tabela(self, ordenacao):
        "ordena os itens da tabela de acordo o parametro passado para ordenacao"

        # pegando as strings armazenadas na tabela
        lista_arquivos = []
        ids = self.tabela.get_children()
        for id in ids:
            item_content = self.tabela.item(id, 'text')
            lista_arquivos.append(item_content)

        if ordenacao == 'nome':
            # pega o nome ignorando o diretorio
            lista_nomes = []
            for item in lista_arquivos:
                lista_nomes.append(item.split('/')[-1])
            
            '''
            utilizando trecho de codigo de bubble sortem vez de .sort(str.lower)
            para fazer as mesmas alterações feitas na lista_nomes
            na lista_arquivos
            '''
            sorted = False
            while not sorted:
                sorted = True
                for i in range(len(lista_nomes) - 1):
                    if lista_nomes[i+1].lower() < lista_nomes[i].lower():
                        sorted = False
                        lista_nomes[i+1], lista_nomes[i] = lista_nomes[i], lista_nomes[i+1]
                        lista_arquivos[i+1], lista_arquivos[i] = lista_arquivos[i], lista_arquivos[i+1]

        elif ordenacao == 'diretorio':
            lista_arquivos.sort(key=str.lower)

        elif ordenacao == 'data':
            pass  # necessario extrair dados do pdf

        self.excluir_arquivos(ids)
        self.adicionar_arquivos(lista_arquivos)



root = Tk()
Application(root)
root.mainloop()
