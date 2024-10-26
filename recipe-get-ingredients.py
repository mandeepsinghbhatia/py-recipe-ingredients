#!/usr/bin/env python

import platform
import sqlite3
import os
# import json
import tkinter as tk
from tkinter import messagebox
import subprocess

DB = "./recipe-ingredients.db"
RECIPES_FILE = "output/recipes.csv"
INGREDIENTS_FILE = "output/ingredients.json"
PRINT_FILE = "output/recipe-ingredients.txt"  # markdown file for printing

window: tk.Tk = None
all_recipes = []
selected_recipes = []
selected_ingredients = {}


def get_all_recipes():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id,name FROM recipes")
    res = c.fetchall()
    for row in res:
        all_recipes.append(f"{row[0]}, {row[1]}")
    conn.close()
    return all_recipes


def add_recipe():
    sel = (window.nametowidget("recipe_frame").nametowidget("all_recipe_list")).curselection()
    lst = window.nametowidget("for_ingredient_frame").nametowidget("for_ingredient_list")
    for item in sel:
        if all_recipes[item] not in selected_recipes:
            lst.insert(tk.END, all_recipes[item])
            selected_recipes.append(all_recipes[item])


def recipe_select_cb(event):
    # print("op")
    try:
        sel = event.widget.curselection()[0]
    except:
        return
    # sel = (window.nametowidget("recipe_frame").nametowidget("all_recipe_list")).curselection()[0]
    window.nametowidget("text_frame").nametowidget("recipe_label").configure(text=all_recipes[sel])


def ing_select_cb(event):
    # print("noop")
    pass


def clear_recipes():
    lst: tk.Listbox = window.nametowidget("for_ingredient_frame").nametowidget("for_ingredient_list")
    lst.delete(0, tk.END)
    selected_recipes.clear()


def remove_recipes():
    lst: tk.Listbox = window.nametowidget("for_ingredient_frame").nametowidget("for_ingredient_list")
    sel = lst.curselection()
    for item in sel:
        vals = str(lst.get(item, item)[0])
        lst.delete(item)
        selected_recipes.remove(vals)


def map_ingredients(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("select ingredient_id from recipes_ingredients where recipe_id=?",
              (id,))
    res = c.fetchall()
    for ing_row in res:
        c.execute("select id, name from ingredients where id=?",
                  (int(ing_row[0]),))
        ing = c.fetchone()
        selected_ingredients[ing[0]] = ing[1]


def open_saved_markdown():
    try:
        ops = platform.system()
        if ops.lower() == "linux":
            p = subprocess.Popen(['xdg-open', PRINT_FILE])
        elif ops.lower() == "windows":
            p = subprocess.Popen(['notepad.exe', PRINT_FILE])
        elif ops.lower() == "darwin":
            p = subprocess.Popen(['open', PRINT_FILE])
        else:
            return
        p.communicate(timeout=2)
    except:
        pass


def save_recipes():
    lst: tk.Listbox = window.nametowidget("for_ingredient_frame").nametowidget("for_ingredient_list")
    sel = lst.get(0, tk.END)
    if len(sel) < 1:
        return
    selected_ingredients.clear()
    for item in sel:
        vals = str(item).split(",")
        map_ingredients(int(vals[0]))

    # with open(INGREDIENTS_FILE, "wt") as fw:
    #    json.dump(selected_ingredients, fw, indent=4)

    with open(PRINT_FILE, "wt") as fw:
        fw.write("# Recipes and Ingredients\n\n")
        fw.write("## Recipes\n")
        for item in selected_recipes:
            vals = str(item).split(",")
            fw.write(f"- {vals[1]}\n")

        fw.write("\n## Ingredients\n")
        count = 0
        for item in selected_ingredients:
            count += 1
            fw.write(f"{count}. {selected_ingredients[item]}\n")

    messagebox.showinfo("Recipe Ingredients Saved.",
                        f"({len(selected_recipes)})Recipe and ({len(selected_ingredients)})Ingredients\n"
                        " information has been successfully Saved.")
    open_saved_markdown()


def create_gui():
    """Generates the main tkinter window."""
    window = tk.Tk()
    window.title("Recipe Ingredient Getter")
    window.geometry("1000x700")
    # window.resizable(False, False)
    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=1)
    window.rowconfigure(0, weight=5)
    window.rowconfigure(1, weight=1)
    # window.rowconfigure(2, weight = 2)

    # Recipe List Frame
    recipe_frame = tk.LabelFrame(window, text="Recipes Available", name="recipe_frame")
    recipe_frame.grid(row=0, column=0, padx=20, pady=20, sticky="news")

    scrollbar = tk.Scrollbar(recipe_frame)
    scrollbar.pack(side="right", fill="y")

    # tk.Label(recipe_frame, text=":", name= "recipe_label").pack(padx=5)
    recipe_list = tk.Listbox(recipe_frame, name="all_recipe_list", selectmode=tk.EXTENDED, yscrollcommand=scrollbar.set)
    recipe_list.pack(expand=True, fill="both")
    for rk in all_recipes:
        recipe_list.insert(tk.END, rk)

    scrollbar.config(command=recipe_list.yview)

    # Ingredient List Frame
    for_ingredient_frame = tk.LabelFrame(window, text="Selected Recipes", name="for_ingredient_frame")
    for_ingredient_frame.grid(row=0, column=1, padx=20, pady=20, sticky="news")

    for_ingredient_list = tk.Listbox(for_ingredient_frame, name="for_ingredient_list")
    for_ingredient_list.pack(expand=True, fill="both")

    load_button = tk.Button(recipe_frame, text="Add Recipe", command=add_recipe)
    load_button.pack(side="left", padx=5)

    save_button = tk.Button(for_ingredient_frame, text="Save Ingredients", command=save_recipes)
    save_button.pack(side="left", padx=5)
    remove_button = tk.Button(for_ingredient_frame, text="Remove", command=remove_recipes)
    remove_button.pack(side="right", padx=5)
    clear_button = tk.Button(for_ingredient_frame, text="Clear", command=clear_recipes)
    clear_button.pack(side="right", padx=5)

    text_frame = tk.LabelFrame(window, text="Recipe", name="text_frame")
    text_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=1, sticky="ew")
    tk.Label(text_frame, text=":", name="recipe_label").pack(padx=5, side="left")

    recipe_list.bind('<<ListboxSelect>>', recipe_select_cb)
    for_ingredient_list.bind('<<ListboxSelect>>', ing_select_cb, add=False)

    return window


if __name__ == "__main__":
    if not os.path.exists("output"):
        os.mkdir("output")
    all_recipes = get_all_recipes()
    window = create_gui()
    window.mainloop()
    messagebox.showinfo("About Recipes Software",
                        "Software By:\t Mandeep Singh Bhatia.\n"
                        "Company:\t SciEngineer Robotics Corp.\n"
                        "Copyright:\t August 2024.\n"
                        "Website:\t\t www.sci.engineer")
