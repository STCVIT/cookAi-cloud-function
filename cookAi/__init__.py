import azure.functions as func
import pandas as pd
import fuzzywuzzy.fuzz as fuzz
import os
import json



def MasterCook(df,user_ingredients):
    
    class Recipe: 
   
 
        def __init__(self, title,ing,time,missing,imgurl,cuisine,instructions): 
            self.title = title 
            self.ingredients=ing
            self.time=time
            self.missing=missing
            self.imgurl=imgurl 
            self.cuisine=cuisine
            self.instructions=instructions            
        def dump(self):
            return {'title': self.title,
                               'ingredients': self.ingredients,                               
                               'missing': self.missing,
                               'time': self.time,
                               'imgurl':self.imgurl,
                               'cuisine':self.cuisine,
                               'instructions':self.instructions }
    

    def CookMan(df,user_ingredients):
        #if "salt" not in set(user_ingredients.split(",")):                  
          #  user_ingredients+=",salt"
        def Cook2(Pingredients):    
            "Comparing the Recipe Ingredients and User Ingredients and decreasing count value for each Recipe ingredient missing.\
            Count describes the no. of ingredients missing from user ingredients to make that recipe."
            flag,count=0,0

            for i in set(Pingredients.split(",")):
                for j in  user_ingredients.split(","):
                    if i in j :              
                        flag=1

                        break
                if (flag==0):
                    count-=1
                else:
                    flag=0
                if count<-10:
                    return count

            return count

        def MainCook(Pingredients):    
            flag,count=0,0
            #ullcount=0
            for i in set(Pingredients.split(",")):
                for j in  user_ingredients.split(","):
                    if fuzz.token_set_ratio(i,j)>80:                 
                        flag=1 
                        break
                if (flag==0):
                    count-=1
                else:
                    flag=0

            return count        


        df["flag"]=df["P-Ingredients"].apply(Cook2)  
        df=df.sort_values(by="flag",ascending=False).head(100)
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
        #df.drop(columns=["flag2","flag","P-Ingredients","URL"],inplace=True)
        df.reset_index(inplace=True,drop=True)
        Cookdf=df.head(30)
        return Cookdf
    dff=CookMan(df,user_ingredients)
    if dff.loc[0,"flag2"] <-4:
        toadd=["salt","sugar","water","milk","wheat","rice"]
        for i in toadd:
            if i not in set(user_ingredients.split(",")):
                user_ingredients+=",{}".format(str(i))
        dff=CookMan(df,user_ingredients)
        
    mylist=[]
    for i in range(5):
        title = dff.loc[i,"TranslatedRecipeName"]
        ing=dff.loc[i,"TranslatedIngredients"]
        time=int(dff.loc[i,"TotalTimeInMins"])
        missing=dff.loc[i,"Missing"]
        imgurl = dff.loc[i,"image-url"]
        cuisine=dff.loc[i,"Cuisine"]
        instructions=dff.loc[i,"TranslatedInstructions"]
        mylist.append(Recipe(title,ing,time,missing,imgurl,cuisine,instructions))        
    dfjson=json.dumps([o.dump() for o in mylist])
    return dfjson

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
    result=MasterCook(df,user_ingredients)
    parsed = json.loads(result)
    return func.HttpResponse(json.dumps(parsed, indent=2))
 