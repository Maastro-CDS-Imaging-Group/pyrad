function [dose_map, metadata] = dose_calc_fn(config, ct_path, mask_struct)
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Copyright 2015 the matRad development team. 
% 
% This file is part of the matRad project. It is subject to the license 
% terms in the LICENSE file found in the top-level directory of this 
% distribution and at https://github.com/e0404/matRad/LICENSES.txt. No part 
% of the matRad project, including this file, may be copied, modified, 
% propagated, or distributed except according to the terms contained in the 
% LICENSE file.
%
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

matRad_rc

% load patient data, i.e. ct, voi, cst
[ct, cst] = matRad_importPatient(ct_path, mask_struct.masks);

% Set mask type and optimization objectives for each mask
for cstIndex=1:size(cst, 1)

    if isfield(mask_struct.TARGET, cst{cstIndex,2})
        cst{cstIndex, 3} = 'TARGET';
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_SquaredDeviation);

    elseif isfield(mask_struct.OAR, cst{cstIndex,2})
        cst{cstIndex, 3} = 'OAR';
        cst{cstIndex,6}{end+1} = struct(DoseObjectives.matRad_SquaredOverdosing);

    elseif isfield(mask_struct.OTHER, cst{cstIndex,2})
        cst{cstIndex, 3} = 'OAR';
    end
end


pln = get_default_plan(ct, cst);
pln = override_struct(pln, config);


%% generate steering file
stf = matRad_generateStf(ct,cst,pln);

%% dose calculation
if strcmp(pln.radiationMode,'photons')
    dij = matRad_calcPhotonDose(ct,stf,pln,cst);
    %dij = matRad_calcPhotonDoseVmc(ct,stf,pln,cst);
elseif strcmp(pln.radiationMode,'protons') || strcmp(pln.radiationMode,'carbon')
    dij = matRad_calcParticleDose(ct,stf,pln,cst);
end

%% inverse planning for imrt
resultGUI = matRad_fluenceOptimization(dij,cst,pln);

%% sequencing
if strcmp(pln.radiationMode,'photons') && (pln.propOpt.runSequencing || pln.propOpt.runDAO)
    %resultGUI = matRad_xiaLeafSequencing(resultGUI,stf,dij,5);
    %resultGUI = matRad_engelLeafSequencing(resultGUI,stf,dij,5);
    resultGUI = matRad_siochiLeafSequencing(resultGUI,stf,dij,5);
end

%% DAO
if strcmp(pln.radiationMode,'photons') && pln.propOpt.runDAO
   resultGUI = matRad_directApertureOptimization(dij,cst,resultGUI.apertureInfo,resultGUI,pln);
   matRad_visApertureInfo(resultGUI.apertureInfo);
end

%% indicator calculation and show DVH and QI
[dvh,qi] = matRad_indicatorWrapper(cst,pln,resultGUI);

meta = struct();
meta.resolution = [ct.resolution.x ct.resolution.y ct.resolution.z];
meta.imageOrigin = [ct.origin.x ct.origin.y ct.origin.z];

dose_map = resultGUI.physicalDose;
metadata = meta;

end