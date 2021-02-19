import azure.functions as func
import pandas as pd
import numpy as np
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
    def csvtojson(dff):
        mylist=[]
        for i in range(30):
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
    

    def CookMan(df,user_ingredients):
        entered=user_ingredients
        toadd=["salt","water","sugar"]
        for i in toadd:
            if str(i) not in set(user_ingredients.split(",")):                  
                user_ingredients+=",{}".format(str(i))
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

        def usedcheck(text):
            count=0
            for i in text.split(","):
                for j in entered.split(","):
                    if j in i:
                        count+=1
            return count
        df["flag"]=df["P-Ingredients"].apply(Cook2)  
        df=df.sort_values(by="flag",ascending=False).head(100)
        df["flag2"]=df["P-Ingredients"].apply(MainCook)
        df["flag1"]=df["P-Ingredients"].apply(usedcheck)
        df=df.sort_values(by=["flag1","flag2"],ascending=[False,False])

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
        common=['salt,''onion','sunflower oil','turmeric powder','red chilli powder','cloves garlic','ginger', 'coriander (dhania) leaves', 
        'tomato','green chillies','cumin seeds (jeera)','curry leaves','water','mustard seeds', 'sugar','lemon', 'ghee',
        'asafoetida (hing)','coriander powder','garam masala powder','coconut','black pepper powder','green chilli',
        'cumin powder (jeera)','dry red chillies','milk','butter','curd','carrot'"oil","rice","wheat","wheat flour","rice flour"]
        def priorityrank(text):
            count=0
            for i in text.split(","):
                if i not in common:
                    count-=1
            return count  
        df["flag3"]=df["Missing"].apply(priorityrank)
        df=df.sort_values(["flag1","flag2","flag3"], ascending=[False,False,False])
        Cookdf=df.head(30)
        return Cookdf
    dff=CookMan(df,user_ingredients)
    dff.reset_index(inplace=True,drop=True)
    if dff.loc[0,"flag2"] <-5:
        toadd=["milk","wheat","rice"]
        for i in toadd:
            if i not in set(user_ingredients.split(",")):
                user_ingredients+=",{}".format(str(i))
        dff=CookMan(df,user_ingredients)
        dff.reset_index(inplace=True,drop=True)
        jsondf=csvtojson(dff)
        return jsondf
    else:
        jsondf=csvtojson(dff)
        return jsondf
    
def main(req: func.HttpRequest):
    
    trial = req.params.get('trial')
    if trial == "yes":
        return func.HttpResponse("function runs")
    # else:
    #     return func.HttpResponse("function still runs bitch")
    df=pd.read_csv(os.path.join("df-en-final.csv"))
    req_body = req.get_json()
    user_ingredients=req_body.get('foodItems')
    result=MasterCook(df,user_ingredients)
    parsed = json.loads(result)
    return func.HttpResponse(json.dumps(parsed, indent=2))