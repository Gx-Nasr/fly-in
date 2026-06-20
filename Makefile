Map = "maps/easy/01_linear_path.txt"

install:
	@uv sync

run:
	@uv run python3 -m src $(Map)

debug:
	@python3 -m pdb main.py

clean:
	@rm -rf src/__pycache__
	@rm -rf __pycache__
	@rm -rf src/.mypy_cache
	@rm -rf .mypy_cache

lint:
	@flake8 ./src
	
	@mypy ./src \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
