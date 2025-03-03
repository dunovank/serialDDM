function alldat = e1b_serialBias_SfN_ModelFreeCorrelation_prevCorrect
% from the csv table, make an overview of repetition behaviour

% get a huge list with values for each participant
% can then work with this dataframe

close all; clc;
addpath(genpath('~/code/Tools'));

global mypath datasets datasetnames colors
cnt = 1;

if ~exist('Gsq', 'var'), Gsq = 0; end
if ~exist('sz', 'var'),  sz = 0; end

% ============================================ %
% ONE LARGE PLOT WITH PANEL FOR EACH DATASET
% ============================================ %

doText = true;

switch sz
    case 1
        whichmdls = ['stimcodingsz'];
    case 0
        whichmdls = ['stimcoding'];
end

close all;
for d = length(datasets):-1:1
    disp(datasets{d});
        
    if Gsq,
        results = readtable(sprintf('%s/summary/%s/allindividualresults_Gsq.csv', mypath, datasets{d}));
    else
        results = readtable(sprintf('%s/summary/%s/allindividualresults.csv', mypath, datasets{d}));
    end
    results = results(results.session == 0, :);
    allresults = struct(); alltitles = {};
    
    % ============================================ %
    % RECODE INTO HISTORY SHIFT POINT ESTIMATES
    % ============================================ %
    
    % use the stimcoding difference
    results.z_prevresp_correct = ...
        results.(['z_1_1__' whichmdls 'dczprevcorrect']) - results.(['z_1_2__' whichmdls 'dczprevcorrect']);
    results.v_prevresp_correct = ...
        results.(['dc_1_1__' whichmdls 'dczprevcorrect']) - results.(['dc_1_2__' whichmdls 'dczprevcorrect']);
    
    results.z_prevresp_error = ...
        results.(['z_0_1__' whichmdls 'dczprevcorrect']) - results.(['z_0_2__' whichmdls 'dczprevcorrect']);
    results.v_prevresp_error = ...
        results.(['dc_0_1__' whichmdls 'dczprevcorrect']) - results.(['dc_0_2__' whichmdls 'dczprevcorrect']);
    
    % assign to structure
    allresults(1).z_prevresp     = results.z_prevresp_correct;
    allresults(1).v_prevresp     = results.v_prevresp_correct;
    allresults(1).criterionshift = results.repetition;
    alltitles{1}                 = cat(2, datasetnames{d}{1}, ' - ', 'Correct');

    % also after error choices
    allresults(2).z_prevresp     = results.z_prevresp_error;
    allresults(2).v_prevresp     = results.v_prevresp_error;
    allresults(2).criterionshift = results.repetition;
    alltitles{2}                 = cat(2, datasetnames{d}{1}, ' - ', 'Error');
    
    disp(datasets{d}); disp(numel(unique(results.subjnr)));
    close all;
    
    % PLOT
    sp1 = subplot(4,4,1); hold on;
    [rho1, tt1] = plotScatter(allresults, 'z_prevresp', 0.585, doText);
    ylabel('P(repeat)');
    
    sp2 = subplot(4,4,2); hold on;
    [rho2, tt2, handles] = plotScatter(allresults, 'v_prevresp', 0.05, doText);
    set(gca, 'yticklabel', []);
    
    set(sp2, 'ylim', get(sp1, 'ylim'), 'ytick', get(sp1, 'ytick'));
    
    % compute the difference in correlation
    [rho3, pval3] = corr(cat(1, allresults(:).v_prevresp), cat(1, allresults(:).z_prevresp), ...
        'rows', 'complete', 'type', 'pearson');
    if pval3 < 0.05,
        fprintf('warning %s: rho = %.3f, pval = %.3f \n', datasets{d}, rho3, pval3);
    end
    [rhodiff, ~, pval] = rddiffci(rho1,rho2,rho3,numel(~isnan( cat(1, allresults(:).criterionshift))), 0.05);
    
    % move together
    sp2.Position(1) = sp2.Position(1) - 0.08;
    ss = suplabel(datasetnames{d}{1}, 't');
    set(ss, 'fontweight', 'normal');
    ss.FontWeight = 'normal';
    ss.Position(2) = ss.Position(2) - 0.03;
    
    % add colored axes after suplabel (which makes them black)
    xlabel(sp1, 'History bias in z');
    set(sp1, 'xcolor', colors(2, :));
    xlabel(sp2, 'History bias in v');
    set(sp2, 'xcolor', colors(1, :));
    
    if doText,
        %% add line between the two correlation coefficients
        txt = {sprintf('\\Deltar(%d) = %.3f, p = %.3f', length(find(~isnan(cat(1, allresults(:).criterionshift) )))-3, rhodiff, pval)};
        if pval < 0.001,
            txt = {sprintf('\\Deltar(%d) = %.3f, p < 0.001', length(find(~isnan(cat(1, allresults(:).criterionshift) )))-3,  rhodiff)};
        end
        title(txt, 'fontweight', 'normal', 'fontsize', 6, 'horizontalalignment', 'left');
    end

    tightfig;
    if Gsq,
        print(gcf, '-dpdf', sprintf('~/Data/serialHDDM/figure1c_Gsq_modelfree_prevcorrect_sz%d_d%d.pdf', d, sz));
    else
        print(gcf, '-dpdf', sprintf('~/Data/serialHDDM/figure1c_HDDM_modelfree_prevcorrect_sz%d_d%d.pdf', d, sz));
        %print(gcf, '-depsc', sprintf('~/Data/serialHDDM/figure1c_HDDM_modelfree_stimcoding_d%d.eps', d));
    end
    
    for a = 1:length(allresults),
        
        % SAVE CORRELATIONS FOR OVERVIEW PLOT
        [r,p,rlo,rup] = corrcoef(allresults(a).z_prevresp, allresults(a).criterionshift);
        alldat(cnt).corrz = r(1,2);
        alldat(cnt).corrz_ci = [rlo(1,2) rup(1,2)];
        alldat(cnt).pz = p(1,2);
        alldat(cnt).bfz = corrbf(r(1,2), numel(allresults(a).z_prevresp));
        
        [r,p,rlo,rup] = corrcoef(allresults(a).v_prevresp, allresults(a).criterionshift);
        alldat(cnt).corrv = r(1,2);
        alldat(cnt).corrv_ci = [rlo(1,2) rup(1,2)];
        alldat(cnt).pv = p(1,2);
        alldat(cnt).bfv = corrbf(r(1,2), numel(allresults(a).v_prevresp));
        
        alldat(cnt).datasets = datasets{d};
        alldat(cnt).datasetnames = alltitles{a};
        
        % also add the difference in r, Steigers test
        [r,p,rlo,rup] = corrcoef(allresults(a).v_prevresp, allresults(a).z_prevresp);
        
        [rhodiff, rhodiffci, pval] = rddiffci(alldat(cnt).corrz,alldat(cnt).corrv, ...
            r(1,2), ...
            numel(allresults(a).v_prevresp), 0.05);
        
        alldat(cnt).corrdiff = rhodiff;
        alldat(cnt).corrdiff_ci = rhodiffci;
        alldat(cnt).pdiff = pval;
        
        cnt = cnt + 1;
    end
