"""
Atualiza automaticamente a seção "Projetos recentes" do README.md
buscando os repositórios públicos mais recentemente atualizados
do usuário no GitHub.

Executado pela GitHub Action em .github/workflows/update-projects.yml
"""

import os
import requests

# ---- Configurações ----
USERNAME = "rhafaelrsilva"
MAX_PROJECTS = 4           # quantos repositórios mostrar
README_PATH = "README.md"
START_MARKER = "<!-- PROJECTS:START -->"
END_MARKER = "<!-- PROJECTS:END -->"


def buscar_repositorios():
    """Busca os repositórios públicos do usuário, ordenados por
    data de atualização (mais recentes primeiro), ignorando forks."""
    url = f"https://api.github.com/users/{USERNAME}/repos"
    params = {"sort": "updated", "direction": "desc", "per_page": 100}

    headers = {}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    resposta = requests.get(url, params=params, headers=headers, timeout=30)
    resposta.raise_for_status()
    repos = resposta.json()

    # Remove forks e repositórios arquivados
    repos = [r for r in repos if not r.get("fork") and not r.get("archived")]

    return repos[:MAX_PROJECTS]


def montar_html(repos):
    """Monta o bloco HTML com os cartões de projeto (estilo pin do GitHub)."""
    linhas = ['<p align="left">']
    for repo in repos:
        nome = repo["name"]
        linhas.append(
            f'  <a href="https://github.com/{USERNAME}/{nome}">\n'
            f'    <img src="https://github-readme-stats.vercel.app/api/pin/'
            f'?username={USERNAME}&repo={nome}&theme=tokyonight" />\n'
            f'  </a>'
        )
    linhas.append('</p>')
    return "\n".join(linhas)


def atualizar_readme(html_novo):
    with open(README_PATH, "r", encoding="utf-8") as f:
        conteudo = f.read()

    inicio = conteudo.find(START_MARKER)
    fim = conteudo.find(END_MARKER)

    if inicio == -1 or fim == -1:
        raise RuntimeError(
            "Marcadores PROJECTS:START / PROJECTS:END não encontrados no README.md"
        )

    novo_conteudo = (
        conteudo[: inicio + len(START_MARKER)]
        + "\n"
        + html_novo
        + "\n"
        + conteudo[fim:]
    )

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(novo_conteudo)


def main():
    repos = buscar_repositorios()
    if not repos:
        print("Nenhum repositório encontrado. README não foi alterado.")
        return

    html = montar_html(repos)
    atualizar_readme(html)
    print(f"README atualizado com {len(repos)} projeto(s): "
          f"{', '.join(r['name'] for r in repos)}")


if __name__ == "__main__":
    main()
