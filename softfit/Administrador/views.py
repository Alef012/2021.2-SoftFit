from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from .forms import CadastroAluno, CadastroAvaliacao, CadastroProfessor, Mensagem
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from calendar import monthrange
from datetime import date
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test

from .services import avaliacao_service, aluno_service, prof_service, estadof_service, objetivo_service, exercicio_service
from .models import Aluno, Professor, EstadoFinanceiro, Objetivo
from .entidades import aluno, avaliacao, professor, estadof, objetivod

def admin_check(user):
    return user.username == 'administrador'

def loginAdmin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('administrador:index'))
        else:
            return render(request, "administrador/login.html", {
                "message": "Administrador não encontrado!"
            })
    else:
        return render(request,"administrador/login.html")
def idadePelaData(data):

    return idade
def logout_view(request):
    logout(request)
    return render(request, "homepage/index.html", {
        "message": "Log out realizado!"
    })

@user_passes_test(admin_check, login_url='/')
def index(request):
    alunos = Aluno.objects.all()
    profs = Professor.objects.all()
    dia = monthrange(date.today().year, date.today().month)[1]
    return render(request, 'Administrador/inicial.html', {'alunos': alunos, 'profs': profs, 'dia':dia})


def IdadePelaData(DatadeNasci):
    Data_atual=datetime.today().strftime('%Y-%m-%d')
    diaNasci,mesNasci,anoNasci = DatadeNasci.split('/')
    anoAtual,mesAtual,diaAtual = Data_atual.split('-')
    idade = (int(anoAtual)-1)-(int(anoNasci))
    if(int(mesAtual>mesNasci) or (int(mesAtual==mesNasci)and(int(diaAtual>=diaNasci)))):
        idade+=1
    return idade

@user_passes_test(admin_check, login_url='/')
def cadastroAluno(request):
    if request.method == "POST":
        form_aluno = CadastroAluno(request.POST)
        form_aval = CadastroAvaliacao(request.POST)
        if form_aluno.is_valid():
            nome = form_aluno.cleaned_data["nome"]
            email = form_aluno.cleaned_data["email"]
            dataDeNascimento = form_aluno.cleaned_data["Data de Nascimento"]
            if form_aval.is_valid():
                peso = form_aval.cleaned_data["peso"]
                altura = form_aval.cleaned_data["altura"]
                imc = peso/(altura*altura)
                braco_d = form_aval.cleaned_data["braco_d"]
                perna_e = form_aval.cleaned_data["perna_e"]
                cintura = form_aval.cleaned_data["cintura"]
                comentario_af = form_aval.cleaned_data["comentario_af"]

                avaliacao_novo = avaliacao.AvaliacaoFisica(peso=peso, altura=altura, imc=imc, braco_d=braco_d, perna_e=perna_e, cintura=cintura, comentario_af=comentario_af)
                avaliacao_db = avaliacao_service.cadastrar_aval(avaliacao_novo)

                estadof_novo = estadof.EstadoFinanceiro(condicao="Em Dia")
                estadof_db = estadof_service.cadastrar_estadof(estadof_novo)

                objetivo_novo = objetivod.Objetivo(opcao="A Selecionar", comentario="Nenhum, por enquanto")
                objetivo_db = objetivo_service.cadastrar_objetivo(objetivo_novo)

                aluno_novo = aluno.Aluno(nome=nome, email=email, avaliacao=avaliacao_db, estadof=estadof_db, frequencia=0, objetivo=objetivo_db)
                aluno_db = aluno_service.cadastrar_aluno(aluno_novo)

                senha = aluno_service.gera_senha()

                user = User.objects.create_user(username=email, email=email, password=senha)

                user.save()

                corpo_email = "Aluno, sua senha provisória de acesso é: " + senha

                send_mail('Senha de Acesso - SoftFit', corpo_email, 'softfit123@gmail.com', [email], fail_silently=False)

                return redirect('/administrador/')
    else:
        form_aluno = CadastroAluno()
        form_aval = CadastroAvaliacao()
    return render(request, 'administrador/cadastroaluno.html', {'form_aluno': form_aluno, 'form_aval': form_aval})

