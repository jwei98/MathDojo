# Math Dojo
Alexa skill to help kids practice math!

Initially built [Multiplication Dojo](https://github.com/jwei98/Multiplication-Dojo) as a hack project, but it ended up gaining some actual traction. With that in mind, wanted to build a more intentional, scalable application.

## Developer Notes

### Setting up local dev environment
1. Ensure you have `python3.8` installed and set up.
2. Clone this repository.
3. Initialize a virtual environment: `python3.8 -m venv ~/.envs/MathDojo`.
4. Activate the venv: `source ~/.envs/MathDojo/bin/activate`.
5. Install dependencies: `pip install -r requirements.txt`.

### Misc.
- Dependencies (e.g. `ask-sdk`) are stored in a [Lambda Layer](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html) to separate code from dependencies. This also makes uploading changes must faster.
- Please do NOT commit `venv` stuff (`env`, `bin`, `lib`, etc.).
- If you `pip install` anything, remember to `pip freeze > requirements.txt` before commiting any changes.
