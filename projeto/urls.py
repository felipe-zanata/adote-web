from django.contrib import admin
from django.urls import path
from restaurante import views

urlpatterns = [
    path('', views.login, name='login'),
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('checkin/', views.check_in, name='checkin'),
    path('cadastrar_usuario/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('gerenciar_user/', views.gerenciar_user, name='gerenciar_user'),
    path('gerenciar_user/id/<str:user_id>/', views.gerenciar_user, name='gerenciar_user_with_id'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/<str:tipo>/', views.deletar_checkin, name='deletar_hist'),
    path('relatorios/<str:id>/<str:valor>/', views.deletar_atividade, name='deletar_atividade'),
    path('login_incorreto/', views.login, name='login_erro'),
    path('login_sempermissao/', views.login_semperm, name='login sem permissao'),
    path('editar_user/<str:tipo_usuario>/', views.editar_user, name='editar_user'),
    path('exec_editar_user/', views.executar_editar_user, name='exec_editar_user'),
    path('gerenciar_user/<str:tipo_usuario>/', views.deletar, name='deletar_user'),
    path('num_refeicoes/', views.num_refeicoes, name='num_refeicoes')
]