@user_passes_test(admin_check, login_url='/')
def editaAluno(request, id):
    aluno_editar = aluno_service.mostrar_aluno(id)
    form_aluno = CadastroAluno(request.POST or None, instance=aluno_editar)
    avaliacao_editar = avaliacao_service.mostrar_avaliacao(aluno_editar.avaliacao.id)
    form_aval = CadastroAvaliacao(request.POST or None, instance=avaliacao_editar)
    if form_aluno.is_valid():
        nome = form_aluno.cleaned_data["nome"]
        email = form_aluno.cleaned_data["email"]
        if form_aval.is_valid():
            peso = form_aval.cleaned_data["peso"]
            altura = form_aval.cleaned_data["altura"]
            imc = peso/(altura*altura)
            braco_d = form_aval.cleaned_data["braco_d"]
            perna_e = form_aval.cleaned_data["perna_e"]
            cintura = form_aval.cleaned_data["cintura"]
            comentario_af = form_aval.cleaned_data["comentario_af"]

            avaliacao_novo = avaliacao.AvaliacaoFisica(peso=peso, altura=altura, imc=imc, braco_d=braco_d, perna_e=perna_e, cintura=cintura, comentario_af=comentario_af)
            avaliacao_edit = avaliacao_service.editar_avaliacao(avaliacao_editar, avaliacao_novo)

            aluno_novo = aluno.Aluno(nome=nome, email=email, avaliacao=avaliacao_edit, frequencia=aluno_editar.frequencia, estadof=aluno_editar.estadof, objetivo=aluno_editar.objetivo)
            aluno_service.editar_aluno(aluno_editar, aluno_novo)
            return redirect('/administrador/')
    return render(request, 'administrador/cadastroaluno.html', {'form_aluno': form_aluno, 'form_aval': form_aval})

@user_passes_test(admin_check, login_url='/')
def mostraAluno(request, id):
    aluno = aluno_service.mostrar_aluno(id)
    avaliacao = avaliacao_service.mostrar_avaliacao(aluno.avaliacao.id)
    objetivo = objetivo_service.mostrar_objetivo(aluno.objetivo.id)
    dia = monthrange(date.today().year, date.today().month)[1]
    return render(request, 'administrador/mostraaluno.html', {'aluno': aluno, 'avaliacao': avaliacao, 'objetivo': objetivo, 'dia': dia})

@user_passes_test(admin_check, login_url='/')
def enviaMensagem(request, id, assunto):
    aluno = aluno_service.mostrar_aluno(id)
    nome = aluno.nome
    if assunto == 1:
        assunto_email = 'Estado Financeiro'
    else:
        assunto_email = 'Frequência'
    if request.method == "POST":
        form_email = Mensagem(data=request.POST, nome=nome, assunto_email=assunto_email)
        if form_email.is_valid():
            corpo_email = form_email.cleaned_data["corpo_email"]
            send_mail(assunto_email, corpo_email, 'softfit123@gmail.com', [aluno.email], fail_silently=False)
            return HttpResponseRedirect(reverse('administrador:mostrarAluno', kwargs={'id': aluno.id}))
        else:
            print(form_email.errors)
    else:
        form_email = Mensagem(nome=nome, assunto_email=assunto_email)
    return render(request, 'administrador/mensagem.html', {'aluno': aluno, 'assunto': assunto, 'form_email': form_email})

@user_passes_test(admin_check, login_url='/')
def removeAluno(request, id):
    aluno = aluno_service.mostrar_aluno(id)
    avaliacao = avaliacao_service.mostrar_avaliacao(aluno.avaliacao.id)
    estadof = estadof_service.mostrar_estadof(aluno.estadof.id)
    objetivo = objetivo_service.mostrar_objetivo(aluno.objetivo.id)
    if request.method == "POST":
        exercicio_service.remover_exercicio_aluno(id)
        aluno_service.remover_aluno(aluno)
        avaliacao_service.remover_avaliacao(avaliacao)
        estadof_service.remover_estadof(estadof)
        objetivo_service.remover_objetivo(objetivo)
        u = User.objects.get(username = aluno.email)
        u.delete()
        return redirect('/administrador/')
    return render(request, 'administrador/confirmarexclusao.html', {'usuario': aluno})

