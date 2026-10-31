# language: pt
Funcionalidade: Gerenciamento de Tarefas
  Como membro da equipe
  Quero gerenciar minhas tarefas
  Para organizar o trabalho do time

  Cenário: Criar uma nova tarefa
    Dado que não existe nenhuma tarefa
    Quando eu criar uma tarefa com título "Estudar BDD"
    Então a tarefa deve ser criada com sucesso
    E o título da tarefa deve ser "Estudar BDD"
    E a tarefa deve estar pendente

  Cenário: Criar uma tarefa sem título é inválido
    Dado que não existe nenhuma tarefa
    Quando eu tentar criar uma tarefa sem título
    Então devo receber um erro de validação

  Cenário: Listar tarefas quando não há nenhuma
    Dado que não existe nenhuma tarefa
    Quando eu listar todas as tarefas
    Então a lista deve estar vazia

  Cenário: Listar tarefas existentes
    Dado que existe uma tarefa com título "Tarefa Um"
    E que existe uma tarefa com título "Tarefa Dois"
    Quando eu listar todas as tarefas
    Então a lista deve conter 2 tarefas

  Cenário: Buscar tarefa existente pelo ID
    Dado que existe uma tarefa com título "Minha Tarefa"
    Quando eu buscar a tarefa pelo seu ID
    Então a tarefa deve ser encontrada
    E o título da tarefa deve ser "Minha Tarefa"

  Cenário: Buscar tarefa que não existe
    Dado que não existe nenhuma tarefa
    Quando eu buscar a tarefa com ID 999
    Então devo receber um erro de não encontrado

  Cenário: Concluir uma tarefa pendente
    Dado que existe uma tarefa com título "Tarefa Pendente"
    Quando eu alternar o status da tarefa
    Então a tarefa deve estar concluída

  Cenário: Reabrir uma tarefa já concluída
    Dado que existe uma tarefa concluída com título "Tarefa Concluída"
    Quando eu alternar o status da tarefa
    Então a tarefa deve estar pendente

  Cenário: Excluir uma tarefa existente
    Dado que existe uma tarefa com título "Tarefa para Excluir"
    Quando eu excluir a tarefa
    Então a tarefa não deve mais existir

  Cenário: Buscar a mesma tarefa duas vezes serve do cache
    Dado que existe uma tarefa com título "Tarefa Cacheada"
    Quando eu buscar a tarefa pelo seu ID
    E eu buscar a tarefa pelo seu ID novamente
    Então ambas as respostas devem retornar a mesma tarefa
