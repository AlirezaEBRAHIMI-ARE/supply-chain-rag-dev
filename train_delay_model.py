import pandas as pd
df = pd.read_csv("online_retail_II.csv")
print(df.shape)
#print(df.head())
print(df.columns)
#print(df.isnull())

#print(df.isnull().sum())
df = df.dropna(subset=['Customer ID'])

df = df[df['Quantity']>0]
df['InvoiceDate']=pd.to_datetime(df['InvoiceDate'])
print (df.shape)
#so we dropped 262k rows from 1.07M tp 805k
print(df.duplicated().sum())
#got 26125
df=df.drop_duplicates()
print(df.duplicated().sum())

df["is_free_or_error"]=df["Price"]<=0


print("Empty cells in description",df["Description"].isna().sum())
#print("Duplicated in Description column",df["Description"].duplicated().sum())
#print("Duplicated in whole file:",df.duplicated().sum())
print(df[df["Price"]<=0].shape[0])
print(df["Description"].describe())
print(df["StockCode"].value_counts().head(20))

excluded = ["POST","D","M","BANK CHARGES","DOT"]
df =df[~df["StockCode"].isin(excluded)]
print ("NEW Shape",df.shape)
print(df["StockCode"].value_counts().head(30))

df["is_free_or_error"]=df["Price"]<=0

print('value of is free ot error',df["is_free_or_error"].value_counts())

df=df[df["is_free_or_error"]== False]
print ((df["is_free_or_error"]==True).sum())


def get_distance(Country):
    if Country=="United Kingdom":
        return "Domestic"
    elif Country in ["Germany", "France", "Netherlands", "Spain", "Belgium"]:
        return "Near"
    else:
        return "Long"

df["ShipDistance"]=df["Country"].apply(get_distance)

df['order_value']=df['Quantity']*df['Price']
def order_size(value):
    if value < 20:
        return "Small"
    elif value < 100:
        return "Medium"
    else:
        return "Large"
df["OrderSize"]=df["order_value"].apply(order_size)

print(df["ShipDistance"].value_counts())
df['OrderValue']=df['Quantity']*df['Price']
print("OrderValuse describe:\n",df["OrderValue"].describe())

def get_order_size(v):
    if v <5:
        return "small"
    elif v<20:
        return "medium"
    else:
        return "large"

df["Ordersize2"]=df["order_value"].apply(get_order_size)
print(df["Ordersize2"].value_counts())

df["Month"] = df["InvoiceDate"].dt.month
print (df["Month"].value_counts().sort_index())

def delivery_risk(m):
    if m >= 9:
        return "High Season"
    elif m>=1 and m<=8:
        return "Normal Season"
    else:
        print("Wrong month")
        return "Unknown"

df["Season"] =  df["Month"].apply(delivery_risk)
print (df["Season"].value_counts())

geo_points = {'Domestic':1,"Near":2,"Long":3}
size_points = {"small":1,"medium":2,"large":3}
season_points={"Normal Season":0,"High Season":1}

df ["DelayRisk"]= df.apply(lambda x :geo_points.get(x["ShipDistance"],0)
                                    +size_points.get(x["Ordersize2"],0)
                                    +season_points.get(x["Season"],0),
    axis=1)
print(df["DelayRisk"].value_counts().sort_index())

#print("DelayRisk unique is:\n",df["DelayRisk"].unique())
#print("ShipDistance unique is \n", df["ShipDistance"].unique())
# print("Ordersize2 unique is :\n",df["Ordersize2"].unique())
# print("Season unique is :\n",df["Season"].unique())

def bucket_risk (score):
    if score<=3:
        return "Low"
    elif score<5:
        return "Medium"
    else:
        return "High"
df["DelayRiskLabel"] = df["DelayRisk"].apply(bucket_risk)
print(df["DelayRiskLabel"].value_counts())

# X=df [["Quantity","Price","Country","Month"]]
# Y =df ["DelayRiskLabel"]
#
# X=pd.get_dummies(X,columns=["Country"])
#
# print(X.shape)
# print(X.columns)
#
# from sklearn.model_selection import train_test_split
# X_train,X_test,Y_train,Y_test= train_test_split(X,Y,test_size=0.2,random_state=42)
#
# print(X_train.shape)
# print(X_test.shape)
#
# from sklearn.ensemble import RandomForestClassifier
# model = RandomForestClassifier(random_state=42)
# model.fit(X_train,Y_train)
#
# predictions = model.predict(X_test)
#
# from sklearn.metrics import accuracy_score,classification_report
#
# print("Accuracy",accuracy_score(Y_test,predictions))
# print("Classification",classification_report(Y_test,predictions))
#
# print(X_test. head())

X=df [["Quantity","Price"]]

Y=df ["DelayRiskLabel"]

from sklearn.model_selection import train_test_split
X_train,X_test,Y_train,Y_test= train_test_split(X,Y,test_size=0.2,random_state=42)


from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(random_state=42)
model.fit(X_train,Y_train)

predictions = model.predict(X_test)

from sklearn.metrics import accuracy_score,classification_report

print("Accuracy\n",accuracy_score(Y_test,predictions))
print("Classification\n",classification_report(Y_test,predictions))

import joblib
joblib.dump(model,'delay_risk_model.pkl')

import mlflow
runs = mlflow.search_runs()
print (runs)
with mlflow.start_run():
    model = RandomForestClassifier(random_state=42,n_estimators=50)
    model.fit(X_train,Y_train)

    predictions = model.predict(X_test)
    acc= accuracy_score(Y_test,predictions)

    mlflow.log_param("model_type","RandomForest")
    mlflow.log_param("features","Quantity,Price")
    mlflow.log_param("n_estimators", 50)
    mlflow.log_metric("accuracy",acc)
    mlflow.sklearn.log_model(model,"model")

    print("Run 3 accuracy:", acc)

from  langchain_community.document_loaders import  TextLoader

files =["shipping_policy.txt", "returns_policy.txt", "customs_faq.txt", "order_tracking_faq.txt"]


all_rules=[]
for x in files:
        loader= TextLoader(x)
        docs=loader.load()
        all_rules.extend(docs)
print(len(all_rules))
print(all_rules)

from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
chunks = splitter.split_documents(all_rules)

print(len(chunks))
print(chunks[0])