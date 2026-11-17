# Put this project on GitHub

Repository creation could not be completed in this session: browser automation stopped
because URL-policy enforcement is unsupported for the available Windows browser.
No repository was created and no repository URL is claimed.

1. Sign in to GitHub and choose New repository.
2. Name it `python-unit-converter` (or another available name), choose Public, and create it.
3. Choose Upload an existing file and upload the contents of this project folder,
   retaining `tests/`, `docs/`, and `.github/workflows/` directory structure.
   Alternatively use Git locally as shown below.
4. Commit the files, open the repository, and verify the source and README are visible.
5. Open Actions and verify the Python tests pass. If uploading through the website,
   include the hidden `.github` folder so the workflow is installed.
6. Copy the repository URL to share the project.

With Git installed, open a terminal in the project directory and run these commands,
replacing YOUR-REPOSITORY-URL with the URL GitHub provides:

```sh
git init
git add .
git commit -m "Add unit converter, tests, and project documentation"
git branch -M main
git remote add origin YOUR-REPOSITORY-URL
git push -u origin main
```

Authenticate with GitHub normally if prompted. Do not paste passwords or access tokens
into source files. Commit later changes under the actual contributor's identity.
