function forestPlot(alldat)

% Code to fit the history-dependent drift diffusion models described in
% Urai AE, Gee JW de, Donner TH (2018) Choice history biases subsequent evidence accumulation. bioRxiv:251595
%
% MIT License
% Copyright (c) Anne Urai, 2018
% anne.urai@gmail.com


ds = [17 10 16 15 1 2 3 7 8 9]; % from the e1b collection script
ds = length(alldat):-1:1;
close all;

global colors;
axiscolors = colors; 

% MAKE AN OVERVIEW PLOT
if numel(alldat) == 3,
subplot(431); 
else
subplot(331); 
end
hold on;
% make a vertical line at zero
plot([0 0], [0.5 length(ds)+0.5], 'color', [0 0 0], 'linewidth', 0.5);

for d = 1:length(ds),
    
    % determine color and marker
    try
        col = alldat(ds(d)).scattercolor;
        mrk = alldat(ds(d)).marker;
        meancol = alldat(ds(d)).meancolor;
    catch
		disp('cannot find colors');
		assert(1==0)
        markercolors = cbrewer('qual', 'Paired', 10);
        transitioncolors = [[0.5 0.5 0.5]; markercolors([7 9 5], :)];
        meancolors = [0 0 0; markercolors([8 10 6], :)];
        markers = {'o', 'v', '^', 's'}; %also indicate with different markers
    
        col 	= transitioncolors(1, :);
        mrk 	= markers{1};
        meancol = meancolors(1, :);
    end
    
    % start at the top
    h = ploterr(alldat(ds(d)).corrz, ...
        length(ds)-d+1,  ...
        {alldat(ds(d)).corrz_ci(1) alldat(ds(d)).corrz_ci(2)}, [], 'o', 'abshhxy', 0.2);
    set(h(1), 'marker', mrk, 'color', col, 'markerfacecolor', meancol, 'markeredgecolor', 'w', ...
        'markersize', 5 , 'linewidth', 0.5);
    set(h(2), 'color', col, 'linewidth', 1);
end

names = {alldat(ds).datasetnames};
for n = 1:length(names),
	if numel(names{n}) > 1,
		names{n} = cat(2, names{n}{1}, ' ', names{n}{2});
	else
		names{n} = names{n}{1};
	end
end
names = fliplr(names);

set(gca, 'ytick', 1:length(ds), 'yticklabel', names);
xlabel('History shift in z');
xlim([-1 1]); offsetAxes;
set(gca, 'xcolor', axiscolors(1, :), 'ycolor', 'k');

plot(nanmean([alldat(ds).corrz]), 0.1, 'd', 'color', 'k', 'markersize', 4);
[h, pval, ci, stats] = ttest([alldat(ds).corrz]);
disp('z bayes factor');
bf = prod([alldat(ds).bfz])
if bf < 100,
    title(sprintf('BF_{10} < 1/100'));
elseif bf > 100,
    title(sprintf('BF_{10} > 100'));
elseif bf < 1,
    title(sprintf('BF_{10} = 1/%.2f', 1/bf));
elseif bf > 1,
    title(sprintf('BF_{10} = %.2f', bf));
end

%% NOW FOR DRIFT CRITERION
% MAKE AN OVERVIEW PLOT
if numel(alldat) == 3,
	sp2 = subplot(432); hold on;
else
	sp2 = subplot(332); hold on;
end

% make a vertical line at zero
plot([0 0], [0.5 length(ds)+0.5], 'color', [0 0 0], 'linewidth', 0.5);

for d = 1:length(ds),
    

    % determine color and marker
    try
        col = alldat(ds(d)).scattercolor;
        mrk = alldat(ds(d)).marker;
        meancol = alldat(ds(d)).meancolor;
    catch
        markercolors = cbrewer('qual', 'Paired', 10);
        transitioncolors = [[0.5 0.5 0.5]; markercolors([7 9 5], :)];
        meancolors = [0 0 0; markercolors([8 10 6], :)];
        markers = {'o', 'v', '^', 's'}; %also indicate with different markers
        
        col = transitioncolors(1, :);
        mrk = markers{1};
        meancol = meancolors(1, :);
    end
    
    
    % start at the top
    h = ploterr(alldat(ds(d)).corrv, ...
        length(ds)-d+1,  ...
        {alldat(ds(d)).corrv_ci(1) alldat(ds(d)).corrv_ci(2)} , [], 'o', 'abshhxy', 0.2);
    set(h(1), 'marker', mrk, 'color', col, 'markerfacecolor', meancol, 'markeredgecolor', 'w', ...
        'markersize', 5, 'linewidth', 0.5);
    set(h(2), 'color', col, 'linewidth', 1);
end

set(gca, 'ytick', 1:length(ds), 'yticklabel', names, 'YAxisLocation', 'right');
xlabel('History shift in v_{bias}');
set(gca, 'xcolor', axiscolors(2, :), 'ycolor', 'k');
xlim([-1 1]); offsetAxes;

% ADD THE AVERAGE??
plot(nanmean([alldat(ds).corrv]), 0.1, 'd', 'color', 'k', 'markersize', 4);
[h, pval, ci, stats] = ttest(fisherz([alldat(ds).corrv]));
disp('v bayes factor');

bf = prod([alldat(ds).bfv])
if bf < 100,
    title(sprintf('BF_{10} < 1/100'));
elseif bf > 100,
    title(sprintf('BF_{10} > 100'));
elseif bf < 1,
    title(sprintf('BF_{10} = 1/%.2f', 1/bf));
elseif bf > 1,
    title(sprintf('BF_{10} = %.2f', bf));
end

% move closer together
sp2.Position(1) = sp2.Position(1) - 0.05;

%% ADD TEXT
for d = 1:length(ds),
    
    if alldat(ds(d)).pdiff < 0.0001,
        txt = sprintf('\\Deltar = %.3f, p < 0.0001', alldat(ds(d)).corrdiff);
    else
        txt = sprintf('\\Deltar = %.3f, p = %.4f', alldat(ds(d)).corrdiff, alldat(ds(d)).pdiff);
    end
    text(-1.3, length(ds)-d+1, txt, ...
        'fontsize', 4);
end


% DO STATS ACROSS DATASETS!
% [h, pval, ci, stats] = ttest(fisherz([alldat(ds).corrv]), fisherz([alldat(ds).corrz]));
[~, h] = suplabel('Correlation with P(repeat)', 'x');
set(h, 'color', 'k');
tightfig;
% print(gcf, '-dpdf', sprintf('~/Data/serialHDDM/forestplot.pdf'));


end

