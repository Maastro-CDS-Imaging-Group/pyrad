%
% Reference paper: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7299262/
%
function [cst] = set_objectives(cst, mask_struct)
% Set mask type and optimization objectives for each mask
for cstIndex=1:size(cst, 1)
    if strcmp(cst{cstIndex,2},"PTVtot")
        cst{cstIndex, 3} = 'TARGET';
        mask_field = getfield(mask_struct.TARGET, "PTVtot");
        penalty = mask_field{1, 2};
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_MaxDVH(penalty, 57.7, 115));
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_MaxDVH(penalty, 55, 1));
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_MinDVH(penalty, 45.5, 99));

    elseif strcmp(cst{cstIndex,2},"BLADDER")
        cst{cstIndex, 3} = 'OAR';
        mask_field = getfield(mask_struct.OAR, cst{cstIndex,2});
        penalty = mask_field{1, 2};
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_MaxDVH(penalty, 45, 35));
    
    elseif strcmp(cst{cstIndex,2},"RECTUM")
        cst{cstIndex, 3} = 'OAR';
        mask_field = getfield(mask_struct.OAR, cst{cstIndex,2});
        penalty = mask_field{1, 2};
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_MaxDVH(penalty, 40, 80));
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_MaxDVH(penalty, 50, 35));

    elseif strcmp(cst{cstIndex,2},"BOWELAREA")
        cst{cstIndex, 3} = 'OAR';
        mask_field = getfield(mask_struct.OAR, cst{cstIndex,2});
        penalty = mask_field{1, 2};
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_MaxDVH(penalty, 40, 30));
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_MaxDVH(penalty, 55, 100));

    elseif strcmp(cst{cstIndex,2},"SMALLBOWEL")
        cst{cstIndex, 3} = 'OAR';
        mask_field = getfield(mask_struct.OAR, cst{cstIndex,2});
        penalty = mask_field{1, 2};
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_MaxDVH(penalty, 40, 30));
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_MaxDVH(penalty, 55, 100));

    elseif strcmp(cst{cstIndex,2},"BODY")
        cst{cstIndex, 3} = 'OAR';
        mask_field = getfield(mask_struct.OTHER, cst{cstIndex,2});
        penalty = mask_field{1, 2};
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_MaxDVH(penalty, 57.7, 100));
    end

end