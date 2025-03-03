function e6_serialBias_SfN_modelFree_CRF_PPC

% Code to fit the history-dependent drift diffusion models described in
% Urai AE, Gee JW de, Donner TH (2018) Choice history biases subsequent evidence accumulation. bioRxiv:251595
%
% MIT License
% Copyright (c) Anne Urai, 2018
% anne.urai@gmail.com

% ========================================== %
% conditional response functions from White & Poldrack
% run on simulated rather than real data
% ========================================== %

addpath(genpath('~/code/Tools'));
warning off; close all; clear;
global datasets datasetnames mypath colors

qntls{1} = [.2, .4, .6, .8, .95]; % White & Poldrack
qntls{2} = [0.1, 0.3, 0.5, 0.7, 0.9]; % Leite & Ratcliff
qntls{3} = [0.3 0.6 0.9];
qntls{4} = [0.5 0.95]; % median split

% redo this for each simulation
models = {'stimcoding_nohist', 'stimcoding_z_prevresp',  ...
    'stimcoding_dc_prevresp', 'stimcoding_dc_z_prevresp' ...
    'data'};
thesecolors = {[0.5 0.5 0.5],  colors(1, :), ...
    colors(2, :), {colors(2, :), colors(1, :)}, [0 0 0]};

fixedEffects = 0;
allcols = colors;

allds.fast  = nan(length(datasets), length(models));
allds.slow = nan(length(datasets), length(models));

