.PHONY: bootstrap fetch etl build test dev clean

bootstrap:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -e "etl[dev]"
	cd web && npm install

fetch:
	.venv/bin/python -m f1_atlas_etl fetch

etl:
	.venv/bin/python -m f1_atlas_etl build

build: etl
	cd web && npm run build

test:
	.venv/bin/pytest -q

dev: etl
	cd web && npm run dev

clean:
	rm -rf web/dist data/derived/*.sqlite web/src/data/generated
