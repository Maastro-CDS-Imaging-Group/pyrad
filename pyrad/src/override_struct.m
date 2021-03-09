function [original] = override_struct(original, config)
    for [val, key] = original
        if isfield(config, key)
            if isa(val, 'struct')
                original.(key) = override_struct(val, config.(key));
            else
                printf("Overriding %s \n", key);
                original.(key) = config.(key);
                return;
            end
        end
    end
end