end

end

function [rho, tt, handles] = plotScatter(allresults, fld, legendWhere, doText)

doText = 0;

% overall correlation
x = cat(1, allresults(:).(fld));
y = cat(1, allresults(:).criterionshift);
% show line
axis square;

% show lines to indicate origin
xlims = [min(x) max(x)];
ylims = [min(y) max(y)];
plot([0 0], ylims, 'color', [0.5 0.5 0.5], 'linewidth', 0.2);
plot(xlims, [0.5 0.5], 'color', [0.5 0.5 0.5], 'linewidth', 0.2); % if p(repeat), 0.5

% color in different grouos
colors = cbrewer('qual', 'Paired', 10);
transitioncolors = [[0.5 0.5 0.5]; colors([5], :)];
meancolors = [0 0 0; colors([6], :)];
markers = {'o', 's'}; %also indicate with different markers

for a = length(allresults):-1:1, % neutral last
    
    [rho, pval] = corr(allresults(a).(fld), allresults(a).criterionshift, 'type', 'pearson', 'rows', 'complete');
    
    if pval < 0.05,
        % CORRELATION LINE SEPARATELY FOR EACH DATASET?
        p = polyfit(allresults(a).(fld), allresults(a).criterionshift, 1);
        xrangeextra = 0.15*range(allresults(a).(fld));
        xrange = linspace(min(allresults(a).(fld))- xrangeextra, ...
            max(allresults(a).(fld))+xrangeextra, 100);
        yrange = polyval(p, xrange);
        l = plot(xrange, yrange);
        l.Color = meancolors(a, :);
        l.LineWidth = 0.5;
        l.LineStyle = '-';
        %else
        % l.LineStyle = ':';
    end
    
    % PLOT ALL DATAPOINTS IN SPECIFIC COLOR
    s  = scatter(allresults(a).(fld), allresults(a).criterionshift, 10, 'w', markers{a});
	set(s, 'markerfacecolor', transitioncolors(a, :));
	handles{a} = s;
    
end

for a = length(allresults):-1:1, % neutral last
    % also add the group mean
    p = ploterr(nanmean(allresults(a).(fld)), nanmean(allresults(a).criterionshift), 2*nanstd(allresults(a).(fld)) ./ sqrt(length(allresults(a).(fld))), ...
        2*nanstd(allresults(a).criterionshift) ./ sqrt(length(allresults(a).criterionshift)), '.', 'abshhxy', 0);
    set(p(1), 'markersize', 0.1, 'color', meancolors(a, :)); % tiny marker
    set(p(2), 'color', meancolors(a, :), 'linewidth', 1);
    set(p(3), 'color', meancolors(a, :), 'linewidth', 1);
end

axis tight; offsetAxes;

if doText,
    % PRINT THE CORRELATION COEFFICIENT
    txt = {sprintf('r_{%d} = %.3f', length(find(~isnan(y)))-2, rho) sprintf('p = %.3f', pval)};
    if pval < 0.001,
        txt = {sprintf('r_{%d} = %.3f', length(find(~isnan(y)))-2,rho) sprintf('p < 0.001')};
    end
    tt = text(min(get(gca, 'xlim')) + legendWhere*(range(get(gca, 'xlim'))), ...
        min(get(gca, 'ylim')) + 0.8*(range(get(gca, 'ylim'))), ...
        txt, 'fontsize', 5);
else
    tt = [];
end
set(gca, 'color', 'none');

end
