# SimpleDeployer

Edit `~/.deployer/deployer.yaml` this is your config file.

```yaml
definitions:
    - outDir: /var/www/graphPlayground
      repository: https://github.com/MikeDombo/graphPlayground.git
      sourceDir: .
      ignore:
          - .*/* # Ignore all directories starting with ".". Ex. .git and .vscode
      noOverwrite:
          - .gitlab-ci.yml # If you have a local config file, for example and don't want it overwritten every time you deploy, add it here
      noRemove:
          - venv/* # If you are using the 'upgrade' option and want to protect files/folders from being removed during the deploy, add them here
      postInstall: # Commands to run after the copy happens. Use this to update node_modules and similar.
          - npm ci
          - npm run build
```

Additional options:

- branch: The branch to clone from Git