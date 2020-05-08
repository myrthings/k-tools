import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

def custom_representative(tipo,date): #date not datetime
    if tipo=='7D':
        iso=dt.date.isocalendar(date)
        return dt.datetime.strptime('{:04d} {:02d} 1'.format(iso[0],iso[1]), '%G %V %u').date()
    elif tipo=='28D':
        iso=dt.date.isocalendar(date)
        return dt.datetime.strptime('{:04d} {:02d} 1'.format(iso[0],iso[1]//4*4 if iso[1]//4!=0 else 1), '%G %V %u').date()
    elif tipo=='M':
        return dt.date(date.year,date.month,1)
    elif tipo=='D':
        return date
    elif tipo=='Q':
        return dt.date(date.year,date.month//3*3 if date.month//3!=0 else 1,1)

def nums(data):
    data['months']=np.arange(len(data))
    #data['months']=data['months'].apply(lambda x: '+{:02}'.format(x))
    return data

def perc(data,name,column):
    data[name]=data[column]/data[column].iloc[0]
    return data

def churn(data,name,column):
    data[name]=data[column].iloc[0]-data[column]
    return data

def cohorts_prep(data):
    pre_cohorts=deepcopy(data)
    pre_cohorts.set_index('Client',inplace=True)
    pre_cohorts['cohort']=pre_cohorts.groupby(level=0)['period'].min()
    pre_cohorts.reset_index(inplace=True)
    pre_cohorts['cohort']=pre_cohorts['cohort'].apply(lambda x: x.strftime('%Y-%m'))
    pre_cohorts['period']=pre_cohorts['period'].apply(lambda x: x.strftime('%Y-%m'))
    return pre_cohorts

def cohort_table(data,plot_col,plot_func,new_plot_col=False):
    cohorts=data.groupby(['cohort','period']).agg({plot_col:plot_func})
    cohorts=cohorts.unstack().fillna(0).stack().reset_index()
    cohorts=cohorts[cohorts['cohort']<=cohorts['period']].set_index(['cohort','period'])
    if new_plot_col:
        cohorts=cohorts.rename(columns={plot_col:new_plot_col})
        plot_col=new_plot_col
    
    cohorts=cohorts.groupby('cohort').apply(perc,name='perc_{}'.format(plot_col),column=plot_col)
    cohorts=cohorts.reset_index().groupby('cohort').apply(nums)#.set_index(['cohort','period'])
    return cohorts


def plot_perc_cohort(data,column_raw,column_perc,title_raw,title_perc,unit=None):
    
    max_coh=round(len(data['cohort'].unique())*0.75)
    max_per=round(len(data['period'].unique())*1.5)

    fig,(ax1,ax2)=plt.subplots(1,2,gridspec_kw={'width_ratios': [1, round(max_per/3) if max_per>2 else 3]},figsize=(max_per,max_coh))

    new=data.groupby('cohort')[[column_raw]].apply(lambda x: -x.iloc[-1]).rename(columns={'mrr':'end'})
    new['start']=data.groupby('cohort')[[column_raw]].apply(lambda x: -x.iloc[0])
    new.sort_index(ascending=False).plot(kind='barh',width=0.9,color=['tab:olive','tab:green'],alpha=0.5,ax=ax1)


    ax=sns.heatmap(data.set_index(['cohort','months'])[column_perc].unstack(),
                   cmap='coolwarm_r',center=1,vmin=0, vmax=2,
                   annot=True,fmt='1.0%',
                   ax=ax2)#,cbar=False)
    bottom, top = ax.get_ylim()
    ax.set_ylim(bottom + 0.75, top - 0.75)
    labels=ax2.get_yticklabels()
    ax2.set_yticklabels(labels,fontsize=14,rotation=0)
    ax2.set_ylabel('')
    ax2.set_xticklabels(['0','+1 month','+2 months']+['+{}'.format(x) for x in range(3,data['months'].max()+1)],fontsize=14)
    ax2.set_xlabel('')

    ax1.set_xlim(xmax=0)
    ax1.set_yticklabels('')
    ax1.set_ylabel('')
    
    ticks=ax1.get_xticks()
    ax1.set_xticks(ticks)
        
    labels=list(map(lambda x: float(x[1:]) if x[0]=='−' else float(x),map(lambda x: x.get_text(),ax1.get_xticklabels())))
    if unit:
        ax1.set_xticklabels([str(round(x/1000,2))+unit if x!=0 else '0' for x in labels],fontsize=14)
    else:
        ax1.set_xticklabels(labels,fontsize=14)
    #ax1.set_xlabel('MRR',fontsize=14)


    ax1.set_title(title_raw,fontsize=20)
    ax2.set_title(title_perc,fontsize=20)

    #fig.suptitle('Cohort analysis',fontsize=20)
    fig.tight_layout()
    #fig.subplots_adjust(top=0.95)
    plt.show()