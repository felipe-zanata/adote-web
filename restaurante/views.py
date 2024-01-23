from django.shortcuts import render, redirect
from django.http import JsonResponse,HttpResponse  
from .crud.firebase_auth import AuthUsuarios
from .crud.firebase_est import Estoque
from django.contrib import messages
from datetime import datetime
import pytz
import json

def login(request):
    request.session.flush()
    try:
        if request.method == "POST":
            matricula = request.POST.get('matricula')
            senha = request.POST.get('senha')
            auth = AuthUsuarios()
            data = auth.select_dados(matricula_usuario=matricula)

            if data['senha'] == senha:
                request.session['id'] = data['id']
                request.session['matricula'] = data['matricula']
                request.session['cpf'] = data['cpf']
                request.session['nome'] = data['nome']
                request.session['tipo_acesso'] = data['tipo_acesso']
                request.session['senha'] = data['senha']
                request.session['centroCusto'] = data['centroCusto']
                request.session['status'] = data['status']
                return redirect('relatorios')
            else:
                print("Senha incorreta")
                return render(request, 'login_erro.html', {'error_message': 'Usuário ou senha incorretos'})
        else:
            return render(request, 'login.html')
    except:
        print('passei except')
        return render(request, 'login_erro.html', {'error_message': 'Usuário ou senha incorretos'})

def login_incorreto(request):
    return render(request, 'login_erro.html', {'error_message': 'Usuário ou senha incorretos'})

def cadastrar_usuario(request):
    tipo_acesso = request.session.get('tipo_acesso', None)
    if tipo_acesso == "admin":
        if request.method == 'POST':
            matricula = request.POST.get("matricula")
            cpf = request.POST.get("cpf")
            nome = request.POST.get("nome")
            senha = request.POST.get("senha")
            tipo_acesso = request.POST.get("tipo_acesso")
            centroCusto = request.POST.get("centroCusto")
            status = request.POST.get("status")
            
            auth = AuthUsuarios()
            existing_user = auth.select_dados(matricula_usuario=matricula) or auth.select_dados(cpf_usuario=cpf)
            
            if existing_user:
                print('ja existe')
                return render(request, 'cadastrar.html', {'error_message': 'CPF ou matrícula já existem.'})
            
            dados = {
                'matricula': matricula,
                'cpf': cpf,
                'nome': nome,
                'senha': senha,
                'centroCusto': centroCusto,
                'status': status,
            }
            new_user = AuthUsuarios()
            new_user.inserir_novo_usuario(dados=dados, tipo_usuario=tipo_acesso)

            return render(request, 'cadastrar.html')

        return render(request, 'cadastrar.html')
    else:
        return render(request, 'login_sempermissao.html')
     
def gerenciar_user(request):
    tipo_acesso = request.session.get('tipo_acesso', None)
    if tipo_acesso == "admin":
        if request.method == 'GET':
            try:
                matricula_usuario = request.GET.get('matricula_usuario')
                auth = AuthUsuarios()
                dados = auth.select_dados(matricula_usuario=matricula_usuario)
                return render(request, 'usuarios.html', context={'dados': dados})
            except Exception as error:
                return render(request, 'usuarios.html')
        else:
            return render(request, 'usuarios.html')
    else:
        return render(request, 'login_sempermissao.html')        

def relatorios(request):
    tipo_acesso = request.session.get('tipo_acesso', None)
    if tipo_acesso == "admin":
        if request.method == 'GET':
            try:
                matricula_usuario = request.GET.get('matricula_usuario')
                reg_checkin = Estoque()
                dados = reg_checkin.select_dados_checkin(matricula_usuario=matricula_usuario)
                return render(request, 'relatorio.html', context={'dados': dados})
            except Exception as error:
                return render(request, 'relatorio.html')
        else:
            return render(request, 'relatorio.html')
    else:
        return render(request, 'login_sempermissao.html')          

