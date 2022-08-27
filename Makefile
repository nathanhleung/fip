.PHONY: frontend frontend-build server cli anvil all

frontend:
	cd frontend && \
		npm run start

frontend-build:
	cd frontend && \
		npm install && \
		npm run build

server:
	cd server && python3 -m flask run -b 0.0.0.0:9000

cli:
	cd cli && python3 main.py --rpc-url http://142.132.152.124:8546 \
		--etherscan-api-key $ETHERSCAN_API_KEY

anvil:
	git submodule update --remote --init --merge && \
		cd foundry && cargo build

all: frontend-build anvil
	pip3 install -r requirements.txt && \
		make cli