import random
import firebase_admin
from datetime import datetime
from firebase_admin import credentials, firestore
import pytz
# from .firebase_mov import Movimentacao

class Estoque:
    _instance = None

    def __init__(self) -> None:
        self.__dir_credencial = 'restaurante\crud\credencial.json'
        self.__firebase = self.configura_credenciais()
        # self.criar_colecao()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Estoque, cls).__new__(cls)
        return cls._instance

    def configura_credenciais(self):
        """cria a conexao de autenticação"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.__dir_credencial)
                firebase_admin.initialize_app(credential=cred)
            return firestore.client()
        
        except Exception as e:
            print("Erro ao configurar a autenticação", str(e))

    def criar_colecao(self):
        colecao = self.__firebase.collection('checkin').add({})

    def insert_novo_produto(self, dados: dict):
        try:
            self.__firebase.collection('checkin').add(dados)
            return "Produto registrado com sucesso"
        except Exception as e:
            return "Erro ao registrar o produto."

    def update_dados_produto(self, dados: dict):
        ret = self.select_dados_produto(dados['sku'])
        if ret:
            self.__firebase.collection('checkin').document(ret['id']).update(dados)

    def select_dados_checkin(self, matricula_usuario: str = None, matricula_cpf: str = None):
        if matricula_usuario:
            dados = self.__firebase.collection('checkin')
            if matricula_cpf == "Matricula":
                docs = dados.where('matricula', '==', matricula_usuario).get()
            elif matricula_cpf == "CPF":
                docs = dados.where('cpf', '==', matricula_usuario).get()

            lista_produtos: dict = {doc.id: doc.to_dict() for doc in docs}

            for chave, valor in lista_produtos.items():
                data_hora_checkin_str = valor['data_hora_checkin']
                data_hora_checkin_obj = datetime.strptime(data_hora_checkin_str, '%d/%m/%Y %H:%M:%S')
                valor['data_hora_checkin'] = data_hora_checkin_obj

            lista_produtos_ordenados = sorted(lista_produtos.items(), key=lambda x: x[1]['data_hora_checkin'], reverse=True)
            lista_produtos_ordenado_dict = dict(lista_produtos_ordenados)                
                
            return lista_produtos_ordenado_dict
        else:
            dados = self.__firebase.collection('checkin').get()#.order_by('data_hora_checkin', direction=firestore.Query.DESCENDING).get()
            lista_produtos: dict = {doc.id: doc.to_dict() for doc in dados}

            for chave, valor in lista_produtos.items():
                data_hora_checkin_str = valor['data_hora_checkin']
                data_hora_checkin_obj = datetime.strptime(data_hora_checkin_str, '%d/%m/%Y %H:%M:%S')
                valor['data_hora_checkin'] = data_hora_checkin_obj

            lista_produtos_ordenados = sorted(lista_produtos.items(), key=lambda x: x[1]['data_hora_checkin'], reverse=True)
            lista_produtos_ordenado_dict = dict(lista_produtos_ordenados)

            return lista_produtos_ordenado_dict

    def select_ultimos_tres(self):
        dados = self.__firebase.collection('checkin').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(3).get()
        lista_produtos: dict = {doc.id: doc.to_dict() for doc in dados}

        return lista_produtos

    def delete_dados_produto(self):
        try:
            # Obtém uma referência para a coleção
            colecao_checkin_ref = self.__firebase.collection('checkin')

            # Itera e exclui cada documento na coleção
            docs = colecao_checkin_ref.stream()
            for doc in docs:
                doc.reference.delete()

        except Exception as e:
            return "Erro ao registrar o produto."
    
    def baixa_produto(self, request, sku: str, tipo: str, qtde: int, referen: str, nome_usuario: str, local: str):

        produto = self.select_dados_produto(sku_id=sku)
        nova_qtde: int = 0
        if produto:
            # verifica tipo movimentação
            if tipo =='entrada':
                nova_qtde = int(produto["quantidade"]) + qtde
            else:
                nova_qtde = int(produto["quantidade"]) - qtde

            # altera os dados com a nova quantidade de estoque
            self.__firebase.collection('checkin').document(produto['id'])\
                                                 .update({'quantidade': nova_qtde})
            
            # est = Movimentacao()
            dados = {
                'nome': nome_usuario,
                'data': self.data_fuso_horario(),
                'referencia': referen,
                'tipo': tipo.upper(),
                'sku':  produto['sku'],
                'descricao': str(produto['descricao']) +" (" + str(produto['obs']) +")",
                'quantidade': qtde,
                'local': local
            }
            # est.insert_movimentacao(dados)
            # self.atualiza_produto(request, produto['id'], nova_qtde)

    def atualiza_produto(request, item_id: str, qtde: int):

        dct_produto: dict = request.session['dados_firebase']
        
        for chave, valor in dct_produto.items():
            if chave == item_id:
                dct_produto[item_id]['quantidade'] = qtde
                # import ipdb;ipdb.set_trace()
                break
        request.session['dados_firebase'] = dct_produto

    def delete_dados_atividade(self, id: str):
            try:
                self.__firebase.collection('checkin').document(id).delete()
            except Exception as e:
                return "Erro ao registrar o produto."    

    def data_certa(self):
        documentos = self.__firebase.collection('checkin').stream()

        for doc in documentos:
            # Obtenha os dados do documento
            data = doc.to_dict()

            # Verifique se o campo 'data_hora_checkin' existe nos dados
            if 'data_hora_checkin' in data:
                # Obtenha a string de data e hora do documento
                data_hora_str = data['data_hora_checkin']
                
                # Converter a string em um objeto datetime

                data_hora_obj = datetime.strptime(data_hora_str, "%d/%m/%Y %H:%M:%S")

                doc.reference.update({'timestamp': data_hora_obj})

#     def excluir_item_por_sku(sku):
#         collection_ref = firestore.client().collection('estoque')
#         docs = collection_ref.stream()

#         for doc in docs:
#             doc.reference.delete()
#             print(f"deletado: {sku}")
#         print("terminou")


if __name__ == '__main__':
    estoque = Estoque()
    estoque.data_certa()



    # import pandas as pd
    # # import random
    # estoque = Estoque()
    # # val = estoque.select_dados_produto()
    # # print(val)

    # df = pd.DataFrame(pd.read_excel(r"C:\Users\2103896595\Desktop\Pasta1.xlsx"))

    # for idx, row in df.iterrows():
    # dados = {
    #     'sku': '123abc',
    #     'descricao': 'teste',
    #     'quantidade': random.randint(1, 100),
    #     'url': 'https://www.google.com.br/',
    #     'obs': 'teste cadastro'
    # }

    
    # estoque.insert_novo_produto(dados)
    # update_dados = {
    #     'sku': '123abc',
    #     'url': 'http//url.arquivo.com',
    #     'obs': 'teste2',
    #     'quantidade': 16
    # }
    # estoque.update_dados_produto(update_dados)
    # estoque.delete_dados_produto('123abc')