for q = 2; %:length(qntls),
    for d = 1:length(datasets),
        
        switch datasets{d}
            case {'Bharath_fMRI', 'Anke_MEG', 'Anke_2afc_sequential', 'Anke_merged'}
                tps = [20 80];
            otherwise
                tps = 0;
        end
        
        % plot
        close all;
        subplot(441); hold on;
        
        for tp = 1:length(tps),
            
            % {colors(1,:), colors(2, :)}, ...
            
            for m = 1:length(models),
                
                switch models{m}
                    case 'data'
                        filename = dir(sprintf('%s/%s/*.csv', mypath, datasets{d}));
                        alldata  = readtable(sprintf('%s/%s/%s', mypath, datasets{d}, filename.name));
                    otherwise
                        if ~exist(sprintf('%s/%s/%s/ppc_data.csv', mypath, datasets{d}, models{m}), 'file'),
                            continue;
                        else
                            fprintf('%s/%s/%s/ppc_data.csv \n', mypath, datasets{d}, models{m});
                        end
                        % load simulated data - make sure this has all the info we need
                        alldata    = readtable(sprintf('%s/%s/%s/ppc_data.csv', mypath, datasets{d}, models{m}));
                        alldata    = sortrows(alldata, {'subj_idx'});
                end
                
                if ~any(ismember(alldata.Properties.VariableNames, 'transitionprob'))
                    alldata.transitionprob = zeros(size(alldata.subj_idx));
                else
                    assert(nanmean(unique(alldata.transitionprob)) == 50, 'rescale units');
                    alldata = alldata(alldata.transitionprob == tps(tp), :);
                end
                
                if m < length(models),
                    % use the simulations rather than the subjects' actual responses
                    alldata.rt          = abs(alldata.rt_sampled);
                    alldata.response    = alldata.response_sampled;
                end
                
                % when there were multiple levels of evidence, do these plots
                % separately for each level
                if any(ismember(alldata.Properties.VariableNames, 'coherence'))
                    origNsubj = numel(unique(alldata.subj_idx));
                    alldata.subj_idx = findgroups(alldata.subj_idx, alldata.coherence);
                    newNsubj = numel(unique(alldata.subj_idx));
                    if origNsubj ~= newNsubj,
                        fprintf('splitting by coherence, nsubj %d newNsubj %d \n', origNsubj, newNsubj);
                    end
                end
                
                % make sure to use absolute RTs!
                alldata.rt = abs(alldata.rt);
                
                % recode into repeat and alternate for the model
                alldata.repeat = zeros(size(alldata.response));
                alldata.repeat(alldata.response == (alldata.prevresp > 0)) = 1;
                
                % for each observers, compute their bias
                [gr, sjs] = findgroups(alldata.subj_idx);
                sjrep = splitapply(@nanmean, alldata.repeat, gr);
                sjrep = sjs(sjrep < 0.5);
                
                % recode into biased and unbiased choices
                alldata.biased = alldata.repeat;
                altIdx = ismember(alldata.subj_idx, sjrep);
                if tps(tp) == 0,
                    alldata.biased(altIdx) = double(~(alldata.biased(altIdx))); % flip
                end
                
                % fixed effects
                if fixedEffects,
                    alldata.subj_idx = ones(size(alldata.subj_idx));
                end
                
                % divide RT into quantiles for each subject
                discretizeRTs = @(x) {discretize(x, quantile(x, [0, qntls{q}]))};
                rtbins = splitapply(discretizeRTs, alldata.rt, findgroups(alldata.subj_idx));
                alldata.rtbins = cat(1, rtbins{:});
                
                % get RT quantiles for choices that are in line with or against the bias
                [gr, sjidx, rtbins] = findgroups(alldata.subj_idx, alldata.rtbins);
                cpres               = array2table([sjidx, rtbins], 'variablenames', {'subj_idx', 'rtbin'});
                cpres.choice        = splitapply(@nanmean, alldata.biased, gr); % choice proportion
                
                % make into a subjects by rtbin matrix
                mat = unstack(cpres, 'choice', 'rtbin');
                mat = mat{:, 2:end}; % remove the last one, only has some weird tail
                
                % biased choice proportion
                if m < length(models),
                    if isnumeric(thesecolors{m})
                        plot(qntls{q}, nanmean(mat, 1), 'color', thesecolors{m}, 'linewidth', 0.5);
                    elseif iscell(thesecolors{m}) % superimposed lines for dashed
                        plot(qntls{q}, nanmean(mat, 1), 'color', thesecolors{m}{1}, 'linewidth', 1.5);
                        plot(qntls{q}, nanmean(mat, 1), ':', 'color', thesecolors{m}{2}, 'linewidth', 1.5);
                    end
                else
                    %% ALSO ADD THE REAL DATA
                    h = ploterr(qntls{q}, nanmean(mat, 1), [], ...
                        1.96 *  nanstd(mat, [], 1) ./ sqrt(size(mat, 1)), 'k', 'abshhxy', 0);
                    set(h(1), 'color', 'k', 'marker', '.', ...
                        'markerfacecolor', 'k', 'markeredgecolor', 'k', 'linewidth', 0.5, 'markersize', 10, ...
                        'linestyle', 'none');
                    set(h(2), 'linewidth', 0.5);
                end
                
                % SAVE
                avg = nanmean(mat, 1);
                allds.fast(d, m) = nanmean(avg(1:2));
                allds.slow(d, m) = nanmean(avg(end-3:end));
				allds.all(d, m, :) = avg;
            end
        end
        
        axis tight; box off;
        set(gca, 'xtick', qntls{q});
        axis square;  offsetAxes;
        if numel(qntls{q}) == 2,
            set(gca, 'xticklabel', {'fast', 'slow'});
            xlabel('Reaction times');
        else
            xlabel('RT (quantiles)');
        end
        set(gca, 'xcolor', 'k', 'ycolor', 'k');
        
        if tps(tp) > 0,
            switch tps(tp)
                case 20
                    title([datasetnames{d}{1} ' Alternating']);
                case 50
                    title([datasetnames{d}{1} ' Neutral']);
                case 80
                    title([datasetnames{d}{1} ' Repetitive']);
            end
            ylabel('Fraction repetitions');
        else
            ylabel('Fraction biased choices');
        end
        
        title(datasetnames{d}{1});
        tightfig;
        set(gca, 'xcolor', 'k', 'ycolor', 'k');
        
        if fixedEffects,
            print(gcf, '-dpdf', sprintf('~/Data/serialHDDM/CRF_PPC_d%d_qntlsR%d_fixed.pdf', d, q));
        else
            print(gcf, '-dpdf', sprintf('~/Data/serialHDDM/CRF_PPC_d%d_qntlsR%d.pdf', d, q));
        end
        fprintf('~/Data/serialHDDM/CRF_PPC_d%d_qntlsR%d.pdf \n', d, q);
    end
	
	savefast(sprintf('~/Data/serialHDDM/allds_q%d.mat', q), 'allds');
    
    % ========================================== %
    %% PLOT ACROSS DATASETS
    % ========================================== %
    
	load(sprintf('~/Data/serialHDDM/allds_q%d.mat', q));
    periods = {'fast', 'slow'};
	
    for p  = 1:2,
        close all;
        subplot(3,3,1); hold on;
		
		plot([1 5], [nanmean(allds.(periods{p})(:, 5)) nanmean(allds.(periods{p})(:, 5))], '--k');
		lower =  nanmean(allds.(periods{p})(:, 5)) - 1.96* nanstd(allds.(periods{p})(:, 5)) ./ sqrt(length(datasets));
		plot([1 5], [lower lower], ':k');
		upper =  nanmean(allds.(periods{p})(:, 5)) + 1.96* nanstd(allds.(periods{p})(:, 5)) ./ sqrt(length(datasets));
		plot([1 5], [upper upper], ':k');
		
        for b = 1:4,
            if ~iscell(thesecolors{b}),
                bar(b, nanmean(allds.(periods{p})(:, b)), 'edgecolor', 'none', ...
                    'facecolor', thesecolors{b}, 'basevalue', 0.5, 'barwidth', 0.6);
            else % add bar hatch
                [ptchs,ptchGrp] = createPatches(b, nanmean(allds.(periods{p})(:, b)), 0.3, thesecolors{b}{1},0, 0.5);
                hatch(ptchs, [0 8 1], thesecolors{b}{2});
            end
        end
        % now the data
        b = ploterr(5, nanmean(allds.(periods{p})(:, 5)), [], ...
          1.96 * nanstd(allds.(periods{p})(:, 5)) ./ sqrt(length(datasets)), ...
            'ko', 'abshhxy', 0);
        set(b(1), 'markerfacecolor', 'k', 'markeredgecolor', 'w', 'markersize', 4);
        
        title(sprintf('%s RTs', capitalize(periods{p})));
        ylabel('Fraction biased choices');
        set(gca, 'xtick', 1:5, 'xticklabel', {'No history', 'z_{bias}', 'v_{bias}', 'Both', 'Data'}, ...
            'xticklabelrotation', -30);
        axis square; axis tight; 
        ylim([0.5 0.56]); 
		set(gca, 'ytick', [0.5:0.02:0.56]);
		offsetAxes;
        tightfig;
        set(gca, 'ycolor', 'k', 'xcolor', 'k');
        print(gcf, '-dpdf', sprintf('~/Data/serialHDDM/CRF_qual_%s_q%d.pdf', periods{p}, q));
    end
	
    % ========================================== %
    %% ALSO PER MODEL
    % ========================================== %
 
	modelnames = {'No history', 'z_{bias}', 'v_{bias}', 'Both', 'Data'};
	close all;
    for m = 1:4,
		subplot(4,8,m); hold on;
        
		if ~iscell(thesecolors{m}),
        	b = bar(1:2, [nanmean(allds.fast(:, m)) nanmean(allds.slow(:, m))], 'edgecolor', 'none', ...
            	'facecolor', thesecolors{m}, 'basevalue', 0.5, 'barwidth', 0.6);
			bl = b.BaseLine; set(bl, 'visible', 'off');
			
        else % add bar hatch
            [ptchs, ptchGrp] = createPatches(1, [nanmean(allds.fast(:, m))], ...
            0.3, thesecolors{m}{1},0, 0.5);
            hatch(ptchs, [0 8 1], thesecolors{m}{2});
			
            [ptchs, ptchGrp] = createPatches(2, [nanmean(allds.slow(:, m))], ...
            0.3, thesecolors{m}{1},0, 0.5);
            hatch(ptchs, [0 8 1], thesecolors{m}{2});
        end
		
        b = ploterr(1:2, [nanmean(allds.fast(:, 5)) nanmean(allds.slow(:, 5))], [], ...
           1.96* [nanstd(allds.fast(:, 5)) nanstd(allds.slow(:, 5))] ./ sqrt(length(datasets)), ...
            'ko', 'abshhxy', 0);
        set(b(1), 'markerfacecolor', 'k', 'markeredgecolor', 'w', 'markersize', 4);
		
		set(gca, 'xtick', 1:2, 'xticklabel', periods);
		title(modelnames{m});

        % axis square; 
		axis tight; 
		get(gca, 'ylim')
        ylim([0.5 0.57]); 
		set(gca, 'ytick', [0.5:0.02:0.56]);
		
		if m == 1,
	        ylabel('Fraction biased choices');
		else
			set(gca, 'yticklabel', []);
		end
		offsetAxes;
        set(gca, 'ycolor', 'k', 'xcolor', 'k');
	end
    tightfig;
    print(gcf, '-dpdf', sprintf('~/Data/serialHDDM/CRF_qual_v2_q%d.pdf', q));
  
	
end
end
