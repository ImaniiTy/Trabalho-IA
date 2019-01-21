# Trabalho-IA

Informacoes sobre a pasta choi-yena:

    -Sao basicamente as librarys que a gente estiver usando
    -sobre o nome: eu so botei um nome aleatorio de uma mina de um grupo de k-pop que eu gosto
    -Para instalar basta rodar o comando: "pip install -e ." o "-e" é para que a library instalada no python possa ser editada
    -o bot deve rodar sem essa instalação porem se der algum proplema isso deve resolver
    
    Sobre cada library:
        -hendrick: tem os codigos dados pelo professor
        -hlt: sao os codigos do SDK do halite
        -utils_:
            -basicamente oque eu fiz ate agora
            -na wrapper.py tem a classe que extende a classe mdp do professor
            -na parameters.py tem os parametros que serao usados durante o codigo e dps testados usando o algoritimo genetico

Para rodar o bot foi usado esse programa disponibilizado pelo halite: https://github.com/HaliteChallenge/Halite-III/tree/master/tools/hlt_client
apos instalar basta abrir um terminal na pasta raiz do projeto(onde esta o MyBot.py) e roda esse comando para executar uma partida:
python3 -m hlt_client play -r "python MyBot.py" -r "python MyBot.py" -b "halite.exe" --output-dir "output" -i 1
