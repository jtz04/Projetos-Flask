Para usar o Flask no VS Code, comece criando e ativando um ambiente virtual, instale o Flask usando pip, e então crie e execute seu aplicativo Python, geralmente com o comando flask run ou python seu_arquivo.py. O VS Code permite que você escolha o interpretador Python, instale extensões e utilize o terminal integrado para gerenciar seu projeto de forma eficiente. 
 Configure o ambiente de desenvolvimento 
Instale o Python: Se ainda não tiver o Python, instale-o a partir do site oficial do Python e certifique-se de adicionar o Python ao seu PATH.
Instale a extensão de Python: No VS Code, pesquise por "Python" no Marketplace e instale a extensão oficial da Microsoft.
Crie um ambiente virtual: Abra o terminal do VS Code (Ctrl+Shift+'), navegue até a pasta do seu projeto e execute python -m venv .venv para criar um novo ambiente virtual.
Ative o ambiente virtual: No mesmo terminal, ative o ambiente virtual. No Windows, use .\.venv\Scripts\activate. No macOS/Linux, use source .venv/bin/activate. O nome do ambiente virtual aparecerá entre parênteses no início da linha de comando. 

Como executar:
Crie a estrutura de pastas conforme mostrado acima

Instale as dependências:
no terminal:

pip install -r requirements.txt

Execute o aplicativo:
no terminal:

python app.py

Para migrações de banco (quando modificar modelos):
no terminal:

flask db init
flask db migrate -m "Descrição da mudança"
flask db upgrade
