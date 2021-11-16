from flask import Flask,request,redirect
from flask import render_template,url_for
import pandas as pd
import numpy as np
import json

def result(idcw_growth,risk,sip,time):
    url1 = 'https://raw.githubusercontent.com/aryantanwar-it/DummyData/master/High_Risk.csv'
    url2 = 'https://raw.githubusercontent.com/aryantanwar-it/DummyData/master/Very_High_Risk.csv'
    url3 = 'https://raw.githubusercontent.com/aryantanwar-it/DummyData/master/moderate_low_risk.csv'
    high_risk = pd.read_csv(url1,sep=',',index_col='Scheme Name')
    very_high_risk = pd.read_csv(url2,sep=',',index_col='Scheme Name')
    low_mod_risk = pd.read_csv(url3,sep=',',index_col='Scheme Name')
    high_risk.drop('Unnamed: 0',axis=1,inplace=True)
    very_high_risk.drop('Unnamed: 0',axis=1,inplace=True)
    low_mod_risk.drop('Unnamed: 0',axis=1,inplace=True)
    bgh = ((high_risk.iloc[0:,len(high_risk.T)-1] - high_risk.iloc[0:,1])/high_risk.iloc[0:,1])*100
    bgh1 = ((very_high_risk.iloc[0:,len(very_high_risk.T)-1] - very_high_risk.iloc[0:,1])/very_high_risk.iloc[0:,1])*100
    bgh2 = ((low_mod_risk.iloc[0:,len(low_mod_risk.T)-1] - low_mod_risk.iloc[0:,1])/low_mod_risk.iloc[0:,1])*100
    bgh = ((1+(bgh/100))**(365/210))-1
    bgh1 = ((1+(bgh1/100))**(365/210))-1
    bgh2 = ((1+(bgh2/100))**(365/210))-1
    new_df = high_risk.drop('Scheme Id',axis=1,inplace=False).T
    n_df = very_high_risk.drop('Scheme Id',axis=1,inplace=False).T
    nw_df = low_mod_risk.drop('Scheme Id',axis=1,inplace=False).T
    pc = new_df.pct_change()
    pc1 = n_df.pct_change()
    pc2 = nw_df.pct_change()
    xc = pd.concat([pc.mean()*10000,pc.std()*10000,bgh*100],axis=1)
    xc.columns=['Expected Returns','Risk','1 yr Return']
    xc_growth = pd.DataFrame([xc.iloc[i,:] for i in range(0,len(pc.std())) if xc.index[i].find('Growth')!=-1 or xc.index[i].find('GROWTH')!=-1]) 
    xc_idcw = pd.DataFrame([xc.iloc[i,:] for i in range(1,len(pc.std())) if xc.index[i].find('Growth')==-1 and xc.index[i].find('GROWTH')==-1])
    xc1 = pd.concat([pc1.mean()*10000,pc1.std()*10000,bgh1*100],axis=1)
    xc1.columns=['Expected Returns','Risk','1 yr Return']
    xc1_growth = pd.DataFrame([xc1.iloc[i,:] for i in range(0,len(pc1.std())) if xc1.index[i].find('Growth')!=-1 or xc1.index[i].find('GROWTH')!=-1]) 
    xc1_idcw = pd.DataFrame([xc1.iloc[i,:] for i in range(1,len(pc1.std())) if xc1.index[i].find('Growth')==-1 and xc1.index[i].find('GROWTH')==-1])
    xc2 = pd.concat([pc2.mean()*10000,pc2.std()*10000,bgh2*100],axis=1)
    xc2.columns=['Expected Returns','Risk','1 yr Return']
    xc2_growth = pd.DataFrame([xc2.iloc[i,:] for i in range(0,len(pc2.std())) if xc2.index[i].find('Growth')!=-1 or xc2.index[i].find('GROWTH')!=-1]) 
    xc2_idcw = pd.DataFrame([xc2.iloc[i,:] for i in range(1,len(pc2.std())) if xc2.index[i].find('Growth')==-1 and xc2.index[i].find('GROWTH')==-1])
    xc_growth=pd.DataFrame([xc_growth.iloc[13,:],xc_growth.iloc[10,:],xc_growth.iloc[6,:],xc_growth.iloc[7,:]])
    xc1_growth=pd.DataFrame([xc1_growth.iloc[9,:],xc1_growth.iloc[7,:]])
    xc2_growth=pd.DataFrame([xc2_growth.iloc[6,:],xc2_growth.iloc[8,:],xc2_growth.iloc[3,:],xc2_growth.iloc[4,:],xc2_growth.iloc[2,:]])
    xc_idcw=pd.DataFrame([xc_idcw.iloc[13,:],xc_idcw.iloc[10,:],xc_idcw.iloc[11,:],xc_idcw.iloc[7,:],xc_idcw.iloc[9,:]])
    xc1_idcw=pd.DataFrame([xc1_idcw.iloc[9,:],xc1_idcw.iloc[7,:]])
    xc2_idcw=pd.DataFrame([xc2_idcw.iloc[5,:],xc2_idcw.iloc[10,:],xc2_idcw.iloc[3,:],xc2_idcw.iloc[2,:]])
    def retur(sip,ret,time):
        ret=ret/100
        ret=ret/12
        return sip*((ret+1)**(time)-1)*((ret+1)/ret)
    def name(xc_c,xc1_c,xc2_c,i,j,k,inv,ris,time):
        s = [0,0,0,0]
        x=0.01
        while x < 0.99:
            y = (ris/(xc_c.iloc[i,1]-xc2_c.iloc[k,1])) - ((x*(xc1_c.iloc[j,1]-xc2_c.iloc[k,1]))/(xc_c.iloc[i,1]-xc2_c.iloc[k,1])) - (xc2_c.iloc[k,1]/(xc_c.iloc[i,1]-xc2_c.iloc[k,1]))
            if y>0.05 and (1-x-y)>0.1 and x>0.05:
                tot = retur(x*inv,xc1_c.iloc[j,0],time)+retur(y*inv,xc_c.iloc[i,0],time)+retur((1-x-y)*inv,xc2_c.iloc[k,0],time)
                if tot>s[0]:
                    s=[tot,x*100,y*100,(1-x-y)*100]
            x+=0.01
        return s
    def portfolio(xc_c,xc1_c,xc2_c,risk_app,inve,time):
        i=0
        x=[0,0,0,0]
        while i<len(xc_c):
            j=0
            while j<len(xc1_c):
                k=0
                while k<len(xc2_c):
                    p=name(xc_c,xc1_c,xc2_c,i,j,k,inve,risk_app,time)
                    if p[0]>x[0]:
                        x=p
                        x.append(xc_c.index[i])
                        x.append(xc1_c.index[j])
                        x.append(xc2_c.index[k])
                    k+=1
                j+=1
            i+=1
        return x
    #idcw_growth=input('IDCW or Growth')
    #risk=int(input('Risk Appetite'))
    #sip=int(input('sip'))
    #time=int(input('time'))
    time=time*12
    if(idcw_growth=='idcw'):
        p = portfolio(xc_idcw,xc1_idcw,xc2_idcw,risk,sip,time)
        #print('Total Returns ',p[0])
        #print('Total Investment ',sip*time)
        #print('Large Cap - ',p[4],' ',p[1])
        #print('Small Cap - ',p[5],' ',p[2])
        #print('Debt Fund - ',p[6],' ',p[3])
        dit = {'smallcap':{'name':p[5],'percent':p[2]},'largecap':{'name':p[4],'percent':p[1]},'debt':{'name':p[6],'percent':p[3]},'amountinvested':sip*time,'return':p[0]}
        return dit
    else:
        p = portfolio(xc_growth,xc1_growth,xc2_growth,risk,sip,time)
        #print('Total Returns ',p[0])
        #print('Total Investment ',sip*time)
        #print('Large Cap - ',p[4],' ',p[1])
        #print('Small Cap - ',p[5],' ',p[2])
        #print('Debt Fund - ',p[6],' ',p[3])
        dit = {'smallcap':{'name':p[5],'percent':p[2]},'largecap':{'name':p[4],'percent':p[1]},'debt':{'name':p[6],'percent':p[3]},'amountinvested':sip*time,'return':p[0]}
        return dit

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#db = SQLAlchemy(app)

'''class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ch = db.Column(db.String(200),nullable=False)
    ti = db.Column(db.Integer, nullable=False)
    per = db.Column(db.Integer,nullable=False)
    amo = db.Column(db.Integer,nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

def __init__(self,ch,ti,per,amo):
    ch = self.ch
    ti = self.ti
    per =self.per
    amo = self.amo'''

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/",methods=['GET','POST'])
def give():
    if request.method == 'POST':
        choice = request.form['ch']
        time = request.form['ti']
        risk = request.form['ri']
        amount = request.form['amo']
        hj = result(choice,int(risk),int(amount),int(time))
        kp = json.dumps(hj)
        return redirect(url_for('success',dic = kp))

@app.route("/success/<dic>")
def success(dic):
    return render_template("success.html",dic=json.loads(dic))

if __name__ == "__main__":
    app.run(debug=True)