def editar_user(request, tipo_usuario):
    tipo_acesso = request.session.get('tipo_acesso', None)
    if tipo_acesso == "admin":        
        id_usuario = request.GET.get('chave')
        print(id_usuario)
        dados = {
            'chave': id_usuario,
            "tipo_acesso": tipo_usuario,
            "matricula": request.GET.get('matricula'),
            "cpf": request.GET.get('cpf'),
            "nome": request.GET.get('nome'),
            "senha" : request.GET.get('senha'),
            "centroCusto" : request.GET.get('centroCusto'),
            "status" : request.GET.get('status')
        }

        return render(request, 'editar_user.html', {'dados': dados})
    else:
        return render(request, 'login_sempermissao.html')  

def executar_editar_user(request):
    tipo_acesso = request.session.get('tipo_acesso', None)
    if tipo_acesso == "admin":    
        if request.method == 'POST':
            id_usuario = request.POST.get('chave')
            tipo_acesso_original = request.POST.get("tipo_acesso_original")
            tipo_acesso = request.POST.get("tipo_acesso")
            matricula = request.POST.get("matricula")
            cpf = request.POST.get("cpf")
            nome = request.POST.get("nome")
            senha = request.POST.get('senha')
            centroCusto = request.POST.get('centroCusto')
            status = request.POST.get('status')
        
            dados = {
                'tipo_acesso': tipo_acesso,
                'matricula': matricula,
                'cpf': cpf,
                'nome': nome,
                'senha': senha,
                'centroCusto': centroCusto,
                'status': status,
            }

            update_user = AuthUsuarios()

            update_user.deletar_usuario(tipo_usuario=tipo_acesso_original   , id_usuario=id_usuario)
            update_user.inserir_novo_usuario(dados=dados, tipo_usuario=tipo_acesso)

            return redirect('gerenciar_user')
        else:
            return render(request, 'gerenciar_user.html')
    else:
        return render(request, 'login_sempermissao.html') 
    
def deletar(request, tipo_usuario):
    tipo_acesso = request.session.get('tipo_acesso', None)
    if tipo_acesso == "admin":     

        id_usuario = request.GET.get('chave')
        auth = AuthUsuarios()
        auth.deletar_usuario(tipo_usuario, id_usuario)

        return redirect(gerenciar_user)

def check_in(request):
    try:
        if request.method == 'POST':
            matricula = request.POST.get('matricula')
            cpf = request.POST.get('cpf')
            auth = AuthUsuarios()
            matricula_cpf = request.POST.get('matricula_cpf')
            data = auth.select_dados_2(matricula_usuario=matricula, tipo_acesso='colaborador', retorno_cpf_matricula=matricula_cpf)
            
            if data and data['matricula'] == matricula and data['status'] == 'Ativo' or data['cpf'] == matricula and data['status'] == 'Ativo':
                try:
                    selected_radio = request.POST.get('radio-group')

                    data_hora_atual = datetime.now()
                    data_hora_formatada = data_hora_atual.strftime("%d/%m/%Y %H:%M:%S")

                    dados = {
                        'matricula': data['matricula'],
                        'cpf': data['cpf'],
                        'nome': data['nome'],
                        'centroCusto': data['centroCusto'],
                        'checkin': selected_radio,
                        'data_hora_checkin': data_hora_formatada,
                        'timestamp': data_hora_atual,
                    }
                    
                    projeto = Estoque()
                    dados_matricula = projeto.select_dados_checkin(matricula_usuario=matricula,matricula_cpf=matricula_cpf)
                    checkin_existente = False

                    # for id, dado in dados_matricula.items():
                    #     data_hora_checkin = datetime.strptime(dado['data_hora_checkin'], '%d/%m/%Y %H:%M:%S')
                    #     hora_checkin = data_hora_checkin.strftime('%H:%M:%S')

                    for id, dado in dados_matricula.items():
                        if isinstance(dado['data_hora_checkin'], str):
                            data_hora_checkin = datetime.strptime(dado['data_hora_checkin'], '%d/%m/%Y %H:%M:%S')
                        elif isinstance(dado['data_hora_checkin'], datetime):
                            data_hora_checkin = dado['data_hora_checkin']
                        else:
                            pass

                        hora_checkin = data_hora_checkin.strftime('%H:%M:%S')

                        if dado['checkin'] == selected_radio and data_hora_checkin.date() == data_hora_atual.date():
                            checkin_existente = True
                            break

                    if checkin_existente:
                        messages.error(request, f'Colaborador já fez este Check-in hoje às {hora_checkin}') 
                        return redirect('checkin')                        
                    else:
                        resposta = projeto.insert_novo_produto(dados)
                        messages.success(request, 'Check-in realizado com sucesso.')
                        return redirect('checkin')
                except json.JSONDecodeError as e:
                    return JsonResponse({"error": "Invalid JSON data"}, status=400)
            else:
                messages.error(request, 'Colaborador desativado. Entre em contato com a equipe.')        
                return redirect('checkin')

    except Exception as e:
        print('Erro:', str(e))
        messages.error(request, 'Matrícula ou CPF não cadastrado. Entre em contato com a equipe.')
        print('Passei except')
        return redirect('checkin')

    try:
        if request.method == 'GET':
            try:
                reg_checkin = Estoque()
                dados = reg_checkin.select_ultimos_tres()
                return render(request, 'checkin/checkin.html', context={'dados': dados})
            except Exception as error:
                return render(request, 'checkin/checkin.html')
        else:
            return render(request, 'checkin/checkin.html')
    except Exception as e:
        print('Erro:', str(e))

    return render(request, 'checkin.html')

