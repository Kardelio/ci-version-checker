# CI Version Checker

## Requirements

Install the following:

* pip3 install requests --break-system-packages
* pip3 install packaging --break-system-packages

Env Vars must be set for Github API
These are below and are your github username and an API key for the API (format: ghp_XXXXX)

```
    export GITHUB_USERNAME="_____"
    export GITHUB_API_KEY="____"
```

## How to run

### Common

Both commands have an auto edit / replace feature that will edit your code with the new versions

Simply add the `--replace` flag to the command, like so:

```
bitrise_checker.py --replace
```

### Bitrise

`Make sure you have a bitrise.yml file in the root of your repo`

1. Navigate to your repository in your terminal
2. Run the scripts bitrise_checker.py

### Github Actions

`Make sure you have a .github/ dir with github action yml files in`

1. Navigate to your repository in your terminal
2. Run the scripts gha_checker.py
