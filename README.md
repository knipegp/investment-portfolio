# Investment Portfolio

## Development

Development instructions so easy that my dad could follow them.

Run the following to setup a development environment:

``` sh
poetry install --sync
poetry run pre-commit install
```

Alternatively, you can enter the Poetry shell and run from within the shell:

``` sh
poetry shell
pre-commit install
```

Alternatively-alternatively, you're using an IDE without the shell and we'll
have to figure something else out.

Before submitting a PR, ensure high code quality by running Tox:

``` sh
tox
```
