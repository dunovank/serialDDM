#!/usr/bin/env python
# encoding: utf-8

"""
Code to fit the history-dependent drift diffusion models described in
Urai AE, Gee JW de, Donner TH (2018) Choice history biases subsequent evidence accumulation. bioRxiv:251595

MIT License
Copyright (c) Anne Urai, 2018
anne.urai@gmail.com
"""
import numpy as np
import os, fnmatch
import hddm
from IPython import embed as shell

# prepare link function for the regression models
def z_link_func(x):
    return 1 / (1 + np.exp(-(x.values.ravel())))

def balance_designmatrix(mydata):
    # remove subjects who did not do all conditions
    for i, sj in enumerate(mydata.subj_idx.unique()):
        sessions = mydata[mydata.subj_idx == sj].session.unique()
        if len(sessions) < len(mydata.session.unique()):
            mydata = mydata[mydata.subj_idx != sj] # drop this subject
    return mydata

def recode_4stimcoding(mydata):
    # split into coherence and stimulus identity
    mydata['coherence'] = mydata.stimulus.abs()
    mydata.stimulus     = np.sign(mydata.stimulus)
    # for stimcoding, the two identities should be 0 and 1
    mydata.ix[mydata['stimulus']==-1,'stimulus'] = 0
    if len(mydata.stimulus.unique()) != 2:
        raise ValueError('Stimcoding needs 2 stimulus types')

    # also create a binary prevcorrect
    mydata['prevcorrect']     = mydata.prevresp
    mydata.prevcorrect[mydata.prevresp != mydata.prevstim] = 0
    mydata.prevcorrect[mydata.prevresp == mydata.prevstim] = 1

    try:
        # also create a binary prevcorrect
        mydata['prev2correct']     = mydata.prevresp
        mydata.prev2correct[mydata.prev2resp != mydata.prev2stim] = 0
        mydata.prev2correct[mydata.prev2resp == mydata.prev2stim] = 1
        # also create a binary prevcorrect
        mydata['prev3correct']     = mydata.prevresp
        mydata.prev3correct[mydata.prev3resp != mydata.prev3stim] = 0
        mydata.prev3correct[mydata.prev3resp == mydata.prev3stim] = 1
    except:
        pass

    return mydata

# ============================================ #
# define the function that will do the work
# ============================================ #