def checkin_valido(request):
    return render(request, 'checkin_validado.html')

def checkin_erro(request):
    return render(request, 'checkin_erro.html')

def login_semperm(request):
    return render(request, 'login_sempermissao.html')

def deletar_checkin(request,  tipo):
    try:
        deletar_tudo = Estoque()
        deletar_tudo.delete_dados_produto()

        return redirect('relatorios')
    except Exception as e:
        return "Erro ao registrar o produto."

def deletar_atividade(request, id: str, valor: str):
    try:
        est = Estoque()
        dados = est.delete_dados_atividade(id)
        return redirect('relatorios')
    except Exception as e:
        return "Erro deletar o checkin."

def num_refeicoes(request):
    tipo_acesso = request.session.get('tipo_acesso', None)
    if tipo_acesso == "admin":
        if request.method == 'GET':
            try:
                matricula_usuario = request.GET.get('matricula_usuario')
                reg_checkin = Estoque()
                dados = reg_checkin.select_dados_checkin(matricula_usuario=matricula_usuario)

                contagem = {}
                # Iterar sobre os check-ins e contar por data e tipo de refeição
                for chave, dados in dados.items():
                    data_hora_checkin = dados['data_hora_checkin']
                    data = datetime.strftime(data_hora_checkin, '%d/%m/%Y')
                    data = str(data).split(' ')[0]  # Obter a parte da data (25/09/2023)
                    # data = data_hora_checkin.split('')[0]  # Obter a parte da data (25/09/2023)
                    tipo_refeicao = str(dados['checkin']).replace(" ", "_")

                    # import ipdb;ipdb.set_trace()

                    # Verificar se a data já está no dicionário de contagem
                    if data not in contagem:
                        contagem[data] = {'Café_da_manhã': 0, 'Almoço': 0, 'Jantar': 0}

                    # Incrementar a contagem do tipo de refeição para a data correspondente
                    contagem[data][tipo_refeicao] += 1

                # Preparar o contexto para renderização
                dados = {'contagem': contagem}
                print(dados)

                return render(request, 'num_refeicoes.html', context={'dados': dados})
            except Exception as error:
                return render(request, 'num_refeicoes.html')
        else:
            return render(request, 'num_refeicoes.html')
    else:
        return render(request, 'login_sempermissao.html')

