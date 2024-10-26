#!/usr/bin/env python
import json
import os.path

#flask --app web-recipe run
from flask import Flask, render_template, request, redirect, url_for, flash
import subprocess

ing_file = "output/ingredients.json"

app = Flask(__name__)

def get_recipes(saved:bool = False):
    flag = "--load" if saved else "--list"
    spl = ',' if saved else ':'
    out = subprocess.check_output(['python3', 'recipe-get.py',flag])
    ret = get_recipe_map(out, spl)
    return ret


def get_recipe_map(out, spl):
    ret = {}
    lines = out.splitlines()
    for line in lines:
        line_str = line.decode().strip()
        if line_str != "":
            rid = line_str.split(spl)[0].strip()
            rname = line_str.split(spl)[1].strip()
            ret[rid] = rname
    return ret


recipes = get_recipes()

def find_recipes(fnd: str):
    spl = ':'
    out = subprocess.check_output(['python3', 'recipe-get.py',"--find", fnd])
    ret = get_recipe_map(out, spl)
    return ret

def save_selection(lst_recipe_id: list):
    for itm in lst_recipe_id:
        subprocess.call(['python3', 'recipe-get.py','--add', itm])

def remove_selection(lst_recipe_id: list):
    for itm in lst_recipe_id:
        subprocess.call(['python3', 'recipe-get.py','--remove', itm])

def delete_selection():
    subprocess.call(['python3', 'recipe-get.py','--delete'])

def save_ingredients():
    subprocess.call(['python3', 'recipe-get.py','--save_ingredients'])

def get_recipe_selection_htm(act="/"):
    saved = get_recipes(saved=True)
    htm=""
    htm += f"<form action='{act}' method='post'>"
    htm += '<input type="hidden" name="form_identifier" value="selection">'
    htm += f"<input type='submit' value='Process Selection'><br><br>"
    htm += f"<input type='checkbox' id='remove_all' name='remove_all' value='remove_all'>"
    htm += f"<label for='remove_all'> Remove All</label><br><br>"
    htm += f"<input type='checkbox' id='remove' name='remove' value='remove'>"
    htm += f"<label for='remove'> Remove Selected</label><br><br><br>"
    for recipe_id in recipes:
        chk = "checked" if recipe_id in saved else ""
        htm += f"<input type='checkbox' id='{recipe_id}' name='recipe_name' value='{recipe_id}' {chk}>"
        htm += f"<label for='{recipe_id}'> {recipes[recipe_id]}</label><br><br>"
    htm += "</form>"
    return htm

def unordered_recipes(lst_recipe_id: list):
    htm = ""
    htm += "<ul>"
    for lst_itm in lst_recipe_id:
        htm += f"<li>{recipes[lst_itm]}</li>"
    htm += "</ul>"
    return htm

def get_search_htm(act="/"):
    htm = ""
    htm += f"<form action='{act}' method='post'>"
    htm += '<input type="hidden" name="form_identifier" value="search">'
    htm += '<label for="fname">Search Recipe Name:</label><br>'
    htm += '<input type="text" id="fname" name="fname" value=""><br>'
    htm += f"<input type='checkbox' id='add_recipe' name='add_recipe' value='add'>"
    htm += f"<label for='add_recipe'> Add found recipe</label><br><br>"
    htm += f"<input type='submit' value='Search'><br><br>"
    htm += "</form>"
    return htm

def get_redirect_frm(act="/ingredients", msg='Get Ingredients'):
    htm = ""
    htm += f"<form action='{act}' method='post'>"
    htm += f"<input type='submit' value='{msg}'><br><br>"
    htm += "</form>"
    return htm


@app.route("/", methods=['GET', 'POST'])
def index():
    htm = "<h1>Recipe, World!</h1>"
    if request.method == "POST":
        form_identifier = request.form.get('form_identifier')
        if form_identifier == 'selection':
            lst = request.form.getlist("recipe_name")
            if request.form.get("remove_all") is not None:
                delete_selection()
            elif len(lst) > 0:
                if request.form.get("remove") is not None:
                    remove_selection(lst)
                    htm += "<h2>Selection Removed</h2>"
                    htm += unordered_recipes(lst)
                else:
                    save_selection(lst)
                    htm += "<h2>Selection added</h2>"
                    htm += unordered_recipes(lst)
        elif form_identifier == 'search':
            mp = find_recipes(request.form.get("fname"))
            lst = []
            for itm in mp:
                lst.append(itm)
            if len(lst) > 0:
                htm += "<h2>Found list:</h2>"
                htm += unordered_recipes(lst)
                if request.form.get("add_recipe"):
                    save_selection(lst)
            else:
                htm += "<h2>Nothing Found.</h2>"

    htm += get_redirect_frm()
    htm += get_search_htm()
    htm += get_recipe_selection_htm()
    return htm



@app.route("/ingredients", methods=['GET', 'POST'])
def ingredients():
    htm = "<h1>Ingredients</h1>"
    htm += get_redirect_frm("/","Home Page")
    save_ingredients()
    if os.path.exists(ing_file):
        with open(ing_file, "rt") as f:
            data = json.load(f)
            htm += f"<p>Date: {data['date']}</p>"
            htm += f"<p>Time: {data['time']}</p>"
            htm += "<h2> Recipes </h2>"
            htm += "<ul>"
            for rcp in data['recipes']:
                htm += f"<li>{data['recipes'][rcp]}</li>"
            htm += "</ul>"
            htm += "<h2> Ingredients </h2>"
            htm += "<table><tr><th>Ingredient</th><th>Quantity</th><th>Units</th></tr>"
            for ing in data['ingredients']:
                htm += "<tr>"
                htm += f"<td>{data['ingredients'][ing][0]}</td>"
                htm += f"<td>{data['ingredients'][ing][1]}</td>"
                htm += f"<td>{data['ingredients'][ing][2]}</td>"
                htm += "</tr>"
            htm += "</table>"
            return htm

    else:
        htm += "<h2>No Recipes Found.</h2>"
    return htm

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

