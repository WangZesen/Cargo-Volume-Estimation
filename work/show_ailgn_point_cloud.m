c = load('tmp/final.mat');
% a = getfield(c, 'matrix1');
% b = getfield(c, 'matrix2');
% d = cat(1, a, b);
% pcshow(d)

a = getfield(c, 'matrix1');
pcshow(a)
