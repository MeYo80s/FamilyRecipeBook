# FamilyRecipeBook

A clean starter for documenting family favorite recipes (no meal-plan or shopping-list automation).

## Structure
- `recipes/` - category folders for recipe files
- `assets/recipes/` - optional recipe photos
- `RECIPE_INDEX.md` - links to recipes in category sections
- `RECIPE_BOOK.md` - generated all-in-one family recipe book
- `templates/recipe-template.md` - copy/paste template for new recipes
- `scripts/generate_recipe_book.py` - rebuilds `RECIPE_BOOK.md`

## Quick Start
1. Copy `templates/recipe-template.md` to a new file under `recipes/...`.
2. Add a link to the recipe in `RECIPE_INDEX.md`.
3. Run: `python3 scripts/generate_recipe_book.py`

## Optional: create a new git repo
- `git init`
- `git add .`
- `git commit -m "Initial family recipe book scaffold"`
