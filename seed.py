import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal, engine
from app.tasks.models import Task
from app.database import Base

TITLES = [
    "Revisar pull requests pendentes",
    "Atualizar documentação da API",
    "Escrever testes de integração",
    "Configurar pipeline de CI/CD",
    "Corrigir bug no endpoint de login",
    "Refatorar camada de serviço",
    "Adicionar validação de campos",
    "Criar migration de novo schema",
    "Revisar logs de produção",
    "Implementar cache na listagem",
    "Subir nova versão para staging",
    "Mapear requisitos do próximo sprint",
    "Revisar cobertura de testes",
    "Otimizar query lenta no relatório",
    "Configurar alertas no Grafana",
    "Migrar secrets para variáveis de ambiente",
    "Deprecar endpoint v1",
    "Revisar dependências desatualizadas",
    "Criar seed de dados para QA",
    "Documentar fluxo de autenticação",
]

DESCRIPTIONS = [
    "Verificar se todos os comentários foram respondidos e aprovações necessárias foram dadas.",
    "Atualizar o README e os exemplos de uso com as mudanças recentes.",
    "Cobrir os cenários de erro e borda que ainda não estão testados.",
    "Automatizar build, testes e deploy para o ambiente de homologação.",
    "O endpoint retorna 500 quando o token está expirado — deve retornar 401.",
    "Extrair lógica duplicada dos controllers para a camada de service.",
    "Adicionar validação de tamanho mínimo e formato no campo de email.",
    "Criar e aplicar migration para a nova coluna `deleted_at` na tabela users.",
    "Investigar erros recorrentes nos logs das últimas 24 horas.",
    "Usar Redis para cachear o resultado por 5 minutos e reduzir carga no banco.",
    "Gerar build, rodar smoke tests e fazer deploy na branch staging.",
    "Coletar histórias de usuário e critérios de aceite junto ao time de produto.",
    "Garantir cobertura mínima de 90% em todas as camadas da aplicação.",
    "Adicionar índice na coluna `created_at` e revisar o plano de execução.",
    "Criar alertas de latência p95 > 500ms e taxa de erro > 1%.",
    "Mover todas as credenciais hardcoded para o vault de secrets.",
    "Adicionar header `Deprecation` e comunicar prazo de desativação.",
    "Rodar `npm audit` e atualizar pacotes com vulnerabilidades conhecidas.",
    "Popular banco de QA com dados realistas para facilitar os testes manuais.",
    "Desenhar diagrama de sequência do fluxo de login com refresh token.",
    None,
]


def seed(n: int = 20) -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        db.query(Task).delete()
        tasks = [
            Task(
                title=random.choice(TITLES),
                description=random.choice(DESCRIPTIONS),
                done=random.random() < 0.3,
            )
            for _ in range(n)
        ]
        db.add_all(tasks)
        db.commit()
        print(f"{n} tasks inseridas com sucesso.")
    finally:
        db.close()


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed(n)
