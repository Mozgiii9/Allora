#!/bin/bash

# Логотип
echo -e '\e[40m\e[32m'
echo -e '███╗   ██╗ ██████╗ ██████╗ ███████╗██████╗ ██╗   ██╗███╗   ██╗███╗   ██╗███████╗██████╗ '
echo -e '████╗  ██║██╔═══██╗██╔══██╗██╔════╝██╔══██╗██║   ██║████╗  ██║████╗  ██║██╔════╝██╔══██╗'
echo -e '██╔██╗ ██║██║   ██║██║  ██║█████╗  ██████╔╝██║   ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝'
echo -e '██║╚██╗██║██║   ██║██║  ██║██╔══╝  ██╔══██╗██║   ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗'
echo -e '██║ ╚████║╚██████╔╝██████╔╝███████╗██║  ██║╚██████╔╝██║ ╚████║██║ ╚████║███████╗██║  ██║'
echo -e '╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝'
echo -e '\e[0m'

echo -e "\nПодписаться на канал may.crypto{🦅} чтобы быть в курсе самых актуальных нод - https://t.me/maycrypto\n"

sleep 2

while true; do
    echo "1. Установить ноду Allora"
    echo "2. Проверить логи ноды Allora"
    echo "3. Проверить статус ноды Allora"
    echo "4. Проверить обновление ноды Allora"
    echo "5. Выйти из скрипта"
    read -p "Выберите опцию: " option

    case $option in
        1)
            echo "Установка ноды..."

            # Обновление пакетов
            echo "Происходит обновление пакетов..."
            if sudo apt update && sudo apt upgrade -y; then
                echo "Обновление пакетов: Успешно"
            else
                echo "Обновление пакетов: Ошибка"
                exit 1
            fi

            # Установка дополнительных пакетов
            echo "Происходит установка дополнительных пакетов..."
            if sudo apt install ca-certificates zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev curl git wget make -y; then
                echo "Установка дополнительных пакетов: Успешно"
            else
                echo "Установка дополнительных пакетов: Ошибка"
                exit 1
            fi

            # Установка Python
            echo "Происходит установка Python..."
            if sudo apt install python3 -y; then
                echo "Установка Python: Успешно"
            else
                echo "Установка Python: Ошибка"
                exit 1
            fi

            echo "Версия Python:"
            python3 --version

            if sudo apt install python3-pip -y; then
                echo "Установка pip для Python: Успешно"
            else
                echo "Установка pip для Python: Ошибка"
                exit 1
            fi

            echo "Версия pip для Python:"
            pip3 --version

            # Установка Docker
            echo "Происходит установка Docker..."
            if curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg &&
               echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null &&
               sudo apt-get update &&
               sudo apt-get install docker-ce docker-ce-cli containerd.io -y; then
                echo "Установка Docker: Успешно"
            else
                echo "Установка Docker: Ошибка"
                exit 1
            fi

            echo "Версия Docker:"
            docker version

            # Установка Docker Compose
            echo "Происходит установка Docker Compose..."
            if sudo apt-get install docker-compose -y; then
                echo "Установка Docker Compose: Успешно"
            else
                echo "Установка Docker Compose: Ошибка"
                exit 1
            fi

            echo "Версия Docker Compose:"
            docker-compose version

            # Установка разрешений
            echo "Происходит установка разрешений для Docker..."
            if sudo groupadd docker && sudo usermod -aG docker $USER; then
                echo "Установка разрешений для Docker: Успешно"
            else
                echo "Установка разрешений для Docker: Разрешение было применено по умолчанию"
            fi

            # Установка GO
            echo "Происходит установка GO..."
            if sudo rm -rf /usr/local/go &&
               curl -L https://go.dev/dl/go1.22.4.linux-amd64.tar.gz | sudo tar -xzf - -C /usr/local &&
               echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> $HOME/.bash_profile &&
               echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> $HOME/.bash_profile &&
               source $HOME/.bash_profile; then
                echo "Установка GO: Успешно"
            else
                echo "Установка GO: Ошибка"
                exit 1
            fi

            echo "Версия GO:"
            go version

            # Установка Allorad Wallet
            echo "Происходит установка Allorad Wallet..."
            if git clone https://github.com/allora-network/allora-chain.git &&
               cd allora-chain && make all; then
                echo "Установка Allorad Wallet: Успешно"
            else
                echo "Установка Allorad Wallet: Ошибка"
                exit 1
            fi

            echo "Версия Allorad Wallet:"
            allorad version

            # Ввод seed фразы и пароля от кошелька
            echo "Введите seed фразу и пароль от кошелька для Allorad..."
            if allorad keys add testkey --recover; then
                echo "Ввод seed фразы и пароля от кошелька: Успешно"
            else
                echo "Ввод seed фразы и пароля от кошелька: Ошибка"
                exit 1
            fi

            # Установка Worker
            echo "Происходит установка Worker..."
            if cd $HOME && git clone https://github.com/allora-network/basic-coin-prediction-node &&
               cd basic-coin-prediction-node &&
               mkdir worker-data head-data &&
               sudo chmod -R 777 worker-data head-data; then
                echo "Установка Worker: Успешно"
            else
                echo "Установка Worker: Ошибка"
                exit 1
            fi

            # Создание ключа
            echo "Создание ключа head..."
            if sudo docker run -it --entrypoint=bash -v $PWD/head-data:/data alloranetwork/allora-inference-base:latest -c "mkdir -p /data/keys && (cd /data/keys && allora-keys)"; then
                echo "Создание ключа head: Успешно"
            else
                echo "Создание ключа head: Ошибка"
                exit 1
            fi

            # Создание Worker ключа
            echo "Создание ключа worker..."
            if sudo docker run -it --entrypoint=bash -v $PWD/worker-data:/data alloranetwork/allora-inference-base:latest -c "mkdir -p /data/keys && (cd /data/keys && allora-keys)"; then
                echo "Создание ключа worker: Успешно"
            else
                echo "Создание ключа worker: Ошибка"
                exit 1
            fi

            # Получить ключ head-id
            echo "Получение head-id..."
            head_id=$(cat head-data/keys/identity)
            if [ -z "$head_id" ]; then
                echo "Получение head-id: Ошибка"
                exit 1
            else
                echo "Получение head-id: Успешно"
            fi

            # Запросить seed фразу пользователя
            read -p "Введите seed фразу: " seed_phrase

            # Удаление файла docker-compose.yml и создание нового файла
            echo "Создание файла docker-compose.yml..."
            if sudo apt install nano -y && rm -rf docker-compose.yml; then
                echo "Создание файла docker-compose.yml: Успешно"
            else
                echo "Создание файла docker-compose.yml: Ошибка"
                exit 1
            fi

            # Создание файла docker-compose.yml
            cat <<EOL > docker-compose.yml