def make_model(mypath, mydata, model_name, trace_id):

    model_filename  = os.path.join(mypath, model_name, 'modelfit-md%d.model'%trace_id)
    print model_filename

    # ============================================ #
    # NO HISTORY FOR MODEL COMPARISON
    # ============================================ #

    if model_name == 'stimcoding_nohist':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        # for Anke's data, also split by transition probability
        if len(mydata.coherence.unique()) > 1:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence']})
        else:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'])

    if model_name == 'stimcoding_nohist_onlyz':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        # for Anke's data, also split by transition probability
        if len(mydata.coherence.unique()) > 1:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence']})
        else:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'])

    elif model_name == 'stimcoding_nohist_onlydc':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        # for Anke's data, also split by transition probability
        if len(mydata.coherence.unique()) > 1:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence']})
        else:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'])

    # ============================================ #
    # STIMCODING PREVRESP
    # ============================================ #

    elif model_name == 'stimcoding_dc_prevresp':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        # also split by transition probability and include coherence-dependence of drift rate
        if 'transitionprob' in mydata.columns:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence'], 'dc':['prevresp', 'transitionprob']})
        elif len(mydata.coherence.unique()) > 1:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence'], 'dc':['prevresp']})
        else:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'dc':['prevresp']})

    elif model_name == 'stimcoding_z_prevresp':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        # for Anke's data, also split by transition probability
        if 'transitionprob' in mydata.columns:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence'], 'z':['prevresp', 'transitionprob']})
        elif len(mydata.coherence.unique()) > 1:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence'], 'z':['prevresp']})
        else:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'z':['prevresp']})

    elif model_name == 'stimcoding_dc_z_prevresp':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        # for Anke's data, also split by transition probability
        if 'transitionprob' in mydata.columns:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence'], 'dc':['prevresp', 'transitionprob'],
                'z':['prevresp', 'transitionprob']})
        elif len(mydata.coherence.unique()) > 1:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence'], 'dc':['prevresp'], 'z':['prevresp']})
        else:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'dc':['prevresp'], 'z':['prevresp']})

    # ============================================ #
    # also estimate across-trial variability in starting point
    # ============================================ #

    if model_name == 'stimcoding_sz_nohist':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        # for Anke's data, also split by transition probability
        if len(mydata.coherence.unique()) > 1:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv', 'sz'), group_only_nodes=['sv', 'sz'],
                depends_on={'v': ['coherence']})
        else:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv', 'sz'), group_only_nodes=['sv', 'sz'])

    elif model_name == 'stimcoding_sz_dc_prevresp':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        # for Anke's data, also split by transition probability and include coherence-dependence of drift rate
        if 'transitionprob' in mydata.columns:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv', 'sz'), group_only_nodes=['sv', 'sz'],
                depends_on={'v': ['coherence'], 'dc':['prevresp', 'transitionprob']})
        elif len(mydata.coherence.unique()) > 1:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv', 'sz'), group_only_nodes=['sv', 'sz'],
                depends_on={'v': ['coherence'], 'dc':['prevresp']})
        else:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv', 'sz'), group_only_nodes=['sv', 'sz'],
                depends_on={'dc':['prevresp']})

    elif model_name == 'stimcoding_sz_z_prevresp':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        # for Anke's data, also split by transition probability
        if 'transitionprob' in mydata.columns:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv', 'sz'), group_only_nodes=['sv', 'sz'],
                depends_on={'v': ['coherence'], 'z':['prevresp', 'transitionprob']})
        elif len(mydata.coherence.unique()) > 1:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv', 'sz'), group_only_nodes=['sv', 'sz'],
                depends_on={'v': ['coherence'], 'z':['prevresp']})
        else:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv', 'sz'), group_only_nodes=['sv', 'sz'],
                depends_on={'z':['prevresp']})

    elif model_name == 'stimcoding_sz_dc_z_prevresp':

        # include across-trial variability in starting point
        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        # for Anke's data, also split by transition probability
        if 'transitionprob' in mydata.columns:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv', 'sz'), group_only_nodes=['sv', 'sz'],
                depends_on={'v': ['coherence'], 'dc':['prevresp', 'transitionprob'],
                'z':['prevresp', 'transitionprob']})
        elif len(mydata.coherence.unique()) > 1:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv', 'sz'), group_only_nodes=['sv', 'sz'],
                depends_on={'v': ['coherence'], 'dc':['prevresp'], 'z':['prevresp']})
        else:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv', 'sz'), group_only_nodes=['sv', 'sz'],
                depends_on={'dc':['prevresp'], 'z':['prevresp']})

    # ============================================ #
    # PHARMA
    # ============================================ #

    elif model_name == 'stimcoding_dc_z_prevresp_pharma':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
            drift_criterion=True, bias=True, p_outlier=0.05,
            include=('sv'), group_only_nodes=['sv'],
            depends_on={'dc':['prevresp', 'drug'], 'z':['prevresp', 'drug']})

    elif model_name == 'stimcoding_dc_prevresp_sessions':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
            drift_criterion=True, bias=True, p_outlier=0.05,
            include=('sv'), group_only_nodes=['sv'],
            depends_on={'dc':['prevresp', 'session']})

    elif model_name == 'stimcoding_dc_z_prevresp_sessions':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
            drift_criterion=True, bias=True, p_outlier=0.05,
            include=('sv'), group_only_nodes=['sv'],
            depends_on={'dc':['prevresp', 'session'], 'z':['prevresp', 'session']})

    # ============================================ #
    # STIMCODING PREVRESP + PREVCORRECT
    # ============================================ #

    elif model_name == 'stimcoding_dc_prevcorrect':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        # also split by transition probability and include coherence-dependence of drift rate
        if 'transitionprob' in mydata.columns:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence'], 'dc':['prevresp', 'prevcorrect', 'transitionprob']})
        elif len(mydata.coherence.unique()) > 1:
            print "splitting by coherence"
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence'], 'dc':['prevresp', 'prevcorrect']})
        else:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'dc':['prevresp', 'prevcorrect']})

    elif model_name == 'stimcoding_z_prevcorrect':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        # also split by transition probability
        if 'transitionprob' in mydata.columns:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence'], 'z':['prevresp', 'prevcorrect', 'transitionprob']})
        elif len(mydata.coherence.unique()) > 1:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence'], 'z':['prevresp', 'prevcorrect']})
        else:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'z':['prevresp', 'prevcorrect']})

    elif model_name == 'stimcoding_dc_z_prevcorrect':

        # get the right variable coding
        mydata = recode_4stimcoding(mydata)

        # also split by transition probability
        if 'transitionprob' in mydata.columns:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence'], 'dc':['prevresp', 'prevcorrect', 'transitionprob'],
                'z':['prevresp', 'prevcorrect', 'transitionprob']})
        elif len(mydata.coherence.unique()) > 1:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'v': ['coherence'], 'dc':['prevresp', 'prevcorrect'], 'z':['prevresp', 'prevcorrect']})
        else:
            m = hddm.HDDMStimCoding(mydata, stim_col='stimulus', split_param='v',
                drift_criterion=True, bias=True, p_outlier=0.05,
                include=('sv'), group_only_nodes=['sv'],
                depends_on={'dc':['prevresp', 'prevcorrect'], 'z':['prevresp', 'prevcorrect']})

    # ============================================ #
    # REGRESSION MODULATION
    # Nienborg @ SfN: ((s*v) + vbias)dt / (s*(v+vbias))dt, does it matter and what are the differential predictions?
    # ============================================ #

    elif model_name == 'regress_dc_prevresp':

        if 'transitionprob' in mydata.columns:
            v_reg = {'model': 'v ~ 1 + stimulus + prevresp:C(transitionprob) ', 'link_func': lambda x:x}
        else:
            v_reg = {'model': 'v ~ 1 + stimulus + prevresp', 'link_func': lambda x:x}

        m = hddm.HDDMRegressor(mydata, v_reg,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False, p_outlier=0.05)

    elif model_name == 'regress_dc2_prevresp':

        v_reg = {'model': 'v ~ (1 + prevresp)*stimulus', 'link_func': lambda x:x}
        m = hddm.HDDMRegressor(mydata, v_reg,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False, p_outlier=0.05)

    # ============================================ #
    # MODULATION BY PUPIL AND RT
    # ============================================ #

    elif model_name == 'regress_dc_prevresp_prevrt':

        if 'transitionprob' in mydata.columns:
         v_reg = {'model': 'v ~ 1 + stimulus + C(transitionprob):prevresp + ' \
         'C(transitionprob):prevrt + C(transitionprob):prevresp:prevrt', 'link_func': lambda x:x}
        else:
         v_reg = {'model': 'v ~ 1 + stimulus + prevresp*prevrt', 'link_func': lambda x:x}

        m = hddm.HDDMRegressor(mydata, v_reg,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False, p_outlier=0.05)

    # ================================================== #
    # THE MOST IMPORTANT MODEL FOR THE UNCERTAINTY MODULATION
    # ================================================== #

    elif model_name == 'regress_dc_z_prevresp_prevrt':

        mydata = mydata.dropna(subset=['prevresp','prevrt'])

        # subselect data
        if 'transitionprob' in mydata.columns:
             v_reg = {'model': 'v ~ 1 + stimulus + C(transitionprob):prevresp + ' \
             'C(transitionprob):prevrt + C(transitionprob):prevresp:prevrt', 'link_func': lambda x:x}
             z_reg = {'model': 'z ~ 1 + prevresp:C(transitionprob) +' \
             'prevresp:prevrt:C(transitionprob) + prevrt:C(transitionprob)',
             'link_func': z_link_func}
        else:
            v_reg = {'model': 'v ~ 1 + stimulus + prevresp*prevrt',
            'link_func': lambda x:x}
            z_reg = {'model': 'z ~ 1 + prevresp*prevrt',
            'link_func': z_link_func}

        reg_both = [v_reg, z_reg]
        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False, p_outlier=0.05)

    elif model_name == 'regress_dc_z_prevresp_prevstim_prevrt_prevpupil':

        # subselect data
        mydata = mydata.dropna(subset=['prevpupil'])
        if len(mydata.session.unique()) < max(mydata.session.unique()):
            mydata["session"] = mydata["session"].map({1:1, 5:2})
        mydata = balance_designmatrix(mydata)

        # boundary separation and drift rate will change over sessions
        if 'transitionprob' in mydata.columns:
            v_reg = {'model': 'v ~ 1 + stimulus + ' \
            'prevresp:C(transitionprob) + prevstim:C(transitionprob) + ' \
            'prevresp:prevpupil:C(transitionprob) + prevstim:prevpupil:C(transitionprob) + ' \
            'prevresp:prevrt:C(transitionprob) + prevstim:prevrt:C(transitionprob)',
            'link_func': lambda x:x}
            z_reg = {'model': 'z ~ 1 + prevresp:C(transitionprob) + prevstim:C(transitionprob) +' \
            'prevresp:prevpupil:C(transitionprob) + prevstim:prevpupil:C(transitionprob) +' \
            'prevresp:prevrt:C(transitionprob) + prevstim:prevrt:C(transitionprob)',
            'link_func': z_link_func}
        else:
            v_reg = {'model': 'v ~ 1 + stimulus + prevresp + prevstim + ' \
            'prevresp:prevrt + prevstim:prevrt + prevresp:prevpupil + prevstim:prevpupil',
            'link_func': lambda x:x}
            z_reg = {'model': 'z ~ 1 + prevresp + prevstim +' \
            'prevresp:prevpupil + prevstim:prevpupil +' \
            'prevresp:prevrt + prevstim:prevrt',
            'link_func': z_link_func}
        reg_both = [v_reg, z_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False,  p_outlier=0.05)

    # ============================================ #
    # MULTIPLE LAGS
    # ============================================ #

    elif model_name == 'regress_dc_z_prev2resp':

        if 'transitionprob' in mydata.columns:
            z_reg = {'model': 'z ~ 1 + prevresp:C(transitionprob)+ prev2resp:C(transitionprob)',
            'link_func': z_link_func}
            v_reg = {'model': 'v ~ 1 + stimulus + prevresp:C(transitionprob)  + prev2resp:C(transitionprob)',
            'link_func': lambda x:x}
        else:
            z_reg = {'model': 'z ~ 1 + prevresp  + prev2resp ', 'link_func': z_link_func}
            v_reg = {'model': 'v ~ 1 + stimulus + prevresp + prev2resp ', 'link_func': lambda x:x}
        reg_both = [z_reg, v_reg]

        # subselect data
        mydata = mydata.dropna(subset=['prev2resp'])

        # specify that we want individual parameters for all regressors, see email Gilles 22.02.2017
        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False,  p_outlier=0.05)

    elif model_name == 'regress_dc_z_prev3resp':

        if 'transitionprob' in mydata.columns:
            z_reg = {'model': 'z ~ 1 + prevresp:C(transitionprob) + prev2resp:C(transitionprob) + prev3resp:C(transitionprob)',
            'link_func': z_link_func}
            v_reg = {'model': 'v ~ 1 + stimulus + prevresp:C(transitionprob) + prev2resp:C(transitionprob) + prev3resp:C(transitionprob)',
            'link_func': lambda x:x}
        else:
            z_reg = {'model': 'z ~ 1 + prevresp + prev2resp + prev3resp ', 'link_func': z_link_func}
            v_reg = {'model': 'v ~ 1 + stimulus + prevresp + prev2resp + prev3resp ', 'link_func': lambda x:x}
        reg_both = [z_reg, v_reg]

        mydata = mydata.dropna(subset=['prev2resp', 'prev3resp'])

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False,  p_outlier=0.05)

    # ============================================ #
    # RT AND PUPIL MODULATION onto DC
    # ============================================ #

    elif model_name == 'regress_dc_prevresp_prevstim_prevpupil':

        # subselect data
        mydata = mydata.dropna(subset=['prevpupil'])
        if len(mydata.session.unique()) < max(mydata.session.unique()):
            mydata["session"] = mydata["session"].map({1:1, 5:2})
            mydata = balance_designmatrix(mydata)

        # in Anke's data, vary both dc and z
        if 'transitionprob' in mydata.columns:
            v_reg = {'model': 'v ~ 1 + stimulus + ' \
                'prevresp:C(transitionprob) + prevstim:C(transitionprob) + ' \
                'prevresp:prevpupil:C(transitionprob) + prevstim:prevpupil:C(transitionprob)',
                'link_func': lambda x:x}
        else:
            v_reg = {'model': 'v ~ 1 + stimulus + prevresp + prevstim + ' \
                'prevresp:prevpupil + prevstim:prevpupil', 'link_func': lambda x:x}
        reg_both = [v_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False,  p_outlier=0.05)

    elif model_name == 'regress_dc_prevresp_prevstim_prevrt':

        # subselect data
        mydata = balance_designmatrix(mydata)

        # boundary separation and drift rate will change over sessions
        if 'transitionprob' in mydata.columns:
            v_reg = {'model': 'v ~ 1 + stimulus + ' \
                'prevresp:C(transitionprob) + prevstim:C(transitionprob) + ' \
                'prevresp:prevrt:C(transitionprob) + prevstim:prevrt:C(transitionprob)',
                'link_func': lambda x:x}
        else:
            v_reg = {'model': 'v ~ 1 + stimulus + prevresp + prevstim + prevresp:prevrt + prevstim:prevrt',
            'link_func': lambda x:x}

        m = hddm.HDDMRegressor(mydata, v_reg,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=True,  p_outlier=0.05)

    elif model_name == 'regress_dc_prevresp_prevstim_prevrt_prevpupil':

        # subselect data
        mydata = mydata.dropna(subset=['prevpupil'])
        if len(mydata.session.unique()) < max(mydata.session.unique()):
            mydata["session"] = mydata["session"].map({1:1, 5:2})

        mydata = balance_designmatrix(mydata)

        # boundary separation and drift rate will change over sessions
        if 'transitionprob' in mydata.columns:
            v_reg = {'model': 'v ~ 1 + stimulus + ' \
                'prevresp:C(transitionprob) + prevstim:C(transitionprob) + ' \
                'prevresp:prevpupil:C(transitionprob) + prevstim:prevpupil:C(transitionprob) + ' \
                'prevresp:prevrt:C(transitionprob) + prevstim:prevrt:C(transitionprob)',
                'link_func': lambda x:x}
        else:
            v_reg = {'model': 'v ~ 1 + stimulus + prevresp + prevstim + ' \
                'prevresp:prevrt + prevstim:prevrt + prevresp:prevpupil + prevstim:prevpupil',
                'link_func': lambda x:x}

        m = hddm.HDDMRegressor(mydata, v_reg,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=True,  p_outlier=0.05)

    # ============================================ #
    # LEARNING EFFECTS, V AND A CHANGE WITH SESSION
    # ============================================ #

    elif model_name == 'regress_dc_z_prevresp_prevstim_prevpupil':

        # subselect data
        mydata = mydata.dropna(subset=['prevpupil'])
        if len(mydata.session.unique()) < max(mydata.session.unique()):
            mydata["session"] = mydata["session"].map({1:1, 5:2})
            mydata = balance_designmatrix(mydata)

        # in Anke's data, vary both dc and z
        if 'transitionprob' in mydata.columns:
            v_reg = {'model': 'v ~ 1 + stimulus + ' \
                'prevresp:C(transitionprob) + prevstim:C(transitionprob) + ' \
                'prevresp:prevpupil:C(transitionprob) + prevstim:prevpupil:C(transitionprob)',
                'link_func': lambda x:x}
            z_reg = {'model': 'z ~ 1 + prevresp:C(transitionprob) + prevstim:C(transitionprob) +' \
                'prevresp:prevpupil:C(transitionprob) + prevstim:prevpupil:C(transitionprob)',
                'link_func': z_link_func}
        else:
            v_reg = {'model': 'v ~ 1 + stimulus + prevresp + prevstim + ' \
                'prevresp:prevpupil + prevstim:prevpupil',
                'link_func': lambda x:x}
            z_reg = {'model': 'z ~ 1 + prevresp + prevstim +' \
                'prevresp:prevpupil + prevstim:prevpupil',
                'link_func': z_link_func}
        reg_both = [v_reg, z_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=True,  p_outlier=0.05)

    # ============================================ #
    # SESSION DEPENDENCE
    # ============================================ #

    elif model_name == 'regress_dc_prevresp_prevstim_vasessions':

        # subselect data
        mydata = balance_designmatrix(mydata)

        # boundary separation and drift rate will change over sessions
        a_reg = {'model': 'a ~ 1 + C(session)', 'link_func': lambda x:x} # boundary separation as a function of sessions
        if 'transitionprob' in mydata.columns:
            v_reg = {'model': 'v ~ 1 + stimulus:C(session) + prevresp:C(transitionprob) + prevstim:C(transitionprob)', 'link_func': lambda x:x}
        else:
            v_reg = {'model': 'v ~ 1 + stimulus:C(session) + prevresp + prevstim', 'link_func': lambda x:x}
        reg_both = [v_reg, a_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=True,  p_outlier=0.05)

    elif model_name == 'regress_dc_z_prevresp_prevstim_vasessions':

        # subselect data
        mydata = balance_designmatrix(mydata)

        # boundary separation and drift rate will change over sessions
        a_reg = {'model': 'a ~ 1 + C(session)', 'link_func': lambda x:x} # boundary separation as a function of sessions
        if 'transitionprob' in mydata.columns:
            v_reg = {'model': 'v ~ 1 + stimulus:C(session) + prevresp:C(transitionprob) + prevstim:C(transitionprob)', 'link_func': lambda x:x}
            z_reg = {'model': 'z ~ 1 + prevresp:C(transitionprob) + prevstim:C(transitionprob)', 'link_func': z_link_func}
            reg_both = [v_reg, a_reg, z_reg]
        else:
            v_reg = {'model': 'v ~ 1 + stimulus:C(session) + prevresp + prevstim', 'link_func': lambda x:x}
            z_reg = {'model': 'z ~ 1 + prevresp+ prevstim', 'link_func': z_link_func}
        reg_both = [v_reg, a_reg, z_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=True,  p_outlier=0.05)

    elif model_name == 'regress_dc_prevresp_prevstim_vasessions_prevrespsessions':

        # subselect data
        mydata = balance_designmatrix(mydata)

        # boundary separation and drift rate will change over sessions
        if 'transitionprob' in mydata.columns:
            raise ValueError('Do not fit session-specific serial bias on Anke''s data')
        else:
            v_reg = {'model': 'v ~ 1 + stimulus:C(session) + prevresp:C(session) + prevstim:C(session)', 'link_func': lambda x:x}
            a_reg = {'model': 'a ~ 1 + C(session)', 'link_func': lambda x:x} # boundary separation as a function of sessions
        reg_both = [v_reg, a_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=True,  p_outlier=0.05)

    elif model_name == 'regress_dc_prevresp_prevstim_vasessions_prevpupil':

        # subselect data
        mydata = mydata.dropna(subset=['prevpupil'])
        if len(mydata.session.unique()) < max(mydata.session.unique()):
            mydata["session"] = mydata["session"].map({1:1, 5:2})
        mydata = balance_designmatrix(mydata)

        # boundary separation and drift rate will change over sessions
        a_reg = {'model': 'a ~ 1 + C(session)', 'link_func': lambda x:x}
        if 'transitionprob' in mydata.columns:
            v_reg = {'model': 'v ~ 1 + stimulus:C(session) + ' \
            'prevresp:C(transitionprob) + prevstim:C(transitionprob) + ' \
            'prevresp:prevpupil:C(transitionprob) + prevstim:prevpupil:C(transitionprob)',
            'link_func': lambda x:x}
        else:
            v_reg = {'model': 'v ~ 1 + stimulus:C(session) + prevresp + prevstim + ' \
            'prevresp:prevpupil + prevstim:prevpupil',
            'link_func': lambda x:x}
        reg_both = [v_reg, a_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=True,  p_outlier=0.05)

    elif model_name == 'regress_dc_prevresp_prevstim_vasessions_prevrt':

        # subselect data
        mydata = balance_designmatrix(mydata)

        # boundary separation and drift rate will change over sessions
        a_reg = {'model': 'a ~ 1 + C(session)', 'link_func': lambda x:x}
        if 'transitionprob' in mydata.columns:
            v_reg = {'model': 'v ~ 1 + stimulus:C(session) + ' \
            'prevresp:C(transitionprob) + prevstim:C(transitionprob) + ' \
            'prevresp:prevrt:C(transitionprob) + prevstim:prevrt:C(transitionprob)',
            'link_func': lambda x:x}
        else:
            v_reg = {'model': 'v ~ 1 + stimulus:C(session) + prevresp + prevstim + prevresp:prevrt + prevstim:prevrt',
            'link_func': lambda x:x}
        reg_both = [v_reg, a_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=True,  p_outlier=0.05)

    elif model_name == 'regress_dc_prevresp_prevstim_vasessions_prevrt_prevpupil':

        # subselect data
        mydata = mydata.dropna(subset=['prevpupil'])
        if len(mydata.session.unique()) < max(mydata.session.unique()):
            mydata["session"] = mydata["session"].map({1:1, 5:2})

        mydata = balance_designmatrix(mydata)

        # boundary separation and drift rate will change over sessions
        a_reg = {'model': 'a ~ 1 + C(session)', 'link_func': lambda x:x}
        if 'transitionprob' in mydata.columns:
            v_reg = {'model': 'v ~ 1 + stimulus:C(session) + ' \
            'prevresp:C(transitionprob) + prevstim:C(transitionprob) + ' \
            'prevresp:prevrt:C(transitionprob) + prevstim:prevrt:C(transitionprob) +' \
            'prevresp:prevpupil:C(transitionprob) + prevstim:prevpupil:C(transitionprob)',
            'link_func': lambda x:x}
        else:
            v_reg = {'model': 'v ~ 1 + stimulus:C(session) + prevresp + prevstim + ' \
            'prevresp:prevrt + prevstim:prevrt + prevresp:prevpupil + prevstim:prevpupil',
            'link_func': lambda x:x}
        reg_both = [v_reg, a_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=True,  p_outlier=0.05)

    # ============================================ #
    # MEG DATA
    # ============================================ #

    elif model_name == 'regress_nohist':

        # only stimulus dependence
        v_reg = {'model': 'v ~ 1 + stimulus', 'link_func': lambda x:x}

        # specify that we want individual parameters for all regressors, see email Gilles 22.02.2017
        m = hddm.HDDMRegressor(mydata, v_reg,
            include=['z', 'sv'], group_only_nodes=['sv'],
            group_only_regressors=False, keep_regressor_trace=False, p_outlier=0.05)

    elif model_name == 'regress_dc_z_prevresp':

        if 'transitionprob' in mydata.columns:
            z_reg = {'model': 'z ~ 1 + C(transitionprob):prevresp', 'link_func': z_link_func}
            v_reg = {'model': 'v ~ 1 + stimulus + C(transitionprob):prevresp', 'link_func': lambda x:x}
        else:
            z_reg = {'model': 'z ~ 1 + prevresp', 'link_func': z_link_func}
            v_reg = {'model': 'v ~ 1 + stimulus + prevresp', 'link_func': lambda x:x}
        reg_both = [z_reg, v_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False,  p_outlier=0.05)

    elif model_name == 'regress_dc_z_visualgamma':

        z_reg = {'model': 'z ~ 1 + visualgamma', 'link_func': z_link_func}
        v_reg = {'model': 'v ~ 1 + stimulus + visualgamma', 'link_func': lambda x:x}
        reg_both = [z_reg, v_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False,  p_outlier=0.05)

    elif model_name == 'regress_dc_z_motorslope':

        z_reg = {'model': 'z ~ 1 + motorslope', 'link_func': z_link_func}
        v_reg = {'model': 'v ~ 1 + stimulus + motorslope', 'link_func': lambda x:x}
        reg_both = [z_reg, v_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False,  p_outlier=0.05)

    elif model_name == 'regress_dc_z_motorstart':

        z_reg = {'model': 'z ~ 1 + motorbeta', 'link_func': z_link_func}
        v_reg = {'model': 'v ~ 1 + stimulus + motorbeta', 'link_func': lambda x:x}
        reg_both = [z_reg, v_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False,  p_outlier=0.05)


    elif model_name == 'regress_dc_z_prevresp_visualgamma':

        z_reg = {'model': 'z ~ 1 + prevresp + visualgamma', 'link_func': z_link_func}
        v_reg = {'model': 'v ~ 1 + stimulus + prevresp + visualgamma', 'link_func': lambda x:x}
        reg_both = [z_reg, v_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False,  p_outlier=0.05)

    elif model_name == 'regress_dc_z_prevresp_motorslope':

        z_reg = {'model': 'z ~ 1 + prevresp + motorslope', 'link_func': z_link_func}
        v_reg = {'model': 'v ~ 1 + stimulus + prevresp + motorslope', 'link_func': lambda x:x}
        reg_both = [z_reg, v_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False,  p_outlier=0.05)

    elif model_name == 'regress_dc_z_prevresp_motorstart':

        z_reg = {'model': 'z ~ 1 + prevresp + motorbeta', 'link_func': z_link_func}
        v_reg = {'model': 'v ~ 1 + stimulus + prevresp + motorbeta', 'link_func': lambda x:x}
        reg_both = [z_reg, v_reg]

        m = hddm.HDDMRegressor(mydata, reg_both,
        include=['z', 'sv'], group_only_nodes=['sv'],
        group_only_regressors=False, keep_regressor_trace=False,  p_outlier=0.05)

    # ============================================ #
    # END OF FUNCTION THAT CREATES THE MODEL
    # ============================================ #

    return m
