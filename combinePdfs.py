#Combina todos os PDFs de um diretório de trabalho atual em um único PDF

import PyPDF2

#Função que pega/puxa os arquivos desejados
def selectFiles(listFileBox):
    pdfFiles = list() #Lista que guardará os nomes de todos os arquivos PDF selecionados pelo usuário
    pdfWriter = PyPDF2.PdfFileWriter()  #Retorna somente um valor que representa um documento PDF ser criado em Python
                                        #Essa ação não criará o arquivo PDF propriamente dito
                                        #pdfWriter irá armazenar as páginas combinadas
                                        #Deve ser criado apenas uma única vez

    for filename in listFileBox: #retorna uma lista de todos os arquivos no diretório de trabalho atual
        if filename.endswith('.pdf'): #pega apenas os arquivos que tem a extensão .pdf do diretório
            pdfFiles.append(filename) #insere os arquivos pdf na lista pdfFiles

    return pdfFiles, pdfWriter
'''
Essa função precisa receber as listas selecionadas pelo usuário na interface gráfica quando ele clica no botão procurar arquivos
'''

#Quando o botão inserir é acionado, essa função é acionada
#Tem a finalidade de armazenar as páginas desejadas pelo usuário
def insertPages(pdfFiles, pdfWriterTemp, option, positionFile):

    pdfFileObj = open(pdfFiles[positionFile], 'rb') #abre o arquivo PDF que o usuário escolheu, em modo de leitura binária 
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj) #pdfReader recebe um objeto PdfFileReader do arquivo PDF

    if option == 1: #Todas as páginas sáo selecionadas
        for pageNum in range(pdfReader.numPages):#percorre todas as páginas do PDF
            pageObj = pdfReader.getPage(pageNum) #pageObj recebe uma página específica
            pdfWriterTemp.addPage(pageObj) #a página é adicionada em um objeto com valor de PDF
    else: #apenas os intervalos desejados são selecionados
        pagTotFiles = list() #Lista que guarda as páginas do intervalo que o usuário escolheu
        #ainda não sei implementar
        #lembrar que a contagem começa em zero, independentemente do número da página

    return pdfWriterTemp
'''
pdfFiles = lista de arquivos pdf escolhidos pelo usuário passada como parâmetro - pdfFiles - são os mesmos mostrados na aba de nomes da interface gráfica e na mesma ordem
option = é a opção de selecionar todas as páginas ou apenas um intervalo específico - o sinal é enviado pela interface gráfica
pdfWriterTemp = Recebe o pdfWriter vazio, ou os que serão preenchidos conforme o usuário aperte no botão inserir
positionFile = retorna a posição do arquivo selecionado na aba da inferface gráfica
numPages = retorna o número total de páginas do PDF
getPage = retorna a página específica do PDF
'''
'''
O PyPDF2 utiliza um índice baseado em zero para obter as páginas: a
primeira página é 0, a segunda página é 1, e assim sucessivamente. A
numeração sempre será dessa maneira, mesmo que as páginas estejam
numeradas de forma diferente no documento
'''

#Essa função é acionada quando o botão combinar é acionado
#Tem a finalidade de combinar todos os arquivos selecionados em um novo PDF.
def combineFiles(pdfWriterTemp):
    pdfOutputFile = open('combinePdfs.pdf', 'wb')#cria um documento pdf em branco, em modo de escrita binária, como o nome padrão 'combinePdfs'
    pdfWriterTemp.write(pdfOutputFile) #transfere as páginas de pdfWriterTemp para o pdf em branco; cria o pdf propriamente dito
    pdfOutputFile.close()#fecha o pdf recentemente criado, o novo documento com os arquivos combinados

