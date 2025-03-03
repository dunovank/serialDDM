
% Code to fit the history-dependent drift diffusion models described in
% Urai AE, Gee JW de, Donner TH (2018) Choice history biases subsequent evidence accumulation. bioRxiv:251595
%
% MIT License
% Copyright (c) Anne Urai, 2018
% anne.urai@gmail.com

%% determine how the figures will look
clear all; clc; close all;
set(groot, 'defaultaxesfontsize', 6, 'defaultaxestitlefontsizemultiplier', 1.1, ...
    'defaultaxeslabelfontsizemultiplier', 1.1, ...
    'defaultaxestitlefontweight', 'bold', ...
    'defaultfigurerenderermode', 'manual', 'defaultfigurerenderer', 'painters', ...
    'DefaultAxesBox', 'off', ...
    'DefaultAxesTickLength', [0.02 0.05], 'defaultaxestickdir', 'out', 'DefaultAxesTickDirMode', 'manual', ...
    'defaultfigurecolormap', [1 1 1], 'defaultTextInterpreter','tex');

global datasets datasetnames mypath colors

usr = getenv('USER');
switch usr
    case 'anne'
        mypath = '~/Data/HDDM';
    case 'aeurai'
        mypath  = '/nfs/aeurai/HDDM';
end

% neutral vs biased plotsC
datasets = {'Murphy', 'JW_PNAS', 'JW_yesno', 'NatComm', 'MEG', 'MEG_MEGsessions', 'Bharath_fMRI', 'Anke_2afc_sequential', 'Anke_MEG'};
datasetnames = { {'Visual motion' '2AFC (RT)'},  {'Visual contrast' 'yes/no (RT)'}, {'Auditory' 'yes/no (RT)'}, ...
    {'Visual motion' '2IFC (FD) #1'}, {'Visual motion' '2IFC (FD) #2'},  {'Visual motion' '2IFC (FD) #2'}, ...
    {'Bharath fMRI' ''}, {'Anke JoN' ''}, {'Anke MEG' ''}};
datasets = datasets(1:5);

% go to code
try
    cd('/Users/anne/Desktop/code/serialDDM');
end

% from Thomas, green blue grey
colors = [141 165 8;  8 141 165; 150 150 150] ./ 256;
colors = [51,160,44; 31,120,180] ./ 256;
colors = [178,223,138; 166,206,227] ./ 256; % lighter
colors = [77,175,74; 55,126,184] ./ 256; % green blue

%% PREPARING DATA
if 1,
    b2_HDDM_readIntoMatlab(datasets);
    b2b_Gsq_readIntoMatlab(datasets);
    b3_makeDataframe(datasets);
end

disp('starting');

% ======================= %
% SCHEMATIC/HYPOTHESES
% ======================= %

f0_schematic_DDM_bias; % figure 3a

% ======================= %
% SANITY CHECKS/ MODEL FITS
% ======================= %

e1_serialBias_SfN_DIC;
e3_serialBias_SfN_repetitionRange;
e2_serialBias_SfN_SanityChecks; % correlate dprime with drift rate
e8_serialBias_SfN_PPC; % figure 2, show that all models fit OK

% % show the fits separately for dc and z
% alldat = e1b_serialBias_SfN_ModelFreeCorrelation_independentFits; % figure 4
% forestPlot(alldat);
% print(gcf, '-dpdf', sprintf('~/Data/serialHDDM/forestplot_indep.pdf'));

e3_serialBias_SfN_Posteriors_StartingPoint;

% ======================= %
% CORRELATIONS WITH P(REPEAT)
% ======================= %

close all;
for sz = [0 1],
    for Gsq = [0 1],

        if Gsq == 1 && sz == 1, continue; end % hierarchical sampling with sz takes forever

        alldat = e1b_serialBias_SfN_ModelFreeCorrelation_grey(Gsq, sz); % figure 4
        forestPlot(alldat);

        switch Gsq
            case 1
                filename = sprintf('~/Data/serialHDDM/forestplot_sz%d_Gsq.pdf', sz);
            case 0
                filename = sprintf('~/Data/serialHDDM/forestplot_sz%d_HDDM.pdf', sz);
        end
        print(gcf, '-dpdf', filename);
    end
end

% ========================= %
% MEG PHARMA
% ========================= %

alldat = e1b_serialBias_SfN_ModelFreeCorrelation_MEGpharma(); % figure 4
forestPlot(fliplr(alldat));
print(gcf, '-dpdf', sprintf('~/Data/serialHDDM/forestplot_pharma.pdf'));

% ======================= %
% MODEL FREE CONFIRMATION
% ======================= %

e6_serialBias_SfN_modelFree_CRF_PPC

% ======================= %
% PREVCORRECT
% ======================= %

% alldat = e1b_serialBias_SfN_ModelFreeCorrelation_prevCorrect;
% forestPlot(alldat);
% print(gcf, '-dpdf', sprintf('~/Data/serialHDDM/forestplot_HDDM_prevcorrect.pdf'));

% ======================= %
% REGRESSION MODELS
% ======================= %

% 1. compare dic between models with just history and with neural data
%e11_serialBias_MEGregression_DIC
%e11_serialBias_MEGregression_posteriors

% e3_serialBias_SfN_RTmodulation;

% POSTERIORS OF STARTING POINT SHIFT
%e3_serialBias_SfN_Posteriors_StartingPoint;

% sv_comparison;
