b = csvread('Save_Point_Cloud/pc_offset_0000.csv');
x = dir('Save_Point_Cloud');
for i = 1:1:size(x, 1) - 3
    filename = ['Save_Point_Cloud/pc_offset_' num2str(i, '%04d') '.csv'];
    a = csvread(filename);
    b = cat(1, a, b);
end
pcshow(b)