version: '3'

services:
  inference:
    container_name: inference-basic-eth-pred
    build:
      context: .
    command: python -u /app/app.py
    ports:
      - "8000:8000"
    networks:
      eth-model-local:
        aliases:
          - inference
        ipv4_address: 172.22.0.4
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/inference/ETH"]
      interval: 10s
      timeout: 5s
      retries: 12
    volumes:
      - ./inference-data:/app/data

  updater:
    container_name: updater-basic-eth-pred
    build: .
    environment:
      - INFERENCE_API_ADDRESS=http://inference:8000
    command: >
      sh -c "
      while true; do
        python -u /app/update_app.py;
        sleep 24h;
      done
      "
    depends_on:
      inference:
        condition: service_healthy
    networks:
      eth-model-local:
        aliases:
          - updater
        ipv4_address: 172.22.0.5

  worker:
    container_name: worker-basic-eth-pred
    environment:
      - INFERENCE_API_ADDRESS=http://inference:8000
      - HOME=/data
    build:
      context: .
      dockerfile: Dockerfile_b7s
    entrypoint:
      - "/bin/bash"
      - "-c"
      - |
        if [ ! -f /data/keys/priv.bin ]; then
          echo "Generating new private keys..."
          mkdir -p /data/keys
          cd /data/keys
          allora-keys
        fi
        # Change boot-nodes below to the key advertised by your head
        allora-node --role=worker --peer-db=/data/peerdb --function-db=/data/function-db \
          --runtime-path=/app/runtime --runtime-cli=bls-runtime --workspace=/data/workspace \
          --private-key=/data/keys/priv.bin --log-level=debug --port=9011 \
          --boot-nodes=/ip4/172.22.0.100/tcp/9010/p2p/$head_id \
          --topic=1 \
          --allora-chain-key-name=testkey \
          --allora-chain-restore-mnemonic='$seed_phrase' \
          --allora-node-rpc-address=https://allora-rpc.edgenet.allora.network/ \
          --allora-chain-topic-id=1
    volumes:
      - ./worker-data:/data
    working_dir: /data
    depends_on:
      - inference
      - head
    networks:
      eth-model-local:
        aliases:
          - worker
        ipv4_address: 172.22.0.10

  head:
    container_name: head-basic-eth-pred
    image: alloranetwork/allora-inference-base-head:latest
    environment:
      - HOME=/data
    entrypoint:
      - "/bin/bash"
      - "-c"
      - |
        if [ ! -f /data/keys/priv.bin ]; then
          echo "Generating new private keys..."
          mkdir -p /data/keys
          cd /data/keys
          allora-keys
        fi
        allora-node --role=head --peer-db=/data/peerdb --function-db=/data/function-db  \
          --runtime-path=/app/runtime --runtime-cli=bls-runtime --workspace=/data/workspace \
          --private-key=/data/keys/priv.bin --log-level=debug --port=9010 --rest-api=:6000
    ports:
      - "6000:6000"
    volumes:
      - ./head-data:/data
    working_dir: /data
    networks:
      eth-model-local:
        aliases:
          - head
        ipv4_address: 172.22.0.100

