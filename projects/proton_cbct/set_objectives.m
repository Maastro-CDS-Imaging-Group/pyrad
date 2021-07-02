%
% Reference paper: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7299262/
%
function [cst] = set_objectives(cst, mask_struct)
% Set mask type and optimization objectives for each mask
% Set mask type and optimization objectives for each mask
for cstIndex=1:size(cst, 1)

    if isfield(mask_struct.TARGET, cst{cstIndex,2})
        cst{cstIndex, 3} = 'TARGET';
        mask_field = getfield(mask_struct.TARGET, cst{cstIndex,2});
        penalty = mask_field{1, 2};
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_SquaredDeviation(penalty, 60));

    elseif isfield(mask_struct.OAR, cst{cstIndex,2})
        cst{cstIndex, 3} = 'OAR';
        mask_field = getfield(mask_struct.OAR, cst{cstIndex,2});
        penalty = mask_field{1, 2};
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_SquaredOverdosing(penalty, 30));

    elseif isfield(mask_struct.OTHER, cst{cstIndex,2})
        cst{cstIndex, 3} = 'OAR';
        mask_field = getfield(mask_struct.OTHER, cst{cstIndex,2});
        penalty = mask_field{1, 2};
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_SquaredOverdosing(penalty, 30));
    end
end
