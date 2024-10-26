#!/usr/bin/env python

import sqlite3
import os
import shutil
import argparse
import json
from datetime import datetime

DB = "./recipe-ingredients.db"
RECIPES_FILE = "output/recipes.csv"
INGREDIENTS_FILE = "output/ingredients.json"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--delete", help="delete recipes", action="store_true")
    parser.add_argument("--list", help="list all recipe names", action="store_true")
    parser.add_argument("--find", help="find recipe names", type=str, required=False)
    parser.add_argument("--load", help="load recipe list", required=False, action="store_true")
    parser.add_argument("--add", help="chosen recipe by id", type=int, required=False)
    parser.add_argument("--remove", help="remove chosen recipe by id", type=int, required=False)
    parser.add_argument("--save_as", help="save recipe list as", type=str, required=False)
    parser.add_argument("--save_ingredients", help="save all recipe ingredients", required=False,
                        action="store_true")
    parser.add_argument("--about", help="program info", action="store_true")
    args = parser.parse_args()
    if not os.path.exists("output"):
        os.mkdir("output")
    if args.delete and os.path.exists(RECIPES_FILE):
        if os.path.exists(RECIPES_FILE):
            os.remove(RECIPES_FILE)
    elif args.load and os.path.exists(RECIPES_FILE):
        if os.path.exists(RECIPES_FILE):
            with open(RECIPES_FILE, "rt") as f:
                print(f.read())
    elif args.list:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT id, name FROM recipes")
        res = c.fetchall()
        for row in res:
            print(f"{row[0]} : {row[1]}\n")
        conn.close()
    elif args.find:
        fnd = args.find
        if fnd != "":
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute(f"SELECT id,name FROM recipes WHERE name LIKE '%{fnd}%'")
            res = c.fetchall()
            for row in res:
                print(f"{row[0]} : {row[1]}\n")
            conn.close()
    elif args.add:
        fnd = args.add
        if fnd:
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("select id, name from recipes where id=?", (fnd,))
            res = c.fetchall()
            print(res)
            if not res:
                print("recipe not found")
                conn.close()
                exit()
            if os.path.exists(RECIPES_FILE):
                with open(RECIPES_FILE, "rt") as fl:
                    ve = False
                    for lin in fl:
                        vals = lin.split(",")
                        if int(vals[0]) == fnd:
                            ve = True
                            break
                    if ve:
                        print("recipe already exists")
                        conn.close()
                        exit()
            with open(RECIPES_FILE, "at") as fw:
                fw.write(f"{fnd},{res[0][1]}\n")
                print(f"recipe added: {res[0][1]}\n")
            conn.close()

    elif args.remove:
        fnd = args.remove
        if fnd:
            tmp = RECIPES_FILE + ".bak"
            shutil.copy(RECIPES_FILE, tmp)
            with open(tmp, "rt") as fl:
                with open(RECIPES_FILE, "wt") as fw:
                    for lin in fl:
                        vals = lin.split(",")
                        if int(vals[0]) != fnd:
                            fw.write(lin)
            os.remove(tmp)
            print("recipe removed")

    elif args.save_as:
        fnd = args.save_as
        try:
            shutil.copyfile(RECIPES_FILE, fnd)
        except:
            print("error making a copy")

    elif args.save_ingredients:
        if not os.path.exists(RECIPES_FILE):
            print("no recipes found")
            exit()
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        try:
            mp = {}
            rp = {}
            with open(RECIPES_FILE, "rt") as fl:
                for lin in fl:
                    vals = lin.split(",")
                    c.execute("select ingredient_id,quantity,units from recipes_ingredients where recipe_id=?",
                              (int(vals[0]),))
                    rp[vals[0]] = vals[1]
                    res = c.fetchall()
                    for ing_row in res:
                        c.execute("select id, name from ingredients where id=?",
                                  (int(ing_row[0]),))
                        ing = c.fetchone()
                        if ing[0] in mp:
                            mp[ing[0]] = (ing[1],mp[ing[0]][1]+ing_row[1],ing_row[2])
                        else:
                            mp[ing[0]] = (ing[1],ing_row[1],ing_row[2])

            with open(INGREDIENTS_FILE, "wt") as fw:
                tdy = datetime.today()
                jsn = {"date": f"{tdy.year}-{tdy.month}-{tdy.day}",
                       "time": f"{tdy.hour}:{tdy.minute}:{tdy.second}",
                       "recipes": rp,
                       "ingredients": mp}
                json.dump(jsn, fw, indent=4)
        except:
            print("Failed to create ingredients file")
    elif args.about:
        print("\nSoftware By:\t Mandeep Singh Bhatia.")
        print("Company:\t SciEngineer Robotics Corp.")
        print("Copyright:\t August 2024.")
        print("Website:\t www.sci.engineer")
    else:
        print("invalid arguments, for help type: recipe-get -h")