networks:
  eth-model-local:
    driver: bridge
    ipam:
      config:
        - subnet: 172.22.0.0/24

volumes:
  inference-data:
  worker-data:
  head-data:
EOL

            # Запуск Worker'а
            echo "Запуск Worker'а..."
            if docker compose build && docker compose up -d; then
                echo "Запуск Worker'а: Успешно"
            else
                echo "Запуск Worker'а: Ошибка"
                exit 1
            fi

            # Проверка статуса ноды
            echo "Проверка статуса ноды..."
            if curl --location 'http://localhost:6000/api/v1/functions/execute' \
                --header 'Content-Type: application/json' \
                --data '{
                    "function_id": "bafybeigpiwl3o73zvvl6dxdqu7zqcub5mhg65jiky2xqb4rdhfmikswzqm",
                    "method": "allora-inference-function.wasm",
                    "parameters": null,
                    "topic": "1",
                    "config": {
                        "env_vars": [
                            {
                                "name": "BLS_REQUEST_PATH",
                                "value": "/api"
                            },
                            {
                                "name": "ALLORA_ARG_PARAMS",
                                "value": "ETH"
                            }
                        ],
                        "number_of_nodes": -1,
                        "timeout": 2
                    }
                }'; then
                echo "Проверка статуса ноды: Успешно"
            else
                echo "Проверка статуса ноды: Ошибка"
            fi

            echo -e "\nПодписаться на канал may.crypto{🦅} чтобы быть в курсе самых актуальных нод - https://t.me/maycrypto\n"
            ;;
        2)
            echo "Через 60 секунд пойдут логи. Для выхода из отображения логов нажмите CTRL+C. Пока Вы можете подписаться на канал may.crypto{🦅} чтобы быть в курсе самых актуальных нод - https://t.me/maycrypto\n"
            sleep 60
            container_id=$(docker ps --filter "ancestor=basic-coin-prediction-node-worker" --format "{{.ID}}")
            if [ -z "$container_id" ]; then
                echo "Контейнер с IMAGE 'basic-coin-prediction-node-worker' не найден."
            else
                docker logs -f $container_id
            fi
            ;;
        3)
            echo "Проверка статуса ноды..."
            if curl --location 'http://localhost:6000/api/v1/functions/execute' \
                --header 'Content-Type: application/json' \
                --data '{
                    "function_id": "bafybeigpiwl3o73zvvl6dxdqu7zqcub5mhg65jiky2xqb4rdhfmikswzqm",
                    "method": "allora-inference-function.wasm",
                    "parameters": null,
                    "topic": "1",
                    "config": {
                        "env_vars": [
                            {
                                "name": "BLS_REQUEST_PATH",
                                "value": "/api"
                            },
                            {
                                "name": "ALLORA_ARG_PARAMS",
                                "value": "ETH"
                            }
                        ],
                        "number_of_nodes": -1,
                        "timeout": 2
                    }
                }'; then
                echo "Проверка статуса ноды: Успешно"
            else
                echo "Проверка статуса ноды: Ошибка"
            fi
            ;;
        4)
            echo "Проверка обновления ноды..."
            response=$(curl -s http://localhost:8000/update)
            if [ "$response" == "0" ]; then
                echo "Версия ноды актуальна."
            else
                echo "Версия ноды неактуальна."
            fi
            ;;
        5)
            echo "Выход из скрипта."
            exit 0
            ;;
        *)
            echo "Неверная опция. Пожалуйста, выберите 1, 2, 3, 4 или 5."
            ;;
    esac
done
