.PHONY: bootstrap build test dev etl clean

bootstrap:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -e "etl[dev]"
	cd web && npm install

etl:
	.venv/bin/python -m f1_atlas_etl.build --out data/derived/atlas.sqlite

build: etl
	cd web && npm run build

test:
	.venv/bin/pytest -q
	cd web && npm test --if-present

dev:
	cd web && npm run dev

clean:
	rm -rf web/dist data/derived/*.sqlite
