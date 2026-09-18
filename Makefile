.PHONY: verify
verify:
	PYTHONPATH=src python3 -m unittest discover -s tests -v
	python3 -m unittest discover -s polyglot-rl-adapters/tests -v
	PYTHONPATH=src python3 -m repo_response_judge.cli judge examples/comparison.json --format json
