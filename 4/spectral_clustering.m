clear; clc;

% load dataset
data = csvread('example1.dat');
col1 = data(:,1);
col2 = data(:,2);

% convert column to 1-based indexing if necessary
if min(min(col1, col2)) == 0
    col1 = col1 + 1;
    col2 = col2 + 1;
end

n = max(max(col1, col2));

% Build adjacency matrix (Sparse)
% strict symmetric handling
A = sparse(col1, col2, 1, n, n);
A = max(A, A');          % Make symmetric
A = double(A > 0);       % Remove duplicates/weights if unweighted

fprintf("Loaded graph: %d nodes and %d edges.\n", n, nnz(A)/2);

% Compute Normalized Laplacian (L_sym = I - D^(-1/2) * A * D^(-1/2))
degrees = sum(A, 2);
D_inv_sqrt = spdiags(1 ./ sqrt(degrees + eps), 0, n, n);
L = speye(n) - (D_inv_sqrt * A * D_inv_sqrt);

% Eigen Decomposition
num_eigs_to_view = min(n, 20); % Calculate top 20 to visualize the gap
opts.issym = 1;
opts.tol = 1e-6;
[V_sorted, D_sorted] = eigs(L, num_eigs_to_view, 'SA', opts);
eigenvalues = diag(D_sorted);
[sorted_vals, idx] = sort(eigenvalues, 'ascend');
sorted_vecs = V_sorted(:, idx);

% Determine K (Eigengap Heuristic)
figure;
plot(sorted_vals, 'o-', 'LineWidth', 1.5);
title('Smallest Eigenvalues of Normalized Laplacian');
xlabel('Index'); ylabel('\lambda_i');
grid on;

% Heuristic: Theoretically, K is where the largest jump (gap) occurs
% Visualizing the potential gap:
diff_eigs = diff(sorted_vals);
[~, max_gap_idx] = max(diff_eigs);
xline(max_gap_idx, '--r', ['Suggested K = ' num2str(max_gap_idx)]);

fprintf("Check the eigenvalue plot. Theoretical gap suggests K=%d.\n", max_gap_idx);

% Clustering
K = 4;  % manually set K based on the plot

% Choose first K eigenvectors
X = sorted_vecs(:, 1:K);

% Normalize rows
row_norms = sqrt(sum(X.^2, 2));
row_norms(row_norms < eps) = 1;
Y = X ./ row_norms;

% Run k-means
fprintf("Running K-means...\n");
cluster_idx = kmeans(Y, K, 'Replicates', 20, 'MaxIter', 1000);

% Visualization
[~, order] = sort(cluster_idx);
figure;
spy(A(order, order));
title(sprintf('Adjacency Matrix Sorted by %d Clusters', K));
xlabel('Node Index (Sorted)'); ylabel('Node Index (Sorted)');

% Graph Visualization
G = graph(A);
figure;
t = tiledlayout(1, 2, 'TileSpacing', 'compact');

% Plot 1: Original
nexttile;
plot(G, 'Layout', 'force', 'NodeColor', [0.5 0.5 0.5], 'EdgeAlpha', 0.3);
title('Initial Graph');
axis square;

% Plot 2: Clustered
nexttile;
p = plot(G, 'Layout', 'force', 'EdgeAlpha', 0.1);
title(sprintf('Detected %d Clusters', K));

% Apply colors
cluster_colors = lines(K);
for i = 1:K
    highlight(p, find(cluster_idx == i), 'NodeColor', cluster_colors(i,:));
end
axis square;