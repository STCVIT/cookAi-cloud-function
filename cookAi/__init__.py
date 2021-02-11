import azure.functions as func
import pandas as pd
import numpy as np
import fuzzywuzzy.fuzz as fuzz
import json
import os


def CookMan(df,user_ingredients):
    def Cook2(Pingredients):    
        "Comparing the Recipe Ingredients and User Ingredients and decreasing count value for each Recipe ingredient missing.\
        Count describes the no. of ingredients missing from user ingredients to make that recipe."
        flag,count=0,0
        ulcount=0
        for i in set(Pingredients.split(",")):
            for j in  user_ingredients.split(","):
                if i==j:               
                    flag=1 
                    ulcount=1
                    break
            if (flag==0):
                count-=1
            else:
                flag=0
            if count<-10:
                return count
        if(ulcount==0):
            return count-1
        else:
            return count

    def MainCook(Pingredients):    
        flag,count=0,0
        ullcount=0
        for i in set(Pingredients.split(",")):
            for j in  user_ingredients.split(","):
                if fuzz.token_set_ratio(i,j)>80:                 
                    flag=1 
                    break
            if (flag==0):
                count-=1
            else:
                flag=0
        if(ullcount==0):
            return count-1
        else:
            return count
    df["flag"]=df["P-Ingredients"].apply(Cook2)  
    df=df.sort_values(by="flag",ascending=False).head(30)
    df["flag2"]=df["P-Ingredients"].apply(MainCook)
    df=df.sort_values(by="flag2",ascending=False)

    def Missing(Pingredients):
        flag=0
        miss=""
        for i in set(Pingredients.split(",")):
            for j in  user_ingredients.split(","):
                if fuzz.token_set_ratio(i,j)>80:                    
                    flag=1 
                    break
            if (flag==0):
                miss+=i+","
                
            else:
                flag=0
        miss = miss[:-1]
        return miss
    df["Missing"]=df["P-Ingredients"].apply(Missing)
    df.drop(columns=["flag2","flag","P-Ingredients"],inplace=True)
    return df

def main(req: func.HttpRequest):
    
    trial = req.params.get('trial')
    if trial == "yes":
        return func.HttpResponse("function runs")
    # else:
    #     return func.HttpResponse("function still runs bitch")
    df=pd.read_csv(os.path.join("df-en-final.csv"))
    df["Ingredient-count"]=df["P-Ingredients"].apply(lambda x:len(x.split(",")))
    df=df[df["Ingredient-count"]>4]
    df.reset_index(drop=True, inplace=True)
    req_body = req.get_json()
    user_ingredients=req_body.get('foodItems')
    Cookdf=CookMan(df,user_ingredients)
    result = Cookdf.to_json(orient="split")
    parsed = json.loads(result)
    return func.HttpResponse(json.dumps(parsed, indent=2))