@user_passes_test(admin_check, login_url='/')
def cadastroProfessor(request):
    if request.method == "POST":
        form_prof = CadastroProfessor(request.POST)
        if form_prof.is_valid():
            nome = form_prof.cleaned_data["nome"]
            email = form_prof.cleaned_data["email"]

            segunda_manha = form_prof.cleaned_data["segunda_manha"]
            segunda_tarde = form_prof.cleaned_data["segunda_tarde"]
            segunda_noite = form_prof.cleaned_data["segunda_noite"]

            terca_manha = form_prof.cleaned_data["terca_manha"]
            terca_tarde = form_prof.cleaned_data["terca_tarde"]
            terca_noite = form_prof.cleaned_data["terca_noite"]

            quarta_manha = form_prof.cleaned_data["quarta_manha"]
            quarta_tarde = form_prof.cleaned_data["quarta_tarde"]
            quarta_noite = form_prof.cleaned_data["quarta_noite"]

            quinta_manha = form_prof.cleaned_data["quinta_manha"]
            quinta_tarde = form_prof.cleaned_data["quinta_tarde"]
            quinta_noite = form_prof.cleaned_data["quinta_noite"]

            sexta_manha = form_prof.cleaned_data["sexta_manha"]
            sexta_tarde = form_prof.cleaned_data["sexta_tarde"]
            sexta_noite = form_prof.cleaned_data["sexta_noite"]

            sabado_manha = form_prof.cleaned_data["sabado_manha"]
            sabado_tarde = form_prof.cleaned_data["sabado_tarde"]

            domingo_manha = form_prof.cleaned_data["domingo_manha"]

            prof_novo = professor.Professor(nome=nome, email=email, 
                                    segunda_manha=segunda_manha, segunda_tarde=segunda_tarde, segunda_noite=segunda_noite, 
                                    terca_manha=terca_manha, terca_tarde=terca_tarde, terca_noite=terca_noite, 
                                    quarta_manha=quarta_manha, quarta_tarde=quarta_tarde, quarta_noite=quarta_noite, 
                                    quinta_manha=quinta_manha, quinta_tarde=quinta_tarde, quinta_noite=quinta_noite, 
                                    sexta_manha=sexta_manha, sexta_tarde=sexta_tarde, sexta_noite=sexta_noite, 
                                    sabado_manha=sabado_manha, sabado_tarde=sabado_tarde, 
                                    domingo_manha=domingo_manha)
            prof_db = prof_service.cadastrar_professor(prof_novo)

            senha = aluno_service.gera_senha()

            user = User.objects.create_user(username=email, email=email, password=senha)

            user.save()

            corpo_email = "Professor, sua senha provisória de acesso é: " + senha

            send_mail('Senha de Acesso - SoftFit', corpo_email, 'softfit123@gmail.com', [email], fail_silently=False)

            return redirect('/administrador/')
    else:
        form_prof = CadastroProfessor()
    return render(request, 'administrador/cadastroprofessor.html', {'form_prof': form_prof})

@user_passes_test(admin_check, login_url='/')
def removeProfessor(request, id):
    prof = prof_service.mostrar_professor(id)
    if request.method == "POST":
        prof_service.remover_professor(prof)
        u = User.objects.get(username = prof.email)
        u.delete()
        return redirect('/administrador/')
    return render(request, 'administrador/confirmarexclusao.html', {'usuario': prof})

@user_passes_test(admin_check, login_url='/')
def editaProfessor(request, id):
    prof_editar = prof_service.mostrar_professor(id)
    form_prof = CadastroProfessor(request.POST or None, instance=prof_editar)
    if form_prof.is_valid():
        nome = form_prof.cleaned_data["nome"]
        email = form_prof.cleaned_data["email"]

        segunda_manha = form_prof.cleaned_data["segunda_manha"]
        segunda_tarde = form_prof.cleaned_data["segunda_tarde"]
        segunda_noite = form_prof.cleaned_data["segunda_noite"]

        terca_manha = form_prof.cleaned_data["terca_manha"]
        terca_tarde = form_prof.cleaned_data["terca_tarde"]
        terca_noite = form_prof.cleaned_data["terca_noite"]

        quarta_manha = form_prof.cleaned_data["quarta_manha"]
        quarta_tarde = form_prof.cleaned_data["quarta_tarde"]
        quarta_noite = form_prof.cleaned_data["quarta_noite"]

        quinta_manha = form_prof.cleaned_data["quinta_manha"]
        quinta_tarde = form_prof.cleaned_data["quinta_tarde"]
        quinta_noite = form_prof.cleaned_data["quinta_noite"]

        sexta_manha = form_prof.cleaned_data["sexta_manha"]
        sexta_tarde = form_prof.cleaned_data["sexta_tarde"]
        sexta_noite = form_prof.cleaned_data["sexta_noite"]

        sabado_manha = form_prof.cleaned_data["sabado_manha"]
        sabado_tarde = form_prof.cleaned_data["sabado_tarde"]

        domingo_manha = form_prof.cleaned_data["domingo_manha"]

        prof_novo = professor.Professor(nome=nome, email=email, 
                                    segunda_manha=segunda_manha, segunda_tarde=segunda_tarde, segunda_noite=segunda_noite, 
                                    terca_manha=terca_manha, terca_tarde=terca_tarde, terca_noite=terca_noite, 
                                    quarta_manha=quarta_manha, quarta_tarde=quarta_tarde, quarta_noite=quarta_noite, 
                                    quinta_manha=quinta_manha, quinta_tarde=quinta_tarde, quinta_noite=quinta_noite, 
                                    sexta_manha=sexta_manha, sexta_tarde=sexta_tarde, sexta_noite=sexta_noite, 
                                    sabado_manha=sabado_manha, sabado_tarde=sabado_tarde, 
                                    domingo_manha=domingo_manha)

        prof_service.editar_professor(prof_editar, prof_novo)
        return redirect('/administrador/')
    return render(request, 'administrador/cadastroprofessor.html', {'form_prof': form_prof})