Map = "maps/easy/01_linear_path.txt"

install:
	@uv sync

run:
	@uv run python3 main.py $(Map)

debug:
	@python3 -m pdb main.py

clean:
	@rm -rf __pycache__
	@rm -rf .mypy_cache

lint:
	@flake8 *.py
	
	@mypy *.py \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
