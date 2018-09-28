# -*- coding: utf-8 -*-
from app.imports import parse_espion_export
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import logging

logger = logging.getLogger(__name__)

def get_steps(fname):
 
    steps = [{'name': 'DA 0.01', 'desc': 'Dark-adapted 0.01 ERG', 'chan':2, 'ylims': (-100,250)},
             {'name': 'DA 3.0', 'desc': 'Dark-adapted 3.0 ERG + OPs', 'chan': 2, 'ylims': (-300,150), 'xlims': (-20,75), 'truncate': 75},
             {'name': 'DA OPs', 'desc': 'Dark-adapted 3.0 ERG + OPs', 'chan': 4, 'ylims': (-50,50), 'xlims': (-20,100)},
             {'name': 'LA 3.0', 'desc': 'Light-adapted 3.0 ERG', 'chan': 2, 'ylims': (-50,100), 'xlims': (-20,100)},
             {'name': '30Hz Flicker', 'desc': 'Light-adapted 3.0 flicker ERG', 'chan': 2, 'ylims': (-100,100), 'xlims': (-20,100)},
             {'name': 'On Response', 'desc': 'Rapid - On', 'chan': 2, 'ylims': (-100,100), 'xlims': (-20,200)},
             {'name': 'Off Response', 'desc': 'Rapid - Off', 'chan': 2, 'ylims': (-100,100), 'xlims': (-20,200)}]
    
#    steps = [{'name': 'LA 3.0', 'desc': 'Light-adapted 3.0 ERG', 'chan': 1, 'ylims': (-200,150), 'xlims': (-20,100)},
#             {'name': 'DA 3.0', 'desc': 'Dark-adapted 3.0 ERG + OPs', 'chan': 1, 'ylims': (-200,150), 'xlims': (-20,100)}]
        
    data = parse_espion_export.load_file(fname)

    data = data[1]
    
    for step in steps:
        for idx, info in data['stimuli'].items():
            if step['desc'] == info['description']:
                step['step_idx'] = idx
    return(steps, data)
    
def plot_step(ax, step, data, params):
    """
    Currently assummes samples start at -20ms and are made every ms
    """
    linetypes = ['solid', 'dashed', 'dashdot']
    colors = ['blue', 'green', 'red']
    
    try:
        data = data['data'][step['step_idx']].channels[step['chan']]
        ax.set_title(step['name'])
        if 'ylims' in step:
            ax.set_ylim(step['ylims'])
        if 'xlims' in step:
            ax.set_xlim(step['xlims'])
    except Exception as e:
        #logger.error('Data not found for channel:{} for step:{} at index:{}'
        #             .format(step['chan'], step['desc'], step['step_idx']))
        return ax #return a blank axis
    
    
    
    truncate = step.get('truncate')
    result_idx = max(data.results.keys())
    result_count = 0
    for result_idx in data.results.keys():
        #yvals = [v/1000 for v in data.results[result_idx].data.values]
        yvals = np.array(data.results[result_idx].data.values) / 1000
        xvals = np.linspace(-20, len(yvals) - 21, len(yvals))
        
        if truncate:
            # import pdb; pdb.set_trace()
            xvals_signal = xvals[xvals <= truncate]
            yvals_signal = yvals[xvals <= truncate]
            xvals_truncate = xvals[xvals > truncate]
            yvals_truncate = np.repeat(yvals_signal[-1], len(xvals_truncate))
            p = ax.plot(xvals_signal, yvals_signal, linestyle=linetypes[result_count], color=colors[result_count], **params)
            p = ax.plot(xvals_truncate, yvals_truncate, linewidth=1, linestyle='dotted', color=colors[result_count], **params)
        else:
            p = ax.plot(xvals, yvals, linestyle=linetypes[result_count], color=colors[result_count], **params)
        result_count = result_count + 1
    return(p)
    
def plot_steps(steps, data):
    steps=steps[0:5]
    nsteps = len(steps)

    sns.set_style('dark')
    
    #sns.despine()
    sns.set_context('talk')
    
    fig = plt.figure()
    axs=[]

    fig, ax = plt.subplots(2, nsteps)
    fig.set_size_inches(10,2)
    for idx in range(nsteps):
        ax = plt.subplot2grid((4, nsteps), (0, idx), rowspan=3)
        plot_step(ax, steps[idx], data, {})
        axs.append(ax)
    ax = plt.subplot2grid((4, nsteps), (3, 0), colspan=nsteps)
    ax.text(0.5,0.5,'Time (ms)',
            verticalalignment='center',
            horizontalalignment='center')    
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.axis('off')
    axs[0].set_ylabel(r'Amplitude ($\mu$V)' )
    plt.tight_layout(pad=0.2,w_pad=0)
    fig.savefig('test L.png')

def plot_steps2(steps, data):
    nsteps = len(steps)
    sns.set_style('dark')
    
    #sns.despine()
    sns.set_context('talk')

    for idx in range(nsteps):
        try:
            fig = plt.figure()
            fig.set_size_inches(4,4)
            ax = fig.add_axes([0.25,0.2,0.7,0.7])
            plot_step(ax, steps[idx], data, {})
            ax.set_ylabel(r'Amplitude ($\mu$V)')
            ax.set_xlabel('Time (ms)')
            ax.get_xaxis().set_visible(True)
            ax.get_yaxis().set_visible(True)
            
            #plt.tight_layout()
            fig.savefig('{} L.png'.format(steps[idx]['name']))
        except:
            pass

if __name__ == '__main__':
    fname = 'c:/Users/twright/Documents/Exports/control_erg'
    fname = 'D:\Lecture\Images\Fundus Albipunctatus\erg export'
    fname = 'D:\Lecture\Images\Best\erg export'
    #fname = 'C:/Users/twright/Documents/Lectures/Electrophys 101/Images/Oguchi/erg_export_orig'
    #fname = 'C:/Users/twright/Documents/Lectures/Electrophys 101/Images/Control/erg_export'
    #fname = 'C:/Users/twright/Documents/Lectures/Electrophys 101/Images/iCSNB/Case 3/erg_export'
    #fname = 'C:/Users/twright/Documents/Lectures/Electrophys 101/Images/cCSNB2/erg_export'
    fname = 'C:/Users/twright/Documents/Lectures/Electrophys 101/Images/stagardt2/erg_export'
    #fname = fname.replace('\\','/')
    #fname = 'c:/Users/twright/Documents/Exports/RetinitisPigmentosa_erg'
    steps, data = get_steps(fname)

    plot_steps(steps, data)
    plot_steps2(steps, data)